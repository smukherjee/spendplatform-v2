"""
Audit Log Router for SpendPlatform v2
US7: Audit & Logging - Administrative access to audit trails
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models.audit_log import AuditLog
from utils import get_current_user

router = APIRouter(prefix="/api/v1/audit", tags=["audit-logging"])


class AuditLogResponse(BaseModel):
    """Response model for audit log data"""
    id: int
    user_id: Optional[int]
    client_id: Optional[int]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    

class AuditLogsListResponse(BaseModel):
    """Response model for audit logs list"""
    logs: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int


@router.get("/logs", response_model=AuditLogsListResponse, summary="Get audit logs for administrators")
def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    action_filter: Optional[str] = Query(None, description="Filter by action type"),
    user_id_filter: Optional[int] = Query(None, description="Filter by user ID"),
    client_id_filter: Optional[int] = Query(None, description="Filter by client ID"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours back to look (1-168)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AuditLogsListResponse:
    """
    US7: Get audit logs for administrators
    
    Access Control:
    - Superadmin: Can see all audit logs
    - Client Admin: Can only see logs for their client
    - Regular users: Access denied
    """
    user_role = current_user.get("role")
    user_client_id = current_user.get("client_id")
    
    # Check permissions
    if user_role not in ["superadmin", "client_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view audit logs"
        )
    
    try:
        # Build query
        query = db.query(AuditLog)
        
        # Apply time filter
        time_filter = datetime.utcnow() - timedelta(hours=hours_back)
        query = query.filter(AuditLog.timestamp >= time_filter)
        
        # Apply role-based filtering
        if user_role == "client_admin":
            # Client admin can only see logs for their client
            query = query.filter(AuditLog.client_id == user_client_id)
        elif user_role == "superadmin" and client_id_filter:
            # Superadmin can filter by specific client
            query = query.filter(AuditLog.client_id == client_id_filter)
        
        # Apply additional filters
        if action_filter:
            query = query.filter(AuditLog.action.ilike(f"%{action_filter}%"))
        
        if user_id_filter:
            query = query.filter(AuditLog.user_id == user_id_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
        
        # Convert to response format
        logs_data = []
        for log in logs:
            logs_data.append({
                "id": log.id,
                "user_id": log.user_id,
                "client_id": log.client_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "timestamp": log.timestamp
            })
        
        return AuditLogsListResponse(
            logs=logs_data,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit logs: {str(e)}"
        )


@router.get("/logs/summary", summary="Get audit log summary statistics")
def get_audit_summary(
    hours_back: int = Query(24, ge=1, le=168, description="Hours back to analyze"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    US7: Get audit log summary statistics for administrators
    """
    user_role = current_user.get("role")
    user_client_id = current_user.get("client_id")
    
    # Check permissions
    if user_role not in ["superadmin", "client_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view audit logs"
        )
    
    try:
        # Build base query
        time_filter = datetime.utcnow() - timedelta(hours=hours_back)
        query = db.query(AuditLog).filter(AuditLog.timestamp >= time_filter)
        
        # Apply role-based filtering
        if user_role == "client_admin":
            query = query.filter(AuditLog.client_id == user_client_id)
        
        # Get all logs for analysis
        logs = query.all()
        
        # Calculate statistics
        total_events = len(logs)
        unique_users = len(set(log.user_id for log in logs if log.user_id))
        unique_clients = len(set(log.client_id for log in logs if log.client_id))
        
        # Event type breakdown
        event_types = {}
        for log in logs:
            event_types[log.action] = event_types.get(log.action, 0) + 1
        
        # Recent activity (last hour)
        recent_time = datetime.utcnow() - timedelta(hours=1)
        recent_events = len([log for log in logs if log.timestamp >= recent_time])
        
        return {
            "period_hours": hours_back,
            "total_events": total_events,
            "unique_users_active": unique_users,
            "unique_clients_active": unique_clients,
            "recent_events_last_hour": recent_events,
            "event_type_breakdown": event_types,
            "analysis_timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audit summary: {str(e)}"
        )