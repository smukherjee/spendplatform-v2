from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base, AuditMixin

class Currency(Base, AuditMixin):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
