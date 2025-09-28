"""
Async Screen Permissions router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/screen-permissions", tags=["screen-permissions-async"])


@router.get("/screens", summary="List all screens")
async def get_screens(
    active_only: bool = Query(True),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all available screens in the system"""
    try:
        # Check cache first
        cache_key = f"screens:{active_only}:{category or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock screens data
        screens = [
            {
                "id": 1,
                "name": "Dashboard",
                "route": "/dashboard",
                "category": "Analytics",
                "description": "Main dashboard with key metrics and charts",
                "is_active": True,
                "icon": "dashboard",
                "order": 1,
                "parent_id": None,
                "permissions_required": ["dashboard_view"]
            },
            {
                "id": 2,
                "name": "Invoice Management",
                "route": "/invoices",
                "category": "Financial",
                "description": "Create, view, and manage invoices",
                "is_active": True,
                "icon": "receipt",
                "order": 2,
                "parent_id": None,
                "permissions_required": ["invoice_view"]
            },
            {
                "id": 3,
                "name": "Create Invoice",
                "route": "/invoices/create",
                "category": "Financial",
                "description": "Create new invoices",
                "is_active": True,
                "icon": "add",
                "order": 1,
                "parent_id": 2,
                "permissions_required": ["invoice_create"]
            },
            {
                "id": 4,
                "name": "Supplier Management",
                "route": "/suppliers",
                "category": "Master Data",
                "description": "Manage supplier information and relationships",
                "is_active": True,
                "icon": "business",
                "order": 3,
                "parent_id": None,
                "permissions_required": ["supplier_view"]
            },
            {
                "id": 5,
                "name": "User Management",
                "route": "/users",
                "category": "Administration",
                "description": "Manage user accounts and permissions",
                "is_active": True,
                "icon": "people",
                "order": 4,
                "parent_id": None,
                "permissions_required": ["user_management"]
            },
            {
                "id": 6,
                "name": "Reports",
                "route": "/reports",
                "category": "Analytics",
                "description": "Generate and view various reports",
                "is_active": True,
                "icon": "assessment",
                "order": 5,
                "parent_id": None,
                "permissions_required": ["reports_view"]
            },
            {
                "id": 7,
                "name": "Settings",
                "route": "/settings",
                "category": "Administration",
                "description": "System and client configuration settings",
                "is_active": True,
                "icon": "settings",
                "order": 6,
                "parent_id": None,
                "permissions_required": ["settings_manage"]
            },
            {
                "id": 8,
                "name": "Audit Logs",
                "route": "/audit",
                "category": "Administration",
                "description": "View system audit logs and security events",
                "is_active": True,
                "icon": "security",
                "order": 7,
                "parent_id": None,
                "permissions_required": ["audit_view"]
            },
            {
                "id": 9,
                "name": "Legacy Screen",
                "route": "/legacy",
                "category": "Other",
                "description": "Old screen for backward compatibility",
                "is_active": False,
                "icon": "archive",
                "order": 99,
                "parent_id": None,
                "permissions_required": ["legacy_access"]
            }
        ]
        
        # Apply filters
        if active_only:
            screens = [s for s in screens if s["is_active"]]
        
        if category:
            screens = [s for s in screens if s["category"].lower() == category.lower()]
        
        # Sort by order
        screens.sort(key=lambda x: (x["order"], x["name"]))
        
        # Cache for 30 minutes
        await redis_cache.set(cache_key, screens, expire=1800)
        
        logger.info(f"Retrieved {len(screens)} screens")
        return screens
        
    except Exception as e:
        logger.error(f"Error getting screens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve screens"
        )


@router.get("/roles/{role_id}/permissions", summary="Get role screen permissions")
async def get_role_screen_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get screen permissions for a specific role"""
    try:
        # Check cache first
        cache_key = f"role_screen_permissions:{role_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock role permissions
        role_permissions_map = {
            1: {  # Super Admin
                "role_id": 1,
                "role_name": "Super Admin",
                "permissions": [
                    {
                        "screen_id": 1,
                        "screen_name": "Dashboard",
                        "screen_route": "/dashboard",
                        "can_view": True,
                        "can_create": True,
                        "can_edit": True,
                        "can_delete": True
                    },
                    {
                        "screen_id": 2,
                        "screen_name": "Invoice Management",
                        "screen_route": "/invoices",
                        "can_view": True,
                        "can_create": True,
                        "can_edit": True,
                        "can_delete": True
                    },
                    {
                        "screen_id": 5,
                        "screen_name": "User Management",
                        "screen_route": "/users",
                        "can_view": True,
                        "can_create": True,
                        "can_edit": True,
                        "can_delete": True
                    },
                    {
                        "screen_id": 7,
                        "screen_name": "Settings",
                        "screen_route": "/settings",
                        "can_view": True,
                        "can_create": True,
                        "can_edit": True,
                        "can_delete": True
                    },
                    {
                        "screen_id": 8,
                        "screen_name": "Audit Logs",
                        "screen_route": "/audit",
                        "can_view": True,
                        "can_create": False,
                        "can_edit": False,
                        "can_delete": False
                    }
                ]
            },
            3: {  # User
                "role_id": 3,
                "role_name": "User",
                "permissions": [
                    {
                        "screen_id": 1,
                        "screen_name": "Dashboard",
                        "screen_route": "/dashboard",
                        "can_view": True,
                        "can_create": False,
                        "can_edit": False,
                        "can_delete": False
                    },
                    {
                        "screen_id": 2,
                        "screen_name": "Invoice Management",
                        "screen_route": "/invoices",
                        "can_view": True,
                        "can_create": True,
                        "can_edit": True,
                        "can_delete": False
                    },
                    {
                        "screen_id": 3,
                        "screen_name": "Create Invoice",
                        "screen_route": "/invoices/create",
                        "can_view": True,
                        "can_create": True,
                        "can_edit": False,
                        "can_delete": False
                    },
                    {
                        "screen_id": 6,
                        "screen_name": "Reports",
                        "screen_route": "/reports",
                        "can_view": True,
                        "can_create": False,
                        "can_edit": False,
                        "can_delete": False
                    }
                ]
            }
        }
        
        if role_id not in role_permissions_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permissions not found"
            )
        
        permissions = role_permissions_map[role_id]
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, permissions, expire=900)
        
        logger.info(f"Retrieved screen permissions for role {role_id}")
        return permissions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role screen permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role screen permissions"
        )


@router.get("/user/{user_id}/accessible-screens", summary="Get user accessible screens")
async def get_user_accessible_screens(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all screens accessible to a specific user based on their roles"""
    try:
        # Check cache first
        cache_key = f"user_accessible_screens:{user_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock user accessible screens
        user_screens_map = {
            1: {  # Superadmin
                "user_id": 1,
                "username": "superadmin",
                "roles": ["Super Admin"],
                "accessible_screens": [
                    {"id": 1, "name": "Dashboard", "route": "/dashboard", "category": "Analytics"},
                    {"id": 2, "name": "Invoice Management", "route": "/invoices", "category": "Financial"},
                    {"id": 3, "name": "Create Invoice", "route": "/invoices/create", "category": "Financial"},
                    {"id": 4, "name": "Supplier Management", "route": "/suppliers", "category": "Master Data"},
                    {"id": 5, "name": "User Management", "route": "/users", "category": "Administration"},
                    {"id": 6, "name": "Reports", "route": "/reports", "category": "Analytics"},
                    {"id": 7, "name": "Settings", "route": "/settings", "category": "Administration"},
                    {"id": 8, "name": "Audit Logs", "route": "/audit", "category": "Administration"}
                ]
            },
            3: {  # Regular User
                "user_id": 3,
                "username": "john.doe",
                "roles": ["User"],
                "accessible_screens": [
                    {"id": 1, "name": "Dashboard", "route": "/dashboard", "category": "Analytics"},
                    {"id": 2, "name": "Invoice Management", "route": "/invoices", "category": "Financial"},
                    {"id": 3, "name": "Create Invoice", "route": "/invoices/create", "category": "Financial"},
                    {"id": 6, "name": "Reports", "route": "/reports", "category": "Analytics"}
                ]
            }
        }
        
        if user_id not in user_screens_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User screens not found"
            )
        
        user_screens = user_screens_map[user_id]
        
        # Add navigation structure
        user_screens["navigation"] = {
            "Analytics": [s for s in user_screens["accessible_screens"] if s["category"] == "Analytics"],
            "Financial": [s for s in user_screens["accessible_screens"] if s["category"] == "Financial"],
            "Master Data": [s for s in user_screens["accessible_screens"] if s["category"] == "Master Data"],
            "Administration": [s for s in user_screens["accessible_screens"] if s["category"] == "Administration"]
        }
        
        # Cache for 10 minutes
        await redis_cache.set(cache_key, user_screens, expire=600)
        
        logger.info(f"Retrieved accessible screens for user {user_id}")
        return user_screens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user accessible screens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user accessible screens"
        )


@router.post("/check-permission", summary="Check user permission for screen")
async def check_user_screen_permission(
    permission_check: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db)
):
    """Check if a user has permission to access a specific screen/action"""
    try:
        user_id = permission_check.get("user_id")
        screen_route = permission_check.get("screen_route")
        action = permission_check.get("action", "view")  # view, create, edit, delete
        
        if not user_id or not screen_route:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id and screen_route are required"
            )
        
        # Mock permission check logic
        permission_result = {
            "user_id": user_id,
            "screen_route": screen_route,
            "action": action,
            "has_permission": True,  # Simplified - in real app would check database
            "reason": "User has required role permissions",
            "user_roles": ["User"],
            "required_permissions": [f"screen_{action}"],
            "checked_at": "2023-12-15T10:30:00Z"
        }
        
        # Simulate some permission failures for demo
        if user_id == 3 and screen_route == "/users" and action in ["create", "edit", "delete"]:
            permission_result.update({
                "has_permission": False,
                "reason": "User role does not have admin permissions",
                "required_permissions": ["user_management"]
            })
        
        logger.info(f"Permission check for user {user_id} on {screen_route}/{action}: {permission_result['has_permission']}")
        return permission_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking screen permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check screen permission"
        )