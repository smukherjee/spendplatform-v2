"""
User Management Service for SpendPlatform v2
US3: User Management (Superadmin)
US4: User Management (Client Admin) 
US5: Role Assignment & Hierarchy
US6: Multitenancy & Data Isolation
US7: Audit & Logging
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.user import User
from models.role import Role
from models.client import Client
from models.audit_log import AuditLog
from services.auth_service import AuthService
from utils import get_password_hash


class UserManagementService:
    """Service for managing users with multi-tenant support and role hierarchy"""
    
    @staticmethod
    def get_users_for_admin(
        db: Session,
        admin_user: dict,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        client_id_filter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get users based on admin role and permissions
        US3: Superadmin sees all users
        US4: Client Admin sees only their tenant users
        US6: Data isolation by client_id
        """
        admin_role = admin_user.get("role")
        admin_client_id = admin_user.get("client_id")
        
        # Build base query with explicit join condition to avoid ambiguity
        query = db.query(User).join(Client, User.client_id == Client.id)
        
        # Apply role-based filtering
        if admin_role == "superadmin":
            # US3: Superadmin can see all users
            if client_id_filter:
                query = query.filter(User.client_id == client_id_filter)
        elif admin_role == "client_admin":
            # US4: Client Admin only sees users from their tenant
            query = query.filter(User.client_id == admin_client_id)
        else:
            # Regular users cannot manage other users
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view users"
            )
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    Client.name.ilike(search_term)
                )
            )
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and get results
        users = query.offset(skip).limit(limit).all()
        
        # Format results
        user_list = []
        for user in users:
            user_roles = [role.name for role in user.roles] if user.roles else []
            client = db.query(Client).filter(Client.id == getattr(user, 'client_id', None)).first()
            
            user_list.append({
                "id": getattr(user, 'id', None),
                "username": user.username,
                "email": user.email,
                "client_id": getattr(user, 'client_id', None),
                "client_name": client.name if client else "Unknown",
                "roles": user_roles,
                "is_active": True,  # Add active status if you have it in your model
                "created_at": getattr(user, 'created_at', None),
                "updated_at": getattr(user, 'updated_at', None)
            })
        
        return {
            "users": user_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    def create_user(
        db: Session,
        admin_user: dict,
        username: str,
        email: str,
        password: str,
        client_id: int,
        role_names: List[str]
    ) -> Dict[str, Any]:
        """
        Create new user with role validation and audit logging
        US3: Superadmin can create any user
        US4: Client Admin can create users in their tenant only
        US5: Role assignment validation
        US7: Audit logging
        """
        admin_role = admin_user.get("role")
        admin_client_id = admin_user.get("client_id")
        admin_user_id = admin_user.get("user_id")
        
        # Validate permissions
        UserManagementService._validate_user_creation_permissions(
            admin_role=admin_role,
            admin_client_id=admin_client_id,
            target_client_id=client_id,
            target_roles=role_names
        )
        
        # Validate password policy
        AuthService.validate_password_policy(password)
        
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Validate client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client not found"
            )
        
        # Validate roles exist and are assignable
        roles = UserManagementService._validate_and_get_roles(
            db=db,
            role_names=role_names,
            admin_role=admin_role
        )
        
        try:
            # Create user
            new_user = User(
                username=username,
                email=email,
                client_id=client_id,
                password_hash=get_password_hash(password)
            )
            
            db.add(new_user)
            db.flush()  # Get the user ID
            
            # Assign roles
            new_user.roles = roles
            
            db.commit()
            
            # Log user creation
            UserManagementService._log_user_management_event(
                db=db,
                admin_user_id=admin_user_id,
                action="create_user",
                target_user_id=getattr(new_user, 'id', None),
                details=f"Created user {username} with roles {role_names} for client {client.name}",
                client_id=client_id
            )
            
            return {
                "id": getattr(new_user, 'id', None),
                "username": new_user.username,
                "email": new_user.email,
                "client_id": new_user.client_id,
                "client_name": client.name,
                "roles": role_names,
                "message": "User created successfully"
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    @staticmethod
    def update_user(
        db: Session,
        admin_user: dict,
        user_id: int,
        email: Optional[str] = None,
        role_names: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update user with permission validation
        US4: Client Admin can only update users in their tenant
        US5: Role assignment validation
        US7: Audit logging
        """
        admin_role = admin_user.get("role")
        admin_client_id = admin_user.get("client_id")
        admin_user_id = admin_user.get("user_id")
        
        # Get target user
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate permissions to update this user
        UserManagementService._validate_user_update_permissions(
            admin_role=admin_role,
            admin_client_id=admin_client_id,
            target_user_client_id=getattr(target_user, 'client_id', None),
            target_roles=role_names
        )
        
        try:
            changes = []
            
            # Update email if provided
            if email and email != target_user.email:
                # Check if email already exists
                existing_user = db.query(User).filter(
                    User.email == email,
                    User.id != user_id
                ).first()
                
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
                
                old_email = target_user.email
                target_user.email = email
                changes.append(f"Email changed from {old_email} to {email}")
            
            # Update roles if provided
            if role_names is not None:
                old_roles = [role.name for role in target_user.roles] if target_user.roles else []
                roles = UserManagementService._validate_and_get_roles(
                    db=db,
                    role_names=role_names,
                    admin_role=admin_role
                )
                target_user.roles = roles
                changes.append(f"Roles changed from {old_roles} to {role_names}")
            
            # Update active status if provided (implement if you have this field)
            if is_active is not None:
                # Implement if you have an is_active field
                changes.append(f"Active status changed to {is_active}")
            
            db.commit()
            
            # Log user update
            if changes:
                UserManagementService._log_user_management_event(
                    db=db,
                    admin_user_id=admin_user_id,
                    action="update_user",
                    target_user_id=user_id,
                    details=f"Updated user {target_user.username}: {'; '.join(changes)}",
                    client_id=getattr(target_user, 'client_id', None)
                )
            
            return {
                "id": user_id,
                "username": target_user.username,
                "email": target_user.email,
                "client_id": getattr(target_user, 'client_id', None),
                "roles": role_names if role_names is not None else [role.name for role in target_user.roles],
                "changes": changes,
                "message": "User updated successfully"
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )
    
    @staticmethod
    def delete_user(
        db: Session,
        admin_user: dict,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete user with permission validation
        US3: Superadmin can delete any user
        US4: Client Admin can delete users in their tenant only
        US7: Audit logging
        """
        admin_role = admin_user.get("role")
        admin_client_id = admin_user.get("client_id")
        admin_user_id = admin_user.get("user_id")
        
        # Get target user
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate permissions
        if admin_role != "superadmin":
            if admin_role != "client_admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to delete users"
                )
            
            # Client admin can only delete users from their tenant
            if getattr(target_user, 'client_id', None) != admin_client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot delete users from other tenants"
                )
        
        # Prevent self-deletion
        if user_id == admin_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        try:
            username = target_user.username
            client_id = getattr(target_user, 'client_id', None)
            
            # Delete user (this will cascade to user_roles)
            db.delete(target_user)
            db.commit()
            
            # Log user deletion
            UserManagementService._log_user_management_event(
                db=db,
                admin_user_id=admin_user_id,
                action="delete_user",
                target_user_id=user_id,
                details=f"Deleted user {username}",
                client_id=client_id
            )
            
            return {
                "message": f"User {username} deleted successfully"
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete user: {str(e)}"
            )
    
    @staticmethod
    def _validate_user_creation_permissions(
        admin_role: str,
        admin_client_id: int,
        target_client_id: int,
        target_roles: List[str]
    ):
        """Validate permissions for user creation"""
        if admin_role == "superadmin":
            # Superadmin can create users anywhere with any role
            return
        
        if admin_role == "client_admin":
            # Client admin can only create users in their own tenant
            if target_client_id != admin_client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot create users in other tenants"
                )
            
            # Client admin cannot assign admin roles
            admin_roles = ["superadmin", "client_admin"]
            if any(role in admin_roles for role in target_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot assign admin roles"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create users"
            )
    
    @staticmethod
    def _validate_user_update_permissions(
        admin_role: str,
        admin_client_id: int,
        target_user_client_id: int,
        target_roles: Optional[List[str]] = None
    ):
        """Validate permissions for user updates"""
        if admin_role == "superadmin":
            # Superadmin can update any user
            return
        
        if admin_role == "client_admin":
            # Client admin can only update users in their tenant
            if target_user_client_id != admin_client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot update users from other tenants"
                )
            
            # Client admin cannot assign admin roles
            if target_roles:
                admin_roles = ["superadmin", "client_admin"]
                if any(role in admin_roles for role in target_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot assign admin roles"
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update users"
            )
    
    @staticmethod
    def _validate_and_get_roles(
        db: Session,
        role_names: List[str],
        admin_role: str
    ) -> List[Role]:
        """Validate role names and return role objects"""
        if not role_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one role must be assigned"
            )
        
        # Get roles from database
        roles = db.query(Role).filter(Role.name.in_(role_names)).all()
        
        if len(roles) != len(role_names):
            found_roles = [role.name for role in roles]
            missing_roles = [name for name in role_names if name not in found_roles]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Roles not found: {missing_roles}"
            )
        
        # Validate role assignment permissions
        if admin_role != "superadmin":
            admin_roles = ["superadmin", "client_admin"]
            forbidden_roles = [role.name for role in roles if role.name in admin_roles]
            if forbidden_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot assign admin roles: {forbidden_roles}"
                )
        
        return roles
    
    @staticmethod
    def _log_user_management_event(
        db: Session,
        admin_user_id: int,
        action: str,
        target_user_id: Optional[int],
        details: str,
        client_id: Optional[int]
    ):
        """Log user management events for audit trail"""
        try:
            audit_log = AuditLog(
                user_id=admin_user_id,
                action=action,
                resource_type="user",
                resource_id=target_user_id,
                details=details,
                timestamp=datetime.utcnow(),
                client_id=client_id
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            # Don't fail the operation due to logging issues
            print(f"Failed to log user management event: {str(e)}")