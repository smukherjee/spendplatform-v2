"""
Async User Management router for SpendPlatform v2 - Enhanced user management
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
router = APIRouter(prefix="/user-management", tags=["user-management-async"])


@router.get("/", summary="Enhanced user management list")
async def get_enhanced_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    role_filter: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns enhanced user list with management capabilities"""
    try:
        # Check cache first
        cache_key = f"enhanced_users:{skip}:{limit}:{client_id or 'all'}:{role_filter or 'all'}:{status_filter or 'all'}:{search or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock enhanced users data
        all_users = [
            {
                "id": 1,
                "username": "superadmin",
                "email": "superadmin@company.com",
                "first_name": "Super",
                "last_name": "Administrator",
                "full_name": "Super Administrator",
                "client_id": 1,
                "client_name": "System Client",
                "roles": ["Super Admin"],
                "primary_role": "Super Admin",
                "is_active": True,
                "last_login": datetime.now().isoformat(),
                "login_count": 1543,
                "failed_login_attempts": 0,
                "account_locked": False,
                "password_expires_at": "2024-06-15T00:00:00Z",
                "created_at": "2023-01-01T00:00:00Z",
                "created_by": "System",
                "department": "IT Administration",
                "job_title": "System Administrator",
                "phone": "+1-555-0001",
                "manager_id": None,
                "manager_name": None,
                "approval_limit": 1000000.00,
                "access_level": "system"
            },
            {
                "id": 2,
                "username": "client_admin",
                "email": "admin@acme.com",
                "first_name": "Client",
                "last_name": "Administrator",
                "full_name": "Client Administrator",
                "client_id": 1,
                "client_name": "Acme Corporation",
                "roles": ["Client Admin"],
                "primary_role": "Client Admin",
                "is_active": True,
                "last_login": datetime.now().isoformat(),
                "login_count": 892,
                "failed_login_attempts": 0,
                "account_locked": False,
                "password_expires_at": "2024-03-15T00:00:00Z",
                "created_at": "2023-02-01T00:00:00Z",
                "created_by": "superadmin",
                "department": "Administration",
                "job_title": "Client Administrator",
                "phone": "+1-555-0002",
                "manager_id": 1,
                "manager_name": "Super Administrator",
                "approval_limit": 100000.00,
                "access_level": "client"
            },
            {
                "id": 3,
                "username": "john.doe",
                "email": "john.doe@acme.com",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "client_id": 1,
                "client_name": "Acme Corporation",
                "roles": ["User", "Approver"],
                "primary_role": "User",
                "is_active": True,
                "last_login": datetime.now().isoformat(),
                "login_count": 456,
                "failed_login_attempts": 1,
                "account_locked": False,
                "password_expires_at": "2024-01-20T00:00:00Z",
                "created_at": "2023-03-15T00:00:00Z",
                "created_by": "client_admin",
                "department": "Finance",
                "job_title": "Financial Analyst",
                "phone": "+1-555-0003",
                "manager_id": 2,
                "manager_name": "Client Administrator",
                "approval_limit": 25000.00,
                "access_level": "user"
            },
            {
                "id": 4,
                "username": "jane.smith",
                "email": "jane.smith@acme.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "full_name": "Jane Smith",
                "client_id": 1,
                "client_name": "Acme Corporation",
                "roles": ["User"],
                "primary_role": "User",
                "is_active": False,  # Inactive user
                "last_login": "2023-11-01T08:30:00Z",
                "login_count": 234,
                "failed_login_attempts": 3,
                "account_locked": True,
                "password_expires_at": "2023-12-01T00:00:00Z",
                "created_at": "2023-05-10T00:00:00Z",
                "created_by": "client_admin",
                "department": "Marketing",
                "job_title": "Marketing Specialist",
                "phone": "+1-555-0004",
                "manager_id": 2,
                "manager_name": "Client Administrator",
                "approval_limit": 5000.00,
                "access_level": "user"
            },
            {
                "id": 5,
                "username": "mike.wilson",
                "email": "mike.wilson@beta.com",
                "first_name": "Mike",
                "last_name": "Wilson",
                "full_name": "Mike Wilson",
                "client_id": 2,
                "client_name": "Beta Industries",
                "roles": ["Client Admin"],
                "primary_role": "Client Admin",
                "is_active": True,
                "last_login": datetime.now().isoformat(),
                "login_count": 678,
                "failed_login_attempts": 0,
                "account_locked": False,
                "password_expires_at": "2024-04-01T00:00:00Z",
                "created_at": "2023-01-20T00:00:00Z",
                "created_by": "superadmin",
                "department": "Administration",
                "job_title": "Operations Manager",
                "phone": "+1-555-0005",
                "manager_id": 1,
                "manager_name": "Super Administrator",
                "approval_limit": 75000.00,
                "access_level": "client"
            }
        ]
        
        # Apply filters
        if client_id:
            all_users = [u for u in all_users if u["client_id"] == client_id]
        
        if role_filter:
            all_users = [u for u in all_users if role_filter in u["roles"]]
        
        if status_filter:
            if status_filter == "active":
                all_users = [u for u in all_users if u["is_active"]]
            elif status_filter == "inactive":
                all_users = [u for u in all_users if not u["is_active"]]
            elif status_filter == "locked":
                all_users = [u for u in all_users if u["account_locked"]]
        
        if search:
            search_lower = search.lower()
            all_users = [
                u for u in all_users 
                if (search_lower in u["full_name"].lower() or 
                    search_lower in u["email"].lower() or
                    search_lower in u["username"].lower() or
                    search_lower in u["department"].lower())
            ]
        
        # Sort by full name
        all_users.sort(key=lambda x: x["full_name"])
        
        # Apply pagination
        total = len(all_users)
        users = all_users[skip:skip + limit]
        
        result = {
            "users": users,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total,
            "summary": {
                "active_users": len([u for u in all_users if u["is_active"]]),
                "inactive_users": len([u for u in all_users if not u["is_active"]]),
                "locked_accounts": len([u for u in all_users if u["account_locked"]]),
                "password_expiring_soon": len([u for u in all_users if u["password_expires_at"] < "2024-01-01T00:00:00Z"])
            }
        }
        
        # Cache for 5 minutes
        await redis_cache.set(cache_key, result, expire=300)
        
        logger.info(f"Retrieved {len(users)} enhanced users (total: {total})")
        return result
        
    except Exception as e:
        logger.error(f"Error getting enhanced users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve enhanced users"
        )


@router.post("/create", summary="Create new user")
async def create_user(
    user_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new user with role assignments"""
    try:
        # Simulate user creation
        new_user = {
            "id": random.randint(1000, 9999),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "full_name": f"{user_data.get('first_name')} {user_data.get('last_name')}",
            "client_id": user_data.get("client_id", 1),
            "client_name": "Acme Corporation",
            "roles": user_data.get("roles", ["User"]),
            "primary_role": user_data.get("roles", ["User"])[0],
            "is_active": True,
            "last_login": None,
            "login_count": 0,
            "failed_login_attempts": 0,
            "account_locked": False,
            "password_expires_at": "2024-06-15T00:00:00Z",
            "created_at": datetime.now().isoformat(),
            "created_by": "system",  # Would be current user
            "department": user_data.get("department"),
            "job_title": user_data.get("job_title"),
            "phone": user_data.get("phone"),
            "manager_id": user_data.get("manager_id"),
            "approval_limit": user_data.get("approval_limit", 5000.00),
            "access_level": "user"
        }
        
        # Clear user caches
        await redis_cache.delete_pattern("enhanced_users:*")
        
        logger.info(f"Created new user: {new_user['username']}")
        return new_user
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/{user_id}", summary="Update user")
async def update_user(
    user_id: int,
    user_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing user"""
    try:
        # Simulate user update
        updated_user = {
            "id": user_id,
            "username": user_data.get("username", f"user_{user_id}"),
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "roles": user_data.get("roles", ["User"]),
            "is_active": user_data.get("is_active", True),
            "department": user_data.get("department"),
            "job_title": user_data.get("job_title"),
            "phone": user_data.get("phone"),
            "approval_limit": user_data.get("approval_limit"),
            "updated_at": datetime.now().isoformat(),
            "updated_by": "system"  # Would be current user
        }
        
        # Clear user caches
        await redis_cache.delete_pattern("enhanced_users:*")
        await redis_cache.delete(f"user_details:{user_id}")
        
        logger.info(f"Updated user: {user_id}")
        return updated_user
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.post("/{user_id}/reset-password", summary="Reset user password")
async def reset_user_password(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Reset password for a user"""
    try:
        # Simulate password reset
        reset_result = {
            "user_id": user_id,
            "temporary_password": f"TempPass{random.randint(1000, 9999)}!",
            "password_expires_at": "2023-12-16T00:00:00Z",  # Expires in 1 day
            "must_change_on_login": True,
            "reset_at": datetime.now().isoformat(),
            "reset_by": "system"  # Would be current user
        }
        
        logger.info(f"Reset password for user: {user_id}")
        return reset_result
        
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.post("/{user_id}/unlock", summary="Unlock user account")
async def unlock_user_account(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Unlock a locked user account"""
    try:
        # Simulate account unlock
        unlock_result = {
            "user_id": user_id,
            "account_locked": False,
            "failed_login_attempts": 0,
            "unlocked_at": datetime.now().isoformat(),
            "unlocked_by": "system"  # Would be current user
        }
        
        # Clear user caches
        await redis_cache.delete_pattern("enhanced_users:*")
        
        logger.info(f"Unlocked user account: {user_id}")
        return unlock_result
        
    except Exception as e:
        logger.error(f"Error unlocking account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock account"
        )


@router.get("/stats/management", summary="Get user management statistics")
async def get_user_management_stats(db: AsyncSession = Depends(get_async_db)):
    """Returns statistics for user management dashboard"""
    try:
        # Check cache first
        cache_key = "user_management_stats"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock management statistics
        stats = {
            "total_users": 127,
            "active_users": 118,
            "inactive_users": 9,
            "locked_accounts": 3,
            "pending_activations": 5,
            "password_expiring_soon": 12,
            "users_by_role": [
                {"role": "User", "count": 89, "percentage": 70.1},
                {"role": "Approver", "count": 23, "percentage": 18.1},
                {"role": "Client Admin", "count": 12, "percentage": 9.4},
                {"role": "Super Admin", "count": 3, "percentage": 2.4}
            ],
            "users_by_client": [
                {"client": "Acme Corporation", "count": 78, "percentage": 61.4},
                {"client": "Beta Industries", "count": 32, "percentage": 25.2},
                {"client": "Gamma LLC", "count": 17, "percentage": 13.4}
            ],
            "recent_activity": {
                "new_users_this_month": 8,
                "password_resets_this_month": 15,
                "account_lockouts_this_month": 3,
                "role_changes_this_month": 5
            },
            "security_alerts": {
                "failed_login_attempts_today": 23,
                "suspicious_login_locations": 2,
                "accounts_with_weak_passwords": 7
            }
        }
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, stats, expire=600)
        
        logger.info("Retrieved user management statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting user management stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user management statistics"
        )