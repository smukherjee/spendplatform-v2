"""
Async Region router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/regions", tags=["region-async"])


@router.get("/", summary="List all regions")
async def get_regions(db: AsyncSession = Depends(get_async_db)):
    """Returns a list of all regions"""
    try:
        # Check cache first
        cache_key = "regions:all"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock region data
        regions = [
            {
                "id": 1,
                "name": "North America",
                "code": "NA",
                "description": "North American region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 2,
                "name": "Europe",
                "code": "EU",
                "description": "European region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 3,
                "name": "Asia Pacific",
                "code": "APAC",
                "description": "Asia Pacific region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 4,
                "name": "Latin America",
                "code": "LATAM",
                "description": "Latin American region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            }
        ]
        
        # Cache for 30 minutes
        await redis_cache.set(cache_key, regions, expire=1800)
        
        logger.info("Retrieved regions list")
        return regions
        
    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve regions"
        )


@router.get("/{region_id}", summary="Get region by ID")
async def get_region(region_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns a specific region by ID"""
    try:
        # Mock region data
        regions = {
            1: {
                "id": 1,
                "name": "North America",
                "code": "NA",
                "description": "North American region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "countries": ["United States", "Canada", "Mexico"]
            },
            2: {
                "id": 2,
                "name": "Europe",
                "code": "EU",
                "description": "European region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "countries": ["United Kingdom", "Germany", "France", "Spain", "Italy"]
            },
            3: {
                "id": 3,
                "name": "Asia Pacific",
                "code": "APAC",
                "description": "Asia Pacific region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "countries": ["Japan", "Australia", "Singapore", "South Korea"]
            },
            4: {
                "id": 4,
                "name": "Latin America",
                "code": "LATAM",
                "description": "Latin American region",
                "client_id": 1,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "countries": ["Brazil", "Argentina", "Chile", "Colombia"]
            }
        }
        
        if region_id in regions:
            return regions[region_id]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting region {region_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve region"
        )