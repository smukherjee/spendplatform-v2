from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.role import RoleCreate, RoleRead
from models.role import Role
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/roles", tags=["Role"])

@router.get("", response_model=List[RoleRead], summary="List all roles")
def get_roles(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all roles (admin level access)."""
    enforce_role(role, ["superadmin", "client_admin"])
    log_audit(action="get_roles", user=role, client_id=client_id, details="List roles")
    
    roles = db.query(Role).filter(Role.is_deleted == False).all()
    # Convert to dict to exclude relationships that aren't in the schema
    return [{"id": r.id, "name": r.name, "permissions": r.permissions} for r in roles]

@router.post("", response_model=RoleRead, summary="Create a new role")
def post_roles(role_in: RoleCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new role (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="post_roles", user=role, client_id=client_id, details=f"Create role: {role_in.name}")
    
    # Create new role
    db_role = Role(
        name=role_in.name,
        permissions=role_in.permissions if hasattr(role_in, 'permissions') else None,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    
    return {"id": db_role.id, "name": db_role.name, "permissions": db_role.permissions}

@router.get("/{id}", response_model=RoleRead, summary="Get a role by ID")
def get_role(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a specific role by ID."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_role", user=role, client_id=client_id, details=f"Get role {id}")
    
    role_obj = db.query(Role).filter(
        Role.id == id,
        Role.is_deleted == False
    ).first()
    
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
        
    return {"id": role_obj.id, "name": role_obj.name, "permissions": role_obj.permissions}

@router.put("/{id}", response_model=RoleRead, summary="Update a role")
def put_role(id: int, role_in: RoleCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a role by ID (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="put_role", user=role, client_id=client_id, details=f"Update role id: {id}")
    
    # Find existing role
    db_role = db.query(Role).filter(
        Role.id == id,
        Role.is_deleted == False
    ).first()
    
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Update fields
    for field, value in role_in.dict().items():
        setattr(db_role, field, value)
    
    setattr(db_role, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_role)
    
    return {"id": db_role.id, "name": db_role.name, "permissions": db_role.permissions}

@router.delete("/{id}", response_model=None, summary="Delete a role")
def delete_role(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a role by ID (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="delete_role", user=role, client_id=client_id, details=f"Delete role id: {id}")
    
    # Find existing role
    db_role = db.query(Role).filter(
        Role.id == id,
        Role.is_deleted == False
    ).first()
    
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Soft delete
    setattr(db_role, "is_deleted", True)
    setattr(db_role, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Role deleted successfully"}