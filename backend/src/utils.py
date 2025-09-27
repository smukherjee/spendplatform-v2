from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Literal, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

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
    role = payload.get("role")
    if role in ["superadmin", "client_admin", "user"]:
        return role
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return decode_access_token(token)

def not_implemented():
    raise HTTPException(status_code=501, detail="Not Implemented")

def get_client_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_access_token(token)
    client_id = payload.get("client_id")
    if client_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing client_id")
    return client_id

def enforce_role(role: str, allowed: list):
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")