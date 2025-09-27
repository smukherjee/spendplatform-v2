from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: EmailStr
    client_id: int
    personalisation: Optional[dict] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    roles: List[str] = []

    model_config = {"from_attributes": True}
