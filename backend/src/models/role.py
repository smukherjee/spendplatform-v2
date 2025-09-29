from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base, AuditMixin

class Role(Base, AuditMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    permissions = Column(JSON, nullable=True)
    hierarchy_level = Column(Integer, nullable=False, default=2)
    parent_role_id = Column(Integer, ForeignKey('role.id', ondelete="SET NULL"), nullable=True)
    client_id = Column(Integer, ForeignKey('client.id', ondelete="CASCADE"), nullable=True)
    users = relationship('User', secondary='user_role', back_populates='roles')
    screen_permissions = relationship('RoleScreenPermission', back_populates='role', foreign_keys='RoleScreenPermission.role_id')
    parent_role = relationship('Role', remote_side=[id], backref=backref('child_roles', lazy='selectin'))
    client = relationship('Client', backref=backref('roles', lazy='selectin'))


# Default hierarchy constants
ROLE_PRIORITY_ORDER = ["superadmin", "client_admin", "user"]


def get_default_hierarchy_level(role_name: str) -> int:
    """Return default hierarchy level for known roles."""
    if role_name:
        lowered = role_name.lower()
        if lowered == "superadmin":
            return 0
        if lowered == "client_admin":
            return 1
    return 2
