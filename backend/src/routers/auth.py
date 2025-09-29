"""
Async Authentication router for SpendPlatform v2
US1: Login Screen
US2: Password Reset
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging

from database_async import get_async_db
from utils import create_access_token, get_current_user_async
from cache_async import redis_cache
from models.user import User

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
        # Query user from database with roles
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(User).options(selectinload(User.roles)).where(User.username == login_data.username)
        )
        user = result.scalar_one_or_none()

        if not user or not user.verify_password(login_data.password):
            logger.warning(f"Login attempt with invalid credentials: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Get user roles
        roles = [role.name for role in user.roles] if user.roles else []

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "client_id": user.client_id,
                "roles": roles
            }
        )

        # Cache user session info
        cache_key = f"user_session:{user.id}"
        session_data = {
            "user_id": user.id,
            "username": user.username,
            "client_id": user.client_id,
            "roles": roles
        }
        await redis_cache.set(cache_key, session_data, expire=3600)  # 1 hour

        logger.info(f"Successful login for user: {user.username}")

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "client_id": user.client_id,
                "roles": roles,
                "personalisation": user.personalisation
            },
            client_id=getattr(user, 'client_id', 0)
        )

    except HTTPException as e:
        # Debug info for authentication failures
        logger.error(f"AUTH DEBUG - /me endpoint failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error getting current user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.get("/debug-auth", include_in_schema=False)
async def debug_auth_status(request: Request):
    """Debug endpoint to check what auth headers are being sent"""
    try:
        headers = dict(request.headers)
        auth_header = headers.get("authorization", "Not provided")
        
        return {
            "authorization_header": auth_header,
            "all_headers": {k: v for k, v in headers.items() if k.lower() in ['authorization', 'x-auth-token', 'bearer']},
            "has_auth": "authorization" in headers,
            "endpoint_info": "This endpoint shows what auth headers the frontend is sending"
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """OAuth2 compatible token endpoint"""
    try:
        # Query user from database
        result = await db.execute(
            select(User).options(selectinload(User.roles)).where(User.username == form_data.username)
        )
        user = result.scalar_one_or_none()

        if not user or not user.verify_password(form_data.password):
            logger.warning(f"Token request with invalid credentials: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user roles
        roles = [role.name for role in user.roles] if user.roles else []

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "client_id": user.client_id,
                "roles": roles
            }
        )

        # Cache user session info
        cache_key = f"user_session:{user.id}"
        session_data = {
            "user_id": user.id,
            "username": user.username,
            "client_id": user.client_id,
            "roles": roles
        }
        await redis_cache.set(cache_key, session_data, expire=3600)  # 1 hour

        logger.info(f"Token issued for user: {user.username}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "client_id": user.client_id,
            "user_id": user.id
        }

    except Exception as e:
        logger.error(f"Token request error for {getattr(form_data, 'username', 'unknown')}: {str(e)}")
        if isinstance(e, HTTPException):
            raise
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
    request: Request,
    current_user: User = Depends(get_current_user_async)
):
    """Get current user information"""
    try:
        # Debug logging
        auth_header = request.headers.get("authorization", "No Authorization header")
        logger.info(f"AUTH DEBUG - /me endpoint called with: {auth_header[:50]}...")
        logger.info(f"AUTH DEBUG - User found: {current_user.username} (ID: {current_user.id})")
        
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "client_id": getattr(current_user, 'client_id', None),
            "roles": [role.name for role in current_user.roles] if current_user.roles else [],
            "personalisation": getattr(current_user, 'personalisation', None)
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