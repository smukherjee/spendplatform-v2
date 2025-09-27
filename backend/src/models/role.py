from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from .base import Base, AuditMixin

class Role(Base, AuditMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    permissions = Column(JSON, nullable=True)
    users = relationship('User', secondary='user_role', back_populates='roles')
