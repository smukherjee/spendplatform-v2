#!/usr/bin/env python3
"""
Test script to create a test user and validate authentication
"""
import sys
import os

# Add the backend/src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.client import Client
from models.role import Role
from werkzeug.security import generate_password_hash

def create_test_user():
    """Create a test user for authentication testing"""
    db: Session = SessionLocal()
    
    try:
        # Check if test client exists
        test_client = db.query(Client).filter(Client.name == "Test Client").first()
        if not test_client:
            test_client = Client(
                name="Test Client",
                contact_email="test@client.com",
                is_active=True
            )
            db.add(test_client)
            db.commit()
            db.refresh(test_client)
            print(f"Created test client: {test_client.name} (ID: {test_client.id})")
        
        # Check if superadmin role exists
        superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
        if not superadmin_role:
            superadmin_role = Role(
                name="superadmin",
                description="Super Administrator with full system access"
            )
            db.add(superadmin_role)
            db.commit()
            db.refresh(superadmin_role)
            print(f"Created superadmin role: {superadmin_role.name}")
        
        # Check if test user exists
        test_user = db.query(User).filter(User.username == "testuser").first()
        if not test_user:
            test_user = User(
                username="testuser",
                email="testuser@example.com",
                password_hash=generate_password_hash("testpass123"),
                first_name="Test",
                last_name="User",
                client_id=test_client.id,
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"Created test user: {test_user.username} (ID: {test_user.id})")
            
            # Add superadmin role to test user
            test_user.roles.append(superadmin_role)
            db.commit()
            print(f"Added superadmin role to test user")
        else:
            print(f"Test user already exists: {test_user.username}")
        
        print("\nTest credentials:")
        print(f"Username: testuser")
        print(f"Password: testpass123")
        print(f"Client ID: {test_client.id}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()