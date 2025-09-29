from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from models.audit import AuditLog
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs", response_model=List[dict], summary="Get audit logs")
def get_audit_logs(
    role: str = Depends(get_current_role), 
    client_id: int = Depends(get_client_id), 
    db: Session = Depends(get_db),
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """Returns audit logs for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_audit_logs", user=role, client_id=client_id, details=f"Get audit logs (limit: {limit}, offset: {offset})")
    
    # Query audit logs based on role
    query = db.query(AuditLog)
    if role != "superadmin":
        query = query.filter(AuditLog.client_id == client_id)
    
    audit_logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    
    # Convert to dict for response
    result = []
    for log in audit_logs:
        result.append({
            "id": log.id,
            "user": log.user,
            "client_id": log.client_id,
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp
        })
    
    return result
