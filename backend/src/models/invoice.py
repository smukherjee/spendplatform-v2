from sqlalchemy import Column, Integer, String, Date, ForeignKey
from .base import Base, AuditMixin

class Invoice(Base, AuditMixin):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    business_unit_id = Column(Integer, ForeignKey('business_unit.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
