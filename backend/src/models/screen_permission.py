from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base, AuditMixin

class Screen(Base, AuditMixin):
    """Defines available screens/routes in the application"""
    __tablename__ = 'screen'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)  # e.g., "Dashboard", "Invoices", "Users"
    route = Column(String, nullable=False, unique=True)  # e.g., "/dashboard", "/invoices", "/users"
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., "Financial", "Admin", "Reporting"
    is_active = Column(Boolean, default=True)
    
    # Relationships
    role_permissions = relationship('RoleScreenPermission', back_populates='screen')

class RoleScreenPermission(Base, AuditMixin):
    """Role-based permissions for screens by client"""
    __tablename__ = 'role_screen_permission'
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    screen_id = Column(Integer, ForeignKey('screen.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    allow_access = Column(Boolean, default=False)  # True = allow, False = deny
    
    # Relationships
    role = relationship('Role', foreign_keys=[role_id])
    screen = relationship('Screen', back_populates='role_permissions')
    client = relationship('Client')

