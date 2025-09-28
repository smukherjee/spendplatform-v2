"""
Comprehensive Performance Testing Suite for FastAPI Backend
Measures before/after metrics for all optimizations
"""

import asyncio
import time
import httpx
import json
import statistics
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    test_name: str
    timestamp: datetime
    response_times: List[float]
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    concurrent_users: int
    total_requests: int
    requests_per_second: float
    cpu_usage_percent: float
    memory_usage_mb: float
    errors: List[str]

class PerformanceTester:
    """Advanced performance testing for FastAPI applications"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_token = None
        self.metrics_history: List[PerformanceMetrics] = []
    
    async def authenticate(self) -> Optional[str]:
        """Get authentication token for protected endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/token",
                    data={
                        "username": "superadmin",
                        "password": "superadmin123"
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if response.status_code == 200:
                    self.session_token = response.json().get("access_token")
                    logger.info("✅ Authentication successful")
                    return self.session_token
                else:
                    logger.error(f"❌ Authentication failed: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return None
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        return headers
    
    async def single_request_test(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Test single request performance"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                
                if method.upper() == "GET":
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.get_headers()
                    )
                elif method.upper() == "POST":
                    response = await client.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        headers=self.get_headers()
                    )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "response_size": len(response.content),
                    "error": None
                }
                
        except Exception as e:
            return {
                "response_time": 30.0,  # Timeout
                "status_code": 0,
                "success": False,
                "response_size": 0,
                "error": str(e)
            }
    
    async def concurrent_request_test(
        self, 
        endpoint: str, 
        concurrent_users: int = 10, 
        requests_per_user: int = 10,
        method: str = "GET",
        data: Dict = None
    ) -> PerformanceMetrics:
        """Test concurrent request handling"""
        
        logger.info(f"🚀 Starting concurrent test: {concurrent_users} users, {requests_per_user} requests each")
        
        # Monitor system resources
        process = psutil.Process()
        cpu_before = process.cpu_percent()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        all_results = []
        errors = []
        
        async def user_session():
            """Simulate a user making multiple requests"""
            user_results = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for _ in range(requests_per_user):
                    result = await self.single_request_test(endpoint, method, data)
                    user_results.append(result)
                    if result["error"]:
                        errors.append(result["error"])
            return user_results
        
        # Run concurrent user sessions
        tasks = [user_session() for _ in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        for user_result in user_results:
            if isinstance(user_result, list):
                all_results.extend(user_result)
            else:
                errors.append(str(user_result))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        response_times = [r["response_time"] for r in all_results if isinstance(r, dict)]
        successful_requests = [r for r in all_results if isinstance(r, dict) and r["success"]]
        
        cpu_after = process.cpu_percent()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        metrics = PerformanceMetrics(
            test_name=f"Concurrent_{endpoint.replace('/', '_')}",
            timestamp=datetime.now(),
            response_times=response_times,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            p50_response_time=statistics.median(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0,
            p99_response_time=statistics.quantiles(response_times, n=100)[98] if len(response_times) > 2 else 0,
            success_rate=(len(successful_requests) / len(all_results)) * 100 if all_results else 0,
            concurrent_users=concurrent_users,
            total_requests=len(all_results),
            requests_per_second=len(all_results) / total_time if total_time > 0 else 0,
            cpu_usage_percent=(cpu_after - cpu_before),
            memory_usage_mb=(memory_after - memory_before),
            errors=errors[:10]  # Keep first 10 errors
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    async def database_query_performance_test(self) -> PerformanceMetrics:
        """Test database query performance patterns"""
        
        logger.info("🗄️ Testing database query performance...")
        
        # Test endpoints that hit database
        endpoints_to_test = [
            "/users",
            "/invoices", 
            "/suppliers",
            "/business-units",
            "/regions"
        ]
        
        all_results = []
        errors = []
        start_time = time.time()
        
        for endpoint in endpoints_to_test:
            # Test with different pagination sizes
            for limit in [10, 50, 100]:
                result = await self.single_request_test(f"{endpoint}?limit={limit}")
                all_results.append(result)
                if result["error"]:
                    errors.append(f"{endpoint}?limit={limit}: {result['error']}")
        
        end_time = time.time()
        
        response_times = [r["response_time"] for r in all_results]
        successful_requests = [r for r in all_results if r["success"]]
        
        metrics = PerformanceMetrics(
            test_name="Database_Query_Performance",
            timestamp=datetime.now(),
            response_times=response_times,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            p50_response_time=statistics.median(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0,
            p99_response_time=statistics.quantiles(response_times, n=100)[98] if len(response_times) > 2 else 0,
            success_rate=(len(successful_requests) / len(all_results)) * 100 if all_results else 0,
            concurrent_users=1,
            total_requests=len(all_results),
            requests_per_second=len(all_results) / (end_time - start_time),
            cpu_usage_percent=0,
            memory_usage_mb=0,
            errors=errors
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    async def memory_usage_test(self) -> PerformanceMetrics:
        """Test memory usage patterns with large datasets"""
        
        logger.info("💾 Testing memory usage patterns...")
        
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Test endpoints that might load large datasets
        large_data_endpoints = [
            "/users?limit=1000",
            "/invoices?limit=1000",
            "/invoice-items?limit=1000"
        ]
        
        all_results = []
        errors = []
        max_memory_usage = memory_before
        
        for endpoint in large_data_endpoints:
            result = await self.single_request_test(endpoint)
            all_results.append(result)
            
            current_memory = process.memory_info().rss / 1024 / 1024
            max_memory_usage = max(max_memory_usage, current_memory)
            
            if result["error"]:
                errors.append(f"{endpoint}: {result['error']}")
        
        memory_after = process.memory_info().rss / 1024 / 1024
        
        response_times = [r["response_time"] for r in all_results]
        successful_requests = [r for r in all_results if r["success"]]
        
        metrics = PerformanceMetrics(
            test_name="Memory_Usage_Test",
            timestamp=datetime.now(),
            response_times=response_times,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            p50_response_time=statistics.median(response_times) if response_times else 0,
            p95_response_time=0,
            p99_response_time=0,
            success_rate=(len(successful_requests) / len(all_results)) * 100 if all_results else 0,
            concurrent_users=1,
            total_requests=len(all_results),
            requests_per_second=0,
            cpu_usage_percent=0,
            memory_usage_mb=max_memory_usage - memory_before,
            errors=errors
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def print_metrics(self, metrics: PerformanceMetrics):
        """Print formatted metrics"""
        print(f"\n{'='*60}")
        print(f"📊 TEST RESULTS: {metrics.test_name}")
        print(f"{'='*60}")
        print(f"Timestamp: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Concurrent Users: {metrics.concurrent_users}")
        print(f"Success Rate: {metrics.success_rate:.1f}%")
        print(f"Requests/Second: {metrics.requests_per_second:.2f}")
        print(f"\n⏱️  Response Times:")
        print(f"  Average: {metrics.avg_response_time*1000:.0f}ms")
        print(f"  Median (P50): {metrics.p50_response_time*1000:.0f}ms")
        print(f"  P95: {metrics.p95_response_time*1000:.0f}ms")
        print(f"  P99: {metrics.p99_response_time*1000:.0f}ms")
        print(f"\n🖥️  Resource Usage:")
        print(f"  CPU Change: {metrics.cpu_usage_percent:.1f}%")
        print(f"  Memory Change: {metrics.memory_usage_mb:.1f}MB")
        
        if metrics.errors:
            print(f"\n❌ Errors ({len(metrics.errors)}):")
            for error in metrics.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
        print()
    
    def save_metrics_to_file(self, filename: str):
        """Save all metrics to JSON file"""
        metrics_data = []
        for metrics in self.metrics_history:
            metrics_dict = asdict(metrics)
            metrics_dict['timestamp'] = metrics.timestamp.isoformat()
            metrics_data.append(metrics_dict)
        
        with open(filename, 'w') as f:
            json.dump(metrics_data, f, indent=2, default=str)
        
        logger.info(f"📄 Metrics saved to {filename}")
    
    def compare_metrics(self, before_file: str, after_file: str) -> Dict[str, Any]:
        """Compare before/after metrics and generate improvement report"""
        
        try:
            with open(before_file, 'r') as f:
                before_data = json.load(f)
            with open(after_file, 'r') as f:
                after_data = json.load(f)
        except FileNotFoundError as e:
            logger.error(f"Metrics file not found: {e}")
            return {}
        
        comparisons = {}
        
        # Group metrics by test name
        before_by_test = {m['test_name']: m for m in before_data}
        after_by_test = {m['test_name']: m for m in after_data}
        
        for test_name in before_by_test:
            if test_name in after_by_test:
                before = before_by_test[test_name]
                after = after_by_test[test_name]
                
                response_time_improvement = (
                    (before['avg_response_time'] - after['avg_response_time']) / 
                    before['avg_response_time'] * 100
                ) if before['avg_response_time'] > 0 else 0
                
                throughput_improvement = (
                    (after['requests_per_second'] - before['requests_per_second']) / 
                    before['requests_per_second'] * 100
                ) if before['requests_per_second'] > 0 else 0
                
                success_rate_change = after['success_rate'] - before['success_rate']
                
                comparisons[test_name] = {
                    "response_time_improvement_percent": response_time_improvement,
                    "throughput_improvement_percent": throughput_improvement,
                    "success_rate_change": success_rate_change,
                    "before_avg_response_time_ms": before['avg_response_time'] * 1000,
                    "after_avg_response_time_ms": after['avg_response_time'] * 1000,
                    "before_requests_per_second": before['requests_per_second'],
                    "after_requests_per_second": after['requests_per_second']
                }
        
        return comparisons
    
    def print_comparison_report(self, comparisons: Dict[str, Any]):
        """Print detailed comparison report"""
        print(f"\n{'='*80}")
        print(f"📈 PERFORMANCE IMPROVEMENT REPORT")
        print(f"{'='*80}")
        
        for test_name, comp in comparisons.items():
            print(f"\n🧪 {test_name}")
            print(f"{'─'*50}")
            
            # Response Time
            rt_improvement = comp['response_time_improvement_percent']
            rt_icon = "🚀" if rt_improvement > 0 else "⚠️" if rt_improvement < -10 else "➡️"
            print(f"{rt_icon} Response Time: {comp['before_avg_response_time_ms']:.0f}ms → {comp['after_avg_response_time_ms']:.0f}ms ({rt_improvement:+.1f}%)")
            
            # Throughput
            tp_improvement = comp['throughput_improvement_percent']
            tp_icon = "🚀" if tp_improvement > 0 else "⚠️" if tp_improvement < -10 else "➡️"
            print(f"{tp_icon} Throughput: {comp['before_requests_per_second']:.1f} → {comp['after_requests_per_second']:.1f} req/s ({tp_improvement:+.1f}%)")
            
            # Success Rate
            sr_change = comp['success_rate_change']
            sr_icon = "✅" if sr_change >= 0 else "❌"
            print(f"{sr_icon} Success Rate: {sr_change:+.1f}%")
        
        # Overall summary
        avg_response_improvement = statistics.mean([c['response_time_improvement_percent'] for c in comparisons.values() if c['response_time_improvement_percent'] != 0])
        avg_throughput_improvement = statistics.mean([c['throughput_improvement_percent'] for c in comparisons.values() if c['throughput_improvement_percent'] != 0])
        
        print(f"\n{'='*80}")
        print(f"🎯 OVERALL IMPROVEMENTS")
        print(f"{'='*80}")
        print(f"Average Response Time Improvement: {avg_response_improvement:+.1f}%")
        print(f"Average Throughput Improvement: {avg_throughput_improvement:+.1f}%")
        print()

async def run_baseline_tests():
    """Run baseline performance tests before optimizations"""
    tester = PerformanceTester()
    
    logger.info("🔐 Authenticating...")
    await tester.authenticate()
    
    logger.info("📊 Running baseline performance tests...")
    
    # Test 1: Single user response times
    metrics = await tester.concurrent_request_test("/users", concurrent_users=1, requests_per_user=10)
    tester.print_metrics(metrics)
    
    # Test 2: Moderate concurrency
    metrics = await tester.concurrent_request_test("/users", concurrent_users=10, requests_per_user=5)
    tester.print_metrics(metrics)
    
    # Test 3: High concurrency (stress test)
    metrics = await tester.concurrent_request_test("/users", concurrent_users=50, requests_per_user=2)
    tester.print_metrics(metrics)
    
    # Test 4: Database query performance
    metrics = await tester.database_query_performance_test()
    tester.print_metrics(metrics)
    
    # Test 5: Memory usage test
    metrics = await tester.memory_usage_test()
    tester.print_metrics(metrics)
    
    # Save baseline metrics
    tester.save_metrics_to_file("performance_baseline.json")
    logger.info("✅ Baseline tests completed!")

async def run_optimized_tests():
    """Run performance tests after optimizations"""
    tester = PerformanceTester("http://localhost:8001")  # Assume optimized version runs on different port
    
    logger.info("🔐 Authenticating with optimized backend...")
    await tester.authenticate()
    
    logger.info("📊 Running optimized performance tests...")
    
    # Same tests as baseline
    metrics = await tester.concurrent_request_test("/users", concurrent_users=1, requests_per_user=10)
    tester.print_metrics(metrics)
    
    metrics = await tester.concurrent_request_test("/users", concurrent_users=10, requests_per_user=5)
    tester.print_metrics(metrics)
    
    metrics = await tester.concurrent_request_test("/users", concurrent_users=50, requests_per_user=2)
    tester.print_metrics(metrics)
    
    # Test higher concurrency levels (should be possible after optimization)
    metrics = await tester.concurrent_request_test("/users", concurrent_users=100, requests_per_user=2)
    tester.print_metrics(metrics)
    
    metrics = await tester.database_query_performance_test()
    tester.print_metrics(metrics)
    
    metrics = await tester.memory_usage_test()
    tester.print_metrics(metrics)
    
    # Save optimized metrics
    tester.save_metrics_to_file("performance_optimized.json")
    logger.info("✅ Optimized tests completed!")

def generate_comparison_report():
    """Generate and display comparison report"""
    tester = PerformanceTester()
    comparisons = tester.compare_metrics("performance_baseline.json", "performance_optimized.json")
    tester.print_comparison_report(comparisons)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "baseline":
            asyncio.run(run_baseline_tests())
        elif command == "optimized":
            asyncio.run(run_optimized_tests())
        elif command == "compare":
            generate_comparison_report()
        else:
            print("Usage: python performance_test.py [baseline|optimized|compare]")
    else:
        print("Usage: python performance_test.py [baseline|optimized|compare]")