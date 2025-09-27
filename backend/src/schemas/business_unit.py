from pydantic import BaseModel
from typing import Optional

class BusinessUnitBase(BaseModel):
    name: str
    code: str
    client_id: int

class BusinessUnitCreate(BusinessUnitBase):
    pass

class BusinessUnitRead(BusinessUnitBase):
    id: int
    class Config:
        orm_mode = True
