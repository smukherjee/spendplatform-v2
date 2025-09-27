#!/usr/bin/env python3
"""
Database setup script to create tables and insert test users.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import models
from models.base import Base
from models.user import User
from models.client import Client
from models.role import Role
from models.user_role import user_role

# Database connection
DATABASE_URL = "postgresql://spend_admin:admin123@localhost/spendplatform"

def create_database_and_tables():
    """Create database and tables."""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Database tables created successfully")
        
        return engine
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Database 'spendplatform' exists")
        print("3. User 'spend_admin' has access")
        return None

def insert_test_data(engine):
    """Insert test clients, roles, and users."""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create test client
        client = Client(name="Test Company")
        session.add(client)
        session.flush()  # Get the ID
        print(f"✅ Created client: {client.name} (ID: {client.id})")
        
        # Create roles
        roles_data = [
            {"name": "superadmin", "permissions": {"all": True}},
            {"name": "client_admin", "permissions": {"client_admin": True}},
            {"name": "user", "permissions": {"user": True}}
        ]
        
        role_objects = {}
        for role_data in roles_data:
            role = Role(name=role_data["name"], permissions=role_data["permissions"])
            session.add(role)
            session.flush()
            role_objects[role_data["name"]] = role
            print(f"✅ Created role: {role.name} (ID: {role.id})")
        
        # Create test users
        users_data = [
            {"username": "superadmin", "email": "superadmin@test.com", "password": "superadminpw", "role": "superadmin"},
            {"username": "clientadmin", "email": "clientadmin@test.com", "password": "clientadminpw", "role": "client_admin"},
            {"username": "user", "email": "user@test.com", "password": "userpw", "role": "user"}
        ]
        
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                client_id=client.id
            )
            user.set_password(user_data["password"])
            session.add(user)
            session.flush()
            
            # Assign role
            role = role_objects[user_data["role"]]
            user.roles.append(role)
            
            print(f"✅ Created user: {user.username} with role {role.name} (ID: {user.id})")
        
        session.commit()
        print("\n🎉 All test data inserted successfully!")
        
        # Display summary
        print("\n📋 Test Users Created:")
        print("Username      | Password      | Role         | Email")
        print("-" * 60)
        for user_data in users_data:
            print(f"{user_data['username']:<12} | {user_data['password']:<12} | {user_data['role']:<12} | {user_data['email']}")
        
        return True
        
    except IntegrityError as e:
        session.rollback()
        print(f"❌ Data already exists or integrity error: {e}")
        return False
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting test data: {e}")
        return False
    finally:
        session.close()

def main():
    print("🚀 Setting up PostgreSQL database with test users...")
    print(f"📍 Database URL: {DATABASE_URL}")
    print("-" * 60)
    
    # Create database and tables
    engine = create_database_and_tables()
    if not engine:
        return False
    
    # Insert test data
    success = insert_test_data(engine)
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("\nYou can now:")
        print("1. Test login at: http://127.0.0.1:8000/docs")
        print("2. Use the frontend login test component")
        print("3. Connect to database with: psql postgresql://spend_admin:admin123@localhost/spendplatform")
    else:
        print("\n❌ Database setup failed!")
    
    return success

if __name__ == "__main__":
    main()