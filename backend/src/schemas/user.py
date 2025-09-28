from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: EmailStr
    client_id: int
    personalisation: Optional[dict] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    client_id: Optional[int] = None
    personalisation: Optional[dict] = None
    password: Optional[str] = None

class UserRead(UserBase):
    id: int
    roles: List[str] = []

    model_config = {"from_attributes": True}

class PasswordReset(BaseModel):
    password: str
