from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base, AuditMixin

class Region(Base, AuditMixin):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
