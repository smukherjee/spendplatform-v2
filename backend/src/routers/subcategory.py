from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.subcategory import SubCategoryCreate, SubCategoryRead
from utils import get_current_role, not_implemented, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/subcategories", tags=["SubCategory"])

@router.get("", response_model=List[SubCategoryRead], summary="List all subcategories")
def get_subcategories(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a list of all subcategories for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_subcategories", user=role, client_id=client_id, details="List subcategories")
    # Example: query = db.query(Subcategory).filter(Subcategory.client_id == client_id) if role != "superadmin" else db.query(Subcategory)
    not_implemented()

@router.post("", response_model=SubCategoryRead, summary="Create a new subcategory")
def post_subcategories(subcat: SubCategoryCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Creates a new subcategory for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_subcategories", user=role, client_id=client_id, details=f"Create subcategory: {subcat.name if hasattr(subcat, 'name') else ''}")
    # Example: subcat.client_id = client_id if role != "superadmin" else subcat.client_id
    not_implemented()

@router.get("/{id}", response_model=SubCategoryRead, summary="Get a subcategory by ID")
def get_subcategory(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a subcategory by ID, filtered by client if not superadmin."""
    log_audit(action="get_subcategory", user=role, client_id=client_id, details=f"Get subcategory id: {id}")
    not_implemented()

@router.put("/{id}", response_model=SubCategoryRead, summary="Update a subcategory")
def put_subcategory(id: int, subcat: SubCategoryCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Updates a subcategory by ID, filtered by client if not superadmin."""
    log_audit(action="put_subcategory", user=role, client_id=client_id, details=f"Update subcategory id: {id}")
    not_implemented()

@router.delete("/{id}", response_model=None, summary="Delete a subcategory")
def delete_subcategory(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Deletes a subcategory by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_subcategory", user=role, client_id=client_id, details=f"Delete subcategory id: {id}")
    not_implemented()
