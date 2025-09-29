"""
Production-ready Screen Permissions router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Dict, Any
import logging

from database_async import get_async_db
from cache_async import redis_cache
from models.user import User
from models.screen_permission import Screen, RoleScreenPermission
from models.role import Role
from services.permission_service import PermissionService, PermissionAction, PermissionResult
from utils import get_current_user_async, get_current_role, get_client_id
from schemas.screen_permission import RolePermissionsMatrixUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/screen-permissions", tags=["screen-permissions-async"])


def _is_superadmin_user(user: User) -> bool:
    return any(
        getattr(role, "hierarchy_level", None) == 0 or getattr(role, "name", "").lower() == "superadmin"
        for role in getattr(user, "roles", []) or []
    )


def _resolve_user_level(user: User) -> int:
    levels = []
    for role in getattr(user, "roles", []) or []:
        level = getattr(role, "hierarchy_level", None)
        if isinstance(level, int):
            levels.append(level)
    return min(levels) if levels else 999


def _user_can_access_role(user: User, target_role: Role, requested_client_id: Optional[int]) -> bool:
    if target_role is None:
        return False

    if _is_superadmin_user(user):
        return True

    user_level = _resolve_user_level(user)
    role_level_raw = getattr(target_role, "hierarchy_level", None)
    role_level = role_level_raw if isinstance(role_level_raw, int) else 999

    if role_level < user_level:
        return False

    user_client_id = getattr(user, "client_id", None)
    role_client_id = getattr(target_role, "client_id", None)
    effective_client_id = requested_client_id if requested_client_id is not None else role_client_id

    if role_client_id is None and role_level > user_level:
        # Global roles above the current user's level are inaccessible
        return False

    if role_client_id is not None and role_client_id != user_client_id:
        return False

    if effective_client_id is not None and effective_client_id != user_client_id:
        return False

    return True


def _filter_roles_by_access(user: User, roles: List[Role], client_id: Optional[int]) -> List[Role]:
    return [role for role in roles if _user_can_access_role(user, role, client_id)]

@router.get("/screens", summary="List all screens")
async def get_screens(
    active_only: bool = Query(True, description="Filter by active screens only"),
    category: Optional[str] = Query(None, description="Filter by screen category"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all available screens in the system"""
    try:
        # Check cache first
        cache_key = f"screens:{active_only}:{category or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Build query
        query = select(Screen)
        if active_only:
            query = query.where(Screen.is_active == True)
        if category:
            query = query.where(Screen.category == category)
        
        query = query.order_by(Screen.order_priority, Screen.name)
        
        result = await db.execute(query)
        screens = result.scalars().all()
        
        # Convert to response format
        screen_list = [
            {
                "id": screen.id,
                "name": screen.name,
                "route": screen.route,
                "category": screen.category,
                "icon": screen.icon,
                "description": screen.description,
                "order_priority": screen.order_priority,
                "is_active": screen.is_active,
                "requires_super_admin": getattr(screen, 'requires_super_admin', False)
            }
            for screen in screens
        ]
        
        # Cache for 30 minutes
        await redis_cache.set(cache_key, screen_list, expire=1800)
        
        logger.info(f"Retrieved {len(screen_list)} screens")
        return screen_list
        
    except Exception as e:
        logger.error(f"Error getting screens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve screens"
        )

@router.get("/check", summary="Check screen permission")
async def check_screen_permission(
    screen_route: str = Query(..., description="Screen route to check"),
    action: str = Query("view", description="Action to check (view, create, edit, delete, export, import)"),
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Check if current user has permission to perform an action on a screen"""
    try:
        # Validate action
        try:
            permission_action = PermissionAction(action.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}. Valid actions: {[a.value for a in PermissionAction]}"
            )
        
        # Use permission service
        permission_service = PermissionService(db)
        current_user_id = int(getattr(current_user, "id"))
        current_client_id = getattr(current_user, "client_id", None)
        if current_client_id is not None:
            current_client_id = int(current_client_id)

        result = await permission_service.check_screen_permission(
            current_user_id, screen_route, permission_action, current_client_id
        )
        
        # Format response for frontend compatibility
        response = {
            "screen_route": screen_route,
            "action": action,
            "has_permission": result.has_permission,
            "reason": result.reason,
            "source": result.source,
            "user_id": current_user.id,
            "username": current_user.username,
            "metadata": result.metadata
        }
        
        logger.info(f"Permission check for user {current_user.username} on route {screen_route}/{action}: {result.has_permission}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking screen permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission check failed"
        )

@router.get("/user/{user_id}/accessible-screens", summary="Get user accessible screens")
async def get_user_accessible_screens(
    user_id: int,
    category: Optional[str] = Query(None, description="Filter by category"),
    include_permissions: bool = Query(True, description="Include detailed permissions for each screen"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all screens accessible to a specific user (No auth required - for menu display)"""
    try:
        # Redirect to the unified role-permissions endpoint
        return await get_role_permissions_by_names(
            role_names=None,
            client_id=None, 
            user_id=user_id,
            db=db
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user accessible screens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accessible screens"
        )

@router.get("/roles/{role_id}/permissions", summary="Get role screen permissions")
async def get_role_screen_permissions(
    role_id: int,
    client_id: Optional[int] = Query(None, description="Client ID for client-specific permissions"),
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Get screen permissions for a specific role"""
    try:
        logger.info(f"Fetching role permissions for role_id={role_id}, client_id={client_id}")

        target_role = await db.get(Role, role_id)
        if target_role is None or getattr(target_role, "is_deleted", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        effective_client_id = client_id if client_id is not None else getattr(target_role, "client_id", None)

        if not _user_can_access_role(current_user, target_role, effective_client_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view role permissions"
            )

        # Use permission service
        permission_service = PermissionService(db)
        logger.info(
            "Calling PermissionService.get_role_permissions_matrix with role_id=%s, client_id=%s",
            role_id,
            effective_client_id
        )
        permissions_matrix = await permission_service.get_role_permissions_matrix(role_id, effective_client_id)

        if not permissions_matrix:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found or no permissions configured"
            )

        logger.info(f"Retrieved permissions matrix: {permissions_matrix}")
        return permissions_matrix

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role screen permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role permissions"
        )


@router.put("/roles/{role_id}/permissions", summary="Update role screen permissions")
async def update_role_screen_permissions(
    role_id: int,
    payload: RolePermissionsMatrixUpdate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Update screen permissions for a specific role"""
    try:
        target_role = await db.get(Role, role_id)
        if target_role is None or getattr(target_role, "is_deleted", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        effective_client_id = payload.client_id if payload.client_id is not None else getattr(target_role, "client_id", None)

        if not _user_can_access_role(current_user, target_role, effective_client_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify role permissions"
            )

        permission_service = PermissionService(db)
        screen_payload = [
            screen.model_dump() if hasattr(screen, "model_dump") else screen.dict()
            for screen in payload.screens
        ]

        await permission_service.update_role_permissions_matrix(role_id, effective_client_id, screen_payload)
        updated_matrix = await permission_service.get_role_permissions_matrix(role_id, effective_client_id)

        if not updated_matrix:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permissions not found after update"
            )

        return {
            "message": "Role permissions updated successfully",
            "role_id": role_id,
            "client_id": effective_client_id,
            "permissions": updated_matrix
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role screen permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role permissions"
        )

@router.get("/admin/role-permissions-flat", summary="Get all role permissions in flat format (Admin only)")
async def get_all_role_permissions_flat(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all role-screen permissions in flat format for admin UI"""
    try:
        effective_client_id = client_id
        if not _is_superadmin_user(current_user):
            user_client_id = getattr(current_user, "client_id", None)
            if client_id is not None and client_id != user_client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden for requested client"
                )
            effective_client_id = user_client_id

        # Get all role screen permissions with related data
        query = select(RoleScreenPermission).options(
            selectinload(RoleScreenPermission.screen),
            selectinload(RoleScreenPermission.role)
        )
        
        if effective_client_id:
            query = query.where(
                or_(
                    RoleScreenPermission.client_id == effective_client_id,
                    RoleScreenPermission.client_id.is_(None)
                )
            )
        
        result = await db.execute(query)
        permissions = result.scalars().all()
        
        # Format for frontend ScreenPermissions component
        formatted_permissions = []
        for perm in permissions:
            if perm.screen and perm.role and _user_can_access_role(current_user, perm.role, effective_client_id):
                formatted_permissions.append({
                    "id": perm.id,
                    "role_id": perm.role_id,
                    "screen_id": perm.screen_id,
                    "client_id": perm.client_id,
                    "allow_access": perm.can_view or False,  # Use can_view as allow_access
                    "screen": {
                        "id": perm.screen.id,
                        "name": perm.screen.name,
                        "route": perm.screen.route,
                        "category": perm.screen.category or "Other",
                        "description": perm.screen.description or "",
                        "is_active": perm.screen.is_active
                    },
                    "role_name": perm.role.name
                })
        
        logger.info(f"Retrieved {len(formatted_permissions)} role permissions for admin UI")
        return formatted_permissions
        
    except Exception as e:
        logger.error(f"Error getting flat role permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role permissions"
        )

@router.get("/admin/role-permissions", summary="Get all role permissions (Admin only)")
async def get_all_role_permissions(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Get comprehensive role-screen permissions mapping (Admin access required)"""
    try:
        is_superadmin = _is_superadmin_user(current_user)
        user_client_id = getattr(current_user, "client_id", None)

        effective_client_id = client_id
        if not is_superadmin:
            if client_id is not None and client_id != user_client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden for requested client"
                )
            effective_client_id = user_client_id

        # Check cache first (per-user scope to respect hierarchy)
        cache_key = f"all_role_permissions:{current_user.id}:{effective_client_id or 'global'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result

        # Get all roles and filter by access
        roles_query = select(Role).where(Role.is_deleted == False).order_by(Role.hierarchy_level, Role.name)
        roles_result = await db.execute(roles_query)
        roles = list(roles_result.scalars().all())
        accessible_roles = _filter_roles_by_access(current_user, roles, effective_client_id)

        # Build comprehensive permissions
        all_permissions = []
        permission_service = PermissionService(db)
        
        for role in accessible_roles:
            target_client = effective_client_id if effective_client_id is not None else getattr(role, "client_id", None)
            role_id_value = getattr(role, "id", None)
            if not isinstance(role_id_value, int):
                continue
            matrix = await permission_service.get_role_permissions_matrix(role_id_value, target_client)
            if matrix:
                all_permissions.append(matrix)
        
        result = {
            "client_id": effective_client_id,
            "total_roles": len(all_permissions),
            "role_permissions": all_permissions
        }

        # Cache for 15 minutes
        await redis_cache.set(cache_key, result, expire=900)
        
        logger.info(f"Retrieved role permissions for {len(all_permissions)} roles")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all role permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role permissions"
        )

@router.post("/invalidate-cache/{user_id}", summary="Invalidate user permissions cache")
async def invalidate_user_permissions_cache(
    user_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Invalidate cached permissions for a specific user"""
    try:
        # Permission check - only admins or the user themselves
        is_admin = _is_superadmin_user(current_user) or _resolve_user_level(current_user) <= 1
        if not is_admin:
            current_user_id = getattr(current_user, "id", None)
            if current_user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to invalidate user cache"
                )
        
        # Use permission service
        permission_service = PermissionService(db)
        await permission_service.invalidate_user_permissions_cache(user_id)
        
        return {
            "message": f"Successfully invalidated permission cache for user {user_id}",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error invalidating user permissions cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invalidate user permissions cache"
        )

@router.get("/role-permissions", summary="Get permissions for specific roles (for menu display)")
async def get_role_permissions_by_names(
    role_names: Optional[str] = Query(None, description="Comma-separated list of role names"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    user_id: Optional[int] = Query(None, description="Get user-specific permissions (requires auth when used)"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get permissions for specific roles or user - used by frontend for menu generation"""
    try:
        # Handle user-specific request
        if user_id:
            # Get user from database to extract roles
            user_query = select(User).options(selectinload(User.roles)).where(User.id == user_id)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Extract role names from user
            role_name_list = [role.name for role in user.roles]
            client_id = getattr(user, 'client_id', None)  # Use user's client_id
            
        elif role_names:
            # Parse role names from parameter
            role_name_list = [name.strip() for name in role_names.split(',')]
        else:
            # Default: get all roles when no specific roles requested
            roles_query = select(Role)
            roles_result = await db.execute(roles_query)
            all_roles = roles_result.scalars().all()
            role_name_list = [str(role.name) for role in all_roles]
        
        # Check cache first
        cache_key = f"role_permissions:{':'.join(sorted(role_name_list))}:{client_id or 'global'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get roles from database
        roles_query = select(Role).where(Role.name.in_(role_name_list))
        roles_result = await db.execute(roles_query)
        roles = roles_result.scalars().all()
        
        if not roles:
            return {"role_permissions": [], "screens": []}
        
        # Get role permissions directly from database
        result_permissions = []
        all_accessible_screens = set()
        
        for role in roles:
            # Get role screen permissions
            if client_id:
                perms_query = select(RoleScreenPermission).options(
                    selectinload(RoleScreenPermission.screen)
                ).where(
                    and_(
                        RoleScreenPermission.role_id == role.id,
                        or_(RoleScreenPermission.client_id == client_id, RoleScreenPermission.client_id.is_(None))
                    )
                )
            else:
                perms_query = select(RoleScreenPermission).options(
                    selectinload(RoleScreenPermission.screen)
                ).where(RoleScreenPermission.role_id == role.id)
            
            perms_result = await db.execute(perms_query)
            role_permissions = perms_result.scalars().all()
            
            # Format role permissions
            formatted_screens = []
            for perm in role_permissions:
                if perm.screen and perm.screen.is_active:
                    screen_data = {
                        "screen_id": perm.screen.id,
                        "screen_name": perm.screen.name,
                        "screen_route": perm.screen.route,
                        "can_view": perm.can_view or False,
                        "can_create": perm.can_create or False,
                        "can_edit": perm.can_edit or False,
                        "can_delete": perm.can_delete or False,
                        "can_export": perm.can_export or False,
                        "can_import": perm.can_import or False
                    }
                    formatted_screens.append(screen_data)
                    
                    # Collect accessible screens
                    if perm.can_view is True:
                        all_accessible_screens.add(perm.screen.route)
            
            if formatted_screens:
                result_permissions.append({
                    "role_id": role.id,
                    "role_name": role.name,
                    "screens": formatted_screens,
                    "total_screens": len(formatted_screens)
                })
        
        # Get screen details for accessible screens
        screens_query = select(Screen).where(
            and_(
                Screen.route.in_(list(all_accessible_screens)),
                Screen.is_active == True
            )
        ).order_by(Screen.order_priority, Screen.name)
        
        screens_result = await db.execute(screens_query)
        screens = screens_result.scalars().all()
        
        # Format screens for frontend
        formatted_screens = [
            {
                "id": screen.id,
                "name": screen.name,
                "route": screen.route,
                "description": screen.description,
                "category": screen.category,
                "icon": screen.icon,
                "order_priority": screen.order_priority,
                "parent_screen_id": screen.parent_screen_id,
                "requires_super_admin": screen.requires_super_admin
            }
            for screen in screens
        ]
        
        # Check if this is a request from ScreenPermissions component (no specific roles/users)
        if not role_names and not user_id:
            # Convert to flat format for ScreenPermissions component
            flat_permissions = []
            for role_perm in result_permissions:
                role_id = role_perm["role_id"]
                role_name = role_perm["role_name"]
                for screen in role_perm["screens"]:
                    flat_permissions.append({
                        "id": f"{role_id}-{screen['screen_id']}",  # Generate fake ID
                        "role_id": role_id,
                        "screen_id": screen["screen_id"],
                        "client_id": 1,  # Default client
                        "allow_access": screen["can_view"],
                        "screen": {
                            "id": screen["screen_id"],
                            "name": screen["screen_name"],
                            "route": screen["screen_route"],
                            "category": "Other",  # Default category
                            "description": screen["screen_name"],
                            "is_active": True
                        },
                        "role_name": role_name
                    })
            
            logger.info(f"Retrieved {len(flat_permissions)} flat role permissions for ScreenPermissions component")
            return flat_permissions
        
        result = {
            "role_permissions": result_permissions,
            "screens": formatted_screens,
            "total_roles": len(result_permissions),
            "total_accessible_screens": len(formatted_screens)
        }
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, result, expire=600)
        
        logger.info(f"Retrieved permissions for roles {role_name_list}: {len(formatted_screens)} accessible screens")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role permissions by names: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role permissions"
        )

@router.get("/menu", summary="Get menu data (unified endpoint)")
async def get_menu_data(
    role_names: Optional[str] = Query(None, description="Comma-separated list of role names"),
    user_id: Optional[int] = Query(None, description="User ID for personalized menu"),
    db: AsyncSession = Depends(get_async_db)
):
    """Unified menu endpoint - works with or without authentication"""
    try:
        # Default to superadmin if nothing provided
        if not role_names and not user_id:
            role_names = "superadmin"
        
        # Use the existing role-permissions endpoint logic
        return await get_role_permissions_by_names(
            role_names=role_names,
            client_id=None,
            user_id=user_id,
            db=db
        )
        
    except Exception as e:
        logger.error(f"Error getting menu data: {e}")
        # Return empty menu instead of error to prevent frontend crashes
        return {
            "role_permissions": [],
            "screens": [],
            "total_roles": 0,
            "total_accessible_screens": 0
        }

@router.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "screen-permissions",
        "version": "2.0.0",
        "features": [
            "database_backed_permissions",
            "granular_crud_permissions", 
            "role_based_access_control",
            "user_permission_overrides",
            "caching_optimized",
            "audit_ready"
        ]
    }