"""
Async Supplier router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/suppliers", tags=["supplier-async"])


@router.get("/", summary="List all suppliers")
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns a list of suppliers with search and pagination"""
    try:
        # Check cache first
        cache_key = f"suppliers:list:{skip}:{limit}:{search or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock supplier data
        all_suppliers = [
            {
                "id": 1,
                "name": "Acme Corporation",
                "code": "ACME001",
                "email": "contact@acme.com",
                "phone": "+1-555-0101",
                "address": "123 Business St, Corporate City, CC 12345",
                "contact_person": "John Smith",
                "status": "active",
                "client_id": 1,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 2,
                "name": "Global Supplies Ltd",
                "code": "GLOB002",
                "email": "info@globalsupplies.com",
                "phone": "+1-555-0102",
                "address": "456 Supply Ave, Trade Town, TT 67890",
                "contact_person": "Jane Doe",
                "status": "active",
                "client_id": 1,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 3,
                "name": "Tech Solutions Inc",
                "code": "TECH003",
                "email": "sales@techsolutions.com",
                "phone": "+1-555-0103",
                "address": "789 Innovation Blvd, Tech Park, TP 11111",
                "contact_person": "Mike Johnson",
                "status": "active",
                "client_id": 1,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 4,
                "name": "Office Plus",
                "code": "OFF004",
                "email": "orders@officeplus.com",
                "phone": "+1-555-0104",
                "address": "321 Office Dr, Business Park, BP 22222",
                "contact_person": "Sarah Wilson",
                "status": "active",
                "client_id": 1,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 5,
                "name": "Industrial Equipment Co",
                "code": "IND005",
                "email": "contact@industrial-eq.com",
                "phone": "+1-555-0105",
                "address": "654 Industrial Way, Factory District, FD 33333",
                "contact_person": "Robert Brown",
                "status": "active",
                "client_id": 1,
                "created_at": "2025-01-01T00:00:00"
            }
        ]
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            all_suppliers = [
                supplier for supplier in all_suppliers
                if search_lower in supplier["name"].lower() or 
                   search_lower in supplier["code"].lower() or
                   search_lower in supplier["contact_person"].lower()
            ]
        
        # Apply pagination
        total = len(all_suppliers)
        suppliers = all_suppliers[skip:skip + limit]
        
        result = {
            "items": suppliers,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total
        }
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, result, expire=600)
        
        logger.info(f"Retrieved {len(suppliers)} suppliers (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve suppliers"
        )


@router.get("/{supplier_id}", summary="Get supplier by ID")
async def get_supplier(supplier_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns a specific supplier by ID"""
    try:
        # Mock supplier data
        suppliers = {
            1: {
                "id": 1,
                "name": "Acme Corporation",
                "code": "ACME001",
                "email": "contact@acme.com",
                "phone": "+1-555-0101",
                "address": "123 Business St, Corporate City, CC 12345",
                "contact_person": "John Smith",
                "status": "active",
                "client_id": 1,
                "payment_terms": "Net 30",
                "tax_id": "123-45-6789",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            },
            2: {
                "id": 2,
                "name": "Global Supplies Ltd",
                "code": "GLOB002",
                "email": "info@globalsupplies.com",
                "phone": "+1-555-0102",
                "address": "456 Supply Ave, Trade Town, TT 67890",
                "contact_person": "Jane Doe",
                "status": "active",
                "client_id": 1,
                "payment_terms": "Net 45",
                "tax_id": "987-65-4321",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
        
        if supplier_id in suppliers:
            return suppliers[supplier_id]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier {supplier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supplier"
        )