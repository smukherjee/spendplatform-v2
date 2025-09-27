from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base, AuditMixin

class SubCategoryL1(Base, AuditMixin):
    __tablename__ = 'subcategory_l1'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, nullable=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)

class SubCategoryL2(Base, AuditMixin):
    __tablename__ = 'subcategory_l2'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('subcategory_l1.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)

class SubCategoryL3(Base, AuditMixin):
    __tablename__ = 'subcategory_l3'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('subcategory_l2.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)

class SubCategoryL4(Base, AuditMixin):
    __tablename__ = 'subcategory_l4'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('subcategory_l3.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
