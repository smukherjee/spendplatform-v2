from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Literal, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from database_async import get_async_db
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def get_current_role(token: str = Depends(oauth2_scheme)) -> Literal["superadmin", "client_admin", "user"]:
    payload = decode_access_token(token)
    roles = payload.get("roles", [])
    
    # Return the highest priority role
    if "superadmin" in roles:
        return "superadmin"
    elif "client_admin" in roles:
        return "client_admin"
    elif "user" in roles:
        return "user"
    
    # Fallback to single role field for backward compatibility
    single_role = payload.get("role")
    if single_role and single_role in ["superadmin", "client_admin", "user"]:
        return single_role
        
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role")

async def get_current_user_async(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Get current user from JWT token with database validation"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"AUTH DEBUG - Token received: {token[:50]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"AUTH DEBUG - Token payload: {payload}")
        
        user_id = payload.get("user_id")
        if user_id is None:
            logger.error("AUTH DEBUG - No user_id in token payload")
            raise HTTPException(status_code=401, detail="Invalid token")

        logger.info(f"AUTH DEBUG - Looking for user_id: {user_id}")
        
        # Query real user from DB with roles loaded
        from sqlalchemy.orm import selectinload
        result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            logger.error(f"AUTH DEBUG - User {user_id} not found in database")
            raise HTTPException(status_code=401, detail="User not found")

        logger.info(f"AUTH DEBUG - User found: {user.username}")
        return user

    except JWTError as e:
        logger.error(f"AUTH DEBUG - JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return decode_access_token(token)

def get_client_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_access_token(token)
    client_id = payload.get("client_id")
    if client_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing client_id")
    return client_id

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing user_id")
    return user_id

def enforce_role(role: str, allowed: list):
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")