"""
Async Client router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clients", tags=["client-async"])


@router.get("/", summary="List all clients")
async def get_clients(db: AsyncSession = Depends(get_async_db)):
    """Returns a list of all clients"""
    try:
        # Mock client data for now
        clients = [
            {
                "id": 1,
                "name": "Default Client",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        ]
        
        logger.info("Retrieved clients list")
        return clients
        
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve clients"
        )


@router.get("/{client_id}", summary="Get client by ID")
async def get_client(client_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns a specific client by ID"""
    try:
        # Mock client data
        if client_id == 1:
            client = {
                "id": 1,
                "name": "Default Client",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
            return client
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client"
        )


@router.get("/{client_id}/settings", summary="Get client settings")
async def get_client_settings(client_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns client settings"""
    try:
        # Mock settings data
        settings = {
            "client_id": client_id,
            "theme": "default",
            "currency": "USD",
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "decimal_places": 2,
            "approval_workflow": True
        }
        
        logger.info(f"Retrieved settings for client {client_id}")
        return settings
        
    except Exception as e:
        logger.error(f"Error getting client settings {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client settings"
        )