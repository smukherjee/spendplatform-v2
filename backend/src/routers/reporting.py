from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.orm import Session
from database import get_db
from models.invoice import Invoice
from models.supplier import Supplier
from models.invoice_item import InvoiceItem
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/reports", tags=["Reporting"])

@router.get("", response_model=List[Dict], summary="List available reports")
def get_available_reports(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of available reports."""
    enforce_role(role, ["client_admin", "superadmin", "user"])
    log_audit(action="get_available_reports", user=role, client_id=client_id, details="List available reports")
    
    return [
        {
            "id": 1,
            "name": "Invoice Summary",
            "endpoint": "/reports/invoice-summary",
            "description": "Summary statistics for invoices"
        },
        {
            "id": 2,
            "name": "Supplier Analysis", 
            "endpoint": "/reports/supplier-analysis",
            "description": "Analysis of supplier data"
        },
        {
            "id": 3,
            "name": "Spend by Category",
            "endpoint": "/reports/spend-by-category", 
            "description": "Spending breakdown by category"
        }
    ]

@router.get("/invoice-summary", response_model=Dict, summary="Get invoice summary report")
def get_invoice_summary(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns invoice summary statistics for the current client."""
    enforce_role(role, ["client_admin", "superadmin", "user"])
    log_audit(action="get_invoice_summary", user=role, client_id=client_id, details="Get invoice summary report")
    
    # Query invoices based on role
    if role == "superadmin":
        invoice_query = db.query(Invoice).filter(Invoice.is_deleted == False)
    else:
        invoice_query = db.query(Invoice).filter(
            Invoice.client_id == client_id,
            Invoice.is_deleted == False
        )
    
    total_invoices = invoice_query.count()
    total_amount = sum([inv.total_amount or 0 for inv in invoice_query.all()])
    
    return {
        "report_type": "invoice_summary",
        "client_id": client_id,
        "total_invoices": total_invoices,
        "total_amount": total_amount,
        "currency": "USD"  # TODO: Make this dynamic based on client settings
    }

@router.get("/supplier-analysis", response_model=Dict, summary="Get supplier analysis report")
def get_supplier_analysis(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns supplier analysis for the current client."""
    enforce_role(role, ["client_admin", "superadmin", "user"])
    log_audit(action="get_supplier_analysis", user=role, client_id=client_id, details="Get supplier analysis report")
    
    # Query suppliers based on role
    if role == "superadmin":
        supplier_query = db.query(Supplier).filter(Supplier.is_deleted == False)
    else:
        supplier_query = db.query(Supplier).filter(
            Supplier.client_id == client_id,
            Supplier.is_deleted == False
        )
    
    total_suppliers = supplier_query.count()
    suppliers = supplier_query.all()
    
    return {
        "report_type": "supplier_analysis",
        "client_id": client_id,
        "total_suppliers": total_suppliers,
        "active_suppliers": len([s for s in suppliers if not s.is_deleted])
    }

@router.get("/spend-by-category", response_model=Dict, summary="Get spend analysis by category")
def get_spend_by_category(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns spend analysis by category for the current client."""
    enforce_role(role, ["client_admin", "superadmin", "user"])
    log_audit(action="get_spend_by_category", user=role, client_id=client_id, details="Get spend by category report")
    
    # Query invoice items based on role
    if role == "superadmin":
        item_query = db.query(InvoiceItem).filter(InvoiceItem.is_deleted == False)
    else:
        item_query = db.query(InvoiceItem).filter(
            InvoiceItem.client_id == client_id,
            InvoiceItem.is_deleted == False
        )
    
    items = item_query.all()
    total_spend = sum([item.total_amount or 0 for item in items])
    
    # Group by type (this could be enhanced to use actual category relationships)
    category_spend = {}
    for item in items:
        category = item.type or "Uncategorized"
        if category not in category_spend:
            category_spend[category] = 0
        category_spend[category] += item.total_amount or 0
    
    return {
        "report_type": "spend_by_category",
        "client_id": client_id,
        "total_spend": total_spend,
        "category_breakdown": category_spend
    }
