"""
Settings router for SpendPlatform v2 - handles general application settings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging

from database_async import get_async_db
from cache_async import redis_cache
from utils import get_current_role, get_client_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings-async"])


@router.get("/", summary="Get application settings")
async def get_settings(
    role: str = Depends(get_current_role),
    client_id: int = Depends(get_client_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns application settings based on user role and client"""
    try:
        cache_key = f"settings:{role}:{client_id}"
        
        # Try cache first
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Base settings available to all users
        settings = {
            "app_name": "SpendPlatform v2",
            "version": "2.0.0",
            "environment": "development",
            "features": {
                "notifications": True,
                "dark_mode": True,
                "export_reports": True,
                "bulk_operations": True
            },
            "ui": {
                "pagination_size": 25,
                "date_format": "DD/MM/YYYY",
                "currency_symbol": "$",
                "decimal_places": 2
            }
        }
        
        # Add role-specific settings
        if role == "superadmin":
            settings.update({
                "admin_features": {
                    "system_monitoring": True,
                    "user_management": True,
                    "client_management": True,
                    "system_settings": True,
                    "audit_logs": True,
                    "backup_restore": True
                },
                "limits": {
                    "max_clients": 1000,
                    "max_users_per_client": 10000,
                    "max_file_upload_mb": 500
                }
            })
        elif role == "client_admin":
            settings.update({
                "admin_features": {
                    "user_management": True,
                    "client_settings": True,
                    "reports": True,
                    "bulk_import": True
                },
                "limits": {
                    "max_users": 1000,
                    "max_file_upload_mb": 100
                }
            })
        else:  # regular user
            settings.update({
                "user_features": {
                    "profile_edit": True,
                    "basic_reports": True,
                    "data_export": True
                },
                "limits": {
                    "max_file_upload_mb": 25
                }
            })
        
        # Add client-specific settings for non-superadmin users
        if role != "superadmin":
            settings["client"] = {
                "id": client_id,
                "name": f"Client {client_id}",
                "timezone": "UTC",
                "locale": "en-US"
            }
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, settings, expire=900)
        
        logger.info(f"Retrieved settings for role: {role}, client: {client_id}")
        return settings
        
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve settings"
        )


@router.put("/", summary="Update application settings")
async def update_settings(
    settings_data: Dict[str, Any],
    role: str = Depends(get_current_role),
    client_id: int = Depends(get_client_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Updates application settings (admin only)"""
    try:
        # Only allow superadmin and client_admin to update settings
        if role not in ["superadmin", "client_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update settings"
            )
        
        # Validate settings data
        allowed_keys = {
            "features", "ui", "client", "notifications", 
            "timezone", "locale", "currency_symbol", "date_format"
        }
        
        # Filter out any non-allowed keys
        filtered_settings = {k: v for k, v in settings_data.items() if k in allowed_keys}
        
        if not filtered_settings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid settings provided"
            )
        
        # For now, just return success (would normally update database)
        # TODO: Implement actual database update logic
        
        # Invalidate cache
        cache_pattern = f"settings:{role}:*" if role == "superadmin" else f"settings:*:{client_id}"
        await redis_cache.delete_pattern(cache_pattern)
        
        logger.info(f"Settings updated by role: {role}, client: {client_id}")
        return {
            "message": "Settings updated successfully",
            "updated_keys": list(filtered_settings.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )


@router.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "settings_endpoint": "operational"}