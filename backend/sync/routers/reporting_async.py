"""
Async Reporting router for SpendPlatform v2
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
router = APIRouter(prefix="/reports", tags=["reporting-async"])


@router.get("/dashboard", summary="Get dashboard data")
async def get_dashboard_data(db: AsyncSession = Depends(get_async_db)):
    """Returns dashboard summary data"""
    try:
        # Check cache first
        cache_key = "dashboard:summary"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock dashboard data
        dashboard_data = {
            "summary": {
                "total_invoices": 1250,
                "pending_invoices": 45,
                "approved_invoices": 892,
                "paid_invoices": 313,
                "total_amount": 2750000.00,
                "pending_amount": 125000.00,
                "paid_amount": 850000.00
            },
            "monthly_spending": [
                {"month": "Jan", "amount": 245000},
                {"month": "Feb", "amount": 278000},
                {"month": "Mar", "amount": 312000},
                {"month": "Apr", "amount": 289000},
                {"month": "May", "amount": 325000},
                {"month": "Jun", "amount": 298000}
            ],
            "top_suppliers": [
                {"name": "Acme Corporation", "amount": 125000, "percentage": 15.2},
                {"name": "Global Supplies Ltd", "amount": 98000, "percentage": 11.9},
                {"name": "Tech Solutions Inc", "amount": 87000, "percentage": 10.6},
                {"name": "Office Plus", "amount": 65000, "percentage": 7.9},
                {"name": "Industrial Equipment Co", "amount": 54000, "percentage": 6.6}
            ],
            "spending_by_category": [
                {"category": "Office Supplies", "amount": 156000, "percentage": 19.0},
                {"category": "IT Equipment", "amount": 134000, "percentage": 16.3},
                {"category": "Professional Services", "amount": 112000, "percentage": 13.6},
                {"category": "Marketing", "amount": 89000, "percentage": 10.8},
                {"category": "Travel", "amount": 67000, "percentage": 8.1}
            ],
            "recent_activities": [
                {
                    "id": 1,
                    "type": "invoice_approved",
                    "description": "Invoice INV-2025-0123 approved",
                    "amount": 5500.00,
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
                },
                {
                    "id": 2,
                    "type": "invoice_created",
                    "description": "New invoice INV-2025-0124 created",
                    "amount": 3200.00,
                    "timestamp": (datetime.now() - timedelta(hours=4)).isoformat()
                },
                {
                    "id": 3,
                    "type": "payment_processed",
                    "description": "Payment processed for INV-2025-0120",
                    "amount": 8900.00,
                    "timestamp": (datetime.now() - timedelta(hours=6)).isoformat()
                }
            ]
        }
        
        # Cache for 5 minutes
        await redis_cache.set(cache_key, dashboard_data, expire=300)
        
        logger.info("Retrieved dashboard data")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )


@router.get("/spending-analysis", summary="Get spending analysis")
async def get_spending_analysis(
    period: str = Query("monthly", regex="^(weekly|monthly|quarterly|yearly)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns spending analysis data"""
    try:
        # Check cache first
        cache_key = f"spending_analysis:{period}:{start_date or 'none'}:{end_date or 'none'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock spending analysis data
        if period == "monthly":
            data_points = [
                {"period": "2025-01", "amount": 245000, "invoice_count": 85},
                {"period": "2025-02", "amount": 278000, "invoice_count": 92},
                {"period": "2025-03", "amount": 312000, "invoice_count": 108},
                {"period": "2025-04", "amount": 289000, "invoice_count": 95},
                {"period": "2025-05", "amount": 325000, "invoice_count": 112},
                {"period": "2025-06", "amount": 298000, "invoice_count": 98}
            ]
        elif period == "weekly":
            base_date = datetime.now() - timedelta(weeks=12)
            data_points = []
            for i in range(12):
                week_start = base_date + timedelta(weeks=i)
                data_points.append({
                    "period": f"Week {i+1}",
                    "amount": random.randint(15000, 25000),
                    "invoice_count": random.randint(5, 15)
                })
        else:
            data_points = [
                {"period": "Q1 2025", "amount": 835000, "invoice_count": 285},
                {"period": "Q2 2025", "amount": 912000, "invoice_count": 305}
            ]
        
        analysis = {
            "period": period,
            "data_points": data_points,
            "total_amount": sum(dp["amount"] for dp in data_points),
            "total_invoices": sum(dp["invoice_count"] for dp in data_points),
            "average_invoice_value": sum(dp["amount"] for dp in data_points) / sum(dp["invoice_count"] for dp in data_points) if data_points else 0,
            "trends": {
                "amount_change": "+12.5%",
                "invoice_count_change": "+8.3%",
                "trend_direction": "increasing"
            }
        }
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, analysis, expire=900)
        
        logger.info(f"Retrieved spending analysis for period: {period}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting spending analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve spending analysis"
        )


@router.get("/supplier-performance", summary="Get supplier performance report")
async def get_supplier_performance(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns supplier performance metrics"""
    try:
        # Check cache first
        cache_key = f"supplier_performance:{limit}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock supplier performance data
        suppliers = [
            {
                "id": 1,
                "name": "Acme Corporation",
                "total_invoices": 125,
                "total_amount": 425000.00,
                "average_invoice_value": 3400.00,
                "on_time_payment_rate": 95.2,
                "average_processing_days": 2.3,
                "quality_score": 4.8,
                "performance_rating": "Excellent"
            },
            {
                "id": 2,
                "name": "Global Supplies Ltd",
                "total_invoices": 98,
                "total_amount": 315000.00,
                "average_invoice_value": 3214.29,
                "on_time_payment_rate": 89.8,
                "average_processing_days": 3.1,
                "quality_score": 4.6,
                "performance_rating": "Good"
            },
            {
                "id": 3,
                "name": "Tech Solutions Inc",
                "total_invoices": 87,
                "total_amount": 298000.00,
                "average_invoice_value": 3425.29,
                "on_time_payment_rate": 92.0,
                "average_processing_days": 2.8,
                "quality_score": 4.7,
                "performance_rating": "Excellent"
            }
        ]
        
        # Limit results
        performance_data = {
            "suppliers": suppliers[:limit],
            "summary": {
                "total_suppliers": len(suppliers),
                "average_quality_score": 4.70,
                "average_on_time_rate": 92.33,
                "best_performer": "Acme Corporation",
                "improvement_needed": 2
            }
        }
        
        # Cache for 30 minutes
        await redis_cache.set(cache_key, performance_data, expire=1800)
        
        logger.info(f"Retrieved supplier performance data for {limit} suppliers")
        return performance_data
        
    except Exception as e:
        logger.error(f"Error getting supplier performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supplier performance data"
        )