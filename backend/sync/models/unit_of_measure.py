from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base, AuditMixin

class UnitOfMeasure(Base, AuditMixin):
    __tablename__ = 'unit_of_measure'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
