from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.user import UserCreate, UserRead
from utils import get_current_role, not_implemented, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/users", tags=["User"])

@router.get("", response_model=List[UserRead], summary="List all users")
def get_users(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a list of all users for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_users", user=role, client_id=client_id, details=f"List users")
    # Example: query = db.query(User).filter(User.client_id == client_id) if role != "superadmin" else db.query(User)
    not_implemented()

@router.post("", response_model=UserRead, summary="Create a new user")
def post_users(user: UserCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Creates a new user for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_users", user=role, client_id=client_id, details=f"Create user: {user.username}")
    # Example: user.client_id = client_id if role != "superadmin" else user.client_id
    not_implemented()

@router.get("/{id}", response_model=UserRead, summary="Get a user by ID")
def get_user(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a user by ID, filtered by client if not superadmin."""
    log_audit(action="get_user", user=role, client_id=client_id, details=f"Get user id: {id}")
    not_implemented()

@router.put("/{id}", response_model=UserRead, summary="Update a user")
def put_user(id: int, user: UserCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Updates a user by ID, filtered by client if not superadmin."""
    log_audit(action="put_user", user=role, client_id=client_id, details=f"Update user id: {id}")
    not_implemented()

@router.delete("/{id}", response_model=None, summary="Delete a user")
def delete_user(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Deletes a user by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_user", user=role, client_id=client_id, details=f"Delete user id: {id}")
    not_implemented()
