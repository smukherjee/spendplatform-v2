"""
Production-ready permission service for screen-based access control
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Dict, Optional, Set, Tuple, Any
from enum import Enum
import logging

from models.screen_permission import Screen, RoleScreenPermission
from models.user import User
from models.role import Role
from models.client import Client
from cache_async import redis_cache

logger = logging.getLogger(__name__)

class PermissionAction(Enum):
    """Enumeration of possible actions on screens"""
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"

class PermissionResult:
    """Result object for permission checks"""
    def __init__(self, has_permission: bool, reason: str = "", source: str = "", metadata: Optional[Dict[str, Any]] = None):
        self.has_permission = has_permission
        self.reason = reason
        self.source = source  # 'role', 'user_override', 'superadmin', 'denied'
        self.metadata = metadata or {}

class PermissionService:
    """Production-ready permission service with caching and performance optimizations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache_prefix = "permissions"
        self.cache_ttl = 900  # 15 minutes
    
    async def check_screen_permission(
        self, 
        user_id: int, 
        screen_route: str, 
        action: PermissionAction = PermissionAction.VIEW,
        client_id: Optional[int] = None
    ) -> PermissionResult:
        """
        Check if a user has permission to perform an action on a screen
        
        Priority order:
        1. Superadmin override (full access)
        2. Role-based permissions
        3. Default deny
        """
        try:
            # Check cache first
            cache_key = f"{self.cache_prefix}:check:{user_id}:{screen_route}:{action.value}:{client_id or 'global'}"
            cached_result = await redis_cache.get(cache_key)
            if cached_result:
                return PermissionResult(**cached_result)
            
            # Get user with roles
            user_query = (
                select(User)
                .options(
                    selectinload(User.roles)
                )
                .where(User.id == user_id)
            )
            user_result = await self.session.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                result = PermissionResult(False, "User not found", "error")
                await self._cache_result(cache_key, result)
                return result
            
            # Get screen
            screen_query = select(Screen).where(and_(Screen.route == screen_route, Screen.is_active == True))
            screen_result = await self.session.execute(screen_query)
            screen = screen_result.scalar_one_or_none()
            
            if not screen:
                result = PermissionResult(False, f"Screen {screen_route} not found or inactive", "screen_not_found")
                await self._cache_result(cache_key, result)
                return result
            
            # Use user's client_id if not provided, ensuring primitive values
            user_client_id = getattr(user, "client_id", None)
            if user_client_id is not None:
                try:
                    user_client_id = int(user_client_id)
                except (TypeError, ValueError):
                    user_client_id = None

            effective_client_id: Optional[int] = client_id if client_id is not None else user_client_id
            
            # Check if screen requires superadmin
            if getattr(screen, 'requires_super_admin', False):
                is_superadmin = await self._is_superadmin(user)
                if not is_superadmin:
                    result = PermissionResult(False, "Screen requires superadmin access", "superadmin_required")
                    await self._cache_result(cache_key, result)
                    return result
            
            # 1. Check superadmin override
            is_superadmin = await self._is_superadmin(user)
            if is_superadmin:
                result = PermissionResult(True, "Superadmin access granted", "superadmin", {
                    "user_roles": [role.name for role in user.roles]
                })
                await self._cache_result(cache_key, result)
                return result
            
            # 2. Check role-based permissions
            role_ids: List[int] = []
            for role in getattr(user, "roles", []) or []:
                role_identifier = getattr(role, "id", None)
                if role_identifier is None:
                    continue
                try:
                    role_ids.append(int(role_identifier))
                except (TypeError, ValueError):
                    continue

            screen_id_value = getattr(screen, "id", None)
            if screen_id_value is None:
                result = PermissionResult(False, "Screen identifier missing", "error")
                await self._cache_result(cache_key, result)
                return result

            try:
                screen_id_int = int(screen_id_value)
            except (TypeError, ValueError):
                result = PermissionResult(False, "Invalid screen identifier", "error")
                await self._cache_result(cache_key, result)
                return result

            role_permissions = await self._get_role_screen_permissions(
                role_ids,
                screen_id_int,
                effective_client_id
            )
            
            # Check for explicit role-level denies
            for perm in role_permissions:
                if getattr(perm, 'deny_access', False):
                    result = PermissionResult(False, f"Access denied by role {perm.role.name}", "role_deny")
                    await self._cache_result(cache_key, result)
                    return result
            
            # Check for role-level grants
            for perm in role_permissions:
                if getattr(perm, 'allow_full_access', False):
                    result = PermissionResult(True, f"Full access granted by role {perm.role.name}", "role_full_access")
                    await self._cache_result(cache_key, result)
                    return result
                
                # Check specific action permission
                has_action_permission = await self._check_action_permission(perm, action)
                if has_action_permission:
                    result = PermissionResult(
                        True, 
                        f"{action.value.title()} permission granted by role {perm.role.name}", 
                        "role_permission",
                        {"role_name": perm.role.name}
                    )
                    await self._cache_result(cache_key, result)
                    return result
            
            # 3. Default deny
            result = PermissionResult(False, f"No permission found for {action.value} on {screen_route}", "default_deny")
            await self._cache_result(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking screen permission: {e}")
            return PermissionResult(False, "Permission check failed", "error", {"error": str(e)})
    
    async def get_user_accessible_screens(
        self, 
        user_id: int, 
        category: Optional[str] = None,
        include_inactive: bool = False
    ) -> List[Dict]:
        """Get all screens accessible to a user"""
        try:
            cache_key = f"{self.cache_prefix}:accessible:{user_id}:{category or 'all'}:{include_inactive}"
            cached_result = await redis_cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get user with roles
            user_query = select(User).options(selectinload(User.roles)).where(User.id == user_id)
            user_result = await self.session.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                return []
            
            # Build screen query
            screen_query = select(Screen)
            if not include_inactive:
                screen_query = screen_query.where(Screen.is_active == True)
            if category:
                screen_query = screen_query.where(Screen.category == category)
            
            screen_query = screen_query.order_by(Screen.order_priority, Screen.name)
            screen_result = await self.session.execute(screen_query)
            screens = screen_result.scalars().all()
            
            accessible_screens = []
            
            # Check each screen
            for screen in screens:
                screen_id_value = getattr(screen, "id", None)
                screen_route_value = getattr(screen, "route", None)
                if screen_id_value is None or screen_route_value is None:
                    continue

                try:
                    screen_id_value = int(screen_id_value)
                except (TypeError, ValueError):
                    continue

                screen_route_str = str(screen_route_value)

                permission_result = await self.check_screen_permission(
                    user_id,
                    screen_route_str,
                    PermissionAction.VIEW,
                    getattr(user, "client_id", None)
                )
                
                if permission_result.has_permission:
                    # Get all permissions for this screen
                    permissions = {}
                    for action in PermissionAction:
                        perm_result = await self.check_screen_permission(
                            user_id,
                            screen_route_str,
                            action,
                            getattr(user, "client_id", None)
                        )
                        permissions[f"can_{action.value}"] = perm_result.has_permission
                    
                    accessible_screens.append({
                        "id": screen_id_value,
                        "name": getattr(screen, "name", None),
                        "route": screen_route_str,
                        "category": getattr(screen, "category", None),
                        "icon": getattr(screen, "icon", None),
                        "description": getattr(screen, "description", None),
                        "order_priority": getattr(screen, "order_priority", None),
                        "permissions": permissions
                    })
            
            # Cache for 10 minutes
            await redis_cache.set(cache_key, accessible_screens, expire=600)
            return accessible_screens
            
        except Exception as e:
            logger.error(f"Error getting accessible screens: {e}")
            return []
    
    async def get_role_permissions_matrix(self, role_id: int, client_id: Optional[int] = None) -> Dict:
        """Get complete permissions matrix for a role"""
        try:
            cache_key = f"{self.cache_prefix}:role_matrix:{role_id}:{client_id or 'global'}"
            cached_result = await redis_cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get role with permissions
            role_query = (
                select(Role)
                .options(selectinload(Role.screen_permissions))
                .where(Role.id == role_id)
            )
            role_result = await self.session.execute(role_query)
            role = role_result.scalar_one_or_none()
            
            if not role:
                return {}
            
            # Get all screens
            screens_query = select(Screen).where(Screen.is_active == True).order_by(Screen.category, Screen.name)
            screens_result = await self.session.execute(screens_query)
            screens = screens_result.scalars().all()
            
            # Build permissions matrix
            permissions_matrix = {
                "role_id": role.id,
                "role_name": role.name,
                "client_id": client_id,
                "screens": []
            }
            
            for screen in screens:
                role_id_value = getattr(role, "id", None)
                screen_id_value = getattr(screen, "id", None)
                if role_id_value is None or screen_id_value is None:
                    continue

                try:
                    role_id_int = int(role_id_value)
                    screen_id_int = int(screen_id_value)
                except (TypeError, ValueError):
                    continue

                # Get permission for this role and screen
                permission_candidates = await self._get_role_screen_permissions(
                    [role_id_int],
                    screen_id_int,
                    client_id
                )
                permission = permission_candidates[0] if permission_candidates else None
                
                screen_permissions = {
                    "screen_id": screen_id_int,
                    "screen_name": getattr(screen, "name", None),
                    "screen_route": getattr(screen, "route", None),
                    "category": getattr(screen, "category", None),
                    "screen_description": getattr(screen, "description", None),
                    "is_active": getattr(screen, "is_active", None),
                    "can_view": permission.can_view if permission else False,
                    "can_create": permission.can_create if permission else False,
                    "can_edit": permission.can_edit if permission else False,
                    "can_delete": permission.can_delete if permission else False,
                    "can_export": permission.can_export if permission else False,
                    "can_import": permission.can_import if permission else False,
                    "allow_full_access": permission.allow_full_access if permission else False,
                    "deny_access": permission.deny_access if permission else False
                }
                
                permissions_matrix["screens"].append(screen_permissions)
            
            # Cache for 15 minutes
            await redis_cache.set(cache_key, permissions_matrix, expire=900)
            return permissions_matrix
            
        except Exception as e:
            logger.error(f"Error getting role permissions matrix: {e}")
            return {}
    
    async def update_role_permissions_matrix(self, role_id: int, client_id: Optional[int], screen_permissions: List[Dict[str, Any]]) -> bool:
        """Update role permissions for the provided screens"""
        try:
            permission_fields = [
                "can_view",
                "can_create",
                "can_edit",
                "can_delete",
                "can_export",
                "can_import",
                "allow_full_access",
                "deny_access"
            ]

            for perm_data in screen_permissions:
                screen_id = perm_data.get("screen_id")
                if not screen_id:
                    continue

                normalized_values = {
                    field: bool(perm_data.get(field, False))
                    for field in permission_fields
                }

                # If deny_access is enabled, disable other grants
                if normalized_values.get("deny_access"):
                    for field in permission_fields:
                        if field != "deny_access":
                            normalized_values[field] = False

                # If allow_full_access is enabled, grant all CRUD permissions and clear deny flag
                if normalized_values.get("allow_full_access"):
                    normalized_values.update({
                        "can_view": True,
                        "can_create": True,
                        "can_edit": True,
                        "can_delete": True,
                        "can_export": True,
                        "can_import": True,
                        "deny_access": False
                    })

                has_effective_permissions = any(normalized_values.values())

                client_filter = (
                    RoleScreenPermission.client_id.is_(None)
                    if client_id is None
                    else RoleScreenPermission.client_id == client_id
                )

                permission_query = (
                    select(RoleScreenPermission)
                    .where(and_(
                        RoleScreenPermission.role_id == role_id,
                        RoleScreenPermission.screen_id == screen_id,
                        client_filter
                    ))
                )
                existing_result = await self.session.execute(permission_query)
                existing_permission = existing_result.scalar_one_or_none()

                if existing_permission:
                    if has_effective_permissions:
                        for field, value in normalized_values.items():
                            setattr(existing_permission, field, value)
                    else:
                        await self.session.delete(existing_permission)
                elif has_effective_permissions:
                    new_permission = RoleScreenPermission(
                        role_id=role_id,
                        screen_id=screen_id,
                        client_id=client_id,
                        **normalized_values
                    )
                    self.session.add(new_permission)

            await self.session.commit()
            await self.invalidate_role_permissions_cache(role_id)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating role permissions matrix: {e}")
            raise

    async def invalidate_user_permissions_cache(self, user_id: int):
        """Invalidate all cached permissions for a user"""
        try:
            pattern = f"{self.cache_prefix}:*:{user_id}:*"
            await redis_cache.delete_pattern(pattern)
            logger.info(f"Invalidated permission cache for user {user_id}")
        except Exception as e:
            logger.error(f"Error invalidating user permissions cache: {e}")
    
    async def invalidate_role_permissions_cache(self, role_id: int):
        """Invalidate all cached permissions for a role"""
        try:
            pattern = f"{self.cache_prefix}:role_matrix:{role_id}:*"
            await redis_cache.delete_pattern(pattern)
            logger.info(f"Invalidated permission cache for role {role_id}")
        except Exception as e:
            logger.error(f"Error invalidating role permissions cache: {e}")
    
    # Private helper methods
    async def _is_superadmin(self, user: User) -> bool:
        """Check if user has superadmin role"""
        for role in getattr(user, "roles", []) or []:
            if getattr(role, "hierarchy_level", None) == 0:
                return True
            name = getattr(role, "name", "").lower()
            if name in ['superadmin', 'super_admin', 'super admin']:
                return True
        return False
    

    
    async def _get_role_screen_permissions(
        self,
        role_ids: List[int],
        screen_id: int,
        client_id: Optional[int]
    ) -> List[RoleScreenPermission]:
        """Get role-based screen permissions, preferring client-specific rows."""
        if not role_ids:
            return []

        filters = [
            RoleScreenPermission.role_id.in_(role_ids),
            RoleScreenPermission.screen_id == screen_id,
        ]

        if client_id is None:
            filters.append(RoleScreenPermission.client_id.is_(None))
        else:
            filters.append(
                or_(
                    RoleScreenPermission.client_id == client_id,
                    RoleScreenPermission.client_id.is_(None)
                )
            )

        query = (
            select(RoleScreenPermission)
            .options(joinedload(RoleScreenPermission.role))
            .where(and_(*filters))
        )

        result = await self.session.execute(query)
        permissions = list(result.scalars().all())

        if client_id is None or not permissions:
            return permissions

        # Prefer client-specific rows when both scoped and global entries exist.
        preferred_by_role: Dict[int, RoleScreenPermission] = {}
        for permission in permissions:
            role_id_value = getattr(permission, "role_id", None)
            if role_id_value is None:
                continue

            role_id_value = int(role_id_value)
            existing = preferred_by_role.get(role_id_value)

            if existing is None:
                preferred_by_role[role_id_value] = permission
                continue

            is_current_exact = getattr(permission, "client_id", None) == client_id
            is_existing_exact = getattr(existing, "client_id", None) == client_id

            if is_current_exact and not is_existing_exact:
                preferred_by_role[role_id_value] = permission

        return list(preferred_by_role.values())
    
    async def _check_action_permission(self, permission, action: PermissionAction) -> Optional[bool]:
        """Check if permission object grants specific action"""
        if getattr(permission, 'allow_full_access', False):
            return True
        
        action_map = {
            PermissionAction.VIEW: getattr(permission, 'can_view', None),
            PermissionAction.CREATE: getattr(permission, 'can_create', None),
            PermissionAction.EDIT: getattr(permission, 'can_edit', None),
            PermissionAction.DELETE: getattr(permission, 'can_delete', None),
            PermissionAction.EXPORT: getattr(permission, 'can_export', None),
            PermissionAction.IMPORT: getattr(permission, 'can_import', None),
        }
        
        return action_map.get(action)
    
    async def _cache_result(self, cache_key: str, result: PermissionResult):
        """Cache permission result"""
        try:
            cache_data = {
                "has_permission": result.has_permission,
                "reason": result.reason,
                "source": result.source,
                "metadata": result.metadata
            }
            await redis_cache.set(cache_key, cache_data, expire=self.cache_ttl)
        except Exception as e:
            logger.error(f"Error caching permission result: {e}")