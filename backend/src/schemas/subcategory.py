from pydantic import BaseModel
from typing import Optional

class SubCategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    client_id: int

class SubCategoryCreate(SubCategoryBase):
    pass

class SubCategoryRead(SubCategoryBase):
    id: int
    model_config = {"from_attributes": True}

# For L1-L4, reuse SubCategoryBase/Create/Read
