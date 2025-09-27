"""
Debug authentication issue
"""
import sys
sys.path.append('/Users/sujoymukherjee/code/spendplatform-v2/backend/src')

from database import SessionLocal
from models.user import User
from utils import create_access_token
import requests

def test_auth_flow():
    # Test database user
    db = SessionLocal()
    user = db.query(User).filter(User.username == 'user').first()
    
    if not user:
        print("❌ User not found in database")
        return
    
    print(f"✅ User found: {user.username}")
    
    # Test password verification
    if user.verify_password('user123'):
        print("✅ Password verification works")
    else:
        print("❌ Password verification failed")
        return
    
    # Test token creation
    try:
        role_mapping = {
            "superadmin": "superadmin",
            "clientadmin": "client_admin", 
            "user": "user"
        }
        user_role = role_mapping.get(str(user.username), "user")
        
        token_data = {
            "sub": user.username,
            "role": user_role,
            "client_id": user.client_id,
            "user_id": user.id
        }
        access_token = create_access_token(token_data)
        print(f"✅ Token created successfully: {access_token[:50]}...")
        
        # Test API call
        print("\n--- Testing API endpoint ---")
        response = requests.post('http://localhost:8000/token', 
                               data={'username': 'user', 'password': 'user123'})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Token creation failed: {e}")
    
    db.close()

if __name__ == "__main__":
    test_auth_flow()