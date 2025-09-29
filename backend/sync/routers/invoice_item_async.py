"""
Async Invoice Item router for SpendPlatform v2
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
router = APIRouter(prefix="/invoice-items", tags=["invoice-items-async"])


@router.get("", summary="List all invoice items")
async def get_invoice_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    invoice_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns a list of invoice items with filtering and pagination"""
    try:
        # Check cache first
        cache_key = f"invoice_items:{skip}:{limit}:{invoice_id or 'all'}:{client_id or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock invoice items data
        categories = ["Office Supplies", "IT & Technology", "Travel", "Marketing", "Facilities"]
        units = ["EA", "KG", "HR", "L", "M"]
        currencies = ["USD", "EUR", "GBP"]
        
        all_items = []
        for i in range(1, 201):  # Generate 200 mock items
            item_qty = random.randint(1, 100)
            unit_price = round(random.uniform(10.0, 500.0), 2)
            total_amount = round(item_qty * unit_price, 2)
            
            all_items.append({
                "id": i,
                "invoice_id": random.randint(1, 50),
                "item_number": f"ITEM-{i:04d}",
                "type": random.choice(["product", "service", "expense"]),
                "description": f"Sample item {i} - {random.choice(['Office chairs', 'Software license', 'Consulting services', 'Travel expenses', 'Marketing materials'])}",
                "subcategory_l1_id": random.randint(1, 5),
                "subcategory_l1_name": random.choice(categories),
                "subcategory_l2_id": random.randint(10, 20),
                "subcategory_l2_name": f"Sub-{random.choice(categories)}",
                "qty": item_qty,
                "unit_of_measure_id": random.randint(1, 5),
                "unit_of_measure_code": random.choice(units),
                "currency_id": random.randint(1, 3),
                "currency_code": random.choice(currencies),
                "unit_price": unit_price,
                "total_amount": total_amount,
                "tax_amount": round(total_amount * 0.08, 2),
                "discount_amount": round(total_amount * random.uniform(0, 0.1), 2),
                "client_id": random.randint(1, 3),
                "created_by": random.randint(1, 5),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_deleted": False,
                "gl_account": f"GL-{random.randint(1000, 9999)}",
                "cost_center": f"CC-{random.randint(100, 999)}"
            })
        
        # Apply filters
        if invoice_id:
            all_items = [item for item in all_items if item["invoice_id"] == invoice_id]
        
        if client_id:
            all_items = [item for item in all_items if item["client_id"] == client_id]
        
        # Sort by item number
        all_items.sort(key=lambda x: x["item_number"])
        
        # Apply pagination
        total = len(all_items)
        items = all_items[skip:skip + limit]
        
        result = {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total,
            "summary": {
                "total_amount": sum(item["total_amount"] for item in all_items),
                "total_tax": sum(item["tax_amount"] for item in all_items),
                "total_discount": sum(item["discount_amount"] for item in all_items),
                "item_count": total
            }
        }
        
        # Cache for 5 minutes
        await redis_cache.set(cache_key, result, expire=300)
        
        logger.info(f"Retrieved {len(items)} invoice items (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting invoice items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice items"
        )


@router.get("/{item_id}", summary="Get invoice item details")
async def get_invoice_item_details(
    item_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns detailed information about a specific invoice item"""
    try:
        # Check cache first
        cache_key = f"invoice_item_details:{item_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock detailed invoice item
        if item_id not in range(1, 201):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice item not found"
            )
        
        item_detail = {
            "id": item_id,
            "invoice_id": random.randint(1, 50),
            "invoice_number": f"INV-2023-{random.randint(1000, 9999)}",
            "item_number": f"ITEM-{item_id:04d}",
            "type": "product",
            "description": "High-quality office chair with ergonomic design",
            "detailed_specification": {
                "brand": "ErgoChair Pro",
                "model": "EC-2023",
                "color": "Black",
                "warranty": "5 years",
                "dimensions": "65cm x 65cm x 120cm"
            },
            "subcategory_l1_id": 1,
            "subcategory_l1_name": "Office Supplies",
            "subcategory_l2_id": 11,
            "subcategory_l2_name": "Furniture",
            "subcategory_l3_id": 111,
            "subcategory_l3_name": "Seating",
            "qty": 2,
            "unit_of_measure_id": 1,
            "unit_of_measure_code": "EA",
            "unit_of_measure_name": "Each",
            "currency_id": 1,
            "currency_code": "USD",
            "currency_symbol": "$",
            "unit_price": 350.00,
            "total_amount": 700.00,
            "tax_amount": 56.00,
            "tax_rate": 8.0,
            "discount_amount": 35.00,
            "discount_percentage": 5.0,
            "net_amount": 721.00,
            "client_id": 1,
            "created_by": 3,
            "created_by_name": "John Doe",
            "created_at": "2023-12-01T10:30:00Z",
            "updated_at": "2023-12-01T10:30:00Z",
            "is_deleted": False,
            "gl_account": "GL-5000",
            "gl_account_name": "Office Equipment",
            "cost_center": "CC-100",
            "cost_center_name": "Administration",
            "supplier_id": 15,
            "supplier_name": "Office Furniture Plus",
            "delivery_date": "2023-12-15",
            "notes": "Deliver to 5th floor reception area"
        }
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, item_detail, expire=600)
        
        logger.info(f"Retrieved invoice item details: {item_id}")
        return item_detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invoice item details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice item details"
        )


@router.get("/invoice/{invoice_id}/items", summary="Get all items for an invoice")
async def get_invoice_items_by_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns all items for a specific invoice"""
    try:
        # Check cache first
        cache_key = f"invoice_items_by_invoice:{invoice_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock invoice items for specific invoice
        items = []
        item_count = random.randint(3, 8)  # 3-8 items per invoice
        
        for i in range(1, item_count + 1):
            qty = random.randint(1, 10)
            unit_price = round(random.uniform(25.0, 200.0), 2)
            total_amount = round(qty * unit_price, 2)
            
            items.append({
                "id": i,
                "invoice_id": invoice_id,
                "item_number": f"ITEM-{i:03d}",
                "description": f"Invoice item {i} - {random.choice(['Software license', 'Office supplies', 'Consulting hours', 'Equipment rental'])}",
                "qty": qty,
                "unit_of_measure_code": random.choice(["EA", "HR", "KG", "L"]),
                "unit_price": unit_price,
                "total_amount": total_amount,
                "tax_amount": round(total_amount * 0.08, 2),
                "subcategory_name": random.choice(["IT & Technology", "Office Supplies", "Professional Services"])
            })
        
        result = {
            "invoice_id": invoice_id,
            "items": items,
            "item_count": len(items),
            "subtotal": sum(item["total_amount"] for item in items),
            "total_tax": sum(item["tax_amount"] for item in items),
            "grand_total": sum(item["total_amount"] + item["tax_amount"] for item in items)
        }
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, result, expire=600)
        
        logger.info(f"Retrieved {len(items)} items for invoice {invoice_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting items for invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice items"
        )


@router.get("/stats/summary", summary="Get invoice items statistics")
async def get_invoice_items_stats(db: AsyncSession = Depends(get_async_db)):
    """Returns statistics about invoice items"""
    try:
        # Check cache first
        cache_key = "invoice_items_stats"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock statistics
        stats = {
            "total_items": 1847,
            "total_value": 2456789.12,
            "average_item_value": 1330.45,
            "items_by_type": [
                {"type": "product", "count": 1108, "percentage": 60.0, "value": 1474073.47},
                {"type": "service", "count": 554, "percentage": 30.0, "value": 737036.74},
                {"type": "expense", "count": 185, "percentage": 10.0, "value": 245678.91}
            ],
            "items_by_category": [
                {"category": "IT & Technology", "count": 462, "value": 614196.78},
                {"category": "Office Supplies", "count": 369, "value": 368578.64},
                {"category": "Professional Services", "count": 277, "value": 491357.82},
                {"category": "Travel & Entertainment", "count": 185, "value": 245678.91},
                {"category": "Other", "count": 554, "value": 736976.97}
            ],
            "top_currencies": [
                {"currency": "USD", "count": 1293, "percentage": 70.0},
                {"currency": "EUR", "count": 369, "percentage": 20.0},
                {"currency": "GBP", "count": 185, "percentage": 10.0}
            ],
            "recent_activity": {
                "items_added_today": 23,
                "items_modified_today": 15,
                "total_value_today": 45678.90
            }
        }
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, stats, expire=900)
        
        logger.info("Retrieved invoice items statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting invoice items stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice items statistics"
        )