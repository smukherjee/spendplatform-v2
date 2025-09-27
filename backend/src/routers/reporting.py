from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database import get_db
from models.invoice import Invoice
from models.supplier import Supplier
from models.invoice_item import InvoiceItem
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit
import json
import os
import glob
from pathlib import Path

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
        },
        {
            "id": 4,
            "name": "Security Assessment",
            "endpoint": "/reports/security-assessment",
            "description": "OWASP security vulnerability assessment"
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

@router.get("/security-assessment", response_model=Dict, summary="Get security assessment report")
@router.get("/security-assessment/{report_date}", response_model=Dict, summary="Get security assessment report by date")
def get_security_assessment(report_date: Optional[str] = None, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns the latest or specified security assessment report."""
    enforce_role(role, ["client_admin", "superadmin"])  # Only admins can view security reports
    log_audit(action="get_security_assessment", user=role, client_id=client_id, details=f"Get security report for date: {report_date}")
    
    try:
        # Get the security testing directory path
        project_root = Path(__file__).parent.parent.parent  # Go up from backend/src/routers to project root
        security_dir = project_root / "securitytesting"
        
        if not security_dir.exists():
            return {
                "report_type": "security_assessment",
                "client_id": client_id,
                "status": "no_reports",
                "message": "No security reports found. Run security tests first.",
                "instructions": "Execute: python securitytesting/run_security_tests.py"
            }
        
        # Find security report files
        if report_date:
            # Look for specific date
            report_pattern = f"security_summary_{report_date}*.json"
        else:
            # Get the latest report
            report_pattern = "security_summary_*.json"
            
        report_files = list(security_dir.glob(report_pattern))
        
        if not report_files:
            return {
                "report_type": "security_assessment", 
                "client_id": client_id,
                "status": "no_reports",
                "message": f"No security reports found for pattern: {report_pattern}",
                "available_reports": [f.name for f in security_dir.glob("security_summary_*.json")]
            }
        
        # Get the most recent report
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        # Load the security report
        with open(latest_report, 'r') as f:
            security_data = json.load(f)
            
        # Also try to load the full OWASP report for additional details
        owasp_report_file = latest_report.name.replace("security_summary_", "owasp_security_report_")
        full_owasp_path = security_dir / owasp_report_file
        
        additional_details = {}
        if full_owasp_path.exists():
            try:
                with open(full_owasp_path, 'r') as f:
                    owasp_data = json.load(f)
                    additional_details = {
                        "detailed_issues_count": len(owasp_data.get('issues', [])),
                        "test_start_time": owasp_data.get('test_start_time'),
                        "test_end_time": owasp_data.get('test_end_time'),
                        "top_categories": list(set([issue.get('category', 'Unknown') for issue in owasp_data.get('issues', [])]))
                    }
            except Exception as e:
                additional_details = {"error": f"Could not load detailed report: {str(e)}"}
        
        # Prepare the response
        response_data = {
            "report_type": "security_assessment",
            "client_id": client_id,
            "report_file": latest_report.name,
            "report_timestamp": security_data.get("timestamp"),
            "summary": {
                "total_issues": security_data.get("total_issues", 0),
                "critical_issues": security_data.get("critical_issues", 0),
                "high_issues": security_data.get("high_issues", 0),
                "test_duration_seconds": security_data.get("test_duration", 0),
                "owasp_categories_tested": len(security_data.get("owasp_categories_tested", [])),
            },
            "security_status": {
                "overall_risk": "HIGH" if security_data.get("critical_issues", 0) > 0 else 
                              "MEDIUM" if security_data.get("high_issues", 0) > 0 else "LOW",
                "requires_immediate_attention": security_data.get("critical_issues", 0) > 0,
                "last_assessment": security_data.get("timestamp")
            },
            "owasp_categories": security_data.get("owasp_categories_tested", []),
            **additional_details
        }
        
        return response_data
        
    except Exception as e:
        log_audit(action="security_assessment_error", user=role, client_id=client_id, details=f"Error loading security report: {str(e)}")
        return {
            "report_type": "security_assessment",
            "client_id": client_id,
            "status": "error",
            "message": f"Error loading security report: {str(e)}",
            "instructions": "Check security testing directory and file permissions"
        }
