# Import all models to ensure SQLAlchemy relationships are properly initialized
from .base import Base, AuditMixin
from .user import User
from .role import Role
from .client import Client
from .user_role import user_role

# Import other models to ensure they're available
try:
    from .audit import AuditLog
    from .business_unit import BusinessUnit
    from .region import Region
    from .supplier import Supplier
    from .currency import Currency
    from .unit_of_measure import UnitOfMeasure
    from .subcategory import SubCategoryL1, SubCategoryL2, SubCategoryL3, SubCategoryL4
    from .invoice import Invoice
    from .invoice_item import InvoiceItem
    from .client_settings import ClientSettings
    from .import_error import ImportError as ImportErrorModel
except ImportError:
    pass  # Some models might not exist yet

__all__ = [
    'Base', 'AuditMixin',
    'User', 'Role', 'Client', 'user_role'
]