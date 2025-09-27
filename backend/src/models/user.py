from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base
from argon2 import PasswordHasher

ph = PasswordHasher()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    personalisation = Column(JSON, nullable=True)
    roles = relationship('Role', secondary='user_role', back_populates='users')
    screen_permissions = relationship('UserScreenPermission', back_populates='user', foreign_keys='UserScreenPermission.user_id')

    def set_password(self, password: str):
        self.password_hash = ph.hash(password)

    def verify_password(self, password: str) -> bool:
        try:
            hash_value = self.password_hash if isinstance(self.password_hash, str) else getattr(self, 'password_hash', None)
            if not isinstance(hash_value, str) or not hash_value:
                return False
            return ph.verify(hash_value, password)
        except Exception:
            return False
