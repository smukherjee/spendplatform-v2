from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.invoice_item import InvoiceItemCreate, InvoiceItemRead
from models.invoice_item import InvoiceItem
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/invoice-items", tags=["InvoiceItem"])

@router.get("", response_model=List[InvoiceItemRead], summary="List all invoice items")
def get_invoice_items(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all invoice items for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin", "user"])
    log_audit(action="get_invoice_items", user=role, client_id=client_id, details="List invoice items")
    
    # Query invoice items based on role
    if role == "superadmin":
        items = db.query(InvoiceItem).filter(InvoiceItem.is_deleted == False).all()
    else:
        items = db.query(InvoiceItem).filter(
            InvoiceItem.client_id == client_id,
            InvoiceItem.is_deleted == False
        ).all()
    
    return items

@router.post("", response_model=InvoiceItemRead, summary="Create a new invoice item")
def post_invoice_items(item: InvoiceItemCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new invoice item for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_invoice_items", user=role, client_id=client_id, details=f"Create invoice item: {item.item_number}")
    
    # Create new invoice item
    db_item = InvoiceItem(
        invoice_id=item.invoice_id,
        item_number=item.item_number,
        type=item.type if hasattr(item, 'type') else None,
        description=item.description if hasattr(item, 'description') else None,
        subcategory_l1_id=item.subcategory_l1_id if hasattr(item, 'subcategory_l1_id') else None,
        subcategory_l2_id=item.subcategory_l2_id if hasattr(item, 'subcategory_l2_id') else None,
        subcategory_l3_id=item.subcategory_l3_id if hasattr(item, 'subcategory_l3_id') else None,
        subcategory_l4_id=item.subcategory_l4_id if hasattr(item, 'subcategory_l4_id') else None,
        qty=item.qty if hasattr(item, 'qty') else None,
        unit_of_measure_id=item.unit_of_measure_id if hasattr(item, 'unit_of_measure_id') else None,
        currency_id=item.currency_id if hasattr(item, 'currency_id') else None,
        unit_price=item.unit_price if hasattr(item, 'unit_price') else None,
        total_amount=item.total_amount if hasattr(item, 'total_amount') else None,
        client_id=client_id if role != "superadmin" else item.client_id,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.get("/{id}", response_model=InvoiceItemRead, summary="Get an invoice item by ID")
def get_invoice_item(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns an invoice item by ID, filtered by client if not superadmin."""
    log_audit(action="get_invoice_item", user=role, client_id=client_id, details=f"Get invoice item id: {id}")
    
    # Query invoice item based on role
    if role == "superadmin":
        item = db.query(InvoiceItem).filter(
            InvoiceItem.id == id,
            InvoiceItem.is_deleted == False
        ).first()
    else:
        item = db.query(InvoiceItem).filter(
            InvoiceItem.id == id,
            InvoiceItem.client_id == client_id,
            InvoiceItem.is_deleted == False
        ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    
    return item

@router.put("/{id}", response_model=InvoiceItemRead, summary="Update an invoice item")
def put_invoice_item(id: int, item: InvoiceItemCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates an invoice item by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_invoice_item", user=role, client_id=client_id, details=f"Update invoice item id: {id}")
    
    # Find existing invoice item
    if role == "superadmin":
        db_item = db.query(InvoiceItem).filter(
            InvoiceItem.id == id,
            InvoiceItem.is_deleted == False
        ).first()
    else:
        db_item = db.query(InvoiceItem).filter(
            InvoiceItem.id == id,
            InvoiceItem.client_id == client_id,
            InvoiceItem.is_deleted == False
        ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    
    # Update fields
    for field, value in item.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_item, field, value)
    
    setattr(db_item, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.delete("/{id}", response_model=None, summary="Delete an invoice item")
def delete_invoice_item(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes an invoice item by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_invoice_item", user=role, client_id=client_id, details=f"Delete invoice item id: {id}")
    
    # Find existing invoice item
    if role == "superadmin":
        db_item = db.query(InvoiceItem).filter(
            InvoiceItem.id == id,
            InvoiceItem.is_deleted == False
        ).first()
    else:
        db_item = db.query(InvoiceItem).filter(
            InvoiceItem.id == id,
            InvoiceItem.client_id == client_id,
            InvoiceItem.is_deleted == False
        ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    
    # Soft delete
    setattr(db_item, "is_deleted", True)
    setattr(db_item, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Invoice item deleted successfully"}