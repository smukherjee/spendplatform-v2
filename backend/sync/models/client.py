from sqlalchemy import Column, Integer, String
from .base import Base, AuditMixin

class Client(Base, AuditMixin):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
