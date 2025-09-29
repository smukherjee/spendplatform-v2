from pydantic import BaseModel
from typing import Optional

class SupplierBase(BaseModel):
    name: str
    contact_info: Optional[str] = None
    region_id: int
    client_id: int

class SupplierCreate(BaseModel):
    name: str
    contact_info: Optional[str] = None
    region_id: int
    client_id: Optional[int] = None  # Auto-assigned by backend

class SupplierRead(SupplierBase):
    id: int
    model_config = {"from_attributes": True}
