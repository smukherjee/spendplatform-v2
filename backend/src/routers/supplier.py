from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.src.schemas.supplier import SupplierCreate, SupplierRead
from backend.src.utils import get_current_role, not_implemented, enforce_role, get_client_id
from backend.src.logging_config import log_audit

router = APIRouter(prefix="/suppliers", tags=["Supplier"])

@router.get("", response_model=List[SupplierRead], summary="List all suppliers")
def get_suppliers(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a list of all suppliers for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_suppliers", user=role, client_id=client_id, details="List suppliers")
    # Example: query = db.query(Supplier).filter(Supplier.client_id == client_id) if role != "superadmin" else db.query(Supplier)
    not_implemented()

@router.post("", response_model=SupplierRead, summary="Create a new supplier")
def post_suppliers(supplier: SupplierCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Creates a new supplier for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_suppliers", user=role, client_id=client_id, details=f"Create supplier: {supplier.name if hasattr(supplier, 'name') else ''}")
    # Example: supplier.client_id = client_id if role != "superadmin" else supplier.client_id
    not_implemented()

@router.get("/{id}", response_model=SupplierRead, summary="Get a supplier by ID")
def get_supplier(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a supplier by ID, filtered by client if not superadmin."""
    log_audit(action="get_supplier", user=role, client_id=client_id, details=f"Get supplier id: {id}")
    not_implemented()

@router.put("/{id}", response_model=SupplierRead, summary="Update a supplier")
def put_supplier(id: int, supplier: SupplierCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Updates a supplier by ID, filtered by client if not superadmin."""
    log_audit(action="put_supplier", user=role, client_id=client_id, details=f"Update supplier id: {id}")
    not_implemented()

@router.delete("/{id}", response_model=None, summary="Delete a supplier")
def delete_supplier(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Deletes a supplier by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_supplier", user=role, client_id=client_id, details=f"Delete supplier id: {id}")
    not_implemented()
