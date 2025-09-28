"""
Authentication service for SpendPlatform v2
Handles login, password reset, and JWT token management with multi-tenancy
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

from database import get_db
from models.user import User
from models.role import Role
from models.client import Client
from models.audit_log import AuditLog
from utils import create_access_token, decode_access_token
from deployment_config import settings


class AuthService:
    """Authentication service with multi-tenant support"""
    
    @staticmethod
    def authenticate_user(db: Session, username_or_email: str, password: str, client_id: Optional[int] = None) -> Optional[User]:
        """
        Authenticate user with multi-tenant validation
        US1: Login with email/username validation
        """
        # Query user by username or email
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            return None
            
        # Verify password
        if not user.verify_password(password):
            return None
            
        # For non-superadmin users, validate client_id if provided
        user_roles = [role.name for role in user.roles] if user.roles else []
        is_superadmin = "superadmin" in user_roles
        if not is_superadmin and client_id is not None:
            # Compare actual values, not SQLAlchemy columns
            user_client_id = getattr(user, 'client_id', None)
            if user_client_id != client_id:
                return None
            
        return user
    
    @staticmethod
    def create_user_token(user: User, db: Session) -> Dict[str, Any]:
        """
        Create JWT token with user, role, and client_id details
        US1: JWT token with user details
        """
        # Get user roles
        user_roles = [role.name for role in user.roles] if user.roles else []
        primary_role = user_roles[0] if user_roles else "user"
        
        # Get client information
        client = db.query(Client).filter(Client.id == user.client_id).first()
        client_name = client.name if client else "Unknown"
        
        token_data = {
            "sub": user.username,
            "user_id": getattr(user, 'id', None),
            "email": user.email,
            "role": primary_role,
            "roles": user_roles,
            "client_id": getattr(user, 'client_id', None),
            "client_name": client_name,
            "is_superadmin": "superadmin" in user_roles,
            "is_client_admin": "client_admin" in user_roles
        }
        
        access_token = create_access_token(token_data)
        
        # Log successful login
        AuthService.log_auth_event(
            db=db,
            user_id=getattr(user, 'id', None),
            event_type="login_success",
            details=f"User {user.username} logged in successfully",
            client_id=getattr(user, 'client_id', None)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": getattr(user, 'id', None),
                "username": user.username,
                "email": user.email,
                "roles": user_roles,
                "client_id": getattr(user, 'client_id', None),
                "client_name": client_name
            }
        }
    
    @staticmethod
    def login(db: Session, form_data: OAuth2PasswordRequestForm, client_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Complete login flow with validation and logging
        US1: Complete login process
        """
        try:
            user = AuthService.authenticate_user(
                db=db,
                username_or_email=form_data.username,
                password=form_data.password,
                client_id=client_id
            )
            
            if not user:
                # Log failed login attempt
                AuthService.log_auth_event(
                    db=db,
                    user_id=None,
                    event_type="login_failed",
                    details=f"Failed login attempt for username: {form_data.username}",
                    client_id=client_id
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username/email or password"
                )
            
            return AuthService.create_user_token(user, db)
            
        except HTTPException:
            raise
        except Exception as e:
            AuthService.log_auth_event(
                db=db,
                user_id=None,
                event_type="login_error",
                details=f"Login error for username: {form_data.username}, Error: {str(e)}",
                client_id=client_id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    @staticmethod
    def generate_reset_token(user: User) -> str:
        """
        Generate secure password reset token
        US2: Secure reset link generation
        """
        reset_data = {
            "user_id": getattr(user, 'id', None),
            "client_id": getattr(user, 'client_id', None),
            "email": user.email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        }
        return create_access_token(reset_data, expires_delta=60)  # 60 minutes
    
    @staticmethod
    def request_password_reset(db: Session, email: str, client_id: int) -> bool:
        """
        Request password reset with client_id validation
        US2: Password reset request with client validation
        """
        try:
            # Find user by email and client_id
            user = db.query(User).filter(
                User.email == email,
                User.client_id == client_id
            ).first()
            
            if not user:
                # Log reset attempt for non-existent user
                AuthService.log_auth_event(
                    db=db,
                    user_id=None,
                    event_type="reset_request_invalid",
                    details=f"Password reset requested for non-existent email: {email}",
                    client_id=client_id
                )
                # Don't reveal if user exists or not
                return True
            
            # Generate reset token
            reset_token = AuthService.generate_reset_token(user)
            
            # Send reset email (implement email service)
            AuthService.send_reset_email(user, reset_token, client_id)
            
            # Log reset request
            AuthService.log_auth_event(
                db=db,
                user_id=getattr(user, 'id', None),
                event_type="reset_request",
                details=f"Password reset requested for user: {user.username}",
                client_id=getattr(user, 'client_id', None)
            )
            
            return True
            
        except Exception as e:
            AuthService.log_auth_event(
                db=db,
                user_id=None,
                event_type="reset_request_error",
                details=f"Password reset error for email: {email}, Error: {str(e)}",
                client_id=client_id
            )
            return False
    
    @staticmethod
    def validate_reset_token(token: str) -> Dict[str, Any]:
        """
        Validate password reset token
        US2: Reset token validation with client_id check
        """
        try:
            payload = decode_access_token(token)
            
            if payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            
            return payload
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """
        Reset password with token validation
        US2: Password reset with policy enforcement
        """
        try:
            # Validate token
            payload = AuthService.validate_reset_token(token)
            user_id = payload.get("user_id")
            client_id = payload.get("client_id")
            
            # Find user
            user = db.query(User).filter(
                User.id == user_id,
                User.client_id == client_id
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            
            # Validate password policy
            AuthService.validate_password_policy(new_password)
            
            # Update password
            user.set_password(new_password)
            db.commit()
            
            # Log password reset
            AuthService.log_auth_event(
                db=db,
                user_id=getattr(user, 'id', None),
                event_type="password_reset",
                details=f"Password reset completed for user: {user.username}",
                client_id=getattr(user, 'client_id', None)
            )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            AuthService.log_auth_event(
                db=db,
                user_id=None,
                event_type="password_reset_error",
                details=f"Password reset error: {str(e)}",
                client_id=None
            )
            return False
    
    @staticmethod
    def validate_password_policy(password: str) -> bool:
        """
        Validate password against security policy
        US2: Password policy enforcement
        """
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        if not any(c.isupper() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter"
            )
        
        if not any(c.islower() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter"
            )
        
        if not any(c.isdigit() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one number"
            )
        
        return True
    
    @staticmethod
    def send_reset_email(user: User, reset_token: str, client_id: int):
        """
        Send password reset email
        US2: Reset email with secure link
        """
        # Get client information
        # This would integrate with your email service
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        # In production, implement actual email sending
        print(f"Password reset link for {user.email}: {reset_link}")
    
    @staticmethod
    def log_auth_event(db: Session, user_id: Optional[int], event_type: str, details: str, client_id: Optional[int]):
        """
        Log authentication events for audit trail
        US7: Audit logging for auth events
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                client_id=client_id,
                action=event_type,
                resource_type="authentication",
                details=details,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
            print(f"✅ AUDIT: {event_type} - {details} (user_id: {user_id}, client_id: {client_id})")
        except Exception as e:
            # Don't fail auth operations due to logging issues
            print(f"⚠️ Failed to log auth event: {str(e)}")
            db.rollback()