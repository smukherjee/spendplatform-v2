from pydantic import BaseModel
from typing import Optional, List

class RoleBase(BaseModel):
    name: str
    permissions: Optional[dict] = None

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    users: List[int] = []
    class Config:
        orm_mode = True
