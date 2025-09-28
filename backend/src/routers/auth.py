"""
Authentication router for SpendPlatform v2
US1: Login Screen
US2: Password Reset
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from database import get_db
from services.auth_service import AuthService
from utils import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


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


class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr
    client_id: int


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str
    new_password: str


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


@router.post("/login", response_model=LoginResponse, summary="User login with JWT token generation")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    US1: Login Screen
    Authenticate user and return JWT token with user, role, and client_id details
    
    - **username**: Username or email address
    - **password**: User password
    - **client_id**: Optional client ID for tenant validation (for non-superadmin users)
    
    Returns JWT token with:
    - User information (id, username, email, roles)
    - Client information (client_id, client_name)
    - Role-based permissions (is_superadmin, is_client_admin)
    """
    try:
        result = AuthService.login(
            db=db,
            form_data=form_data,
            client_id=client_id
        )
        
        return LoginResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            user=result["user"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post("/password-reset/request", response_model=MessageResponse, summary="Request password reset")
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    US2: Password Reset
    Request password reset via email with client_id validation
    
    - **email**: User email address
    - **client_id**: Client ID for tenant validation
    
    Sends secure reset link tied to client_id with expiry
    """
    try:
        success = AuthService.request_password_reset(
            db=db,
            email=request.email,
            client_id=request.client_id
        )
        
        if success:
            return MessageResponse(
                message="If an account with this email exists, a password reset link has been sent.",
                success=True
            )
        else:
            # Don't reveal whether account exists
            return MessageResponse(
                message="If an account with this email exists, a password reset link has been sent.",
                success=True
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset service error"
        )


@router.post("/password-reset/confirm", response_model=MessageResponse, summary="Confirm password reset")
def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    US2: Password Reset
    Reset password with token validation and policy enforcement
    
    - **token**: Password reset token from email link
    - **new_password**: New password (must meet policy requirements)
    
    Validates token, enforces password policy, and updates password
    """
    try:
        success = AuthService.reset_password(
            db=db,
            token=request.token,
            new_password=request.new_password
        )
        
        if success:
            return MessageResponse(
                message="Password has been reset successfully. You can now log in with your new password.",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset service error"
        )


@router.get("/validate-token", summary="Validate JWT token")
def validate_token(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Validate current JWT token and return user information
    Used by frontend to check if user is still authenticated
    """
    return {
        "valid": True,
        "user": current_user
    }


@router.post("/logout", response_model=MessageResponse, summary="User logout")
def logout(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    """
    User logout (client-side token invalidation)
    
    Note: Since we're using stateless JWT tokens, actual logout happens on the client side
    by removing the token. This endpoint can be used for audit logging.
    """
    # In a stateless JWT system, logout is primarily client-side
    # This endpoint exists for potential audit logging or future token blacklisting
    
    return MessageResponse(
        message="Logged out successfully",
        success=True
    )


# Backward compatibility - keep the original /token endpoint
@router.post("/token", response_model=Dict[str, str], summary="OAuth2 compatible login endpoint")
def login_oauth2_compatible(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    OAuth2 compatible login endpoint for backward compatibility
    Returns only access_token and token_type
    """
    try:
        result = AuthService.login(
            db=db,
            form_data=form_data,
            client_id=None  # No client_id validation for backward compatibility
        )
        
        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )