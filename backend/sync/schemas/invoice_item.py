from pydantic import BaseModel
from typing import Optional

class InvoiceItemBase(BaseModel):
    invoice_id: int
    item_number: str
    type: Optional[str] = None
    description: Optional[str] = None
    subcategory_l1_id: Optional[int] = None
    subcategory_l2_id: Optional[int] = None
    subcategory_l3_id: Optional[int] = None
    subcategory_l4_id: Optional[int] = None
    qty: Optional[float] = None
    unit_of_measure_id: Optional[int] = None
    currency_id: Optional[int] = None
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    client_id: int

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemRead(InvoiceItemBase):
    id: int
    model_config = {"from_attributes": True}
