"""Async Role router for SpendPlatform v2 with hierarchy-aware access control."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, cast
import logging

from database_async import get_async_db
from cache_async import redis_cache
from models.role import Role
from models.user import User
from schemas.role import RoleCreate, RoleRead
from utils import get_current_user_async

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/roles", tags=["role-async"])

ROLE_CACHE_TTL_SECONDS = 900


def _is_superadmin(user: User) -> bool:
    return any(
        (getattr(role, "hierarchy_level", None) == 0) or (getattr(role, "name", "").lower() == "superadmin")
        for role in getattr(user, "roles", [])
    )


def _resolve_user_level(user: User) -> int:
    levels = []
    for role in getattr(user, "roles", []) or []:
        level = getattr(role, "hierarchy_level", None)
        if isinstance(level, int):
            levels.append(level)
    return min(levels) if levels else 999


def _user_can_manage_role(user: User, target_role: Role) -> bool:
    if target_role is None:
        return False

    if _is_superadmin(user):
        return True

    user_level = _resolve_user_level(user)
    raw_level = getattr(target_role, "hierarchy_level", None)
    target_level = raw_level if isinstance(raw_level, int) else 999

    if target_level < user_level:
        return False

    user_client_id = getattr(user, "client_id", None)
    target_client_id = getattr(target_role, "client_id", None)

    if target_client_id is None and target_level > user_level:
        # Non-superadmins may only view global roles at their own level
        return False

    if target_client_id is not None and target_client_id != user_client_id:
        return False

    return True


async def _invalidate_role_cache() -> None:
    await redis_cache.delete_pattern("roles:*")


def _serialize_role(role: Role) -> dict:
    return {
        "id": role.id,
        "name": role.name,
        "permissions": role.permissions,
        "hierarchy_level": role.hierarchy_level,
        "parent_role_id": role.parent_role_id,
        "client_id": role.client_id,
    }


@router.get("/", summary="List accessible roles", response_model=List[RoleRead])
@router.get("", summary="List accessible roles", response_model=List[RoleRead])
async def get_roles(
    client_id: Optional[int] = Query(None, description="Filter by client ID when permitted"),
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Return roles the current user is allowed to view based on hierarchy and client scope."""
    try:
        user_level = _resolve_user_level(current_user)
        is_superadmin = _is_superadmin(current_user)
        user_client_id = getattr(current_user, "client_id", None)

        if not is_superadmin:
            if client_id is not None and client_id != user_client_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for requested client")
            effective_client_id = user_client_id
        else:
            effective_client_id = client_id

        cache_key = f"roles:{current_user.id}:{user_level}:{effective_client_id or 'global'}"
        cached = await redis_cache.get(cache_key)
        if cached is not None:
            return cached

        query = select(Role).where(Role.is_deleted == False)

        if not is_superadmin:
            query = query.where(Role.hierarchy_level >= user_level)
            query = query.where(
                or_(
                    Role.client_id == user_client_id,
                    and_(Role.client_id.is_(None), Role.hierarchy_level == user_level)
                )
            )
        elif effective_client_id is not None:
            query = query.where(
                or_(Role.client_id == effective_client_id, Role.client_id.is_(None))
            )

        query = query.order_by(Role.hierarchy_level, Role.name)
        result = await db.execute(query)
        roles = result.scalars().all()

        payload = [_serialize_role(role) for role in roles]
        await redis_cache.set(cache_key, payload, expire=ROLE_CACHE_TTL_SECONDS)
        return payload

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error getting roles")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve roles") from exc


@router.get("/{role_id}", summary="Get role by ID", response_model=RoleRead)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Return details for a specific role if the user has access."""
    role = await db.get(Role, role_id)

    if role is None or getattr(role, "is_deleted", False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if not _user_can_manage_role(current_user, role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions for this role")

    return RoleRead.model_validate(cast(Role, role))


@router.post("", summary="Create a new role", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a role at the same or lower hierarchy level as the requester."""
    is_superadmin = _is_superadmin(current_user)
    user_level = _resolve_user_level(current_user)

    requested_level = (
        role_in.hierarchy_level
        if isinstance(role_in.hierarchy_level, int)
        else user_level
    )
    if not is_superadmin and requested_level < user_level:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create higher-level role")

    target_client_id = role_in.client_id if is_superadmin else getattr(current_user, "client_id", None)
    if not is_superadmin and role_in.client_id is not None and role_in.client_id != target_client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid client scope")

    parent_role_id = role_in.parent_role_id
    if parent_role_id is not None:
        parent_role = await db.get(Role, parent_role_id)
        if parent_role is None or getattr(parent_role, "is_deleted", False):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent role not found")
        if not _user_can_manage_role(current_user, parent_role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot reference parent role")
    else:
        parent_role = None

    new_role = Role(
        name=role_in.name,
        permissions=role_in.permissions,
        hierarchy_level=requested_level,
        parent_role_id=parent_role.id if parent_role else None,
        client_id=target_client_id,
        created_by=getattr(current_user, "id", None)
    )

    db.add(new_role)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists for this client") from exc

    await db.refresh(new_role)
    await _invalidate_role_cache()
    return RoleRead.model_validate(new_role)


@router.put("/{role_id}", summary="Update an existing role", response_model=RoleRead)
async def update_role(
    role_id: int,
    role_in: RoleCreate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a role while respecting hierarchy rules."""
    db_role = await db.get(Role, role_id)
    if db_role is None or getattr(db_role, "is_deleted", False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    role = cast(Role, db_role)

    if not _user_can_manage_role(current_user, role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions for this role")

    is_superadmin = _is_superadmin(current_user)
    user_level = _resolve_user_level(current_user)

    current_level_value = getattr(role, "hierarchy_level", None)
    requested_level = (
        role_in.hierarchy_level
        if isinstance(role_in.hierarchy_level, int)
        else (current_level_value if isinstance(current_level_value, int) else user_level)
    )
    if not is_superadmin and requested_level < user_level:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot elevate role hierarchy")

    target_client_id = role_in.client_id if is_superadmin else getattr(current_user, "client_id", None)
    if not is_superadmin and role_in.client_id is not None and role_in.client_id != target_client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid client scope")

    parent_role_id = role_in.parent_role_id
    if parent_role_id is not None:
        parent_role = await db.get(Role, parent_role_id)
        if parent_role is None or getattr(parent_role, "is_deleted", False):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent role not found")
        if not _user_can_manage_role(current_user, parent_role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot reference parent role")
    else:
        parent_role = None

    setattr(role, "name", role_in.name)
    setattr(role, "permissions", role_in.permissions)
    setattr(role, "hierarchy_level", requested_level)
    parent_role_id_value: Optional[int] = getattr(parent_role, "id", None) if parent_role else None
    setattr(role, "parent_role_id", parent_role_id_value)
    if target_client_id is not None:
        setattr(role, "client_id", target_client_id)
    setattr(role, "updated_by", getattr(current_user, "id", None))

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists for this client") from exc

    await db.refresh(role)
    await _invalidate_role_cache()
    return RoleRead.model_validate(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    """Soft delete a role if permitted."""
    role = await db.get(Role, role_id)
    if role is None or getattr(role, "is_deleted", False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if not _user_can_manage_role(current_user, role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions for this role")

    role.is_deleted = True
    role.updated_by = getattr(current_user, "id", None)

    await db.commit()
    await _invalidate_role_cache()
    return None