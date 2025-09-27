from pydantic import BaseModel
from typing import Optional

class RegionBase(BaseModel):
    name: str
    code: str
    client_id: int

class RegionCreate(RegionBase):
    pass

class RegionRead(RegionBase):
    id: int
    class Config:
        orm_mode = True
