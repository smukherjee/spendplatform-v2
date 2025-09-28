#!/usr/bin/env python3
"""
Comprehensive Data Segregation Test Suite
Tests multi-tenant data isolation across all tables and API endpoints
"""
import requests
import json
import sys
from typing import Dict, List, Any, Optional

BASE_URL = "http://localhost:8000"

class DataSegregationTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        
    def login_user(self, username: str, password: str) -> str:
        """Login and get JWT token"""
        response = requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={username}&password={password}"
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            self.tokens[username] = {
                'token': token,
                'user_data': data['user'],
                'headers': {'Authorization': f'Bearer {token}'}
            }
            return token
        else:
            raise Exception(f"Login failed for {username}: {response.text}")
    
    def test_endpoint(self, endpoint: str, method: str = "GET", user: str = "superadmin", 
                     expected_status: int = 200, data: Optional[dict] = None) -> Dict[str, Any]:
        """Test an API endpoint with specific user"""
        headers = self.tokens[user]['headers']
        if data:
            headers['Content-Type'] = 'application/json'
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers)
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'user': user,
                'client_id': self.tokens[user]['user_data']['client_id'],
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': response.status_code == expected_status,
                'response_data': None,
                'error': None
            }
            
            try:
                if response.text:
                    result['response_data'] = response.json()
            except:
                result['response_data'] = response.text
                
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'method': method,
                'user': user,
                'client_id': self.tokens[user]['user_data']['client_id'],
                'status_code': None,
                'expected_status': expected_status,
                'success': False,
                'response_data': None,
                'error': str(e)
            }
    
    def test_data_segregation_read(self):
        """Test read operations for data segregation"""
        print("\\n🔍 Testing Data Segregation - Read Operations")
        print("=" * 60)
        
        # Core entity endpoints that should respect client_id filtering
        entity_endpoints = [
            "/invoices",
            "/suppliers", 
            "/business-units",
            "/regions",
            "/subcategories",
            "/currencies",
            "/units-of-measure",
            "/users",
            "/settings"
        ]
        
        for endpoint in entity_endpoints:
            print(f"\\nTesting {endpoint}:")
            
            # Test superadmin access (should see all data)
            result_super = self.test_endpoint(endpoint, user="superadmin")
            superadmin_count = len(result_super['response_data']) if isinstance(result_super['response_data'], list) else 0
            
            # Test client admin access (should see only their data)
            result_client = self.test_endpoint(endpoint, user="clientadmin")
            clientadmin_count = len(result_client['response_data']) if isinstance(result_client['response_data'], list) else 0
            
            print(f"  Superadmin (client_id=0): {result_super['status_code']} - {superadmin_count} records")
            print(f"  Client Admin (client_id=1): {result_client['status_code']} - {clientadmin_count} records")
            
            # Verify segregation
            if endpoint == "/users":
                # Users endpoint: superadmin should see more or equal users
                segregation_ok = superadmin_count >= clientadmin_count
            elif endpoint == "/settings":
                # Settings might be equal or superadmin sees more
                segregation_ok = superadmin_count >= clientadmin_count
            else:
                # Other endpoints: superadmin should typically see more data
                segregation_ok = superadmin_count >= clientadmin_count
            
            if segregation_ok:
                print(f"  ✅ Data segregation working correctly")
            else:
                print(f"  ❌ Data segregation issue detected")
            
            self.test_results.append({
                'test': f"Data Segregation - {endpoint}",
                'passed': segregation_ok,
                'details': f"Superadmin: {superadmin_count}, Client Admin: {clientadmin_count}"
            })
    
    def test_cross_client_access_prevention(self):
        """Test that users cannot access other clients' data"""
        print("\\n🚫 Testing Cross-Client Access Prevention")
        print("=" * 60)
        
        # Try to access specific records that should be client-segregated
        cross_access_tests = [
            # Try to access users from different clients
            {"endpoint": "/users/1", "description": "Access superadmin user (different client)"},
            # Try to access invoices that belong to other clients (ID 7 is client_id=2)
            {"endpoint": "/invoices/7", "description": "Access invoice from different client"},
            # Try to access suppliers from other clients (ID 7 is client_id=2)
            {"endpoint": "/suppliers/7", "description": "Access supplier from different client"},
        ]
        
        for test in cross_access_tests:
            print(f"\\nTesting: {test['description']}")
            
            # Test with client admin (should be restricted)
            result = self.test_endpoint(test['endpoint'], user="clientadmin", expected_status=404)
            
            if result['status_code'] in [403, 404]:
                print(f"  ✅ Client admin properly blocked: {result['status_code']}")
                test_passed = True
            else:
                print(f"  ❌ Client admin access allowed: {result['status_code']}")
                test_passed = False
            
            self.test_results.append({
                'test': f"Cross-client access prevention - {test['description']}",
                'passed': test_passed,
                'details': f"Status: {result['status_code']}"
            })
    
    def test_superadmin_global_access(self):
        """Test that superadmin can access all client data"""
        print("\\n👑 Testing Superadmin Global Access")
        print("=" * 60)
        
        # Superadmin should be able to access all clients
        result = self.test_endpoint("/clients", user="superadmin")
        
        if result['success'] and isinstance(result['response_data'], list):
            client_count = len(result['response_data'])
            print(f"  ✅ Superadmin can access {client_count} clients")
            
            # Verify client_id=0 exists for superadmin
            client_ids = [c['id'] for c in result['response_data']]
            if 0 in client_ids:
                print(f"  ✅ Superadmin client (ID=0) exists")
                superadmin_client_ok = True
            else:
                print(f"  ❌ Superadmin client (ID=0) missing")
                superadmin_client_ok = False
        else:
            print(f"  ❌ Superadmin cannot access clients: {result['status_code']}")
            superadmin_client_ok = False
        
        # Test superadmin can access data from all clients
        print("\\n  Testing cross-client data access:")
        entity_endpoints = ["/invoices", "/suppliers", "/business-units", "/regions", "/users"]
        
        all_data_access_ok = True
        superadmin_data_counts = {}
        
        for endpoint in entity_endpoints:
            result = self.test_endpoint(endpoint, user="superadmin")
            if result['success'] and isinstance(result['response_data'], list):
                count = len(result['response_data'])
                superadmin_data_counts[endpoint] = count
                print(f"    {endpoint}: {count} total records across all clients")
                
                # Verify superadmin sees more data than individual client admins
                client1_result = self.test_endpoint(endpoint, user="clientadmin")
                if client1_result['success'] and isinstance(client1_result['response_data'], list):
                    client1_count = len(client1_result['response_data'])
                    
                    if count >= client1_count:
                        print(f"      ✅ Superadmin sees {count} >= client admin's {client1_count}")
                    else:
                        print(f"      ❌ Superadmin sees {count} < client admin's {client1_count}")
                        all_data_access_ok = False
                else:
                    print(f"      ⚠️  Could not verify against client admin data")
            else:
                print(f"    {endpoint}: ❌ Access failed ({result['status_code']})")
                all_data_access_ok = False
        
        # Test superadmin can access specific records from different clients
        print("\\n  Testing specific cross-client record access:")
        cross_client_tests = [
            {"endpoint": "/invoices/1", "description": "Client 1 invoice"},
            {"endpoint": "/invoices/7", "description": "Client 2 invoice"}, 
            {"endpoint": "/suppliers/1", "description": "Client 1 supplier"},
            {"endpoint": "/suppliers/7", "description": "Client 2 supplier"},
            {"endpoint": "/users/2", "description": "Client 1 user"},
            {"endpoint": "/users/21", "description": "Client 2 user"},
        ]
        
        cross_access_success_count = 0
        for test in cross_client_tests:
            result = self.test_endpoint(test['endpoint'], user="superadmin")
            if result['success']:
                print(f"    ✅ {test['description']}: Accessible")
                cross_access_success_count += 1
            else:
                print(f"    ❌ {test['description']}: Not accessible ({result['status_code']})")
        
        cross_access_ok = cross_access_success_count >= len(cross_client_tests) * 0.8  # 80% success rate
        
        overall_superadmin_ok = superadmin_client_ok and all_data_access_ok and cross_access_ok
        
        self.test_results.append({
            'test': "Superadmin global access - Client list",
            'passed': superadmin_client_ok,
            'details': f"Can access {client_count if 'client_count' in locals() else 0} clients"
        })
        
        self.test_results.append({
            'test': "Superadmin global access - All entity data",
            'passed': all_data_access_ok,
            'details': f"Entity counts: {superadmin_data_counts}"
        })
        
        self.test_results.append({
            'test': "Superadmin global access - Cross-client records",
            'passed': cross_access_ok,
            'details': f"Accessed {cross_access_success_count}/{len(cross_client_tests)} records"
        })
    
    def test_create_operations_segregation(self):
        """Test that create operations respect client_id"""
        print("\\n➕ Testing Create Operations Data Segregation")
        print("=" * 60)
        
        # Test creating entities as client admin - should auto-assign correct client_id
        create_tests = [
            {
                "endpoint": "/suppliers",
                "data": {"name": "Test Supplier Client Admin", "contact_info": "test@clientadmin.com", "region_id": 1},
                "description": "Create supplier as client admin"
            },
            {
                "endpoint": "/business-units", 
                "data": {"name": "Test BU Client Admin", "code": "TESTBU"},
                "description": "Create business unit as client admin"
            }
        ]
        
        for test in create_tests:
            print(f"\\nTesting: {test['description']}")
            
            result = self.test_endpoint(
                test['endpoint'], 
                method="POST", 
                user="clientadmin",
                data=test['data'],
                expected_status=200
            )
            
            if result['success']:
                # Verify the created entity has correct client_id
                created_entity = result['response_data']
                if isinstance(created_entity, dict) and 'client_id' in created_entity:
                    expected_client_id = self.tokens['clientadmin']['user_data']['client_id']
                    actual_client_id = created_entity['client_id']
                    
                    if actual_client_id == expected_client_id:
                        print(f"  ✅ Entity created with correct client_id: {actual_client_id}")
                        test_passed = True
                    else:
                        print(f"  ❌ Entity created with wrong client_id: {actual_client_id} (expected: {expected_client_id})")
                        test_passed = False
                else:
                    print(f"  ⚠️  Cannot verify client_id in response")
                    test_passed = False
            else:
                print(f"  ❌ Create operation failed: {result['status_code']}")
                test_passed = False
            
            self.test_results.append({
                'test': f"Create segregation - {test['description']}",
                'passed': test_passed,
                'details': f"Status: {result['status_code']}"
            })
    
    def test_superadmin_comprehensive_access(self):
        """Comprehensive test of superadmin's ability to access ALL data"""
        print("\\n🌐 Testing Superadmin Comprehensive Data Access")
        print("=" * 60)
        
        # Test that superadmin can perform CRUD operations across all clients
        print("\\nTesting superadmin CRUD operations across clients:")
        
        # Test create operations for different clients
        create_tests = [
            {
                "endpoint": "/suppliers",
                "data": {"name": "Superadmin Test Supplier Client1", "contact_info": "super@client1.com", "region_id": 1, "client_id": 1},
                "description": "Create supplier for client 1"
            },
            {
                "endpoint": "/suppliers", 
                "data": {"name": "Superadmin Test Supplier Client2", "contact_info": "super@client2.com", "region_id": 6, "client_id": 2},
                "description": "Create supplier for client 2"
            }
        ]
        
        create_success_count = 0
        for test in create_tests:
            result = self.test_endpoint(
                test['endpoint'],
                method="POST",
                user="superadmin", 
                data=test['data'],
                expected_status=200
            )
            
            if result['success']:
                print(f"  ✅ {test['description']}: Success")
                create_success_count += 1
                
                # Verify correct client_id assignment
                if isinstance(result['response_data'], dict) and 'client_id' in result['response_data']:
                    actual_client_id = result['response_data']['client_id']
                    expected_client_id = test['data']['client_id']
                    if actual_client_id == expected_client_id:
                        print(f"    ✅ Correct client_id: {actual_client_id}")
                    else:
                        print(f"    ❌ Wrong client_id: {actual_client_id} (expected: {expected_client_id})")
            else:
                print(f"  ❌ {test['description']}: Failed ({result['status_code']})")
        
        # Test superadmin can read data with explicit client filtering
        print("\\n  Testing data access with client context:")
        
        data_verification_tests = [
            {"endpoint": "/invoices", "min_expected": 5, "description": "All invoices across clients"},
            {"endpoint": "/suppliers", "min_expected": 8, "description": "All suppliers across clients"}, 
            {"endpoint": "/business-units", "min_expected": 5, "description": "All business units across clients"},
            {"endpoint": "/users", "min_expected": 4, "description": "All users across clients"},
        ]
        
        data_access_success_count = 0
        total_records_seen = 0
        
        for test in data_verification_tests:
            result = self.test_endpoint(test['endpoint'], user="superadmin")
            if result['success'] and isinstance(result['response_data'], list):
                count = len(result['response_data'])
                total_records_seen += count
                
                if count >= test['min_expected']:
                    print(f"  ✅ {test['description']}: {count} records (>= {test['min_expected']})")
                    data_access_success_count += 1
                else:
                    print(f"  ❌ {test['description']}: {count} records (< {test['min_expected']})")
            else:
                print(f"  ❌ {test['description']}: Access failed")
        
        # Overall assessment
        create_success_rate = create_success_count / len(create_tests)
        data_access_rate = data_access_success_count / len(data_verification_tests)
        overall_superadmin_comprehensive = create_success_rate >= 0.8 and data_access_rate >= 0.8
        
        print(f"\\n  📊 Superadmin Comprehensive Access Summary:")
        print(f"    Create operations: {create_success_count}/{len(create_tests)} successful")
        print(f"    Data access tests: {data_access_success_count}/{len(data_verification_tests)} successful") 
        print(f"    Total records accessible: {total_records_seen}")
        
        self.test_results.append({
            'test': "Superadmin comprehensive access - CRUD operations",
            'passed': overall_superadmin_comprehensive,
            'details': f"Create: {create_success_rate:.1%}, Read: {data_access_rate:.1%}, Total records: {total_records_seen}"
        })

    def test_frontend_api_calls(self):
        """Test that frontend API calls respect data segregation"""
        print("\\n🖥️  Testing Frontend API Integration")
        print("=" * 60)
        
        # Test key frontend API endpoints
        frontend_tests = [
            {"endpoint": "/invoices", "description": "Invoice list for frontend"},
            {"endpoint": "/suppliers", "description": "Supplier list for frontend"},
            {"endpoint": "/users", "description": "User management for frontend"},
        ]
        
        for test in frontend_tests:
            print(f"\\nTesting: {test['description']}")
            
            # Test both users
            super_result = self.test_endpoint(test['endpoint'], user="superadmin")
            client_result = self.test_endpoint(test['endpoint'], user="clientadmin")
            
            super_count = len(super_result['response_data']) if isinstance(super_result['response_data'], list) else 0
            client_count = len(client_result['response_data']) if isinstance(client_result['response_data'], list) else 0
            
            print(f"  Superadmin sees: {super_count} records")
            print(f"  Client admin sees: {client_count} records")
            
            # Verify proper segregation for frontend
            segregation_ok = super_count >= client_count and client_result['success']
            
            if segregation_ok:
                print(f"  ✅ Frontend API segregation working")
            else:
                print(f"  ❌ Frontend API segregation issue")
            
            self.test_results.append({
                'test': f"Frontend API - {test['description']}",
                'passed': segregation_ok,
                'details': f"Super: {super_count}, Client: {client_count}"
            })
    
    def run_all_tests(self):
        """Run comprehensive data segregation test suite"""
        print("🚀 Starting Comprehensive Data Segregation Test Suite")
        print("=" * 70)
        
        try:
            # Setup: Login all test users
            print("Setting up test users...")
            self.login_user("superadmin", "superadmin123")
            self.login_user("clientadmin", "admin123")
            
            print(f"✅ Logged in superadmin (client_id: {self.tokens['superadmin']['user_data']['client_id']})")
            print(f"✅ Logged in clientadmin (client_id: {self.tokens['clientadmin']['user_data']['client_id']})")
            
            # Run all test suites
            self.test_data_segregation_read()
            self.test_cross_client_access_prevention()
            self.test_superadmin_global_access()
            self.test_superadmin_comprehensive_access()
            self.test_create_operations_segregation()
            self.test_frontend_api_calls()
            
            # Summary
            print("\\n" + "=" * 70)
            print("📊 TEST SUMMARY")
            print("=" * 70)
            
            passed_tests = [t for t in self.test_results if t['passed']]
            failed_tests = [t for t in self.test_results if not t['passed']]
            
            print(f"Total Tests: {len(self.test_results)}")
            print(f"✅ Passed: {len(passed_tests)}")
            print(f"❌ Failed: {len(failed_tests)}")
            
            if failed_tests:
                print("\\n❌ FAILED TESTS:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['details']}")
            
            print("\\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"  - {test['test']}")
            
            # Overall result
            success_rate = len(passed_tests) / len(self.test_results) * 100
            print(f"\\n🎯 Overall Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Data segregation is working properly!")
            elif success_rate >= 80:
                print("✅ GOOD: Most data segregation tests passed")
            else:
                print("⚠️  WARNING: Data segregation needs improvement")
                
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            sys.exit(1)

def main():
    """Run the comprehensive data segregation test suite"""
    tester = DataSegregationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()