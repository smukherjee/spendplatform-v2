"""
Async Audit router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import random

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audit", tags=["audit-async"])


@router.get("/logs", summary="Get audit logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns audit logs with filtering and pagination"""
    try:
        # Check cache first
        cache_key = f"audit_logs:{skip}:{limit}:{action or 'all'}:{user_id or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Generate mock audit logs
        actions = ["login", "logout", "create_invoice", "approve_invoice", "update_user", "delete_supplier", "export_report"]
        users = ["superadmin", "client_admin", "john.doe", "jane.smith", "mike.johnson"]
        
        all_logs = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(1, 201):  # Generate 200 mock audit logs
            log_date = base_date + timedelta(hours=random.randint(0, 720))  # 30 days worth
            selected_action = random.choice(actions)
            selected_user = random.choice(users)
            
            all_logs.append({
                "id": i,
                "action": selected_action,
                "user_id": random.randint(1, 5),
                "username": selected_user,
                "client_id": 1,
                "resource_type": selected_action.split('_')[-1] if '_' in selected_action else "system",
                "resource_id": random.randint(1, 100) if selected_action not in ["login", "logout"] else None,
                "details": f"User {selected_user} performed {selected_action}",
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0 (compatible; SpendPlatform/2.0)",
                "timestamp": log_date.isoformat(),
                "status": "success" if random.random() > 0.1 else "failed"
            })
        
        # Apply filters
        if action:
            all_logs = [log for log in all_logs if log["action"] == action]
        
        if user_id:
            all_logs = [log for log in all_logs if log["user_id"] == user_id]
        
        # Sort by timestamp (newest first)
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        total = len(all_logs)
        logs = all_logs[skip:skip + limit]
        
        result = {
            "items": logs,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total
        }
        
        # Cache for 2 minutes
        await redis_cache.set(cache_key, result, expire=120)
        
        logger.info(f"Retrieved {len(logs)} audit logs (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.get("/stats", summary="Get audit statistics")
async def get_audit_stats(db: AsyncSession = Depends(get_async_db)):
    """Returns audit statistics"""
    try:
        # Check cache first
        cache_key = "audit_stats"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock audit statistics
        stats = {
            "total_events": 15432,
            "events_today": 127,
            "events_this_week": 892,
            "events_this_month": 3456,
            "top_actions": [
                {"action": "login", "count": 3421, "percentage": 22.2},
                {"action": "create_invoice", "count": 2156, "percentage": 14.0},
                {"action": "approve_invoice", "count": 1897, "percentage": 12.3},
                {"action": "update_user", "count": 1234, "percentage": 8.0},
                {"action": "export_report", "count": 987, "percentage": 6.4}
            ],
            "top_users": [
                {"username": "superadmin", "count": 2341, "percentage": 15.2},
                {"username": "client_admin", "count": 1876, "percentage": 12.2},
                {"username": "john.doe", "count": 1456, "percentage": 9.4},
                {"username": "jane.smith", "count": 1234, "percentage": 8.0},
                {"username": "mike.johnson", "count": 987, "percentage": 6.4}
            ],
            "success_rate": 94.7,
            "failed_events": 819,
            "security_events": 23
        }
        
        # Cache for 5 minutes
        await redis_cache.set(cache_key, stats, expire=300)
        
        logger.info("Retrieved audit statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting audit stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit statistics"
        )


@router.get("/security-events", summary="Get security events")
async def get_security_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns security-related audit events"""
    try:
        # Check cache first
        cache_key = f"security_events:{skip}:{limit}:{severity or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock security events
        security_events = [
            {
                "id": 1,
                "event_type": "failed_login_attempt",
                "severity": "medium",
                "description": "Multiple failed login attempts from IP 192.168.1.100",
                "ip_address": "192.168.1.100",
                "username": "admin",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "status": "blocked",
                "risk_score": 65
            },
            {
                "id": 2,
                "event_type": "suspicious_access",
                "severity": "high",
                "description": "Access attempt from unusual geographic location",
                "ip_address": "203.45.67.89",
                "username": "john.doe",
                "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                "status": "flagged",
                "risk_score": 82
            },
            {
                "id": 3,
                "event_type": "privilege_escalation",
                "severity": "critical",
                "description": "Unauthorized attempt to access admin functions",
                "ip_address": "192.168.1.150",
                "username": "temp_user",
                "timestamp": (datetime.now() - timedelta(hours=12)).isoformat(),
                "status": "blocked",
                "risk_score": 95
            }
        ]
        
        # Apply severity filter
        if severity:
            security_events = [event for event in security_events if event["severity"] == severity]
        
        # Apply pagination
        total = len(security_events)
        events = security_events[skip:skip + limit]
        
        result = {
            "items": events,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total
        }
        
        # Cache for 1 minute (shorter for security data)
        await redis_cache.set(cache_key, result, expire=60)
        
        logger.info(f"Retrieved {len(events)} security events (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting security events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security events"
        )