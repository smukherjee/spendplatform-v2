"""
Simple database seeder that adds missing test data to existing database.
"""

from sqlalchemy.orm import Session
from database import SessionLocal
from models.client import Client
from models.user import User
from models.role import Role
from models.user_role import user_role
from models.business_unit import BusinessUnit
from models.region import Region
from models.supplier import Supplier
from models.invoice import Invoice
from models.invoice_item import InvoiceItem
from models.subcategory import SubCategoryL1, SubCategoryL2
from models.currency import Currency
from models.unit_of_measure import UnitOfMeasure
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_test_data():
    """Add comprehensive test data to existing database."""
    
    db: Session = SessionLocal()
    
    try:
        logger.info("Adding test data to existing database...")
        
        # Check existing data
        existing_clients = db.query(Client).count()
        existing_users = db.query(User).count()
        existing_invoices = db.query(Invoice).count()
        
        logger.info(f"Current state: {existing_clients} clients, {existing_users} users, {existing_invoices} invoices")
        
        # Get the existing client (should be ACME Corporation or similar)
        client = db.query(Client).first()
        if not client:
            logger.error("No client found in database!")
            return
        
        client_id = client.id
        logger.info(f"Using client: {client.name} (ID: {client_id})")
        
        # Ensure baseline role hierarchy exists
        role_changes = False

        superadmin_role = (
            db.query(Role)
            .filter(Role.name == "superadmin", Role.client_id.is_(None))
            .one_or_none()
        )

        if not superadmin_role:
            superadmin_role = Role(
                name="superadmin",
                permissions={
                    "clients": ["create", "read", "update", "delete"],
                    "users": ["create", "read", "update", "delete"],
                    "all_entities": ["create", "read", "update", "delete"],
                    "config": ["read", "update"],
                    "reports": ["create", "read", "update", "delete"]
                },
                hierarchy_level=0,
                client_id=None,
                parent_role_id=None
            )
            db.add(superadmin_role)
            db.flush()
            role_changes = True
        else:
            if getattr(superadmin_role, "hierarchy_level", None) != 0:
                setattr(superadmin_role, "hierarchy_level", 0)
                role_changes = True
            if getattr(superadmin_role, "client_id", None) is not None:
                setattr(superadmin_role, "client_id", None)
                role_changes = True
            if getattr(superadmin_role, "parent_role_id", None) is not None:
                setattr(superadmin_role, "parent_role_id", None)
                role_changes = True

        client_admin_role = (
            db.query(Role)
            .filter(Role.name == "client_admin", Role.client_id == client_id)
            .one_or_none()
        )

        if not client_admin_role:
            client_admin_role = Role(
                name="client_admin",
                permissions={
                    "users": ["create", "read", "update", "delete"],
                    "all_entities": ["create", "read", "update", "delete"],
                    "config": ["read", "update"],
                    "reports": ["create", "read", "update", "delete"]
                },
                hierarchy_level=1,
                client_id=client_id,
                parent_role_id=superadmin_role.id
            )
            db.add(client_admin_role)
            db.flush()
            role_changes = True
        else:
            if getattr(client_admin_role, "hierarchy_level", None) != 1:
                setattr(client_admin_role, "hierarchy_level", 1)
                role_changes = True
            if getattr(client_admin_role, "client_id", None) != client_id:
                setattr(client_admin_role, "client_id", client_id)
                role_changes = True
            if getattr(client_admin_role, "parent_role_id", None) != superadmin_role.id:
                setattr(client_admin_role, "parent_role_id", superadmin_role.id)
                role_changes = True

        user_role = (
            db.query(Role)
            .filter(Role.name == "user", Role.client_id == client_id)
            .one_or_none()
        )

        if not user_role:
            user_role = Role(
                name="user",
                permissions={
                    "invoices": ["create", "read", "update"],
                    "suppliers": ["read"],
                    "business_units": ["read"],
                    "regions": ["read"],
                    "reports": ["read"]
                },
                hierarchy_level=2,
                client_id=client_id,
                parent_role_id=client_admin_role.id
            )
            db.add(user_role)
            db.flush()
            role_changes = True
        else:
            if getattr(user_role, "hierarchy_level", None) != 2:
                setattr(user_role, "hierarchy_level", 2)
                role_changes = True
            if getattr(user_role, "client_id", None) != client_id:
                setattr(user_role, "client_id", client_id)
                role_changes = True
            if getattr(user_role, "parent_role_id", None) != client_admin_role.id:
                setattr(user_role, "parent_role_id", client_admin_role.id)
                role_changes = True

        if role_changes:
            db.commit()
            logger.info("✅ Baseline roles ensured and updated")
        
        # Add business units
        if db.query(BusinessUnit).count() == 0:
            business_units = [
                BusinessUnit(name="Procurement", code="PROC", client_id=client_id, created_by=1),
                BusinessUnit(name="Finance", code="FIN", client_id=client_id, created_by=1),
                BusinessUnit(name="Operations", code="OPS", client_id=client_id, created_by=1),
                BusinessUnit(name="IT", code="IT", client_id=client_id, created_by=1),
            ]
            
            for bu in business_units:
                db.add(bu)
            db.commit()
            logger.info("✅ Created business units")
        
        # Add regions
        if db.query(Region).count() == 0:
            regions = [
                Region(name="North America", code="NA", client_id=client_id, created_by=1),
                Region(name="Europe", code="EU", client_id=client_id, created_by=1),
                Region(name="Asia Pacific", code="APAC", client_id=client_id, created_by=1),
            ]
            
            for region in regions:
                db.add(region)
            db.commit()
            logger.info("✅ Created regions")
        
        # Add currencies
        if db.query(Currency).count() == 0:
            currencies = [
                Currency(code="USD", name="US Dollar", client_id=client_id, created_by=1),
                Currency(code="EUR", name="Euro", client_id=client_id, created_by=1),
                Currency(code="GBP", name="British Pound", client_id=client_id, created_by=1),
            ]
            
            for currency in currencies:
                db.add(currency)
            db.commit()
            logger.info("✅ Created currencies")
        
        # Add units of measure
        if db.query(UnitOfMeasure).count() == 0:
            units = [
                UnitOfMeasure(name="Each", client_id=client_id, created_by=1),
                UnitOfMeasure(name="Kilogram", client_id=client_id, created_by=1),
                UnitOfMeasure(name="Liter", client_id=client_id, created_by=1),
                UnitOfMeasure(name="Hour", client_id=client_id, created_by=1),
            ]
            
            for unit in units:
                db.add(unit)
            db.commit()
            logger.info("✅ Created units of measure")
        
        # Add categories
        if db.query(SubCategoryL1).count() == 0:
            l1_categories = [
                SubCategoryL1(name="Office Supplies", client_id=client_id, created_by=1),
                SubCategoryL1(name="IT Equipment", client_id=client_id, created_by=1),
                SubCategoryL1(name="Professional Services", client_id=client_id, created_by=1),
            ]
            
            for cat in l1_categories:
                db.add(cat)
            db.commit()
            
            # Add L2 categories
            l2_categories = [
                SubCategoryL2(name="Stationery", parent_id=1, client_id=client_id, created_by=1),
                SubCategoryL2(name="Furniture", parent_id=1, client_id=client_id, created_by=1),
                SubCategoryL2(name="Computers", parent_id=2, client_id=client_id, created_by=1),
                SubCategoryL2(name="Networking", parent_id=2, client_id=client_id, created_by=1),
                SubCategoryL2(name="Consulting", parent_id=3, client_id=client_id, created_by=1),
            ]
            
            for cat in l2_categories:
                db.add(cat)
            db.commit()
            logger.info("✅ Created category hierarchy")
        
        # Add suppliers
        if db.query(Supplier).count() == 0:
            suppliers = [
                Supplier(name="Office Depot Inc", contact_info="contact@officedepot.com", region_id=1, client_id=client_id, created_by=1),
                Supplier(name="Dell Technologies", contact_info="sales@dell.com", region_id=1, client_id=client_id, created_by=1),
                Supplier(name="Accenture", contact_info="info@accenture.com", region_id=2, client_id=client_id, created_by=1),
                Supplier(name="Staples Europe", contact_info="eu@staples.com", region_id=2, client_id=client_id, created_by=1),
            ]
            
            for supplier in suppliers:
                db.add(supplier)
            db.commit()
            logger.info("✅ Created suppliers")
        
        # Add invoices and invoice items
        if db.query(Invoice).count() == 0:
            invoices = [
                Invoice(invoice_number="INV-2024-001", date=date(2024, 1, 15), supplier_id=1, business_unit_id=1, client_id=client_id, created_by=1),
                Invoice(invoice_number="INV-2024-002", date=date(2024, 1, 20), supplier_id=2, business_unit_id=4, client_id=client_id, created_by=1),
                Invoice(invoice_number="INV-2024-003", date=date(2024, 2, 1), supplier_id=3, business_unit_id=2, client_id=client_id, created_by=1),
                Invoice(invoice_number="INV-2024-004", date=date(2024, 2, 10), supplier_id=4, business_unit_id=1, client_id=client_id, created_by=1),
            ]
            
            for invoice in invoices:
                db.add(invoice)
            db.commit()
            logger.info("✅ Created invoices")
            
            # Add invoice items
            invoice_items = [
                InvoiceItem(invoice_id=1, item_number="1", type="Product", description="Office chairs", 
                           subcategory_l1_id=1, subcategory_l2_id=2, qty=10, unit_of_measure_id=1, 
                           currency_id=1, unit_price=150.00, total_amount=1500.00, client_id=client_id, created_by=1),
                InvoiceItem(invoice_id=1, item_number="2", type="Product", description="Printer paper", 
                           subcategory_l1_id=1, subcategory_l2_id=1, qty=20, unit_of_measure_id=1, 
                           currency_id=1, unit_price=25.00, total_amount=500.00, client_id=client_id, created_by=1),
                
                InvoiceItem(invoice_id=2, item_number="1", type="Product", description="Dell laptops", 
                           subcategory_l1_id=2, subcategory_l2_id=3, qty=5, unit_of_measure_id=1, 
                           currency_id=1, unit_price=1200.00, total_amount=6000.00, client_id=client_id, created_by=1),
                
                InvoiceItem(invoice_id=3, item_number="1", type="Service", description="IT Consulting", 
                           subcategory_l1_id=3, subcategory_l2_id=5, qty=40, unit_of_measure_id=4, 
                           currency_id=1, unit_price=150.00, total_amount=6000.00, client_id=client_id, created_by=1),
            ]
            
            for item in invoice_items:
                db.add(item)
            db.commit()
            logger.info("✅ Created invoice items")
        
        logger.info("🎉 Test data added successfully!")
        
        # Print summary
        final_invoices = db.query(Invoice).count()
        final_suppliers = db.query(Supplier).count()
        final_bus = db.query(BusinessUnit).count()
        
        logger.info(f"Final counts: {final_invoices} invoices, {final_suppliers} suppliers, {final_bus} business units")
        
    except Exception as e:
        logger.error(f"Error during data addition: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data()