"""
Async Business Unit router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/business-units", tags=["business-unit-async"])


@router.get("/", summary="List all business units")
async def get_business_units(db: AsyncSession = Depends(get_async_db)):
    """Returns a list of all business units"""
    try:
        # Check cache first
        cache_key = "business_units:all"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock business unit data for now
        business_units = [
            {
                "id": 1,
                "name": "Corporate",
                "code": "CORP",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 2,
                "name": "Marketing",
                "code": "MKT",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 3,
                "name": "Operations",
                "code": "OPS",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            }
        ]
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, business_units, expire=600)
        
        logger.info("Retrieved business units list")
        return business_units
        
    except Exception as e:
        logger.error(f"Error getting business units: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve business units"
        )


@router.get("/{bu_id}", summary="Get business unit by ID")
async def get_business_unit(bu_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns a specific business unit by ID"""
    try:
        # Mock business unit data
        business_units = {
            1: {"id": 1, "name": "Corporate", "code": "CORP", "client_id": 1, "is_active": True},
            2: {"id": 2, "name": "Marketing", "code": "MKT", "client_id": 1, "is_active": True},
            3: {"id": 3, "name": "Operations", "code": "OPS", "client_id": 1, "is_active": True}
        }
        
        if bu_id in business_units:
            return business_units[bu_id]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business unit not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business unit {bu_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve business unit"
        )