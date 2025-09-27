from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.sql import func

Base = declarative_base()

class AuditMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('user.id', use_alter=True), nullable=True)
    updated_by = Column(Integer, ForeignKey('user.id', use_alter=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
