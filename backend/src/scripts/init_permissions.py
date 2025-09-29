"""
Database initialization script for screen permissions system
Run this to populate initial screens and permissions data
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List, Dict, Any
import asyncio
import logging

from database_async import AsyncSessionLocal, async_engine
from models.screen_permission import Screen, RoleScreenPermission
from models.role import Role
from models.client import Client

logger = logging.getLogger(__name__)

# Complete list of screens based on available routers
INITIAL_SCREENS = [
    # Analytics & Dashboard
    {"name": "Dashboard", "route": "/dashboard", "category": "Analytics", "icon": "dashboard", "order_priority": 1, "description": "Main dashboard with overview metrics"},
    
    # Financial Management
    {"name": "Invoice Management", "route": "/invoices", "category": "Financial", "icon": "receipt", "order_priority": 10, "description": "Manage invoices and billing"},
    {"name": "Invoice Items", "route": "/invoice-items", "category": "Financial", "icon": "list", "order_priority": 11, "description": "Manage individual invoice line items"},
    
    # Master Data Management
    {"name": "Supplier Management", "route": "/suppliers", "category": "Master Data", "icon": "business", "order_priority": 20, "description": "Manage supplier information and relationships"},
    {"name": "Business Units", "route": "/business-units", "category": "Master Data", "icon": "corporate_fare", "order_priority": 21, "description": "Manage organizational business units"},
    {"name": "Regions", "route": "/regions", "category": "Master Data", "icon": "public", "order_priority": 22, "description": "Manage geographical regions"},
    {"name": "Currencies", "route": "/currency", "category": "Master Data", "icon": "attach_money", "order_priority": 23, "description": "Manage currency settings and exchange rates"},
    {"name": "Subcategories", "route": "/subcategories", "category": "Master Data", "icon": "category", "order_priority": 24, "description": "Manage product and service subcategories"},
    {"name": "Units of Measure", "route": "/unit-of-measure", "category": "Master Data", "icon": "straighten", "order_priority": 25, "description": "Manage measurement units"},
    
    # User & Access Management
    {"name": "User Management", "route": "/users", "category": "Administration", "icon": "people", "order_priority": 30, "description": "Manage user accounts and profiles"},
    {"name": "Advanced User Management", "route": "/user-management", "category": "Administration", "icon": "admin_panel_settings", "order_priority": 31, "description": "Advanced user administration tools"},
    {"name": "Client Management", "route": "/clients", "category": "Administration", "icon": "domain", "order_priority": 32, "description": "Manage client organizations", "requires_super_admin": True},
    {"name": "Role Management", "route": "/roles", "category": "Administration", "icon": "security", "order_priority": 33, "description": "Manage user roles and permissions"},
    
    # Reporting & Analytics
    {"name": "Reports", "route": "/reporting", "category": "Analytics", "icon": "assessment", "order_priority": 40, "description": "Generate and view reports"},
    
    # System Administration
    {"name": "Audit", "route": "/audit", "category": "Administration", "icon": "fact_check", "order_priority": 50, "description": "System audit and compliance tools"},
    {"name": "Audit Logs", "route": "/audit-logs", "category": "Administration", "icon": "history", "order_priority": 51, "description": "View system audit logs"},
    {"name": "Settings", "route": "/settings", "category": "Administration", "icon": "settings", "order_priority": 52, "description": "General application settings"},
    {"name": "Client Settings", "route": "/client-settings", "category": "Administration", "icon": "tune", "order_priority": 53, "description": "Client-specific configuration settings"},
    {"name": "Screen Permissions", "route": "/screen-permissions", "category": "Administration", "icon": "lock", "order_priority": 54, "description": "Manage screen access permissions"},
    
    # Data Management
    {"name": "Import Errors", "route": "/import-errors", "category": "Data Management", "icon": "error", "order_priority": 60, "description": "View and resolve data import errors"},
]

# Default role permissions configuration
DEFAULT_ROLE_PERMISSIONS = {
    "superadmin": {
        "description": "Full system access with all permissions",
        "permissions": {
            # All screens with full permissions
            "default": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_export": True, "can_import": True},
            # Audit screens are view-only even for superadmin
            "overrides": {
                "/audit": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": True, "can_import": False},
                "/audit-logs": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": True, "can_import": False},
            }
        }
    },
    "client_admin": {
        "description": "Administrative access within client organization",
        "permissions": {
            "default": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
            "grants": {
                # Analytics & Dashboard
                "/dashboard": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": True, "can_import": False},
                
                # Financial Management
                "/invoices": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_export": True, "can_import": True},
                "/invoice-items": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_export": True, "can_import": False},
                
                # Master Data Management
                "/suppliers": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_export": True, "can_import": True},
                "/business-units": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_export": True, "can_import": False},
                "/regions": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_export": True, "can_import": False},
                "/currency": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                "/unit-of-measure": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_export": True, "can_import": False},
                
                # User Management
                "/users": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_export": True, "can_import": False},
                "/user-management": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_export": True, "can_import": False},
                "/roles": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                
                # Reporting
                "/reporting": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_export": True, "can_import": False},
                
                # Administration
                "/audit": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": True, "can_import": False},
                "/client-settings": {"can_view": True, "can_create": False, "can_edit": True, "can_delete": False, "can_export": False, "can_import": False},
                "/settings": {"can_view": True, "can_create": False, "can_edit": True, "can_delete": False, "can_export": False, "can_import": False},
                "/screen-permissions": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
            }
        }
    },
    "user": {
        "description": "Standard user access for operational tasks",
        "permissions": {
            "default": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
            "grants": {
                # Analytics & Dashboard
                "/dashboard": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                
                # Financial Management - limited access
                "/invoices": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_export": True, "can_import": False},
                "/invoice-items": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_export": False, "can_import": False},
                
                # Master Data - read-only access
                "/suppliers": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                "/business-units": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                "/regions": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                "/currency": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                "/unit-of-measure": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": False, "can_import": False},
                
                # Reporting - basic access
                "/reporting": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_export": True, "can_import": False},
            }
        }
    }
}

async def init_screens(session: AsyncSession) -> None:
    """Initialize screens in the database"""
    logger.info("Initializing screens...")
    
    try:
        # Delete existing data in correct order (foreign keys first)
        await session.execute(delete(RoleScreenPermission))
        await session.execute(delete(Screen))
        await session.commit()
        
        # Insert new screens
        for screen_data in INITIAL_SCREENS:
            screen = Screen(**screen_data)
            session.add(screen)
        
        await session.commit()
        logger.info(f"Successfully initialized {len(INITIAL_SCREENS)} screens")
        
    except Exception as e:
        logger.error(f"Error initializing screens: {e}")
        await session.rollback()
        raise

async def init_role_permissions(session: AsyncSession) -> None:
    """Initialize default role permissions"""
    logger.info("Initializing role permissions...")
    
    try:
        # Get all screens and roles
        screens_result = await session.execute(select(Screen))
        screens = {screen.route: screen for screen in screens_result.scalars().all()}
        
        roles_result = await session.execute(select(Role))
        roles = {role.name: role for role in roles_result.scalars().all()}
        
        # Delete existing role permissions
        await session.execute(delete(RoleScreenPermission))
        await session.commit()
        
        # Create permissions for each role
        permissions_created = 0
        for role_name, role_config in DEFAULT_ROLE_PERMISSIONS.items():
            if role_name not in roles:
                logger.warning(f"Role '{role_name}' not found, skipping permissions")
                continue
            
            role = roles[role_name]
            permissions = role_config["permissions"]
            
            for screen_route, screen in screens.items():
                # Determine permissions for this screen
                if role_name == "superadmin":
                    # Super admin gets all permissions except for overrides
                    if screen_route in permissions.get("overrides", {}):
                        screen_permissions = permissions["overrides"][screen_route]
                    else:
                        screen_permissions = permissions["default"]
                else:
                    # Other roles use grants system
                    if screen_route in permissions.get("grants", {}):
                        screen_permissions = permissions["grants"][screen_route]
                    else:
                        screen_permissions = permissions["default"]
                
                # Create role screen permission
                role_permission = RoleScreenPermission(
                    role_id=role.id,
                    screen_id=screen.id,
                    client_id=None,  # Global permissions
                    **screen_permissions
                )
                session.add(role_permission)
                permissions_created += 1
        
        await session.commit()
        logger.info(f"Successfully created {permissions_created} role permissions")
        
    except Exception as e:
        logger.error(f"Error initializing role permissions: {e}")
        await session.rollback()
        raise

async def initialize_permissions_system():
    """Main initialization function"""
    logger.info("Starting permissions system initialization...")
    
    async with AsyncSessionLocal() as session:
        try:
            await init_screens(session)
            await init_role_permissions(session)
            logger.info("✅ Permissions system initialization completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Permissions system initialization failed: {e}")
            raise

async def verify_initialization():
    """Verify that initialization was successful"""
    logger.info("Verifying permissions system initialization...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Count screens
            screens_result = await session.execute(select(func.count(Screen.id)))
            screen_count = screens_result.scalar() or 0
            
            # Count permissions
            permissions_result = await session.execute(select(func.count(RoleScreenPermission.id)))
            permission_count = permissions_result.scalar() or 0
            
            # Count roles
            roles_result = await session.execute(select(func.count(Role.id)))
            role_count = roles_result.scalar() or 0
            
            logger.info(f"📊 Verification Results:")
            logger.info(f"  - Screens: {screen_count}")
            logger.info(f"  - Role Permissions: {permission_count}")
            logger.info(f"  - Roles: {role_count}")
            
            if screen_count > 0 and permission_count > 0:
                logger.info("✅ Permissions system verification passed")
                return True
            else:
                logger.error("❌ Permissions system verification failed - missing data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Permissions system verification failed: {e}")
            return False

if __name__ == "__main__":
    import asyncio
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        try:
            await initialize_permissions_system()
            await verify_initialization()
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            exit(1)
    
    asyncio.run(main())