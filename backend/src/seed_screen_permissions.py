#!/usr/bin/env python3
"""
Screen Permission Seeding Script
Seeds the database with initial screens and permissions for superadmin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.screen_permission import Screen, RoleScreenPermission
from models.role import Role
from models.client import Client

def seed_screens():
    """Seed the database with initial screens and permissions"""
    db = SessionLocal()
    
    try:
        # Define all application screens
        screens_data = [
            # Financial Management
            {"name": "Dashboard", "route": "/dashboard", "category": "Financial", "description": "Main dashboard with overview"},
            {"name": "Invoices", "route": "/invoices", "category": "Financial", "description": "Invoice management"},
            {"name": "Invoice Detail", "route": "/invoices/:id", "category": "Financial", "description": "View invoice details"},
            {"name": "Invoice Edit", "route": "/invoices/:id/edit", "category": "Financial", "description": "Edit invoice"},
            {"name": "Suppliers", "route": "/suppliers", "category": "Financial", "description": "Supplier management"},
            {"name": "Supplier Detail", "route": "/suppliers/:id", "category": "Financial", "description": "View supplier details"},
            {"name": "Supplier Edit", "route": "/suppliers/:id/edit", "category": "Financial", "description": "Edit supplier"},
            
            # Administration
            {"name": "Users", "route": "/users", "category": "Administration", "description": "User management"},
            {"name": "User Detail", "route": "/users/:id", "category": "Administration", "description": "View user details"},
            {"name": "User Edit", "route": "/users/:id/edit", "category": "Administration", "description": "Edit user"},
            {"name": "Roles", "route": "/roles", "category": "Administration", "description": "Role management"},
            {"name": "Role Detail", "route": "/roles/:id", "category": "Administration", "description": "View role details"},
            {"name": "Role Edit", "route": "/roles/:id/edit", "category": "Administration", "description": "Edit role"},
            {"name": "Clients", "route": "/clients", "category": "Administration", "description": "Client management"},
            {"name": "Client Detail", "route": "/clients/:id", "category": "Administration", "description": "View client details"},
            {"name": "Client Edit", "route": "/clients/:id/edit", "category": "Administration", "description": "Edit client"},
            
            # Configuration
            {"name": "Business Units", "route": "/business-units", "category": "Configuration", "description": "Business unit management"},
            {"name": "Business Unit Detail", "route": "/business-units/:id", "category": "Configuration", "description": "View business unit details"},
            {"name": "Business Unit Edit", "route": "/business-units/:id/edit", "category": "Configuration", "description": "Edit business unit"},
            {"name": "Regions", "route": "/regions", "category": "Configuration", "description": "Region management"},
            {"name": "Region Detail", "route": "/regions/:id", "category": "Configuration", "description": "View region details"},
            {"name": "Region Edit", "route": "/regions/:id/edit", "category": "Configuration", "description": "Edit region"},
            {"name": "Subcategories", "route": "/subcategories", "category": "Configuration", "description": "Subcategory management"},
            {"name": "Subcategory Detail", "route": "/subcategories/:id", "category": "Configuration", "description": "View subcategory details"},
            {"name": "Subcategory Edit", "route": "/subcategories/:id/edit", "category": "Configuration", "description": "Edit subcategory"},
            {"name": "Unit of Measure", "route": "/unit-of-measures", "category": "Configuration", "description": "Unit of measure management"},
            {"name": "Unit of Measure Detail", "route": "/unit-of-measures/:id", "category": "Configuration", "description": "View unit of measure details"},
            {"name": "Unit of Measure Edit", "route": "/unit-of-measures/:id/edit", "category": "Configuration", "description": "Edit unit of measure"},
            {"name": "Currency", "route": "/currencies", "category": "Configuration", "description": "Currency management"},
            {"name": "Currency Detail", "route": "/currencies/:id", "category": "Configuration", "description": "View currency details"},
            {"name": "Currency Edit", "route": "/currencies/:id/edit", "category": "Configuration", "description": "Edit currency"},
            
            # System
            {"name": "Settings", "route": "/settings", "category": "System", "description": "System settings"},
            {"name": "Client Settings", "route": "/client-settings", "category": "System", "description": "Client-specific settings"},
            {"name": "Import Errors", "route": "/import-errors", "category": "System", "description": "Import error management"},
            {"name": "Reporting", "route": "/reports", "category": "System", "description": "Report generation"},
            {"name": "Screen Permissions", "route": "/screen-permissions", "category": "System", "description": "Screen permission management"},
        ]
        
        # Create screens if they don't exist
        created_screens = []
        for screen_data in screens_data:
            existing = db.query(Screen).filter(Screen.route == screen_data["route"]).first()
            if not existing:
                screen = Screen(**screen_data)
                db.add(screen)
                created_screens.append(screen_data["name"])
        
        db.commit()
        
        if created_screens:
            print(f"✅ Created {len(created_screens)} screens: {', '.join(created_screens)}")
        else:
            print("✅ All screens already exist")
        
        # Get superadmin role
        superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
        if not superadmin_role:
            print("❌ Superadmin role not found. Please seed roles first.")
            return
        
        # Get all clients
        clients = db.query(Client).all()
        if not clients:
            print("❌ No clients found. Please seed clients first.")
            return
        
        # Grant superadmin access to all screens for all clients
        all_screens = db.query(Screen).all()
        permissions_created = 0
        
        for client in clients:
            for screen in all_screens:
                # Check if permission already exists
                existing_perm = db.query(RoleScreenPermission).filter(
                    RoleScreenPermission.role_id == superadmin_role.id,
                    RoleScreenPermission.screen_id == screen.id,
                    RoleScreenPermission.client_id == client.id
                ).first()
                
                if not existing_perm:
                    permission = RoleScreenPermission(
                        role_id=superadmin_role.id,
                        screen_id=screen.id,
                        client_id=client.id,
                        allow_access=True
                    )
                    db.add(permission)
                    permissions_created += 1
        
        db.commit()
        
        if permissions_created > 0:
            print(f"✅ Created {permissions_created} superadmin permissions")
        else:
            print("✅ All superadmin permissions already exist")
        
        # Grant basic permissions to client_admin and user roles
        client_admin_role = db.query(Role).filter(Role.name == "client_admin").first()
        user_role = db.query(Role).filter(Role.name == "user").first()
        
        # Define basic screens that all authenticated users should access
        basic_screens = ["/dashboard", "/invoices", "/suppliers", "/business-units", "/regions"]
        admin_screens = ["/users", "/roles", "/settings", "/client-settings", "/screen-permissions"]
        
        for client in clients:
            # Grant basic access to all roles
            for role in [client_admin_role, user_role]:
                if not role:
                    continue
                    
                screen_list = basic_screens.copy()
                if str(role.name) == "client_admin":
                    screen_list.extend(admin_screens)
                
                for screen_route in screen_list:
                    screen = db.query(Screen).filter(Screen.route == screen_route).first()
                    if not screen:
                        continue
                    
                    existing_perm = db.query(RoleScreenPermission).filter(
                        RoleScreenPermission.role_id == role.id,
                        RoleScreenPermission.screen_id == screen.id,
                        RoleScreenPermission.client_id == client.id
                    ).first()
                    
                    if not existing_perm:
                        permission = RoleScreenPermission(
                            role_id=role.id,
                            screen_id=screen.id,
                            client_id=client.id,
                            allow_access=True
                        )
                        db.add(permission)
                        permissions_created += 1
        
        db.commit()
        print(f"✅ Screen permission seeding completed! Total permissions created: {permissions_created}")
        
    except Exception as e:
        print(f"❌ Error seeding screen permissions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding screen permissions...")
    seed_screens()
    print("✅ Screen permission seeding complete!")