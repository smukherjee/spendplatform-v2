"""
Async Currency router for SpendPlatform v2
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from datetime import datetime

from database_async import get_async_db
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/currencies", tags=["currencies-async"])


@router.get("/", summary="Get all currencies")
async def get_currencies(
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns list of currencies with exchange rates"""
    try:
        # Check cache first
        cache_key = f"currencies:{active_only}:{search or 'all'}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock currency data
        currencies = [
            {
                "id": 1,
                "code": "USD",
                "name": "US Dollar",
                "symbol": "$",
                "exchange_rate": 1.0,  # Base currency
                "is_active": True,
                "is_base": True,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 2,
                "code": "EUR",
                "name": "Euro",
                "symbol": "€",
                "exchange_rate": 0.85,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 3,
                "code": "GBP",
                "name": "British Pound",
                "symbol": "£",
                "exchange_rate": 0.73,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 4,
                "code": "JPY",
                "name": "Japanese Yen",
                "symbol": "¥",
                "exchange_rate": 110.23,
                "is_active": True,
                "is_base": False,
                "decimal_places": 0,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 5,
                "code": "CAD",
                "name": "Canadian Dollar",
                "symbol": "C$",
                "exchange_rate": 1.25,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 6,
                "code": "AUD",
                "name": "Australian Dollar",
                "symbol": "A$",
                "exchange_rate": 1.38,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 7,
                "code": "CHF",
                "name": "Swiss Franc",
                "symbol": "Fr",
                "exchange_rate": 0.92,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 8,
                "code": "CNY",
                "name": "Chinese Yuan",
                "symbol": "¥",
                "exchange_rate": 6.45,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 9,
                "code": "INR",
                "name": "Indian Rupee",
                "symbol": "₹",
                "exchange_rate": 74.85,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": 10,
                "code": "BRL",
                "name": "Brazilian Real",
                "symbol": "R$",
                "exchange_rate": 5.12,
                "is_active": False,  # Inactive currency for testing
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        # Apply filters
        if active_only:
            currencies = [c for c in currencies if c["is_active"]]
        
        if search:
            search_lower = search.lower()
            currencies = [
                c for c in currencies 
                if search_lower in c["code"].lower() or search_lower in c["name"].lower()
            ]
        
        # Cache for 30 minutes (currency data doesn't change often)
        await redis_cache.set(cache_key, currencies, expire=1800)
        
        logger.info(f"Retrieved {len(currencies)} currencies")
        return currencies
        
    except Exception as e:
        logger.error(f"Error getting currencies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve currencies"
        )


@router.get("/{currency_id}", summary="Get currency details")
async def get_currency_details(
    currency_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns detailed information about a specific currency"""
    try:
        # Check cache first
        cache_key = f"currency_details:{currency_id}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock currency details - simulate database lookup
        currency_map = {
            1: {
                "id": 1,
                "code": "USD",
                "name": "US Dollar",
                "symbol": "$",
                "exchange_rate": 1.0,
                "is_active": True,
                "is_base": True,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat(),
                "country": "United States",
                "country_code": "US",
                "historical_rates": [
                    {"date": "2023-12-01", "rate": 1.0},
                    {"date": "2023-11-01", "rate": 1.0},
                    {"date": "2023-10-01", "rate": 1.0}
                ],
                "usage_stats": {
                    "total_transactions": 15432,
                    "total_amount": 2847293.45,
                    "percentage_of_total": 68.5
                }
            },
            2: {
                "id": 2,
                "code": "EUR",
                "name": "Euro",
                "symbol": "€",
                "exchange_rate": 0.85,
                "is_active": True,
                "is_base": False,
                "decimal_places": 2,
                "last_updated": datetime.now().isoformat(),
                "country": "European Union",
                "country_code": "EU",
                "historical_rates": [
                    {"date": "2023-12-01", "rate": 0.85},
                    {"date": "2023-11-01", "rate": 0.86},
                    {"date": "2023-10-01", "rate": 0.84}
                ],
                "usage_stats": {
                    "total_transactions": 3421,
                    "total_amount": 687453.23,
                    "percentage_of_total": 18.2
                }
            }
        }
        
        if currency_id not in currency_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Currency not found"
            )
        
        currency = currency_map[currency_id]
        
        # Cache for 15 minutes
        await redis_cache.set(cache_key, currency, expire=900)
        
        logger.info(f"Retrieved details for currency {currency_id}")
        return currency
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting currency details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve currency details"
        )


@router.get("/exchange-rates/latest", summary="Get latest exchange rates")
async def get_latest_exchange_rates(
    base_currency: str = Query("USD"),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns latest exchange rates for all currencies"""
    try:
        # Check cache first
        cache_key = f"exchange_rates:{base_currency}"
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Mock exchange rates data
        rates = {
            "base_currency": base_currency,
            "last_updated": datetime.now().isoformat(),
            "rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "GBP": 0.73,
                "JPY": 110.23,
                "CAD": 1.25,
                "AUD": 1.38,
                "CHF": 0.92,
                "CNY": 6.45,
                "INR": 74.85
            },
            "source": "Central Bank API",
            "next_update": (datetime.now()).replace(hour=16, minute=0, second=0).isoformat()
        }
        
        # Adjust rates if base currency is not USD
        if base_currency != "USD" and base_currency in rates["rates"]:
            base_rate = rates["rates"][base_currency]
            adjusted_rates = {}
            for currency, rate in rates["rates"].items():
                adjusted_rates[currency] = round(rate / base_rate, 4)
            rates["rates"] = adjusted_rates
        
        # Cache for 1 hour
        await redis_cache.set(cache_key, rates, expire=3600)
        
        logger.info(f"Retrieved exchange rates for base currency {base_currency}")
        return rates
        
    except Exception as e:
        logger.error(f"Error getting exchange rates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exchange rates"
        )


@router.post("/convert", summary="Convert between currencies")
async def convert_currency(
    from_currency: str = Query(..., description="Source currency code"),
    to_currency: str = Query(..., description="Target currency code"),
    amount: float = Query(..., gt=0, description="Amount to convert"),
    db: AsyncSession = Depends(get_async_db)
):
    """Converts amount from one currency to another"""
    try:
        # Check cache for exchange rates
        cache_key = f"conversion:{from_currency}:{to_currency}"
        cached_rate = await redis_cache.get(cache_key)
        
        if not cached_rate:
            # Mock exchange rates (in production, this would come from a real API)
            exchange_rates = {
                "USD": 1.0,
                "EUR": 0.85,
                "GBP": 0.73,
                "JPY": 110.23,
                "CAD": 1.25,
                "AUD": 1.38,
                "CHF": 0.92,
                "CNY": 6.45,
                "INR": 74.85
            }
            
            if from_currency not in exchange_rates or to_currency not in exchange_rates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid currency code"
                )
            
            # Calculate conversion rate
            from_rate = exchange_rates[from_currency]
            to_rate = exchange_rates[to_currency]
            conversion_rate = to_rate / from_rate
            
            # Cache the conversion rate for 1 hour
            await redis_cache.set(cache_key, conversion_rate, expire=3600)
        else:
            conversion_rate = cached_rate
        
        # Perform conversion
        converted_amount = round(amount * conversion_rate, 2)
        
        result = {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "original_amount": amount,
            "converted_amount": converted_amount,
            "exchange_rate": conversion_rate,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Converted {amount} {from_currency} to {converted_amount} {to_currency}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to convert currency"
        )