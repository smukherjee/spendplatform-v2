from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.supplier import SupplierCreate, SupplierRead
from models.supplier import Supplier
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/suppliers", tags=["Supplier"])

@router.get("", response_model=List[SupplierRead], summary="List all suppliers")
def get_suppliers(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all suppliers for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "user", "superadmin"])
    log_audit(action="get_suppliers", user=role, client_id=client_id, details="List suppliers")
    
    # Query suppliers based on role
    if role == "superadmin":
        suppliers = db.query(Supplier).filter(Supplier.is_deleted == False).all()
    else:
        suppliers = db.query(Supplier).filter(
            Supplier.client_id == client_id,
            Supplier.is_deleted == False
        ).all()
    
    return suppliers

@router.post("", response_model=SupplierRead, summary="Create a new supplier")
def post_suppliers(supplier: SupplierCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new supplier for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_suppliers", user=role, client_id=client_id, details=f"Create supplier: {supplier.name}")
    
    # Create new supplier
    db_supplier = Supplier(
        name=supplier.name,
        contact_info=supplier.contact_info,
        region_id=supplier.region_id,
        client_id=client_id if role != "superadmin" else supplier.client_id,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    
    return db_supplier

@router.get("/{id}", response_model=SupplierRead, summary="Get a supplier by ID")
def get_supplier(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a supplier by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "user", "superadmin"])
    log_audit(action="get_supplier", user=role, client_id=client_id, details=f"Get supplier id: {id}")
    
    # Query supplier based on role
    if role == "superadmin":
        supplier = db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.is_deleted == False
        ).first()
    else:
        supplier = db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.client_id == client_id,
            Supplier.is_deleted == False
        ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return supplier

@router.put("/{id}", response_model=SupplierRead, summary="Update a supplier")
def put_supplier(id: int, supplier: SupplierCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a supplier by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_supplier", user=role, client_id=client_id, details=f"Update supplier id: {id}")
    
    # Find existing supplier
    if role == "superadmin":
        db_supplier = db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.is_deleted == False
        ).first()
    else:
        db_supplier = db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.client_id == client_id,
            Supplier.is_deleted == False
        ).first()
    
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Update fields
    for field, value in supplier.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_supplier, field, value)
    
    setattr(db_supplier, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_supplier)
    
    return db_supplier

@router.delete("/{id}", response_model=None, summary="Delete a supplier")
def delete_supplier(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a supplier by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_supplier", user=role, client_id=client_id, details=f"Delete supplier id: {id}")
    
    # Find existing supplier
    if role == "superadmin":
        db_supplier = db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.is_deleted == False
        ).first()
    else:
        db_supplier = db.query(Supplier).filter(
            Supplier.id == id,
            Supplier.client_id == client_id,
            Supplier.is_deleted == False
        ).first()
    
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Soft delete
    setattr(db_supplier, "is_deleted", True)
    setattr(db_supplier, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Supplier deleted successfully"}
