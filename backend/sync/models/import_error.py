from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from .base import Base, AuditMixin

class ImportError(Base, AuditMixin):
    __tablename__ = 'import_error'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=True)
    row_number = Column(Integer, nullable=True)
    error_type = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    error_details = Column(JSON, nullable=True)
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
