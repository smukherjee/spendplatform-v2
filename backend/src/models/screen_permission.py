from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UniqueConstraint, Index
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
    icon = Column(String, nullable=True)  # e.g., "dashboard", "invoice", "users"
    order_priority = Column(Integer, default=0)  # For menu ordering
    parent_screen_id = Column(Integer, ForeignKey('screen.id'), nullable=True)  # For hierarchical menus
    is_active = Column(Boolean, default=True)
    requires_super_admin = Column(Boolean, default=False)  # Superadmin only screens
    
    # Relationships
    role_permissions = relationship('RoleScreenPermission', back_populates='screen')
    parent_screen = relationship('Screen', remote_side=[id], back_populates='child_screens')
    child_screens = relationship('Screen', back_populates='parent_screen')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_screen_route', 'route'),
        Index('idx_screen_category', 'category'),
        Index('idx_screen_active', 'is_active'),
    )

class RoleScreenPermission(Base, AuditMixin):
    """Role-based permissions for screens with granular CRUD permissions"""
    __tablename__ = 'role_screen_permission'
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    screen_id = Column(Integer, ForeignKey('screen.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=True)  # Null = applies to all clients
    
    # Granular permissions
    can_view = Column(Boolean, default=False)
    can_create = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_import = Column(Boolean, default=False)
    
    # Advanced permissions
    allow_full_access = Column(Boolean, default=False)  # Override all individual permissions
    deny_access = Column(Boolean, default=False)  # Explicit deny (takes precedence)
    
    # Relationships
    role = relationship('Role', foreign_keys=[role_id], back_populates='screen_permissions')
    screen = relationship('Screen', back_populates='role_permissions')
    client = relationship('Client')
    
    # Constraints and indexes for performance
    __table_args__ = (
        UniqueConstraint('role_id', 'screen_id', 'client_id', name='uq_role_screen_client'),
        Index('idx_role_screen_perm_role', 'role_id'),
        Index('idx_role_screen_perm_screen', 'screen_id'),
        Index('idx_role_screen_perm_client', 'client_id'),
        Index('idx_role_screen_perm_view', 'can_view'),
    )

class UserScreenPermission(Base, AuditMixin):
    """User-specific permission overrides (optional - for granular control)"""
    __tablename__ = 'user_screen_permission'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    screen_id = Column(Integer, ForeignKey('screen.id'), nullable=False)
    
    # Override permissions
    can_view = Column(Boolean, nullable=True)  # Null = inherit from role
    can_create = Column(Boolean, nullable=True)
    can_edit = Column(Boolean, nullable=True)
    can_delete = Column(Boolean, nullable=True)
    can_export = Column(Boolean, nullable=True)
    can_import = Column(Boolean, nullable=True)
    
    # Override flags
    grant_access = Column(Boolean, default=False)  # Force grant access
    deny_access = Column(Boolean, default=False)  # Force deny access
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id])
    screen = relationship('Screen', foreign_keys=[screen_id])
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'screen_id', name='uq_user_screen'),
        Index('idx_user_screen_perm_user', 'user_id'),
        Index('idx_user_screen_perm_screen', 'screen_id'),
    )

