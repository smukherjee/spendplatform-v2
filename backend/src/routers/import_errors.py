"""
Async Import Errors router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import random

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import-errors", tags=["import-errors-async"])


@router.get("", summary="List all import errors")
@router.get("/", summary="List all import errors")
async def get_import_errors(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    resolved: Optional[bool] = Query(None),
    error_type: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns a list of import errors with filtering and pagination"""
    try:
        # Check cache first
        cache_key = f"import_errors:{skip}:{limit}:{resolved}:{error_type or 'all'}:{client_id or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock import errors data
        error_types = ["validation_error", "duplicate_entry", "missing_field", "invalid_format", "reference_error"]
        
        all_errors = []
        for i in range(1, 101):  # Generate 100 mock errors
            error_date = datetime.now()
            selected_error_type = random.choice(error_types)
            is_resolved = random.choice([True, False, False])  # More unresolved errors
            
            all_errors.append({
                "id": i,
                "invoice_id": random.randint(1, 200) if random.random() > 0.3 else None,
                "row_number": random.randint(1, 1000),
                "error_type": selected_error_type,
                "error_message": f"Error in row {random.randint(1, 1000)}: {selected_error_type.replace('_', ' ').title()}",
                "error_details": {
                    "field": random.choice(["amount", "supplier_name", "date", "category", "invoice_number"]),
                    "expected_format": "Numeric value",
                    "actual_value": "N/A", 
                    "suggestion": "Please provide a valid numeric amount"
                },
                "resolved": is_resolved,
                "resolution_notes": "Fixed manually by admin" if is_resolved else None,
                "client_id": random.randint(1, 3),
                "created_by": random.randint(1, 5),
                "created_at": error_date.isoformat(),
                "resolved_at": error_date.isoformat() if is_resolved else None,
                "severity": random.choice(["low", "medium", "high"]),
                "import_batch_id": f"BATCH_{random.randint(1000, 9999)}"
            })
        
        # Apply filters
        if resolved is not None:
            all_errors = [e for e in all_errors if e["resolved"] == resolved]
        
        if error_type:
            all_errors = [e for e in all_errors if e["error_type"] == error_type]
        
        if client_id:
            all_errors = [e for e in all_errors if e["client_id"] == client_id]
        
        # Sort by created date (newest first)
        all_errors.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total = len(all_errors)
        errors = all_errors[skip:skip + limit]
        
        result = {
            "items": errors,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total,
            "summary": {
                "total_errors": total,
                "resolved_errors": len([e for e in all_errors if e["resolved"]]),
                "unresolved_errors": len([e for e in all_errors if not e["resolved"]])
            }
        }
        
        # Cache for 2 minutes
        await redis_cache.set(cache_key, result, expire=120)
        
        logger.info(f"Retrieved {len(errors)} import errors (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting import errors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve import errors"
        )


@router.get("/stats/summary", summary="Get import errors statistics")
async def get_import_errors_stats(db: AsyncSession = Depends(get_async_db)):
    """Returns statistics about import errors"""
    try:
        # Check cache first
        cache_key = "import_errors_stats"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock statistics
        stats = {
            "total_errors": 98,
            "resolved_errors": 45,
            "unresolved_errors": 53,
            "resolution_rate": 45.9,
            "errors_by_type": [
                {"type": "validation_error", "count": 32, "percentage": 32.7},
                {"type": "duplicate_entry", "count": 21, "percentage": 21.4},
                {"type": "missing_field", "count": 18, "percentage": 18.4},
                {"type": "invalid_format", "count": 15, "percentage": 15.3},
                {"type": "reference_error", "count": 12, "percentage": 12.2}
            ],
            "errors_by_severity": [
                {"severity": "high", "count": 23, "percentage": 23.5},
                {"severity": "medium", "count": 41, "percentage": 41.8},
                {"severity": "low", "count": 34, "percentage": 34.7}
            ],
            "recent_batches": [
                {"batch_id": "BATCH_1234", "errors": 12, "resolved": 8},
                {"batch_id": "BATCH_1235", "errors": 8, "resolved": 3},
                {"batch_id": "BATCH_1236", "errors": 15, "resolved": 10}
            ]
        }
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, stats, expire=600)
        
        logger.info("Retrieved import errors statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting import errors stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve import errors statistics"
        )