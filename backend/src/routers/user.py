from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserUpdate, UserRead, PasswordReset
from models.user import User
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/users", tags=["User"])

@router.get("", response_model=List[UserRead], summary="List all users")
def get_users(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all users for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_users", user=role, client_id=client_id, details="List users")
    
    # Query users based on role
    if role == "superadmin":
        users = db.query(User).all()
    else:
        users = db.query(User).filter(User.client_id == client_id).all()
    
    # Convert to dict to exclude relationships that aren't in the schema
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "client_id": u.client_id,
        "personalisation": u.personalisation,
        "roles": [r.name for r in u.roles] if hasattr(u, 'roles') and u.roles else []
    } for u in users]

@router.post("", response_model=UserRead, summary="Create a new user")
def post_users(user: UserCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new user for the current client (unless superadmin)."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Log incoming request details
    logger.info(f"🔍 USER CREATE REQUEST - Role: {role}, Client ID: {client_id}")
    logger.info(f"📝 Request data: username={user.username}, email={user.email}, client_id={getattr(user, 'client_id', 'not_provided')}")
    logger.info(f"🔐 Password provided: {hasattr(user, 'password') and bool(getattr(user, 'password', None))}")
    
    try:
        enforce_role(role, ["client_admin", "superadmin"])
        logger.info(f"✅ Role enforcement passed for: {role}")
    except Exception as e:
        logger.error(f"❌ Role enforcement failed: {str(e)}")
        raise
    
    log_audit(action="post_users", user=role, client_id=client_id, details=f"Create user: {user.username}")
    
    # Determine client_id to use
    target_client_id = client_id if role != "superadmin" else user.client_id
    logger.info(f"🏢 Target client_id: {target_client_id} (role={role})")
    
    # Create new user
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            client_id=target_client_id,
            personalisation=user.personalisation if hasattr(user, 'personalisation') else None
        )
        logger.info(f"👤 User object created: {db_user.username} for client {db_user.client_id}")
    except Exception as e:
        logger.error(f"❌ Failed to create User object: {str(e)}")
        raise
    
    # Set password if provided
    if hasattr(user, 'password'):
        logger.info(f"🔐 Setting password for user: {user.username}")
        try:
            db_user.set_password(user.password)
            logger.info(f"✅ Password set successfully")
        except Exception as e:
            logger.error(f"❌ Failed to set password: {str(e)}")
            raise
    else:
        logger.warning(f"⚠️ No password provided for user: {user.username}")
    
    # Database operations
    try:
        logger.info(f"💾 Adding user to database session...")
        db.add(db_user)
        
        logger.info(f"💾 Committing user to database...")
        db.commit()
        
        logger.info(f"🔄 Refreshing user object...")
        db.refresh(db_user)
        
        logger.info(f"✅ User created successfully with ID: {db_user.id}")
    except Exception as e:
        logger.error(f"❌ Database operation failed: {str(e)}")
        db.rollback()
        raise
    
    result = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "client_id": db_user.client_id,
        "personalisation": db_user.personalisation,
        "roles": [r.name for r in db_user.roles] if hasattr(db_user, 'roles') and db_user.roles else []
    }
    
    logger.info(f"📤 Returning user data: {result}")
    return result

@router.get("/{id}", response_model=UserRead, summary="Get a user by ID")
def get_user(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a specific user by ID."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_user", user=role, client_id=client_id, details=f"Get user {id}")
    
    # Query user based on role
    if role == "superadmin":
        user = db.query(User).filter(User.id == id).first()
    else:
        user = db.query(User).filter(
            User.id == id,
            User.client_id == client_id
        ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "client_id": user.client_id,
        "personalisation": user.personalisation,
        "roles": [r.name for r in user.roles] if hasattr(user, 'roles') and user.roles else []
    }

@router.put("/{id}", response_model=UserRead, summary="Update a user")
def put_user(id: int, user: UserUpdate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a user by ID."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_user", user=role, client_id=client_id, details=f"Update user id: {id}")
    
    # Find existing user
    if role == "superadmin":
        db_user = db.query(User).filter(User.id == id).first()
    else:
        db_user = db.query(User).filter(
            User.id == id,
            User.client_id == client_id
        ).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields (only update fields that are provided and not None)
    for field, value in user.dict(exclude_unset=True).items():
        if field == "password":
            if value:  # Only update password if provided and not empty
                db_user.set_password(value)
        elif field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        elif value is not None:  # Only update if value is provided
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "client_id": db_user.client_id,
        "personalisation": db_user.personalisation,
        "roles": [r.name for r in db_user.roles] if hasattr(db_user, 'roles') and db_user.roles else []
    }

@router.delete("/{id}", response_model=None, summary="Delete a user")
def delete_user(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a user by ID."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_user", user=role, client_id=client_id, details=f"Delete user id: {id}")
    
    # Find existing user
    if role == "superadmin":
        db_user = db.query(User).filter(User.id == id).first()
    else:
        db_user = db.query(User).filter(
            User.id == id,
            User.client_id == client_id
        ).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Hard delete (no soft delete in User model)
    db.delete(db_user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.patch("/{id}/password", summary="Reset user password")
def reset_user_password(id: int, password_data: PasswordReset, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Resets a user's password (admin only)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="reset_password", user=role, client_id=client_id, details=f"Reset password for user id: {id}")
    
    # Validate password
    new_password = password_data.password
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    # Find existing user
    if role == "superadmin":
        db_user = db.query(User).filter(User.id == id).first()
    else:
        db_user = db.query(User).filter(
            User.id == id,
            User.client_id == client_id
        ).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    db_user.set_password(new_password)
    db.commit()
    
    return {"message": "Password reset successfully"}