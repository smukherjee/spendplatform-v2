from pydantic import BaseModel
from typing import Optional

class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: int
    class Config:
        orm_mode = True
