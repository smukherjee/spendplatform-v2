from pydantic import BaseModel
from typing import Optional
from typing import Optional

class BusinessUnitBase(BaseModel):
    name: str
    code: str
    client_id: int

class BusinessUnitCreate(BaseModel):
    name: str
    code: str
    client_id: Optional[int] = None  # Auto-assigned by backend

class BusinessUnitRead(BusinessUnitBase):
    id: int
    model_config = {"from_attributes": True}
