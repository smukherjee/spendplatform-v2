from fastapi import APIRouter, Depends, HTTPException
from backend.src.utils import get_current_role, not_implemented, get_client_id
from backend.src.logging_config import log_audit

router = APIRouter(prefix="/reports", tags=["Reporting"])

@router.get("", response_model=None, summary="List all reports")
def get_reports(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a list of all reports for the current client (unless superadmin)."""
    log_audit(action="get_reports", user=role, client_id=client_id, details="List reports")
    # Example: query = db.query(Report).filter(Report.client_id == client_id) if role != "superadmin" else db.query(Report)
    not_implemented()

@router.post("", response_model=None, summary="Create a new report")
def post_reports(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Creates a new report for the current client (unless superadmin)."""
    log_audit(action="post_reports", user=role, client_id=client_id, details="Create report")
    # Example: report.client_id = client_id if role != "superadmin" else report.client_id
    not_implemented()

@router.get("/{id}", response_model=None, summary="Get a report by ID")
def get_report(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a report by ID, filtered by client if not superadmin."""
    log_audit(action="get_report", user=role, client_id=client_id, details=f"Get report id: {id}")
    not_implemented()
