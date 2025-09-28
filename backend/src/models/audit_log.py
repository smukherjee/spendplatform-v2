"""
Audit Log model for tracking all user activities
US7: Comprehensive audit logging
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class AuditLog(Base):
    """
    Audit log for tracking all user management activities
    US7: Audit & Logging requirements
    """
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)  # Nullable for system events
    client_id = Column(Integer, ForeignKey('client.id'), nullable=True)  # For multi-tenant filtering
    action = Column(String(100), nullable=False)  # login, logout, create_user, update_user, etc.
    resource_type = Column(String(50), nullable=True)  # user, role, client, etc.
    resource_id = Column(Integer, nullable=True)  # ID of the affected resource
    details = Column(Text, nullable=True)  # Additional details about the action
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)  # Browser/client info
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="audit_logs")
    client = relationship("Client", backref="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id}, timestamp={self.timestamp})>"