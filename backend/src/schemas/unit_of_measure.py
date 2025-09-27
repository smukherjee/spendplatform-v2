from pydantic import BaseModel
from typing import Optional

class UnitOfMeasureBase(BaseModel):
    name: str
    client_id: int

class UnitOfMeasureCreate(UnitOfMeasureBase):
    pass

class UnitOfMeasureRead(UnitOfMeasureBase):
    id: int
    class Config:
        orm_mode = True
