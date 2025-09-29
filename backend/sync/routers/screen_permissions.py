from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
import time
from database import get_db
from models.screen_permission import Screen, RoleScreenPermission
from models.role import Role
from models.user import User
from schemas.screen_permission import (
    ScreenCreate, ScreenRead, 
    RoleScreenPermissionCreate, RoleScreenPermissionRead, RoleScreenPermissionWithDetails,

    BulkRolePermissionUpdate, PermissionCheckResponse
)
from utils import get_current_role, get_client_id, get_current_user_id, enforce_role
from logging_config import log_audit

router = APIRouter(prefix="/screen-permissions", tags=["ScreenPermissions"])

# Screen management endpoints
@router.get("/screens", response_model=List[ScreenRead], summary="List all screens")
def get_screens(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Get all available screens in the system."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_screens", user=role, client_id=client_id, details="List all screens")
    
    screens = db.query(Screen).filter(Screen.is_active == True).order_by(Screen.category, Screen.name).all()
    return screens

@router.post("/screens", response_model=ScreenRead, summary="Create a new screen")
def create_screen(screen: ScreenCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Create a new screen (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="create_screen", user=role, client_id=client_id, details=f"Create screen: {screen.name}")
    
    # Check if screen already exists
    existing = db.query(Screen).filter(Screen.name == screen.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Screen with this name already exists")
    
    existing_route = db.query(Screen).filter(Screen.route == screen.route).first()
    if existing_route:
        raise HTTPException(status_code=400, detail="Screen with this route already exists")
    
    db_screen = Screen(**screen.model_dump())
    db.add(db_screen)
    db.commit()
    db.refresh(db_screen)
    return db_screen

# Role permission endpoints
@router.get("/role-permissions", response_model=List[RoleScreenPermissionWithDetails], summary="Get role permissions")
def get_role_permissions(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Get role-based screen permissions for current client (or all for superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_role_permissions", user=role, client_id=client_id, details="List role permissions")
    
    query = db.query(RoleScreenPermission).options(
        joinedload(RoleScreenPermission.screen),
        joinedload(RoleScreenPermission.role)
    )
    
    if role != "superadmin":
        query = query.filter(RoleScreenPermission.client_id == client_id)
    
    permissions = query.all()
    
    # Format response with additional details
    result = []
    for perm in permissions:
        result.append({
            **perm.__dict__,
            "screen": perm.screen,
            "role_name": perm.role.name if perm.role else None
        })
    
    return result

@router.post("/role-permissions/bulk", response_model=List[RoleScreenPermissionRead], summary="Bulk update role permissions")
def bulk_update_role_permissions(update: BulkRolePermissionUpdate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Bulk update role permissions for a specific role and client."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="bulk_update_role_permissions", user=role, client_id=client_id, details=f"Bulk update for role {update.role_id}")
    
    # Verify role exists
    db_role = db.query(Role).filter(Role.id == update.role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # For non-superadmin, ensure they can only update their client's permissions
    target_client_id = client_id if role != "superadmin" else update.client_id
    
    results = []
    for perm_data in update.permissions:
        screen_id = perm_data["screen_id"]
        allow_access = perm_data["allow_access"]
        
        # Check if permission already exists
        existing = db.query(RoleScreenPermission).filter(
            RoleScreenPermission.role_id == update.role_id,
            RoleScreenPermission.screen_id == screen_id,
            RoleScreenPermission.client_id == target_client_id
        ).first()
        
        if existing:
            existing.allow_access = allow_access
            results.append(existing)
        else:
            new_perm = RoleScreenPermission(
                role_id=update.role_id,
                screen_id=screen_id,
                client_id=target_client_id,
                allow_access=allow_access
            )
            db.add(new_perm)
            results.append(new_perm)
    
    db.commit()
    for result in results:
        db.refresh(result)
    
    # Log cache invalidation need
    log_audit(action="permission_update_cache_invalidation", user=role, client_id=client_id, details=f"Role permissions updated for role {update.role_id}, cache should be cleared")
    
    return results

# Role-based permissions only - user permissions removed

# Cache invalidation endpoint
@router.post("/invalidate-cache", summary="Invalidate permission cache")
def invalidate_permission_cache(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Endpoint to signal frontend to clear permission cache."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="invalidate_permission_cache", user=role, client_id=client_id, details="Permission cache invalidation requested")
    
    return {"message": "Cache invalidation signal sent", "timestamp": int(time.time())}

# Permission check endpoint
@router.get("/check", response_model=PermissionCheckResponse, summary="Check screen access permission")
def check_screen_permission(screen_route: str, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Check if current user has access to a specific screen."""
    log_audit(action="check_screen_permission", user=role, client_id=client_id, details=f"Check access to {screen_route}")
    
    # Superadmin always has access
    if role == "superadmin":
        return PermissionCheckResponse(
            screen_route=screen_route,
            has_access=True,
            source="superadmin",
            message="Superadmin has access to all screens"
        )
    
    # Find the screen
    screen = db.query(Screen).filter(Screen.route == screen_route).first()
    if not screen:
        return PermissionCheckResponse(
            screen_route=screen_route,
            has_access=False,
            source="denied",
            message="Screen not found"
        )
    
    # Check role-based permissions (user-specific permissions removed)
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.roles:
        return PermissionCheckResponse(
            screen_route=screen_route,
            has_access=False,
            source="denied",
            message="User has no roles assigned"
        )
    
    # Check all user's roles for permission
    for user_role in user.roles:
        role_perm = db.query(RoleScreenPermission).filter(
            RoleScreenPermission.role_id == user_role.id,
            RoleScreenPermission.screen_id == screen.id,
            RoleScreenPermission.client_id == client_id
        ).first()
        
        if role_perm and bool(role_perm.allow_access):
            return PermissionCheckResponse(
                screen_route=screen_route,
                has_access=True,
                source="role",
                message=f"Access granted via role: {user_role.name}"
            )
    
    return PermissionCheckResponse(
        screen_route=screen_route,
        has_access=False,
        source="denied",
        message="No permissions found for this screen"
    )