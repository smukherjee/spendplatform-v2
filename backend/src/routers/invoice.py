from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.invoice import InvoiceCreate, InvoiceRead
from models.invoice import Invoice
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit
from datetime import datetime

router = APIRouter(prefix="/invoices", tags=["Invoice"])

@router.get("", response_model=List[InvoiceRead], summary="List all invoices")
def get_invoices(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all invoices for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "user", "superadmin"])
    log_audit(action="get_invoices", user=role, client_id=client_id, details="List invoices")
    
    # Query invoices based on role
    if role == "superadmin":
        invoices = db.query(Invoice).filter(Invoice.is_deleted == False).all()
    else:
        invoices = db.query(Invoice).filter(
            Invoice.client_id == client_id,
            Invoice.is_deleted == False
        ).all()
    
    return invoices

@router.post("", response_model=InvoiceRead, summary="Create a new invoice")
def post_invoices(invoice: InvoiceCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new invoice for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "user", "superadmin"])
    log_audit(action="post_invoices", user=role, client_id=client_id, details=f"Create invoice: {invoice.invoice_number}")
    
    # Use the date directly since it's now a date object from Pydantic
    invoice_date = invoice.date
    
    # Create new invoice
    db_invoice = Invoice(
        invoice_number=invoice.invoice_number,
        date=invoice_date,
        supplier_id=invoice.supplier_id,
        business_unit_id=invoice.business_unit_id,
        client_id=client_id if role != "superadmin" else invoice.client_id,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice

@router.get("/{id}", response_model=InvoiceRead, summary="Get an invoice by ID")
def get_invoice(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns an invoice by ID, filtered by client if not superadmin."""
    log_audit(action="get_invoice", user=role, client_id=client_id, details=f"Get invoice id: {id}")
    
    # Query invoice based on role
    if role == "superadmin":
        invoice = db.query(Invoice).filter(
            Invoice.id == id,
            Invoice.is_deleted == False
        ).first()
    else:
        invoice = db.query(Invoice).filter(
            Invoice.id == id,
            Invoice.client_id == client_id,
            Invoice.is_deleted == False
        ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice

@router.put("/{id}", response_model=InvoiceRead, summary="Update an invoice")
def put_invoice(id: int, invoice: InvoiceCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates an invoice by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "user", "superadmin"])
    log_audit(action="put_invoice", user=role, client_id=client_id, details=f"Update invoice id: {id}")
    
    # Find existing invoice
    if role == "superadmin":
        db_invoice = db.query(Invoice).filter(
            Invoice.id == id,
            Invoice.is_deleted == False
        ).first()
    else:
        db_invoice = db.query(Invoice).filter(
            Invoice.id == id,
            Invoice.client_id == client_id,
            Invoice.is_deleted == False
        ).first()
    
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update fields using setattr to handle SQLAlchemy columns properly
    for field, value in invoice.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_invoice, field, value)
    
    setattr(db_invoice, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice

@router.delete("/{id}", response_model=None, summary="Delete an invoice")
def delete_invoice(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes an invoice by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_invoice", user=role, client_id=client_id, details=f"Delete invoice id: {id}")
    
    # Find existing invoice
    if role == "superadmin":
        db_invoice = db.query(Invoice).filter(
            Invoice.id == id,
            Invoice.is_deleted == False
        ).first()
    else:
        db_invoice = db.query(Invoice).filter(
            Invoice.id == id,
            Invoice.client_id == client_id,
            Invoice.is_deleted == False
        ).first()
    
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Soft delete
    setattr(db_invoice, "is_deleted", True)
    setattr(db_invoice, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Invoice deleted successfully"}
