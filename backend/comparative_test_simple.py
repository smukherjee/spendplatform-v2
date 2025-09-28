#!/usr/bin/env python3
"""
Simple Comparative Performance Testing
Tests sync vs async endpoints without authentication complexity
"""
import asyncio
import httpx
import statistics
import time
import json
from datetime import datetime

class SimpleComparativeTester:
    """Simple sync vs async performance comparison"""
    
    def __init__(self):
        self.sync_base_url = "http://localhost:8000"
        self.async_base_url = "http://localhost:8001"
    
    async def test_endpoint_performance(self, url: str, endpoint: str, concurrent: int, requests_per_user: int):
        """Test endpoint with concurrent users"""
        async def single_user_requests():
            """Single user making multiple requests"""
            times = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for _ in range(requests_per_user):
                    start = time.time()
                    try:
                        response = await client.get(f"{url}{endpoint}")
                        elapsed = time.time() - start
                        if response.status_code == 200:
                            times.append(elapsed * 1000)  # Convert to ms
                        else:
                            print(f"❌ Error response: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Request failed: {e}")
                        elapsed = time.time() - start
                        times.append(elapsed * 1000)  # Still record the time
            return times
        
        # Run concurrent users
        start_time = time.time()
        tasks = [single_user_requests() for _ in range(concurrent)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Flatten all response times
        all_times = []
        for user_times in results:
            all_times.extend(user_times)
        
        if not all_times:
            return {
                "success_rate": 0.0,
                "avg_response_ms": 0,
                "p95_response_ms": 0,
                "requests_per_sec": 0,
                "total_time": total_time
            }
        
        total_requests = concurrent * requests_per_user
        successful_requests = len(all_times)
        
        return {
            "success_rate": (successful_requests / total_requests) * 100,
            "avg_response_ms": round(statistics.mean(all_times), 2),
            "p95_response_ms": round(statistics.quantiles(all_times, n=20)[18], 2) if len(all_times) > 1 else all_times[0],
            "requests_per_sec": round(successful_requests / total_time, 2),
            "total_time": round(total_time, 2)
        }
    
    async def run_comparative_test(self):
        """Run comprehensive comparative test"""
        print("🚀 Simple Comparative Performance Testing")
        print("Comparing sync vs async endpoints...")
        
        # Test configurations
        test_configs = [
            {"name": "Single User", "concurrent": 1, "requests": 10},
            {"name": "Light Load", "concurrent": 5, "requests": 4},
            {"name": "Moderate Load", "concurrent": 10, "requests": 3},
            {"name": "Heavy Load", "concurrent": 25, "requests": 2},
            {"name": "Stress Test", "concurrent": 50, "requests": 1}
        ]
        
        endpoints = [
            {"path": "/users?limit=25", "sync_path": "/api/test/users?limit=25", "async_path": "/api/v1/users-async/test?limit=25"},
            {"path": "/users?limit=100", "sync_path": "/api/test/users?limit=100", "async_path": "/api/v1/users-async/test?limit=100"}
        ]
        
        all_results = []
        
        for endpoint in endpoints:
            print(f"\n{'='*60}")
            print(f"🎯 Testing endpoint: {endpoint['path']}")
            print(f"{'='*60}")
            
            for config in test_configs:
                print(f"\n📊 {config['name']} Test ({config['concurrent']} users × {config['requests']} requests)")
                print("-" * 50)
                
                print(f"🧪 Sync: {self.sync_base_url}{endpoint['sync_path']}")
                sync_results = await self.test_endpoint_performance(
                    self.sync_base_url, endpoint['sync_path'], 
                    config['concurrent'], config['requests']
                )
                
                print(f"🧪 Async: {self.async_base_url}{endpoint['async_path']}")
                async_results = await self.test_endpoint_performance(
                    self.async_base_url, endpoint['async_path'], 
                    config['concurrent'], config['requests']
                )
                
                # Calculate improvements
                response_improvement = 0
                throughput_improvement = 0
                
                if sync_results['avg_response_ms'] > 0:
                    response_improvement = ((sync_results['avg_response_ms'] - async_results['avg_response_ms']) / sync_results['avg_response_ms']) * 100
                
                if sync_results['requests_per_sec'] > 0:
                    throughput_improvement = ((async_results['requests_per_sec'] - sync_results['requests_per_sec']) / sync_results['requests_per_sec']) * 100
                
                print(f"\n🔄 SYNC Results:")
                print(f"  Success Rate: {sync_results['success_rate']:.1f}%")
                print(f"  Requests/sec: {sync_results['requests_per_sec']}")
                print(f"  Avg Response: {sync_results['avg_response_ms']:.0f}ms")
                print(f"  P95 Response: {sync_results['p95_response_ms']:.0f}ms")
                print(f"  Total Time: {sync_results['total_time']:.2f}s")
                
                print(f"\n⚡ ASYNC Results:")
                print(f"  Success Rate: {async_results['success_rate']:.1f}%")
                print(f"  Requests/sec: {async_results['requests_per_sec']}")
                print(f"  Avg Response: {async_results['avg_response_ms']:.0f}ms")
                print(f"  P95 Response: {async_results['p95_response_ms']:.0f}ms")
                print(f"  Total Time: {async_results['total_time']:.2f}s")
                
                print(f"\n📈 IMPROVEMENTS:")
                print(f"  Response Time: {response_improvement:+.1f}%")
                print(f"  Throughput: {throughput_improvement:+.1f}%")
                print(f"  Success Rate: {async_results['success_rate'] - sync_results['success_rate']:+.1f}%")
                
                # Store results
                result = {
                    "endpoint": endpoint['path'],
                    "test_config": config['name'],
                    "sync": sync_results,
                    "async": async_results,
                    "improvements": {
                        "response_time_pct": response_improvement,
                        "throughput_pct": throughput_improvement,
                        "success_rate_diff": async_results['success_rate'] - sync_results['success_rate']
                    }
                }
                all_results.append(result)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_performance_comparison_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n📄 Results saved to {filename}")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"📊 OVERALL PERFORMANCE SUMMARY")
        print(f"{'='*80}")
        
        if all_results:
            avg_response_improvement = statistics.mean([r['improvements']['response_time_pct'] for r in all_results])
            avg_throughput_improvement = statistics.mean([r['improvements']['throughput_pct'] for r in all_results])
            avg_success_diff = statistics.mean([r['improvements']['success_rate_diff'] for r in all_results])
            
            print(f"\n🎯 AVERAGE IMPROVEMENTS:")
            print(f"  Response Time: {avg_response_improvement:+.1f}%")
            print(f"  Throughput: {avg_throughput_improvement:+.1f}%")
            print(f"  Success Rate: {avg_success_diff:+.1f}%")
            
            best_response = max([r['improvements']['response_time_pct'] for r in all_results])
            best_throughput = max([r['improvements']['throughput_pct'] for r in all_results])
            
            print(f"\n🚀 BEST IMPROVEMENTS:")
            print(f"  Best Response Time: {best_response:+.1f}%")
            print(f"  Best Throughput: {best_throughput:+.1f}%")
        
        print(f"\n{'='*80}")

async def main():
    """Main function"""
    print("🚀 Starting Simple Comparative Performance Testing...")
    print("Make sure both servers are running:")
    print("  - Sync server on port 8000")
    print("  - Async server on port 8001")
    
    input("\nPress Enter to continue...")
    
    tester = SimpleComparativeTester()
    await tester.run_comparative_test()

if __name__ == "__main__":
    asyncio.run(main())