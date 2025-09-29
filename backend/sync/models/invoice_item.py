from sqlalchemy import Column, Integer, String, Float, ForeignKey
from .base import Base, AuditMixin

class InvoiceItem(Base, AuditMixin):
    __tablename__ = 'invoice_item'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=False)
    item_number = Column(String, nullable=False)
    type = Column(String, nullable=True)
    description = Column(String, nullable=True)
    subcategory_l1_id = Column(Integer, ForeignKey('subcategory_l1.id'), nullable=True)
    subcategory_l2_id = Column(Integer, ForeignKey('subcategory_l2.id'), nullable=True)
    subcategory_l3_id = Column(Integer, ForeignKey('subcategory_l3.id'), nullable=True)
    subcategory_l4_id = Column(Integer, ForeignKey('subcategory_l4.id'), nullable=True)
    qty = Column(Float, nullable=True)
    unit_of_measure_id = Column(Integer, ForeignKey('unit_of_measure.id'), nullable=True)
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=True)
    unit_price = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
