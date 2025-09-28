"""
Async Client Settings router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["client-settings-async"])


@router.get("", summary="Get client settings")
async def get_client_settings(
    client_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns client settings for the specified client"""
    try:
        # Check cache first
        cache_key = f"client_settings:{client_id or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock client settings data
        if client_id:
            # Return specific client settings
            settings = [{
                "id": 1,
                "client_id": client_id,
                "feature_flags": {
                    "enable_multi_currency": True,
                    "enable_approval_workflow": True,
                    "enable_bulk_import": True,
                    "enable_advanced_reporting": True,
                    "enable_supplier_portal": False,
                    "enable_mobile_app": True,
                    "enable_api_access": True
                },
                "branding": {
                    "primary_color": "#1976d2",
                    "secondary_color": "#424242",
                    "logo_url": "/assets/client-logo.png",
                    "company_name": "Acme Corporation",
                    "favicon_url": "/assets/favicon.ico"
                },
                "ui_personalisation": {
                    "default_currency": "USD",
                    "date_format": "MM/DD/YYYY",
                    "number_format": "US",
                    "timezone": "America/New_York",
                    "language": "en-US",
                    "items_per_page": 25,
                    "enable_dark_mode": False,
                    "dashboard_layout": "standard"
                },
                "business_rules": {
                    "auto_approval_limit": 1000.00,
                    "require_po_number": True,
                    "mandatory_cost_center": True,
                    "invoice_numbering_format": "INV-{YYYY}-{######}",
                    "fiscal_year_start": "01-01"
                },
                "integrations": {
                    "erp_system": "SAP",
                    "accounting_system": "QuickBooks",
                    "email_notifications": True,
                    "webhook_url": "https://api.client.com/webhooks/spend",
                    "api_rate_limit": 1000
                }
            }]
        else:
            # Return all client settings (for superadmin)
            settings = [
                {
                    "id": 1,
                    "client_id": 1,
                    "feature_flags": {"enable_multi_currency": True, "enable_approval_workflow": True},
                    "branding": {"primary_color": "#1976d2", "company_name": "Acme Corporation"},
                    "ui_personalisation": {"default_currency": "USD", "timezone": "America/New_York"}
                },
                {
                    "id": 2,
                    "client_id": 2,
                    "feature_flags": {"enable_multi_currency": False, "enable_approval_workflow": True},
                    "branding": {"primary_color": "#4caf50", "company_name": "Beta Industries"},
                    "ui_personalisation": {"default_currency": "EUR", "timezone": "Europe/London"}
                }
            ]
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, settings, expire=900)
        
        logger.info(f"Retrieved client settings for client_id: {client_id or 'all'}")
        return settings
        
    except Exception as e:
        logger.error(f"Error getting client settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client settings"
        )


@router.put("", summary="Update client settings")
async def update_client_settings(
    settings_data: Dict[str, Any],
    client_id: int = 1,
    db: AsyncSession = Depends(get_async_db)
):
    """Updates client settings for the specified client"""
    try:
        # Simulate updating settings
        updated_settings = {
            "id": 1,
            "client_id": client_id,
            "feature_flags": settings_data.get("feature_flags", {}),
            "branding": settings_data.get("branding", {}),
            "ui_personalisation": settings_data.get("ui_personalisation", {}),
            "business_rules": settings_data.get("business_rules", {}),
            "integrations": settings_data.get("integrations", {}),
            "updated_at": "2023-12-15T10:30:00Z"
        }
        
        # Clear cache
        cache_key = f"client_settings:{client_id}"
        await redis_cache.delete(cache_key)
        
        logger.info(f"Updated client settings for client_id: {client_id}")
        return updated_settings
        
    except Exception as e:
        logger.error(f"Error updating client settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client settings"
        )


@router.get("/features", summary="Get available features")
async def get_available_features(db: AsyncSession = Depends(get_async_db)):
    """Returns all available feature flags and their descriptions"""
    try:
        # Check cache first
        cache_key = "available_features"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock available features
        features = {
            "feature_flags": [
                {
                    "key": "enable_multi_currency",
                    "name": "Multi-Currency Support",
                    "description": "Enable support for multiple currencies and exchange rates",
                    "category": "Financial",
                    "default_value": True
                },
                {
                    "key": "enable_approval_workflow", 
                    "name": "Approval Workflow",
                    "description": "Enable multi-level approval workflow for invoices",
                    "category": "Process",
                    "default_value": True
                },
                {
                    "key": "enable_bulk_import",
                    "name": "Bulk Import",
                    "description": "Enable bulk import of invoices and data",
                    "category": "Data Management",
                    "default_value": True
                },
                {
                    "key": "enable_advanced_reporting",
                    "name": "Advanced Reporting",
                    "description": "Enable advanced analytics and custom reports",
                    "category": "Analytics",
                    "default_value": False
                },
                {
                    "key": "enable_supplier_portal",
                    "name": "Supplier Portal",
                    "description": "Enable supplier self-service portal",
                    "category": "Collaboration",
                    "default_value": False
                },
                {
                    "key": "enable_mobile_app",
                    "name": "Mobile Application",
                    "description": "Enable mobile app access",
                    "category": "Access",
                    "default_value": True
                }
            ],
            "ui_options": [
                {
                    "key": "default_currency",
                    "name": "Default Currency",
                    "type": "select",
                    "options": ["USD", "EUR", "GBP", "JPY", "CAD"],
                    "default_value": "USD"
                },
                {
                    "key": "date_format",
                    "name": "Date Format",
                    "type": "select",
                    "options": ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
                    "default_value": "MM/DD/YYYY"
                },
                {
                    "key": "items_per_page",
                    "name": "Items Per Page",
                    "type": "select",
                    "options": [10, 25, 50, 100],
                    "default_value": 25
                }
            ]
        }
        
        # Cache for 1 hour (features don't change often)
        await redis_cache.set(cache_key, features, expire=3600)
        
        logger.info("Retrieved available features")
        return features
        
    except Exception as e:
        logger.error(f"Error getting available features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available features"
        )