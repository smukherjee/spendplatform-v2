"""
Async Unit of Measure router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/units-of-measure", tags=["units-of-measure-async"])


@router.get("/", summary="Get all units of measure")
async def get_units_of_measure(
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns list of units of measure with optional filtering"""
    try:
        # Check cache first
        cache_key = f"units_of_measure:{category or 'all'}:{active_only}:{search or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock units of measure data
        units = [
            # Quantity/Count units
            {
                "id": 1,
                "code": "EA",
                "name": "Each",
                "description": "Individual items or pieces",
                "category": "quantity",
                "is_active": True,
                "base_unit": True,
                "conversion_factor": 1.0,
                "symbol": "ea",
                "usage_count": 1543
            },
            {
                "id": 2,
                "code": "PCS",
                "name": "Pieces",
                "description": "Individual pieces or units",
                "category": "quantity",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 1.0,  # Same as Each
                "symbol": "pcs",
                "usage_count": 987
            },
            {
                "id": 3,
                "code": "DOZ",
                "name": "Dozen",
                "description": "Set of 12 items",
                "category": "quantity",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 12.0,  # 12 pieces
                "symbol": "doz",
                "usage_count": 234
            },
            # Weight units
            {
                "id": 4,
                "code": "KG",
                "name": "Kilogram",
                "description": "Metric unit of mass",
                "category": "weight",
                "is_active": True,
                "base_unit": True,
                "conversion_factor": 1.0,
                "symbol": "kg",
                "usage_count": 456
            },
            {
                "id": 5,
                "code": "LB",
                "name": "Pound",
                "description": "Imperial unit of weight",
                "category": "weight",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 0.453592,  # kg
                "symbol": "lb",
                "usage_count": 321
            },
            {
                "id": 6,
                "code": "G",
                "name": "Gram",
                "description": "Small metric unit of mass",
                "category": "weight",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 0.001,  # kg
                "symbol": "g",
                "usage_count": 178
            },
            # Volume units
            {
                "id": 7,
                "code": "L",
                "name": "Liter",
                "description": "Metric unit of volume",
                "category": "volume",
                "is_active": True,
                "base_unit": True,
                "conversion_factor": 1.0,
                "symbol": "L",
                "usage_count": 289
            },
            {
                "id": 8,
                "code": "GAL",
                "name": "Gallon",
                "description": "Imperial unit of volume",
                "category": "volume",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 3.78541,  # liters
                "symbol": "gal",
                "usage_count": 167
            },
            {
                "id": 9,
                "code": "ML",
                "name": "Milliliter",
                "description": "Small metric unit of volume",
                "category": "volume",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 0.001,  # liters
                "symbol": "ml",
                "usage_count": 145
            },
            # Length units
            {
                "id": 10,
                "code": "M",
                "name": "Meter",
                "description": "Metric unit of length",
                "category": "length",
                "is_active": True,
                "base_unit": True,
                "conversion_factor": 1.0,
                "symbol": "m",
                "usage_count": 203
            },
            {
                "id": 11,
                "code": "FT",
                "name": "Foot",
                "description": "Imperial unit of length",
                "category": "length",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 0.3048,  # meters
                "symbol": "ft",
                "usage_count": 134
            },
            {
                "id": 12,
                "code": "CM",
                "name": "Centimeter",
                "description": "Small metric unit of length",
                "category": "length",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 0.01,  # meters
                "symbol": "cm",
                "usage_count": 89
            },
            # Time units
            {
                "id": 13,
                "code": "HR",
                "name": "Hour",
                "description": "Unit of time - 60 minutes",
                "category": "time",
                "is_active": True,
                "base_unit": True,
                "conversion_factor": 1.0,
                "symbol": "hr",
                "usage_count": 567
            },
            {
                "id": 14,
                "code": "DAY",
                "name": "Day",
                "description": "Unit of time - 24 hours",
                "category": "time",
                "is_active": True,
                "base_unit": False,
                "conversion_factor": 24.0,  # hours
                "symbol": "day",
                "usage_count": 345
            },
            {
                "id": 15,
                "code": "MIN",
                "name": "Minute",
                "description": "Unit of time - 60 seconds",
                "category": "time",
                "is_active": False,  # Inactive for testing
                "base_unit": False,
                "conversion_factor": 0.0167,  # hours
                "symbol": "min",
                "usage_count": 23
            }
        ]
        
        # Apply filters
        if category:
            units = [u for u in units if u["category"].lower() == category.lower()]
        
        if active_only:
            units = [u for u in units if u["is_active"]]
        
        if search:
            search_lower = search.lower()
            units = [
                u for u in units 
                if (search_lower in u["name"].lower() or 
                    search_lower in u["code"].lower() or
                    search_lower in u["description"].lower())
            ]
        
        # Cache for 30 minutes (UOM data doesn't change often)
        await redis_cache.set(cache_key, units, expire=1800)
        
        logger.info(f"Retrieved {len(units)} units of measure")
        return units
        
    except Exception as e:
        logger.error(f"Error getting units of measure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve units of measure"
        )


@router.get("/{unit_id}", summary="Get unit of measure details")
async def get_unit_details(
    unit_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns detailed information about a specific unit of measure"""
    try:
        # Check cache first
        cache_key = f"unit_details:{unit_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock unit details
        unit_map = {
            1: {
                "id": 1,
                "code": "EA",
                "name": "Each",
                "description": "Individual items or pieces",
                "category": "quantity",
                "is_active": True,
                "base_unit": True,
                "conversion_factor": 1.0,
                "symbol": "ea",
                "usage_count": 1543,
                "related_units": [
                    {"id": 2, "code": "PCS", "name": "Pieces", "conversion": 1.0},
                    {"id": 3, "code": "DOZ", "name": "Dozen", "conversion": 12.0}
                ],
                "common_items": [
                    "Office supplies",
                    "Computer accessories", 
                    "Furniture pieces",
                    "Electronic devices"
                ],
                "usage_by_category": [
                    {"category": "Office Supplies", "count": 678, "percentage": 43.9},
                    {"category": "IT & Technology", "count": 456, "percentage": 29.5},
                    {"category": "Marketing Materials", "count": 234, "percentage": 15.2},
                    {"category": "Other", "count": 175, "percentage": 11.3}
                ]
            },
            4: {
                "id": 4,
                "code": "KG",
                "name": "Kilogram",
                "description": "Metric unit of mass",
                "category": "weight",
                "is_active": True,
                "base_unit": True,
                "conversion_factor": 1.0,
                "symbol": "kg",
                "usage_count": 456,
                "related_units": [
                    {"id": 5, "code": "LB", "name": "Pound", "conversion": 2.20462},
                    {"id": 6, "code": "G", "name": "Gram", "conversion": 0.001}
                ],
                "common_items": [
                    "Raw materials",
                    "Shipping items",
                    "Bulk supplies",
                    "Industrial materials"
                ],
                "usage_by_category": [
                    {"category": "Manufacturing", "count": 234, "percentage": 51.3},
                    {"category": "Shipping", "count": 123, "percentage": 27.0},
                    {"category": "Raw Materials", "count": 67, "percentage": 14.7},
                    {"category": "Other", "count": 32, "percentage": 7.0}
                ]
            }
        }
        
        if unit_id not in unit_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit of measure not found"
            )
        
        unit = unit_map[unit_id]
        
        # Cache for 20 minutes
        await redis_cache.set(cache_key, unit, expire=1200)
        
        logger.info(f"Retrieved details for unit {unit_id}")
        return unit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting unit details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve unit details"
        )


@router.get("/categories/summary", summary="Get unit categories summary")
async def get_unit_categories_summary(db: AsyncSession = Depends(get_async_db)):
    """Returns summary of all unit categories"""
    try:
        # Check cache first
        cache_key = "unit_categories_summary"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock categories summary
        summary = {
            "categories": [
                {
                    "name": "quantity",
                    "display_name": "Quantity/Count",
                    "description": "Units for counting items",
                    "total_units": 3,
                    "active_units": 3,
                    "usage_count": 2764,
                    "base_units": ["EA"],
                    "most_used": "EA"
                },
                {
                    "name": "weight",
                    "display_name": "Weight/Mass",
                    "description": "Units for measuring weight",
                    "total_units": 3,
                    "active_units": 3,
                    "usage_count": 955,
                    "base_units": ["KG"],
                    "most_used": "KG"
                },
                {
                    "name": "volume",
                    "display_name": "Volume/Capacity",
                    "description": "Units for measuring volume",
                    "total_units": 3,
                    "active_units": 3,
                    "usage_count": 601,
                    "base_units": ["L"],
                    "most_used": "L"
                },
                {
                    "name": "length",
                    "display_name": "Length/Distance",
                    "description": "Units for measuring length",
                    "total_units": 3,
                    "active_units": 3,
                    "usage_count": 426,
                    "base_units": ["M"],
                    "most_used": "M"
                },
                {
                    "name": "time",
                    "display_name": "Time/Duration",
                    "description": "Units for measuring time",
                    "total_units": 3,
                    "active_units": 2,
                    "usage_count": 935,
                    "base_units": ["HR"],
                    "most_used": "HR"
                }
            ],
            "total_units": 15,
            "active_units": 14,
            "total_usage": 5681
        }
        
        # Cache for 1 hour
        await redis_cache.set(cache_key, summary, expire=3600)
        
        logger.info("Retrieved unit categories summary")
        return summary
        
    except Exception as e:
        logger.error(f"Error getting unit categories summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve unit categories summary"
        )


@router.post("/convert", summary="Convert between units")
async def convert_units(
    from_unit_code: str = Query(..., description="Source unit code"),
    to_unit_code: str = Query(..., description="Target unit code"),
    quantity: float = Query(..., gt=0, description="Quantity to convert"),
    db: AsyncSession = Depends(get_async_db)
):
    """Convert quantity from one unit to another within the same category"""
    try:
        # Mock unit conversion data
        units_data = {
            "EA": {"category": "quantity", "factor": 1.0},
            "PCS": {"category": "quantity", "factor": 1.0},
            "DOZ": {"category": "quantity", "factor": 12.0},
            "KG": {"category": "weight", "factor": 1.0},
            "LB": {"category": "weight", "factor": 0.453592},
            "G": {"category": "weight", "factor": 0.001},
            "L": {"category": "volume", "factor": 1.0},
            "GAL": {"category": "volume", "factor": 3.78541},
            "ML": {"category": "volume", "factor": 0.001},
            "M": {"category": "length", "factor": 1.0},
            "FT": {"category": "length", "factor": 0.3048},
            "CM": {"category": "length", "factor": 0.01},
            "HR": {"category": "time", "factor": 1.0},
            "DAY": {"category": "time", "factor": 24.0},
            "MIN": {"category": "time", "factor": 0.0167}
        }
        
        if from_unit_code not in units_data or to_unit_code not in units_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid unit code"
            )
        
        from_unit = units_data[from_unit_code]
        to_unit = units_data[to_unit_code]
        
        # Check if units are in the same category
        if from_unit["category"] != to_unit["category"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot convert between different unit categories"
            )
        
        # Convert to base unit first, then to target unit
        base_quantity = quantity * from_unit["factor"]
        converted_quantity = base_quantity / to_unit["factor"]
        
        result = {
            "from_unit": from_unit_code,
            "to_unit": to_unit_code,
            "original_quantity": quantity,
            "converted_quantity": round(converted_quantity, 6),
            "category": from_unit["category"],
            "conversion_factor": round(from_unit["factor"] / to_unit["factor"], 6)
        }
        
        logger.info(f"Converted {quantity} {from_unit_code} to {converted_quantity} {to_unit_code}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting units: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to convert units"
        )