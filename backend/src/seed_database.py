"""
Database seeder for creating test data according to the constitution and data model specifications.
Creates multi-tenant data with proper RBAC, audit trails, and all required entities.
"""

import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.base import Base
from models.client import Client
from models.user import User
from models.role import Role
from models.user_role import user_role
from models.business_unit import BusinessUnit
from models.region import Region
from models.supplier import Supplier
from models.invoice import Invoice
from models.invoice_item import InvoiceItem
from models.subcategory import SubCategoryL1, SubCategoryL2, SubCategoryL3, SubCategoryL4
from models.currency import Currency
from models.unit_of_measure import UnitOfMeasure
from models.client_settings import ClientSettings
from datetime import date, datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """Create all tables and seed with test data following the enterprise-grade constitution."""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if comprehensive data already exists
        if db.query(Invoice).count() > 0:
            logger.info("Database already has comprehensive data. Skipping.")
            return
        
        # Check if we need to add more clients and users
        existing_clients = db.query(Client).count()
        if existing_clients > 0:
            logger.info(f"Found {existing_clients} existing clients. Adding additional test data...")
            # Skip to invoice creation since basic structure exists
        
        logger.info("Starting database seeding...")
        
        # 1. Create Clients (Multi-tenancy)
        clients = [
            Client(id=0, name="SuperAdmin Global Access", created_by=1, updated_by=1),
            Client(id=1, name="ACME Corporation", created_by=1, updated_by=1),
            Client(id=2, name="Global Enterprises", created_by=1, updated_by=1),
            Client(id=3, name="Tech Solutions Inc", created_by=1, updated_by=1)
        ]
        
        for client in clients:
            db.add(client)
        db.commit()
        logger.info("✅ Created clients")
        
        # 2. Create Roles (RBAC)
        roles = [
            Role(id=1, name="superadmin", permissions={
                "clients": ["create", "read", "update", "delete"],
                "users": ["create", "read", "update", "delete"],
                "all_entities": ["create", "read", "update", "delete"],
                "config": ["read", "update"],
                "reports": ["create", "read", "update", "delete"]
            }),
            Role(id=2, name="client_admin", permissions={
                "users": ["create", "read", "update", "delete"],
                "all_entities": ["create", "read", "update", "delete"],
                "config": ["read", "update"],
                "reports": ["create", "read", "update", "delete"]
            }),
            Role(id=3, name="user", permissions={
                "invoices": ["create", "read", "update"],
                "suppliers": ["read"],
                "business_units": ["read"],
                "regions": ["read"],
                "reports": ["read"]
            })
        ]
        
        for role in roles:
            db.add(role)
        db.commit()
        logger.info("✅ Created roles")
        
        # 3. Create Users with proper password hashing
        users = [
            # Superadmin (global access with dedicated client)
            User(id=1, username="superadmin", email="admin@spendplatform.com", client_id=0),
            
            # ACME Corporation users
            User(id=2, username="acme_admin", email="admin@acme.com", client_id=1),
            User(id=3, username="acme_user1", email="user1@acme.com", client_id=1),
            User(id=4, username="acme_user2", email="user2@acme.com", client_id=1),
            
            # Global Enterprises users
            User(id=5, username="global_admin", email="admin@global.com", client_id=2),
            User(id=6, username="global_user1", email="user1@global.com", client_id=2),
            
            # Tech Solutions users
            User(id=7, username="tech_admin", email="admin@tech.com", client_id=3),
            User(id=8, username="tech_user1", email="user1@tech.com", client_id=3)
        ]
        
        # Set passwords from environment variables (with fallbacks for development)
        environment = os.getenv('ENVIRONMENT', 'development')
        
        if environment == 'production':
            # In production, require environment variables for all passwords
            superadmin_password = os.getenv('SEED_SUPERADMIN_PASSWORD')
            admin_password = os.getenv('SEED_ADMIN_PASSWORD')
            user_password = os.getenv('SEED_USER_PASSWORD')
            
            if not all([superadmin_password, admin_password, user_password]):
                raise ValueError(
                    "Production environment requires SEED_SUPERADMIN_PASSWORD, "
                    "SEED_ADMIN_PASSWORD, and SEED_USER_PASSWORD environment variables"
                )
        else:
            # Development fallbacks
            superadmin_password = os.getenv('SEED_SUPERADMIN_PASSWORD', 'Dev_SuperAdmin_2024!')
            admin_password = os.getenv('SEED_ADMIN_PASSWORD', 'Dev_Admin_2024!')
            user_password = os.getenv('SEED_USER_PASSWORD', 'Dev_User_2024!')
            
        # Ensure passwords are strings (should never be None due to fallbacks or validation above)
        assert superadmin_password is not None, "Superadmin password cannot be None"
        assert admin_password is not None, "Admin password cannot be None"  
        assert user_password is not None, "User password cannot be None"
        
        users[0].set_password(superadmin_password)  # superadmin
        users[1].set_password(admin_password)       # acme_admin
        users[2].set_password(user_password)        # acme_user1
        users[3].set_password(user_password)        # acme_user2
        users[4].set_password(admin_password)       # global_admin
        users[5].set_password(user_password)        # global_user1
        users[6].set_password(admin_password)       # tech_admin
        users[7].set_password(user_password)        # tech_user1
        
        for user in users:
            db.add(user)
        db.commit()
        logger.info("✅ Created users with secure passwords")
        
        # 4. Assign roles to users using relationship
        user_role_assignments = [
            (1, 1),  # superadmin -> superadmin
            (2, 2),  # acme_admin -> client_admin
            (3, 3),  # acme_user1 -> user
            (4, 3),  # acme_user2 -> user
            (5, 2),  # global_admin -> client_admin
            (6, 3),  # global_user1 -> user
            (7, 2),  # tech_admin -> client_admin
            (8, 3),  # tech_user1 -> user
        ]
        
        # Insert into the association table
        for user_id, role_id in user_role_assignments:
            db.execute(user_role.insert().values(user_id=user_id, role_id=role_id))
        db.commit()
        logger.info("✅ Assigned roles to users")
        
        # 5. Create Client Settings
        client_settings = [
            ClientSettings(
                id=1, client_id=1,
                feature_flags={"advanced_reporting": True, "multi_currency": True, "audit_logs": True},
                branding={"logo": "acme_logo.png", "primary_color": "#FF6B35", "company_name": "ACME Corporation"},
                ui_personalisation={"default_theme": "light", "default_currency": "USD", "date_format": "MM/DD/YYYY"}
            ),
            ClientSettings(
                id=2, client_id=2,
                feature_flags={"advanced_reporting": True, "multi_currency": False, "audit_logs": True},
                branding={"logo": "global_logo.png", "primary_color": "#2E86AB", "company_name": "Global Enterprises"},
                ui_personalisation={"default_theme": "dark", "default_currency": "EUR", "date_format": "DD/MM/YYYY"}
            ),
            ClientSettings(
                id=3, client_id=3,
                feature_flags={"advanced_reporting": False, "multi_currency": True, "audit_logs": False},
                branding={"logo": "tech_logo.png", "primary_color": "#A23B72", "company_name": "Tech Solutions Inc"},
                ui_personalisation={"default_theme": "light", "default_currency": "GBP", "date_format": "YYYY-MM-DD"}
            )
        ]
        
        for setting in client_settings:
            db.add(setting)
        db.commit()
        logger.info("✅ Created client settings")
        
        # 6. Create Regions
        regions = [
            # ACME regions
            Region(id=1, name="North America", code="NA", client_id=1, created_by=2),
            Region(id=2, name="Europe", code="EU", client_id=1, created_by=2),
            Region(id=3, name="Asia Pacific", code="APAC", client_id=1, created_by=2),
            
            # Global Enterprises regions
            Region(id=4, name="Americas", code="AM", client_id=2, created_by=5),
            Region(id=5, name="EMEA", code="EMEA", client_id=2, created_by=5),
            
            # Tech Solutions regions
            Region(id=6, name="UK & Ireland", code="UK", client_id=3, created_by=7),
            Region(id=7, name="Continental Europe", code="CE", client_id=3, created_by=7)
        ]
        
        for region in regions:
            db.add(region)
        db.commit()
        logger.info("✅ Created regions")
        
        # 7. Create Business Units  
        business_units = [
            # ACME business units
            BusinessUnit(id=1, name="Procurement", code="PROC", client_id=1, created_by=2),
            BusinessUnit(id=2, name="Finance", code="FIN", client_id=1, created_by=2),
            BusinessUnit(id=3, name="Operations", code="OPS", client_id=1, created_by=2),
            BusinessUnit(id=4, name="IT", code="IT", client_id=1, created_by=2),
            
            # Global Enterprises business units
            BusinessUnit(id=5, name="Purchasing", code="PUR", client_id=2, created_by=5),
            BusinessUnit(id=6, name="Manufacturing", code="MFG", client_id=2, created_by=5),
            
            # Tech Solutions business units
            BusinessUnit(id=7, name="Development", code="DEV", client_id=3, created_by=7),
            BusinessUnit(id=8, name="Support", code="SUP", client_id=3, created_by=7)
        ]
        
        for bu in business_units:
            db.add(bu)
        db.commit()
        logger.info("✅ Created business units")
        
        # 8. Create Currencies
        currencies = [
            # ACME currencies
            Currency(id=1, code="USD", name="US Dollar", client_id=1, created_by=2),
            Currency(id=2, code="EUR", name="Euro", client_id=1, created_by=2),
            Currency(id=3, code="GBP", name="British Pound", client_id=1, created_by=2),
            
            # Global Enterprises currencies
            Currency(id=4, code="EUR", name="Euro", client_id=2, created_by=5),
            Currency(id=5, code="USD", name="US Dollar", client_id=2, created_by=5),
            
            # Tech Solutions currencies
            Currency(id=6, code="GBP", name="British Pound", client_id=3, created_by=7),
            Currency(id=7, code="EUR", name="Euro", client_id=3, created_by=7)
        ]
        
        for currency in currencies:
            db.add(currency)
        db.commit()
        logger.info("✅ Created currencies")
        
        # 9. Create Units of Measure
        units = [
            # ACME units
            UnitOfMeasure(id=1, name="Each", client_id=1, created_by=2),
            UnitOfMeasure(id=2, name="Kilogram", client_id=1, created_by=2),
            UnitOfMeasure(id=3, name="Liter", client_id=1, created_by=2),
            UnitOfMeasure(id=4, name="Hour", client_id=1, created_by=2),
            
            # Global Enterprises units
            UnitOfMeasure(id=5, name="Piece", client_id=2, created_by=5),
            UnitOfMeasure(id=6, name="Meter", client_id=2, created_by=5),
            
            # Tech Solutions units
            UnitOfMeasure(id=7, name="License", client_id=3, created_by=7),
            UnitOfMeasure(id=8, name="User", client_id=3, created_by=7)
        ]
        
        for unit in units:
            db.add(unit)
        db.commit()
        logger.info("✅ Created units of measure")
        
        # 10. Create Category Hierarchy (L1 -> L4)
        # L1 Categories
        l1_categories = [
            # ACME L1
            SubCategoryL1(id=1, name="Office Supplies", client_id=1, created_by=2),
            SubCategoryL1(id=2, name="IT Equipment", client_id=1, created_by=2),
            SubCategoryL1(id=3, name="Professional Services", client_id=1, created_by=2),
            
            # Global L1
            SubCategoryL1(id=4, name="Raw Materials", client_id=2, created_by=5),
            SubCategoryL1(id=5, name="Machinery", client_id=2, created_by=5),
            
            # Tech L1
            SubCategoryL1(id=6, name="Software", client_id=3, created_by=7),
            SubCategoryL1(id=7, name="Hardware", client_id=3, created_by=7)
        ]
        
        for cat in l1_categories:
            db.add(cat)
        db.commit()
        
        # L2 Categories
        l2_categories = [
            SubCategoryL2(id=1, name="Stationery", parent_id=1, client_id=1, created_by=2),
            SubCategoryL2(id=2, name="Furniture", parent_id=1, client_id=1, created_by=2),
            SubCategoryL2(id=3, name="Computers", parent_id=2, client_id=1, created_by=2),
            SubCategoryL2(id=4, name="Networking", parent_id=2, client_id=1, created_by=2),
            SubCategoryL2(id=5, name="Consulting", parent_id=3, client_id=1, created_by=2),
            
            SubCategoryL2(id=6, name="Steel", parent_id=4, client_id=2, created_by=5),
            SubCategoryL2(id=7, name="Production Equipment", parent_id=5, client_id=2, created_by=5),
            
            SubCategoryL2(id=8, name="Development Tools", parent_id=6, client_id=3, created_by=7),
            SubCategoryL2(id=9, name="Servers", parent_id=7, client_id=3, created_by=7)
        ]
        
        for cat in l2_categories:
            db.add(cat)
        db.commit()
        logger.info("✅ Created category hierarchy")
        
        # 11. Create Suppliers
        suppliers = [
            # ACME suppliers
            Supplier(id=1, name="Office Depot Inc", contact_info="contact@officedepot.com", region_id=1, client_id=1, created_by=2),
            Supplier(id=2, name="Dell Technologies", contact_info="sales@dell.com", region_id=1, client_id=1, created_by=2),
            Supplier(id=3, name="Accenture", contact_info="info@accenture.com", region_id=2, client_id=1, created_by=2),
            Supplier(id=4, name="Staples Europe", contact_info="eu@staples.com", region_id=2, client_id=1, created_by=2),
            
            # Global suppliers
            Supplier(id=5, name="ArcelorMittal", contact_info="sales@arcelormittal.com", region_id=4, client_id=2, created_by=5),
            Supplier(id=6, name="Siemens AG", contact_info="info@siemens.com", region_id=5, client_id=2, created_by=5),
            
            # Tech suppliers
            Supplier(id=7, name="Microsoft UK", contact_info="uk@microsoft.com", region_id=6, client_id=3, created_by=7),
            Supplier(id=8, name="AWS Europe", contact_info="support@aws.amazon.com", region_id=7, client_id=3, created_by=7)
        ]
        
        for supplier in suppliers:
            db.add(supplier)
        db.commit()
        logger.info("✅ Created suppliers")
        
        # 12. Create Invoices
        invoices = [
            # ACME invoices
            Invoice(id=1, invoice_number="INV-2024-001", date=date(2024, 1, 15), supplier_id=1, business_unit_id=1, client_id=1, created_by=3),
            Invoice(id=2, invoice_number="INV-2024-002", date=date(2024, 1, 20), supplier_id=2, business_unit_id=4, client_id=1, created_by=3),
            Invoice(id=3, invoice_number="INV-2024-003", date=date(2024, 2, 1), supplier_id=3, business_unit_id=2, client_id=1, created_by=4),
            Invoice(id=4, invoice_number="INV-2024-004", date=date(2024, 2, 10), supplier_id=4, business_unit_id=1, client_id=1, created_by=3),
            
            # Global invoices
            Invoice(id=5, invoice_number="GL-2024-001", date=date(2024, 1, 5), supplier_id=5, business_unit_id=6, client_id=2, created_by=6),
            Invoice(id=6, invoice_number="GL-2024-002", date=date(2024, 1, 25), supplier_id=6, business_unit_id=6, client_id=2, created_by=6),
            
            # Tech invoices
            Invoice(id=7, invoice_number="TECH-2024-001", date=date(2024, 1, 10), supplier_id=7, business_unit_id=7, client_id=3, created_by=8),
            Invoice(id=8, invoice_number="TECH-2024-002", date=date(2024, 1, 30), supplier_id=8, business_unit_id=7, client_id=3, created_by=8)
        ]
        
        for invoice in invoices:
            db.add(invoice)
        db.commit()
        logger.info("✅ Created invoices")
        
        # 13. Create Invoice Items
        invoice_items = [
            # ACME invoice items
            InvoiceItem(id=1, invoice_id=1, item_number="1", type="Product", description="Office chairs", 
                       subcategory_l1_id=1, subcategory_l2_id=2, qty=10, unit_of_measure_id=1, 
                       currency_id=1, unit_price=150.00, total_amount=1500.00, client_id=1, created_by=3),
            InvoiceItem(id=2, invoice_id=1, item_number="2", type="Product", description="Printer paper", 
                       subcategory_l1_id=1, subcategory_l2_id=1, qty=20, unit_of_measure_id=1, 
                       currency_id=1, unit_price=25.00, total_amount=500.00, client_id=1, created_by=3),
            
            InvoiceItem(id=3, invoice_id=2, item_number="1", type="Product", description="Dell laptops", 
                       subcategory_l1_id=2, subcategory_l2_id=3, qty=5, unit_of_measure_id=1, 
                       currency_id=1, unit_price=1200.00, total_amount=6000.00, client_id=1, created_by=3),
            
            InvoiceItem(id=4, invoice_id=3, item_number="1", type="Service", description="IT Consulting", 
                       subcategory_l1_id=3, subcategory_l2_id=5, qty=40, unit_of_measure_id=4, 
                       currency_id=1, unit_price=150.00, total_amount=6000.00, client_id=1, created_by=4),
            
            # Global invoice items
            InvoiceItem(id=5, invoice_id=5, item_number="1", type="Product", description="Steel plates", 
                       subcategory_l1_id=4, subcategory_l2_id=6, qty=1000, unit_of_measure_id=2, 
                       currency_id=4, unit_price=2.50, total_amount=2500.00, client_id=2, created_by=6),
            
            # Tech invoice items
            InvoiceItem(id=6, invoice_id=7, item_number="1", type="Service", description="Office 365 licenses", 
                       subcategory_l1_id=6, subcategory_l2_id=8, qty=50, unit_of_measure_id=7, 
                       currency_id=6, unit_price=12.50, total_amount=625.00, client_id=3, created_by=8)
        ]
        
        for item in invoice_items:
            db.add(item)
        db.commit()
        logger.info("✅ Created invoice items")
        
        logger.info("🎉 Database seeding completed successfully!")
        logger.info("Test users created with environment-configured passwords:")
        if environment == 'production':
            logger.info("  - superadmin (superadmin role) - password from SEED_SUPERADMIN_PASSWORD")
            logger.info("  - acme_admin (client_admin role) - password from SEED_ADMIN_PASSWORD")
            logger.info("  - acme_user1 (user role) - password from SEED_USER_PASSWORD")
            logger.info("  - global_admin (client_admin role) - password from SEED_ADMIN_PASSWORD")
            logger.info("  - tech_admin (client_admin role) - password from SEED_ADMIN_PASSWORD")
        else:
            logger.info("  - superadmin (superadmin role) - using development default password")
            logger.info("  - acme_admin (client_admin role) - using development default password")
            logger.info("  - acme_user1 (user role) - using development default password")
            logger.info("  - global_admin (client_admin role) - using development default password")
            logger.info("  - tech_admin (client_admin role) - using development default password")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()