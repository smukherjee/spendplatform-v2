"""
Async Role router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/roles", tags=["role-async"])


@router.get("/", summary="List all roles")
async def get_roles(db: AsyncSession = Depends(get_async_db)):
    """Returns a list of all roles"""
    try:
        # Check cache first
        cache_key = "roles:all"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock role data
        roles = [
            {
                "id": 1,
                "name": "superadmin",
                "description": "Super Administrator with full system access",
                "permissions": ["*"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 2,
                "name": "client_admin",
                "description": "Client Administrator with client-level access",
                "permissions": ["client:read", "client:write", "user:read", "user:write", "invoice:read", "invoice:write"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 3,
                "name": "user",
                "description": "Standard user with limited access",
                "permissions": ["invoice:read", "supplier:read", "report:read"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 4,
                "name": "approver",
                "description": "Invoice approver with approval permissions",
                "permissions": ["invoice:read", "invoice:approve", "supplier:read", "report:read"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            }
        ]
        
        # Cache for 30 minutes
        await redis_cache.set(cache_key, roles, expire=1800)
        
        logger.info("Retrieved roles list")
        return roles
        
    except Exception as e:
        logger.error(f"Error getting roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve roles"
        )


@router.get("/{role_id}", summary="Get role by ID")
async def get_role(role_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns a specific role by ID"""
    try:
        # Mock role data
        roles = {
            1: {
                "id": 1,
                "name": "superadmin",
                "description": "Super Administrator with full system access",
                "permissions": ["*"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "user_count": 1
            },
            2: {
                "id": 2,
                "name": "client_admin",
                "description": "Client Administrator with client-level access",
                "permissions": ["client:read", "client:write", "user:read", "user:write", "invoice:read", "invoice:write"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "user_count": 3
            },
            3: {
                "id": 3,
                "name": "user",
                "description": "Standard user with limited access",
                "permissions": ["invoice:read", "supplier:read", "report:read"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "user_count": 12
            },
            4: {
                "id": 4,
                "name": "approver",
                "description": "Invoice approver with approval permissions",
                "permissions": ["invoice:read", "invoice:approve", "supplier:read", "report:read"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "user_count": 5
            }
        }
        
        if role_id in roles:
            return roles[role_id]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role"
        )