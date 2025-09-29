from pydantic import BaseModel, ConfigDict
from typing import Optional

class RoleBase(BaseModel):
    name: str
    permissions: Optional[dict] = None
    hierarchy_level: Optional[int] = None
    parent_role_id: Optional[int] = None
    client_id: Optional[int] = None

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
