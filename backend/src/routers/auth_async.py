"""
Async Authentication router for SpendPlatform v2
US1: Login Screen
US2: Password Reset
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging

from database_async import get_async_db
from utils import create_access_token
from cache_async import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication-async"])


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str
    client_id: Optional[int] = None


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str
    user: Dict[str, Any]
    client_id: int


class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr
    client_id: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate user and return access token"""
    try:
        # Simple authentication for testing - in production, would query database
        if login_data.username == "superadmin" and login_data.password == "superadmin123":
            # Create access token
            access_token = create_access_token(
                data={
                    "sub": "superadmin",
                    "user_id": 1,
                    "client_id": 1,
                    "roles": ["superadmin"]
                }
            )
            
            # Cache user session info
            cache_key = "user_session:1"
            session_data = {
                "user_id": 1,
                "username": "superadmin",
                "client_id": 1,
                "roles": ["superadmin"]
            }
            await redis_cache.set(cache_key, session_data, expire=3600)  # 1 hour
            
            logger.info("Successful login for superadmin")
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user={
                    "id": 1,
                    "username": "superadmin",
                    "email": "superadmin@test.com",
                    "client_id": 1,
                    "roles": ["superadmin"],
                    "personalisation": None
                },
                client_id=1
            )
        else:
            logger.warning(f"Login attempt with invalid credentials: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """OAuth2 compatible token endpoint"""
    try:
        # Simple authentication for testing
        if form_data.username == "superadmin" and form_data.password == "superadmin123":
            # Create access token
            access_token = create_access_token(
                data={
                    "sub": "superadmin",
                    "user_id": 1,
                    "client_id": 1,
                    "roles": ["superadmin"]
                }
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "client_id": 1
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout user and invalidate session"""
    try:
        # For now, just return success
        # In production, would need proper JWT token invalidation
        logger.info("User logout requested")
        
        return MessageResponse(
            message="Successfully logged out",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return MessageResponse(
            message="Logout completed",
            success=True
        )


@router.get("/me")
async def get_current_user_info(
    db: AsyncSession = Depends(get_async_db)
):
    """Get current user information"""
    try:
        # For now, return mock user data
        # In production, would extract user info from JWT token
        return {
            "id": 1,
            "username": "superadmin",
            "email": "superadmin@test.com",
            "client_id": 1,
            "roles": ["superadmin"],
            "personalisation": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


# Async utility function for getting current user
async def get_current_user_async():
    """Placeholder for async current user dependency"""
    # This would need to be implemented with proper JWT validation
    # For now, return a mock user for testing
    return {
        "user_id": 1,
        "username": "superadmin",
        "client_id": 1,
        "roles": ["superadmin"]
    }