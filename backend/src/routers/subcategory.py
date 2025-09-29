"""
Async Subcategory router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subcategories", tags=["subcategories-async"])


@router.get("/", summary="Get all subcategories")
async def get_subcategories(
    category_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns list of subcategories with optional filtering"""
    try:
        # Check cache first
        cache_key = f"subcategories:{category_id or 'all'}:{active_only}:{search or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock subcategory data with categories
        subcategories = [
            # Office Supplies subcategories
            {
                "id": 1,
                "name": "Paper & Stationery",
                "description": "Paper, pens, notebooks, and basic stationery items",
                "category_id": 1,
                "category_name": "Office Supplies",
                "is_active": True,
                "code": "OS-001",
                "budget_limit": 5000.00,
                "spend_ytd": 3245.67,
                "transaction_count": 156
            },
            {
                "id": 2,
                "name": "Computer Accessories",
                "description": "Keyboards, mice, cables, and computer peripherals",
                "category_id": 1,
                "category_name": "Office Supplies",
                "is_active": True,
                "code": "OS-002",
                "budget_limit": 8000.00,
                "spend_ytd": 6123.45,
                "transaction_count": 89
            },
            {
                "id": 3,
                "name": "Furniture",
                "description": "Desks, chairs, filing cabinets, and office furniture",
                "category_id": 1,
                "category_name": "Office Supplies",
                "is_active": True,
                "code": "OS-003",
                "budget_limit": 15000.00,
                "spend_ytd": 12456.78,
                "transaction_count": 34
            },
            # Travel & Entertainment subcategories
            {
                "id": 4,
                "name": "Airfare",
                "description": "Flight tickets and related travel expenses",
                "category_id": 2,
                "category_name": "Travel & Entertainment",
                "is_active": True,
                "code": "TE-001",
                "budget_limit": 50000.00,
                "spend_ytd": 34567.89,
                "transaction_count": 123
            },
            {
                "id": 5,
                "name": "Hotels & Accommodation",
                "description": "Hotel stays, Airbnb, and other accommodation",
                "category_id": 2,
                "category_name": "Travel & Entertainment",
                "is_active": True,
                "code": "TE-002",
                "budget_limit": 30000.00,
                "spend_ytd": 23456.78,
                "transaction_count": 87
            },
            {
                "id": 6,
                "name": "Meals & Entertainment",
                "description": "Business meals, client entertainment, and catering",
                "category_id": 2,
                "category_name": "Travel & Entertainment",
                "is_active": True,
                "code": "TE-003",
                "budget_limit": 20000.00,
                "spend_ytd": 18765.43,
                "transaction_count": 234
            },
            # IT & Technology subcategories
            {
                "id": 7,
                "name": "Software Licenses",
                "description": "Software subscriptions and licensing fees",
                "category_id": 3,
                "category_name": "IT & Technology",
                "is_active": True,
                "code": "IT-001",
                "budget_limit": 25000.00,
                "spend_ytd": 22345.67,
                "transaction_count": 67
            },
            {
                "id": 8,
                "name": "Hardware",
                "description": "Computers, servers, and IT hardware",
                "category_id": 3,
                "category_name": "IT & Technology",
                "is_active": True,
                "code": "IT-002",
                "budget_limit": 40000.00,
                "spend_ytd": 35678.90,
                "transaction_count": 45
            },
            {
                "id": 9,
                "name": "Cloud Services",
                "description": "AWS, Azure, Google Cloud, and other cloud services",
                "category_id": 3,
                "category_name": "IT & Technology",
                "is_active": True,
                "code": "IT-003",
                "budget_limit": 18000.00,
                "spend_ytd": 16234.56,
                "transaction_count": 78
            },
            # Marketing & Advertising subcategories
            {
                "id": 10,
                "name": "Digital Marketing",
                "description": "Online ads, social media marketing, SEO services",
                "category_id": 4,
                "category_name": "Marketing & Advertising",
                "is_active": True,
                "code": "MA-001",
                "budget_limit": 35000.00,
                "spend_ytd": 28765.43,
                "transaction_count": 156
            },
            {
                "id": 11,
                "name": "Print & Traditional Media",
                "description": "Print ads, billboards, radio, and TV advertising",
                "category_id": 4,
                "category_name": "Marketing & Advertising",
                "is_active": False,  # Inactive for testing
                "code": "MA-002",
                "budget_limit": 10000.00,
                "spend_ytd": 2345.67,
                "transaction_count": 23
            },
            {
                "id": 12,
                "name": "Events & Trade Shows",
                "description": "Conference participation, booth rentals, event sponsorship",
                "category_id": 4,
                "category_name": "Marketing & Advertising",
                "is_active": True,
                "code": "MA-003",
                "budget_limit": 25000.00,
                "spend_ytd": 19876.54,
                "transaction_count": 34
            }
        ]
        
        # Apply filters
        if category_id:
            subcategories = [s for s in subcategories if s["category_id"] == category_id]
        
        if active_only:
            subcategories = [s for s in subcategories if s["is_active"]]
        
        if search:
            search_lower = search.lower()
            subcategories = [
                s for s in subcategories 
                if (search_lower in s["name"].lower() or 
                    search_lower in s["description"].lower() or
                    search_lower in s["code"].lower())
            ]
        
        # Add spending analysis
        for subcategory in subcategories:
            if subcategory["budget_limit"] > 0:
                subcategory["budget_utilization"] = round(
                    (subcategory["spend_ytd"] / subcategory["budget_limit"]) * 100, 1
                )
                subcategory["remaining_budget"] = subcategory["budget_limit"] - subcategory["spend_ytd"]
            else:
                subcategory["budget_utilization"] = 0
                subcategory["remaining_budget"] = 0
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, subcategories, expire=900)
        
        logger.info(f"Retrieved {len(subcategories)} subcategories")
        return subcategories
        
    except Exception as e:
        logger.error(f"Error getting subcategories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subcategories"
        )


@router.get("/{subcategory_id}", summary="Get subcategory details")
async def get_subcategory_details(
    subcategory_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns detailed information about a specific subcategory"""
    try:
        # Check cache first
        cache_key = f"subcategory_details:{subcategory_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock subcategory details
        subcategory_map = {
            1: {
                "id": 1,
                "name": "Paper & Stationery",
                "description": "Paper, pens, notebooks, and basic stationery items",
                "category_id": 1,
                "category_name": "Office Supplies",
                "is_active": True,
                "code": "OS-001",
                "budget_limit": 5000.00,
                "spend_ytd": 3245.67,
                "transaction_count": 156,
                "budget_utilization": 64.9,
                "remaining_budget": 1754.33,
                "monthly_spending": [
                    {"month": "Jan", "amount": 245.67},
                    {"month": "Feb", "amount": 356.78},
                    {"month": "Mar", "amount": 234.56},
                    {"month": "Apr", "amount": 456.78},
                    {"month": "May", "amount": 345.67},
                    {"month": "Jun", "amount": 567.89}
                ],
                "top_suppliers": [
                    {"supplier": "Office Depot", "amount": 1234.56, "percentage": 38.0},
                    {"supplier": "Staples", "amount": 987.65, "percentage": 30.4},
                    {"supplier": "Amazon Business", "amount": 543.21, "percentage": 16.7}
                ],
                "approval_rules": {
                    "single_transaction_limit": 500.00,
                    "requires_manager_approval": True,
                    "auto_approve_threshold": 100.00
                }
            },
            7: {
                "id": 7,
                "name": "Software Licenses",
                "description": "Software subscriptions and licensing fees",
                "category_id": 3,
                "category_name": "IT & Technology",
                "is_active": True,
                "code": "IT-001",
                "budget_limit": 25000.00,
                "spend_ytd": 22345.67,
                "transaction_count": 67,
                "budget_utilization": 89.4,
                "remaining_budget": 2654.33,
                "monthly_spending": [
                    {"month": "Jan", "amount": 3456.78},
                    {"month": "Feb", "amount": 4567.89},
                    {"month": "Mar", "amount": 3234.56},
                    {"month": "Apr", "amount": 4321.09},
                    {"month": "May", "amount": 3567.12},
                    {"month": "Jun", "amount": 3198.23}
                ],
                "top_suppliers": [
                    {"supplier": "Microsoft", "amount": 8765.43, "percentage": 39.2},
                    {"supplier": "Adobe", "amount": 6543.21, "percentage": 29.3},
                    {"supplier": "Salesforce", "amount": 4321.09, "percentage": 19.3}
                ],
                "approval_rules": {
                    "single_transaction_limit": 2000.00,
                    "requires_manager_approval": True,
                    "auto_approve_threshold": 500.00
                }
            }
        }
        
        if subcategory_id not in subcategory_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategory not found"
            )
        
        subcategory = subcategory_map[subcategory_id]
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, subcategory, expire=600)
        
        logger.info(f"Retrieved details for subcategory {subcategory_id}")
        return subcategory
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subcategory details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subcategory details"
        )


@router.get("/category/{category_id}/summary", summary="Get category subcategory summary")
async def get_category_subcategory_summary(
    category_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns summary of all subcategories within a category"""
    try:
        # Check cache first
        cache_key = f"category_subcategory_summary:{category_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock category summaries
        category_summaries = {
            1: {  # Office Supplies
                "category_id": 1,
                "category_name": "Office Supplies",
                "total_subcategories": 3,
                "active_subcategories": 3,
                "total_budget": 28000.00,
                "total_spend": 21825.90,
                "budget_utilization": 77.9,
                "total_transactions": 279,
                "subcategories": [
                    {
                        "id": 1,
                        "name": "Paper & Stationery",
                        "spend": 3245.67,
                        "budget": 5000.00,
                        "utilization": 64.9
                    },
                    {
                        "id": 2,
                        "name": "Computer Accessories",
                        "spend": 6123.45,
                        "budget": 8000.00,
                        "utilization": 76.5
                    },
                    {
                        "id": 3,
                        "name": "Furniture",
                        "spend": 12456.78,
                        "budget": 15000.00,
                        "utilization": 83.0
                    }
                ]
            },
            3: {  # IT & Technology
                "category_id": 3,
                "category_name": "IT & Technology",
                "total_subcategories": 3,
                "active_subcategories": 3,
                "total_budget": 83000.00,
                "total_spend": 74259.13,
                "budget_utilization": 89.5,
                "total_transactions": 190,
                "subcategories": [
                    {
                        "id": 7,
                        "name": "Software Licenses",
                        "spend": 22345.67,
                        "budget": 25000.00,
                        "utilization": 89.4
                    },
                    {
                        "id": 8,
                        "name": "Hardware",
                        "spend": 35678.90,
                        "budget": 40000.00,
                        "utilization": 89.2
                    },
                    {
                        "id": 9,
                        "name": "Cloud Services",
                        "spend": 16234.56,
                        "budget": 18000.00,
                        "utilization": 90.2
                    }
                ]
            }
        }
        
        if category_id not in category_summaries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        summary = category_summaries[category_id]
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, summary, expire=900)
        
        logger.info(f"Retrieved subcategory summary for category {category_id}")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category subcategory summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category subcategory summary"
        )