"""
Comparative Performance Testing Script
Tests both sync and async versions and compares results
"""

import asyncio
import httpx
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime

class ComparativePerformanceTester:
    """Compare sync vs async API performance"""
    
    def __init__(self):
        self.sync_base_url = "http://localhost:8000"
        self.async_base_url = "http://localhost:8001"
        self.auth_token = None
    
    async def authenticate(self, base_url: str):
        """Get authentication token"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/token",
                    data={
                        "username": "superadmin",
                        "password": "superadmin123"
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if response.status_code == 200:
                    return response.json().get("access_token")
        except Exception as e:
            print(f"Authentication failed for {base_url}: {e}")
            return None
    
    def get_headers(self, token: str = None):
        """Get headers with optional authentication"""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    async def test_single_request(self, base_url: str, endpoint: str, token: str = None):
        """Test a single request and return timing data"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=self.get_headers(token)
                )
                end_time = time.time()
                
                return {
                    "response_time": end_time - start_time,
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "response_size": len(response.content),
                    "error": None
                }
        except Exception as e:
            return {
                "response_time": 30.0,
                "status_code": 0,
                "success": False,
                "response_size": 0,
                "error": str(e)
            }
    
    async def test_concurrent_requests(self, base_url: str, endpoint: str, 
                                     concurrent_users: int, requests_per_user: int,
                                     token: str = None):
        """Test concurrent request performance"""
        
        print(f"🧪 Testing {base_url} - {concurrent_users} users, {requests_per_user} requests each")
        
        async def user_session():
            results = []
            for _ in range(requests_per_user):
                result = await self.test_single_request(base_url, endpoint, token)
                results.append(result)
            return results
        
        start_time = time.time()
        tasks = [user_session() for _ in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Flatten results
        all_results = []
        errors = []
        for user_result in user_results:
            if isinstance(user_result, list):
                all_results.extend(user_result)
            else:
                errors.append(str(user_result))
        
        # Calculate metrics
        response_times = [r["response_time"] for r in all_results if isinstance(r, dict)]
        successful_requests = [r for r in all_results if isinstance(r, dict) and r["success"]]
        
        total_time = end_time - start_time
        
        return {
            "base_url": base_url,
            "endpoint": endpoint,
            "concurrent_users": concurrent_users,
            "total_requests": len(all_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(all_results) - len(successful_requests),
            "success_rate": (len(successful_requests) / len(all_results) * 100) if all_results else 0,
            "total_time": total_time,
            "requests_per_second": len(all_results) / total_time if total_time > 0 else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0,
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 2 else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "errors": errors[:5]  # First 5 errors
        }
    
    async def run_comprehensive_comparison(self):
        """Run comprehensive performance comparison"""
        
        print("🔐 Authenticating with both servers...")
        
        # Get auth tokens for both servers
        sync_token = await self.authenticate(self.sync_base_url)
        async_token = await self.authenticate(self.async_base_url)
        
        if not sync_token:
            print("❌ Failed to authenticate with sync server")
            return
        if not async_token:
            print("❌ Failed to authenticate with async server")
            return
        
        print("✅ Authentication successful for both servers")
        
        # Test scenarios
        test_scenarios = [
            {"users": 1, "requests": 10, "name": "Single User"},
            {"users": 5, "requests": 4, "name": "Light Load"},
            {"users": 10, "requests": 3, "name": "Moderate Load"},
            {"users": 25, "requests": 2, "name": "Heavy Load"},
            {"users": 50, "requests": 1, "name": "Stress Test"}
        ]
        
        endpoints_to_test = [
            "/users?limit=25",
            "/users?limit=100"
        ]
        
        all_results = []
        
        for endpoint in endpoints_to_test:
            print(f"\n{'='*60}")
            print(f"🎯 Testing endpoint: {endpoint}")
            print(f"{'='*60}")
            
            for scenario in test_scenarios:
                print(f"\n📊 {scenario['name']} Test ({scenario['users']} users × {scenario['requests']} requests)")
                print("-" * 50)
                
                # Test sync version
                sync_result = await self.test_concurrent_requests(
                    self.sync_base_url, endpoint, 
                    scenario['users'], scenario['requests'], 
                    sync_token
                )
                sync_result['version'] = 'sync'
                sync_result['scenario'] = scenario['name']
                
                # Test async version
                async_result = await self.test_concurrent_requests(
                    self.async_base_url + "/api/v1", endpoint.replace('/users', '/users-async'), 
                    scenario['users'], scenario['requests'], 
                    async_token
                )
                async_result['version'] = 'async'
                async_result['scenario'] = scenario['name']
                
                # Store results
                all_results.extend([sync_result, async_result])
                
                # Print comparison
                self.print_comparison(sync_result, async_result)
                
                # Brief pause between tests
                await asyncio.sleep(1)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_comparison_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to {filename}")
        
        # Generate summary report
        self.generate_summary_report(all_results)
    
    def print_comparison(self, sync_result, async_result):
        """Print comparison between sync and async results"""
        
        print(f"\n🔄 SYNC Version:")
        self.print_metrics(sync_result)
        
        print(f"\n⚡ ASYNC Version:")
        self.print_metrics(async_result)
        
        # Calculate improvements
        response_time_improvement = (
            (sync_result['avg_response_time'] - async_result['avg_response_time']) / 
            sync_result['avg_response_time'] * 100
        ) if sync_result['avg_response_time'] > 0 else 0
        
        throughput_improvement = (
            (async_result['requests_per_second'] - sync_result['requests_per_second']) / 
            sync_result['requests_per_second'] * 100
        ) if sync_result['requests_per_second'] > 0 else 0
        
        success_rate_diff = async_result['success_rate'] - sync_result['success_rate']
        
        print(f"\n📈 IMPROVEMENTS:")
        print(f"  Response Time: {response_time_improvement:+.1f}%")
        print(f"  Throughput: {throughput_improvement:+.1f}%")
        print(f"  Success Rate: {success_rate_diff:+.1f}%")
    
    def print_metrics(self, result):
        """Print formatted metrics for a single result"""
        print(f"  Success Rate: {result['success_rate']:.1f}%")
        print(f"  Requests/sec: {result['requests_per_second']:.2f}")
        print(f"  Avg Response: {result['avg_response_time']*1000:.0f}ms")
        print(f"  P95 Response: {result['p95_response_time']*1000:.0f}ms")
        print(f"  Total Time: {result['total_time']:.2f}s")
        if result['errors']:
            print(f"  Errors: {len(result['errors'])}")
    
    def generate_summary_report(self, all_results):
        """Generate overall summary report"""
        
        print(f"\n{'='*80}")
        print(f"📊 OVERALL PERFORMANCE SUMMARY")
        print(f"{'='*80}")
        
        # Group by scenario
        sync_results = [r for r in all_results if r['version'] == 'sync']
        async_results = [r for r in all_results if r['version'] == 'async']
        
        # Calculate overall averages
        sync_avg_response = statistics.mean([r['avg_response_time'] for r in sync_results])
        async_avg_response = statistics.mean([r['avg_response_time'] for r in async_results])
        
        sync_avg_throughput = statistics.mean([r['requests_per_second'] for r in sync_results])
        async_avg_throughput = statistics.mean([r['requests_per_second'] for r in async_results])
        
        sync_avg_success = statistics.mean([r['success_rate'] for r in sync_results])
        async_avg_success = statistics.mean([r['success_rate'] for r in async_results])
        
        overall_response_improvement = (sync_avg_response - async_avg_response) / sync_avg_response * 100
        overall_throughput_improvement = (async_avg_throughput - sync_avg_throughput) / sync_avg_throughput * 100
        overall_success_improvement = async_avg_success - sync_avg_success
        
        print(f"\n🎯 AVERAGE IMPROVEMENTS ACROSS ALL TESTS:")
        print(f"  Response Time: {overall_response_improvement:+.1f}%")
        print(f"  Throughput: {overall_throughput_improvement:+.1f}%") 
        print(f"  Success Rate: {overall_success_improvement:+.1f}%")
        
        print(f"\n📈 DETAILED AVERAGES:")
        print(f"  Sync Average Response Time: {sync_avg_response*1000:.0f}ms")
        print(f"  Async Average Response Time: {async_avg_response*1000:.0f}ms")
        print(f"  Sync Average Throughput: {sync_avg_throughput:.2f} req/s")
        print(f"  Async Average Throughput: {async_avg_throughput:.2f} req/s")
        
        # Find best improvements
        best_response_improvement = max([
            (r_sync['avg_response_time'] - r_async['avg_response_time']) / r_sync['avg_response_time'] * 100
            for r_sync, r_async in zip(sync_results, async_results)
            if r_sync['avg_response_time'] > 0
        ])
        
        best_throughput_improvement = max([
            (r_async['requests_per_second'] - r_sync['requests_per_second']) / r_sync['requests_per_second'] * 100
            for r_sync, r_async in zip(sync_results, async_results)
            if r_sync['requests_per_second'] > 0
        ])
        
        print(f"\n🚀 BEST CASE IMPROVEMENTS:")
        print(f"  Best Response Time Improvement: {best_response_improvement:.1f}%")
        print(f"  Best Throughput Improvement: {best_throughput_improvement:.1f}%")
        
        print(f"\n{'='*80}")

async def main():
    """Run the comparative performance test"""
    tester = ComparativePerformanceTester()
    await tester.run_comprehensive_comparison()

if __name__ == "__main__":
    print("🚀 Starting Comparative Performance Testing...")
    print("This will test both sync (port 8000) and async (port 8001) versions")
    print("Make sure both servers are running before starting the test.")
    
    input("Press Enter to continue...")
    
    asyncio.run(main())