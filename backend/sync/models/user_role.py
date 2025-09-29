from sqlalchemy import Table, Column, Integer, ForeignKey
from .base import Base

user_role = Table(
    'user_role', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('role.id'), primary_key=True)
)
