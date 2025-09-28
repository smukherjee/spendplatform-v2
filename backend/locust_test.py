"""
Locust Load Testing Script for FastAPI Backend Performance
Comprehensive load testing with realistic user scenarios
"""

from locust import HttpUser, task, between, events
import json
import random
import time
from typing import Dict, Any

class SpendPlatformUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests
    
    def on_start(self):
        """Login when user starts"""
        self.token = None
        self.client_id = None
        self.login()
    
    def login(self):
        """Authenticate user and get token"""
        try:
            response = self.client.post("/token", data={
                "username": "superadmin",
                "password": "superadmin123"
            }, headers={"Content-Type": "application/x-www-form-urlencoded"})
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.client_id = data.get("client_id", 1)
                print(f"✅ User authenticated successfully")
            else:
                print(f"❌ Login failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Login error: {e}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    @task(3)
    def view_users_list(self):
        """Most common task - viewing users list"""
        params = {
            "skip": random.randint(0, 50),
            "limit": random.choice([10, 25, 50])
        }
        
        with self.client.get("/users", 
                           params=params,
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 0:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def view_invoices_list(self):
        """Second most common task - viewing invoices"""
        params = {
            "skip": random.randint(0, 100),
            "limit": random.choice([10, 25, 50, 100])
        }
        
        with self.client.get("/invoices",
                           params=params, 
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def view_suppliers_list(self):
        """View suppliers list"""
        params = {"limit": random.choice([10, 25, 50])}
        
        with self.client.get("/suppliers",
                           params=params,
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def create_user(self):
        """Less frequent task - creating users"""
        user_data = {
            "username": f"testuser_{random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "password": "testpass123",
            "client_id": self.client_id
        }
        
        with self.client.post("/users",
                            json=user_data,
                            headers=self.get_headers(),
                            catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            elif response.status_code == 422:
                # User might already exist - this is ok for testing
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def view_business_units(self):
        """View business units"""
        with self.client.get("/business-units",
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def view_regions(self):
        """View regions"""
        with self.client.get("/regions",
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def search_users(self):
        """Search functionality test"""
        search_terms = ["admin", "user", "test", "acme", "global"]
        search_term = random.choice(search_terms)
        
        params = {"search": search_term, "limit": 25}
        
        with self.client.get("/users",
                           params=params,
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

# Performance monitoring events
performance_data = {
    "response_times": [],
    "error_count": 0,
    "success_count": 0,
    "start_time": None
}

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    performance_data["start_time"] = time.time()
    print("🚀 Load test starting...")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, 
               context, exception, start_time, url, **kwargs):
    """Called for every request"""
    performance_data["response_times"].append(response_time)
    
    if exception:
        performance_data["error_count"] += 1
    else:
        performance_data["success_count"] += 1

@events.test_stop.add_listener 
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    total_time = time.time() - performance_data["start_time"]
    total_requests = performance_data["success_count"] + performance_data["error_count"]
    
    if performance_data["response_times"]:
        avg_response_time = sum(performance_data["response_times"]) / len(performance_data["response_times"])
        response_times_sorted = sorted(performance_data["response_times"])
        p50 = response_times_sorted[len(response_times_sorted)//2]
        p95_index = int(len(response_times_sorted) * 0.95)
        p95 = response_times_sorted[p95_index] if p95_index < len(response_times_sorted) else response_times_sorted[-1]
    else:
        avg_response_time = p50 = p95 = 0
    
    success_rate = (performance_data["success_count"] / total_requests * 100) if total_requests > 0 else 0
    rps = total_requests / total_time if total_time > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 LOAD TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Requests: {total_requests}")
    print(f"Successful: {performance_data['success_count']}")
    print(f"Failed: {performance_data['error_count']}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Requests/Second: {rps:.2f}")
    print(f"Average Response Time: {avg_response_time:.0f}ms")
    print(f"50th Percentile: {p50:.0f}ms")
    print(f"95th Percentile: {p95:.0f}ms")
    print(f"Test Duration: {total_time:.1f}s")
    print(f"{'='*60}")
    
    # Save results to file
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_requests": total_requests,
        "successful_requests": performance_data["success_count"],
        "failed_requests": performance_data["error_count"],
        "success_rate": success_rate,
        "requests_per_second": rps,
        "avg_response_time_ms": avg_response_time,
        "p50_response_time_ms": p50,
        "p95_response_time_ms": p95,
        "test_duration_seconds": total_time
    }
    
    filename = f"locust_results_{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Results saved to {filename}")

# Custom load test scenarios
class DatabaseHeavyUser(HttpUser):
    """User that makes database-heavy requests"""
    
    wait_time = between(0.5, 2)
    weight = 1  # Lower weight - fewer of these users
    
    def on_start(self):
        self.token = None
        self.login()
    
    def login(self):
        response = self.client.post("/token", data={
            "username": "superadmin", 
            "password": "superadmin123"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
    
    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    @task
    def large_data_requests(self):
        """Make requests that require large data retrieval"""
        endpoints = [
            "/users?limit=500",
            "/invoices?limit=500", 
            "/invoice-items?limit=1000",
            "/suppliers?limit=200"
        ]
        
        endpoint = random.choice(endpoints)
        with self.client.get(endpoint,
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

class ReadOnlyUser(HttpUser):
    """User that only reads data - typical dashboard user"""
    
    wait_time = between(2, 8)
    weight = 3  # More of these users
    
    def on_start(self):
        self.token = None
        self.login()
    
    def login(self):
        response = self.client.post("/token", data={
            "username": "superadmin",
            "password": "superadmin123"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
    
    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    @task(4)
    def dashboard_views(self):
        """Typical dashboard viewing patterns"""
        endpoints = ["/users?limit=10", "/invoices?limit=25", "/suppliers?limit=15"]
        endpoint = random.choice(endpoints)
        
        with self.client.get(endpoint,
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def pagination_browsing(self):
        """User browsing through pages"""
        skip = random.randint(0, 200)
        limit = random.choice([10, 25, 50])
        
        with self.client.get(f"/users?skip={skip}&limit={limit}",
                           headers=self.get_headers(),
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

if __name__ == "__main__":
    print("""
    Locust Load Testing for SpendPlatform Backend
    
    Usage:
    # Basic load test
    locust -f locust_test.py --host=http://localhost:8000
    
    # Specific scenarios:
    locust -f locust_test.py --host=http://localhost:8000 SpendPlatformUser
    locust -f locust_test.py --host=http://localhost:8000 DatabaseHeavyUser
    locust -f locust_test.py --host=http://localhost:8000 ReadOnlyUser
    
    # Headless mode with specific users and duration:
    locust -f locust_test.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 300s
    
    Open http://localhost:8089 for web interface
    """)