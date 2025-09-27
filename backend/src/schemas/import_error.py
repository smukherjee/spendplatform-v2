from pydantic import BaseModel
from typing import Optional

class ImportErrorBase(BaseModel):
    invoice_id: Optional[int] = None
    row_number: Optional[int] = None
    error_type: str
    error_message: str
    error_details: Optional[dict] = None
    resolved: bool = False
    resolved_by: Optional[int] = None
    resolved_at: Optional[str] = None
    client_id: int

class ImportErrorCreate(ImportErrorBase):
    pass

class ImportErrorRead(ImportErrorBase):
    id: int
    class Config:
        orm_mode = True
