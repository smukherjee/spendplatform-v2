from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.src.schemas.invoice import InvoiceCreate, InvoiceRead
from backend.src.utils import get_current_role, not_implemented, enforce_role, get_client_id
from backend.src.logging_config import log_audit

router = APIRouter(prefix="/invoices", tags=["Invoice"])

@router.get("", response_model=List[InvoiceRead], summary="List all invoices")
def get_invoices(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a list of all invoices for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_invoices", user=role, client_id=client_id, details="List invoices")
    # Example: query = db.query(Invoice).filter(Invoice.client_id == client_id) if role != "superadmin" else db.query(Invoice)
    not_implemented()

@router.post("", response_model=InvoiceRead, summary="Create a new invoice")
def post_invoices(invoice: InvoiceCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Creates a new invoice for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_invoices", user=role, client_id=client_id, details=f"Create invoice: {invoice.invoice_number}")
    # Example: invoice.client_id = client_id if role != "superadmin" else invoice.client_id
    not_implemented()

@router.get("/{id}", response_model=InvoiceRead, summary="Get an invoice by ID")
def get_invoice(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns an invoice by ID, filtered by client if not superadmin."""
    log_audit(action="get_invoice", user=role, client_id=client_id, details=f"Get invoice id: {id}")
    # Example: query = db.query(Invoice).filter(Invoice.id == id, Invoice.client_id == client_id) if role != "superadmin" else db.query(Invoice).filter(Invoice.id == id)
    not_implemented()

@router.put("/{id}", response_model=InvoiceRead, summary="Update an invoice")
def put_invoice(id: int, invoice: InvoiceCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Updates an invoice by ID, filtered by client if not superadmin."""
    log_audit(action="put_invoice", user=role, client_id=client_id, details=f"Update invoice id: {id}")
    not_implemented()

@router.delete("/{id}", response_model=None, summary="Delete an invoice")
def delete_invoice(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Deletes an invoice by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_invoice", user=role, client_id=client_id, details=f"Delete invoice id: {id}")
    not_implemented()
