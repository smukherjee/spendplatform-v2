from pydantic import BaseModel
from typing import Optional

class CurrencyBase(BaseModel):
    code: str
    name: str
    client_id: int

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyRead(CurrencyBase):
    id: int
    model_config = {"from_attributes": True}
