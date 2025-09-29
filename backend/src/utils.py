from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Iterable, List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from database_async import get_async_db
from models.user import User
from models.role import ROLE_PRIORITY_ORDER

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

def role_priority(role_name: str) -> int:
    if not isinstance(role_name, str):
        return len(ROLE_PRIORITY_ORDER)

    normalized = role_name.strip().lower()
    try:
        return ROLE_PRIORITY_ORDER.index(normalized)
    except ValueError:
        return len(ROLE_PRIORITY_ORDER)


def normalize_role_names(role_names: Iterable[str]) -> List[str]:
    seen = set()
    cleaned: List[str] = []

    for name in role_names or []:
        if not isinstance(name, str):
            continue
        trimmed = name.strip()
        if not trimmed:
            continue
        lowered = trimmed.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        cleaned.append(lowered)

    cleaned.sort(key=role_priority)
    return cleaned


def _resolve_highest_role(roles: list[str], role_levels: Optional[Dict[str, int]] = None) -> Optional[str]:
    normalized_roles = normalize_role_names(roles)

    if role_levels:
        normalized_levels = {
            (name or "").strip().lower(): level
            for name, level in role_levels.items()
            if isinstance(name, str) and isinstance(level, int)
        }
        if normalized_levels:
            best_role = min(normalized_levels.items(), key=lambda item: item[1])[0]
            if not normalized_roles or best_role in normalized_roles:
                return best_role

    if not normalized_roles:
        return None

    return min(normalized_roles, key=role_priority)


def get_current_role(token: str = Depends(oauth2_scheme)) -> str:
    payload = decode_access_token(token)
    roles = payload.get("roles", [])

    resolved_role = _resolve_highest_role(roles, payload.get("role_levels"))
    if resolved_role:
        return resolved_role

    single_role = payload.get("role")
    if single_role:
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
    if not allowed:
        return

    role_priority_value = role_priority(role)
    allowed_priorities = [role_priority(allowed_role) for allowed_role in allowed]

    if role_priority_value > min(allowed_priorities):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")