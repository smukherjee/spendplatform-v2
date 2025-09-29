from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class RoleBase(BaseModel):
    name: str
    permissions: Optional[dict] = None

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
