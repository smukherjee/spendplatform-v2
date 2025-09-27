from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base, AuditMixin

class Supplier(Base, AuditMixin):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact_info = Column(String, nullable=True)
    region_id = Column(Integer, ForeignKey('region.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
