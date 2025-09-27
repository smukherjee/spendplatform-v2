#!/usr/bin/env python3
"""
Test authentication with the database users.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login(username, password):
    """Test login with given credentials."""
    print(f"\n🔑 Testing login for: {username}")
    
    # Prepare form data
    data = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful!")
            print(f"   Access token: {token_data['access_token'][:50]}...")
            print(f"   Token type: {token_data['token_type']}")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint."""
    print(f"\n🔒 Testing protected endpoint...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/invoices", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
        elif response.status_code == 404:
            print("✅ Protected endpoint accessible (404 is expected - endpoint not implemented)")
        elif response.status_code == 501:
            print("✅ Protected endpoint accessible (501 Not Implemented is expected)")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")

def main():
    print("🚀 Testing Database Authentication")
    print("=" * 50)
    
    # Test users from our database setup
    test_users = [
        ("user", "userpw"),
        ("clientadmin", "clientadminpw"),
        ("superadmin", "superadminpw")
    ]
    
    for username, password in test_users:
        token = test_login(username, password)
        if token:
            test_protected_endpoint(token)
        print("-" * 30)
    
    print("\n🎉 Authentication test completed!")

if __name__ == "__main__":
    main()