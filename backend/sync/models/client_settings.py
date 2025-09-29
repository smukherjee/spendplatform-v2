from sqlalchemy import Column, Integer, JSON, ForeignKey
from .base import Base, AuditMixin

class ClientSettings(Base, AuditMixin):
    __tablename__ = 'client_settings'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    feature_flags = Column(JSON, nullable=True)
    branding = Column(JSON, nullable=True)
    ui_personalisation = Column(JSON, nullable=True)
