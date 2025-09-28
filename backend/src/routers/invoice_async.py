"""
Async Invoice router for SpendPlatform v2
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
router = APIRouter(prefix="/invoices", tags=["invoice-async"])


@router.get("/", summary="List all invoices")
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns a list of invoices with pagination"""
    try:
        # Check cache first
        cache_key = f"invoices:list:{skip}:{limit}:{status_filter or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Generate mock invoice data
        base_date = datetime.now() - timedelta(days=30)
        statuses = ["pending", "approved", "paid", "rejected"]
        suppliers = ["Acme Corp", "Global Supplies", "Tech Solutions", "Office Plus"]
        
        all_invoices = []
        for i in range(1, 101):  # Generate 100 mock invoices
            invoice_date = base_date + timedelta(days=random.randint(0, 30))
            all_invoices.append({
                "id": i,
                "invoice_number": f"INV-{2025}-{i:04d}",
                "supplier_name": random.choice(suppliers),
                "invoice_date": invoice_date.isoformat(),
                "due_date": (invoice_date + timedelta(days=30)).isoformat(),
                "amount": round(random.uniform(100, 10000), 2),
                "currency": "USD",
                "status": random.choice(statuses),
                "description": f"Invoice {i} description",
                "client_id": 1,
                "created_at": invoice_date.isoformat()
            })
        
        # Apply status filter
        if status_filter:
            all_invoices = [inv for inv in all_invoices if inv["status"] == status_filter]
        
        # Apply pagination
        total = len(all_invoices)
        invoices = all_invoices[skip:skip + limit]
        
        result = {
            "items": invoices,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total
        }
        
        # Cache for 5 minutes
        await redis_cache.set(cache_key, result, expire=300)
        
        logger.info(f"Retrieved {len(invoices)} invoices (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoices"
        )


@router.get("/{invoice_id}", summary="Get invoice by ID")
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns a specific invoice by ID"""
    try:
        # Mock invoice data
        if invoice_id <= 100:
            base_date = datetime.now() - timedelta(days=random.randint(1, 30))
            invoice = {
                "id": invoice_id,
                "invoice_number": f"INV-{2025}-{invoice_id:04d}",
                "supplier_name": "Acme Corp",
                "supplier_id": 1,
                "invoice_date": base_date.isoformat(),
                "due_date": (base_date + timedelta(days=30)).isoformat(),
                "amount": round(random.uniform(100, 10000), 2),
                "currency": "USD",
                "status": "pending",
                "description": f"Invoice {invoice_id} description",
                "client_id": 1,
                "business_unit_id": 1,
                "created_at": base_date.isoformat(),
                "line_items": [
                    {
                        "id": 1,
                        "description": "Product A",
                        "quantity": 2,
                        "unit_price": 500.00,
                        "total": 1000.00
                    },
                    {
                        "id": 2,
                        "description": "Service B",
                        "quantity": 1,
                        "unit_price": 250.00,
                        "total": 250.00
                    }
                ]
            }
            return invoice
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice"
        )


@router.put("/{invoice_id}/status", summary="Update invoice status")
async def update_invoice_status(
    invoice_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_async_db)
):
    """Updates invoice status"""
    try:
        new_status = status_data.get("status")
        if new_status not in ["pending", "approved", "paid", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        
        # Mock status update - in production would update database
        logger.info(f"Updated invoice {invoice_id} status to {new_status}")
        
        return {
            "id": invoice_id,
            "status": new_status,
            "updated_at": datetime.now().isoformat(),
            "message": f"Invoice status updated to {new_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating invoice {invoice_id} status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update invoice status"
        )