"""
Async user management router with performance optimizations
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload
from typing import Optional
import asyncio
import logging
import time

from database_async import get_async_db
from cache_async import redis_cache
from models.user import User
from models.role import Role
from schemas_optimized import UserReadOptimized, PaginatedUserResponse
from utils import get_current_role, enforce_role, get_client_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users-async", tags=["User-Async"])

@router.get("/", response_model=PaginatedUserResponse)
async def get_users_optimized(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    search: Optional[str] = Query(None, description="Search term for username or email"),
    role: str = Depends(get_current_role),
    client_id: int = Depends(get_client_id),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get paginated users with optimized async queries and caching
    """
    start_time = time.time()
    
    try:
        # Enforce role-based access
        enforce_role(role, ["client_admin", "superadmin"])
        
        # Build cache key
        cache_key = f"users:{client_id}:{skip}:{limit}:{search or 'all'}:{role}"
        
        # Try cache first
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for users query: {cache_key} ({time.time() - start_time:.3f}s)")
            return cached_result
        
        # Build base query with eager loading to prevent N+1 queries
        query = select(User).options(
            selectinload(User.roles)  # Prevent N+1 queries for roles
        )
        
        # Apply role-based filtering
        if role != "superadmin":
            query = query.where(User.client_id == client_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                func.lower(User.username).like(search_term) |
                func.lower(User.email).like(search_term)
            )
        
        # Build count query (same filters)
        count_query = select(func.count(User.id))
        if role != "superadmin":
            count_query = count_query.where(User.client_id == client_id)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(
                func.lower(User.username).like(search_term) |
                func.lower(User.email).like(search_term)
            )
        
        # Execute queries concurrently for better performance
        users_task = db.execute(query.offset(skip).limit(limit))
        count_task = db.execute(count_query)
        
        users_result, count_result = await asyncio.gather(users_task, count_task)
        
        users = users_result.scalars().all()
        total = count_result.scalar()
        
        # Convert to response format
        user_items = []
        for user in users:
            user_items.append(UserReadOptimized(
                id=user.id,
                username=user.username,
                email=user.email,
                client_id=user.client_id,
                personalisation=user.personalisation,
                roles=[role.name for role in user.roles] if user.roles else []
            ))
        
        # Prepare response
        response = PaginatedUserResponse(
            items=user_items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total
        )
        
        # Cache result for 5 minutes
        await redis_cache.set(cache_key, response, expire=300)
        
        query_time = time.time() - start_time
        logger.info(f"Retrieved {len(users)} users for client {client_id} in {query_time:.3f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve users"
        )

@router.get("/health", include_in_schema=False)
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """Health check endpoint"""
    return {"status": "healthy", "users_endpoint": "operational"}

@router.get("/test", response_model=PaginatedUserResponse, include_in_schema=False)
async def get_users_test(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(25, ge=1, le=1000, description="Number of users to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Test endpoint without authentication for performance testing"""
    cache_key = f"users_test:{skip}:{limit}"
    
    # Try cache first
    cached_result = await redis_cache.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        # Execute query with eager loading
        query = (
            select(User)
            .options(selectinload(User.roles))  # Eager load roles to avoid N+1
            .offset(skip)
            .limit(limit)
        )
        
        start_time = time.time()
        result = await db.execute(query)
        users = result.scalars().all()
        query_time = time.time() - start_time
        
        # Get total count efficiently
        count_query = select(func.count(User.id))
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Convert users to schema format
        user_items = []
        for user in users:
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "client_id": user.client_id,
                "personalisation": user.personalisation,
                "roles": [role.name for role in user.roles] if user.roles else []
            }
            user_items.append(UserReadOptimized(**user_dict))
        
        response = PaginatedUserResponse(
            items=user_items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit < total)
        )
        
        # Cache for 5 minutes
        await redis_cache.set(cache_key, response, expire=300)
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching users test: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Background task functions
async def invalidate_user_cache(client_id: int):
    """Invalidate user cache for client"""
    try:
        await redis_cache.delete_pattern(f"users:{client_id}:*")
        logger.info(f"Invalidated user cache for client {client_id}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for client {client_id}: {str(e)}")

async def log_user_activity(user_id: int, action: str, details: str = ""):
    """Log user activity for audit"""
    logger.info(f"AUDIT: User {user_id} performed {action} - {details}")