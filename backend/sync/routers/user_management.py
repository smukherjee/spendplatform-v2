"""
Enhanced User Management Router for SpendPlatform v2
US3: User Management (Superadmin)
US4: User Management (Client Admin)
US5: Role Assignment & Hierarchy
US6: Multitenancy & Data Isolation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

from database import get_db
from services.user_management_service import UserManagementService
from utils import get_current_user, get_current_role

router = APIRouter(prefix="/api/v1/users", tags=["user-management"])


class CreateUserRequest(BaseModel):
    """Request model for creating a user"""
    username: str
    email: EmailStr
    password: str
    client_id: int
    roles: List[str]


class UpdateUserRequest(BaseModel):
    """Request model for updating a user"""
    email: Optional[EmailStr] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Response model for user data"""
    id: int
    username: str
    email: str
    client_id: int
    client_name: str
    roles: List[str]
    is_active: bool = True


class UsersListResponse(BaseModel):
    """Response model for users list"""
    users: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int


@router.get("", response_model=UsersListResponse, summary="Get users list")
def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for username, email, or client name"),
    client_id: Optional[int] = Query(None, description="Filter by client ID (superadmin only)"),
    current_user: dict = Depends(get_current_user),
    current_role: str = Depends(get_current_role),
    db: Session = Depends(get_db)
) -> UsersListResponse:
    """
    Get paginated list of users based on admin permissions
    
    US3: Superadmin sees all users with optional client filtering
    US4: Client Admin sees only users from their tenant
    US6: Data isolation enforced by client_id
    """
    try:
        result = UserManagementService.get_users_for_admin(
            db=db,
            admin_user=current_user,
            skip=skip,
            limit=limit,
            search=search,
            client_id_filter=client_id
        )
        
        return UsersListResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.post("", response_model=Dict[str, Any], summary="Create new user")
def create_user(
    request: CreateUserRequest,
    current_user: dict = Depends(get_current_user),
    current_role: str = Depends(get_current_role),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new user with role validation
    
    US3: Superadmin can create users in any client with any role
    US4: Client Admin can create users only in their tenant with non-admin roles
    US5: Role assignment validation based on admin hierarchy
    US7: Audit logging for user creation
    """
    try:
        result = UserManagementService.create_user(
            db=db,
            admin_user=current_user,
            username=request.username,
            email=request.email,
            password=request.password,
            client_id=request.client_id,
            role_names=request.roles
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put("/{user_id}", response_model=Dict[str, Any], summary="Update user")
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    current_user: dict = Depends(get_current_user),
    current_role: str = Depends(get_current_role),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update user information and roles
    
    US4: Client Admin can only update users in their tenant
    US5: Role assignment validation
    US6: Multi-tenant data isolation
    US7: Audit logging for user updates
    """
    try:
        result = UserManagementService.update_user(
            db=db,
            admin_user=current_user,
            user_id=user_id,
            email=request.email,
            role_names=request.roles,
            is_active=request.is_active
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/{user_id}", response_model=Dict[str, str], summary="Delete user")
def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    current_role: str = Depends(get_current_role),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete user with permission validation
    
    US3: Superadmin can delete any user
    US4: Client Admin can delete users only in their tenant
    US6: Multi-tenant data isolation
    US7: Audit logging for user deletion
    """
    try:
        result = UserManagementService.delete_user(
            db=db,
            admin_user=current_user,
            user_id=user_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.get("/{user_id}", response_model=Dict[str, Any], summary="Get user details")
def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    current_role: str = Depends(get_current_role),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific user
    
    US4: Client Admin can only view users in their tenant
    US6: Multi-tenant data isolation
    """
    try:
        admin_client_id = current_user.get("client_id")
        admin_role = current_user.get("role")
        
        # Get user from database
        from models.user import User
        from models.client import Client
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        if admin_role != "superadmin":
            if admin_role != "client_admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            # Client admin can only view users from their tenant
            user_client_id = getattr(user, 'client_id', None)
            if user_client_id != admin_client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot view users from other tenants"
                )
        
        # Get client information
        client = db.query(Client).filter(Client.id == getattr(user, 'client_id', None)).first()
        user_roles = [role.name for role in user.roles] if user.roles else []
        
        return {
            "id": getattr(user, 'id', None),
            "username": user.username,
            "email": user.email,
            "client_id": getattr(user, 'client_id', None),
            "client_name": client.name if client else "Unknown",
            "roles": user_roles,
            "is_active": True,
            "created_at": getattr(user, 'created_at', None),
            "updated_at": getattr(user, 'updated_at', None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )