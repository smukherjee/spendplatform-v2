from pydantic import BaseModel
from typing import Optional
from datetime import date

class InvoiceBase(BaseModel):
    invoice_number: str
    date: date
    supplier_id: int
    business_unit_id: int
    client_id: int

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceRead(InvoiceBase):
    id: int
    class Config:
        orm_mode = True
