"""Async Audit Logs router for SpendPlatform v2 - Enhanced audit functionality"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import random

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audit-logs", tags=["audit-logs-async"])


@router.get("/", summary="Get detailed audit logs")
async def get_detailed_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action_filter: Optional[str] = Query(None),
    user_id_filter: Optional[int] = Query(None),
    client_id_filter: Optional[int] = Query(None),
    hours_back: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns detailed audit logs with advanced filtering"""
    try:
        # Check cache first
        cache_key = f"audit_logs_detailed:{skip}:{limit}:{action_filter or 'all'}:{user_id_filter or 'all'}:{client_id_filter or 'all'}:{hours_back}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Generate comprehensive mock audit logs
        actions = ["login", "logout", "create_invoice", "approve_invoice", "reject_invoice", 
                  "update_user", "delete_supplier", "export_report", "bulk_import", "settings_change"]
        users = ["superadmin", "client_admin", "john.doe", "jane.smith", "mike.johnson"]
        
        all_logs = []
        base_date = datetime.now() - timedelta(hours=hours_back)
        
        for i in range(1, 501):  # Generate 500 detailed logs
            log_date = base_date + timedelta(minutes=random.randint(0, hours_back * 60))
            selected_action = random.choice(actions)
            selected_user = random.choice(users)
            
            all_logs.append({
                "id": i,
                "user_id": random.randint(1, 5),
                "username": selected_user,
                "client_id": random.randint(1, 3),
                "action": selected_action,
                "resource_type": selected_action.split('_')[-1] if '_' in selected_action else "system",
                "resource_id": random.randint(1, 100) if selected_action not in ["login", "logout"] else None,
                "details": f"User {selected_user} performed {selected_action} with result: {'success' if random.random() > 0.1 else 'failed'}",
                "ip_address": f"192.168.{random.randint(1, 3)}.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0 (compatible; SpendPlatform/2.0)",
                "timestamp": log_date.isoformat(),
                "session_id": f"sess_{random.randint(100000, 999999)}",
                "risk_score": random.randint(1, 100),
                "geographic_location": random.choice(["New York, US", "London, UK", "Tokyo, JP"])
            })
        
        # Apply filters
        if action_filter:
            all_logs = [log for log in all_logs if log["action"] == action_filter]
        
        if user_id_filter:
            all_logs = [log for log in all_logs if log["user_id"] == user_id_filter]
        
        if client_id_filter:
            all_logs = [log for log in all_logs if log["client_id"] == client_id_filter]
        
        # Sort by timestamp (newest first)
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        total = len(all_logs)
        logs = all_logs[skip:skip + limit]
        
        result = {
            "logs": logs,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total,
            "filters_applied": {
                "action": action_filter,
                "user_id": user_id_filter,
                "client_id": client_id_filter,
                "hours_back": hours_back
            }
        }
        
        # Cache for 1 minute
        await redis_cache.set(cache_key, result, expire=60)
        
        logger.info(f"Retrieved {len(logs)} detailed audit logs (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting detailed audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve detailed audit logs"
        )


@router.get("/summary", summary="Get audit logs summary")
async def get_audit_logs_summary(
    hours_back: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns summary statistics for audit logs"""
    try:
        # Check cache first
        cache_key = f"audit_logs_summary:{hours_back}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock audit summary
        summary = {
            "time_period_hours": hours_back,
            "total_events": random.randint(1000, 5000),
            "unique_users": random.randint(20, 50),
            "unique_clients": 3,
            "success_events": random.randint(900, 4500),
            "failed_events": random.randint(50, 500),
            "success_rate": round(random.uniform(85.0, 98.0), 1),
            "top_actions": [
                {"action": "login", "count": random.randint(500, 1000), "percentage": random.randint(20, 35)},
                {"action": "create_invoice", "count": random.randint(200, 500), "percentage": random.randint(10, 20)},
                {"action": "approve_invoice", "count": random.randint(100, 300), "percentage": random.randint(5, 15)}
            ],
            "risk_events": {
                "high_risk": random.randint(0, 5), 
                "medium_risk": random.randint(5, 20),
                "low_risk": random.randint(50, 200)
            }
        }
        
        # Cache for 5 minutes
        await redis_cache.set(cache_key, summary, expire=300)
        
        logger.info(f"Retrieved audit logs summary for {hours_back} hours")
        return summary
        
    except Exception as e:
        logger.error(f"Error getting audit logs summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs summary"
        )