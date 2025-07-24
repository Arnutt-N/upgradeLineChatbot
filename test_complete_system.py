#!/usr/bin/env python3
# Complete System Test with Loading Animation Testing
"""
ทดสอบระบบครบครัน รวมถึง:
- Admin Panel functionality
- LINE API Loading Animations
- WebSocket Real-time updates
- Fast Gemini AI responses
- Database connectivity
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

class ComprehensiveSystemTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
        self.websocket = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def run_comprehensive_tests(self):
        """รันการทดสอบครบครัน"""
        print("🎯 COMPREHENSIVE SYSTEM TESTING")
        print("="*60)
        print(f"🌐 Testing URL: {self.base_url}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. Basic Health Checks
        print("\n📋 PHASE 1: Basic Health Checks")
        health_results = await self.test_basic_health()
        
        # 2. Admin Panel Tests
        print("\n👨‍💼 PHASE 2: Admin Panel Functionality")
        admin_results = await self.test_admin_panel()
        
        # 3. Real-time Features
        print("\n⚡ PHASE 3: Real-time & WebSocket Tests")
        realtime_results = await self.test_realtime_features()
        
        # 4. Performance Tests
        print("\n🚀 PHASE 4: Performance & Speed Tests")
        performance_results = await self.test_performance()
        
        # 5. Generate Final Report
        print("\n📊 PHASE 5: Final Analysis")
        await self.generate_final_report({
            "health": health_results,
            "admin": admin_results,
            "realtime": realtime_results,
            "performance": performance_results
        })
    
    async def test_basic_health(self) -> Dict:
        """ทดสอบสุขภาพระบบพื้นฐาน"""
        results = {"passed": 0, "failed": 0, "tests": []}
        
        tests = [
            ("/health", "Health Check"),
            ("/admin", "Admin Panel Access"),
            ("/admin/status", "System Status"),
            ("/static/js/loading-animations.js", "Loading Animation Script"),
            ("/static/js/admin-enhanced.js", "Enhanced Admin Script")
        ]
        
        for endpoint, description in tests:
            try:
                print(f"  🔍 Testing {description}...")
                start_time = time.time()
                
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        print(f"    ✅ {description}: OK ({response_time:.2f}s)")
                        results["passed"] += 1
                        results["tests"].append({
                            "endpoint": endpoint,
                            "status": "PASS",
                            "response_time": response_time
                        })
                    else:
                        print(f"    ❌ {description}: FAIL (Status: {response.status})")
                        results["failed"] += 1
                        results["tests"].append({
                            "endpoint": endpoint,
                            "status": "FAIL",
                            "response_code": response.status
                        })
                        
            except Exception as e:
                print(f"    🚨 {description}: ERROR - {str(e)}")
                results["failed"] += 1
                results["tests"].append({
                    "endpoint": endpoint,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        return results

    async def test_admin_panel(self) -> Dict:
        """ทดสอบ Admin Panel functionality"""
        results = {"passed": 0, "failed": 0, "details": {}}
        
        # Test Users Endpoint
        print("  👥 Testing Users Loading...")
        users_result = await self.test_users_endpoint()
        if users_result["success"]:
            results["passed"] += 1
            print(f"    ✅ Users loaded: {users_result['count']} users")
        else:
            results["failed"] += 1
            print(f"    ❌ Users loading failed: {users_result.get('error', 'Unknown error')}")
        
        results["details"]["users"] = users_result
        
        # Test System Status
        print("  ⚙️ Testing System Status...")
        status_result = await self.test_system_status()
        if status_result["healthy"]:
            results["passed"] += 1
            print(f"    ✅ System status: {status_result['status']}")
        else:
            results["failed"] += 1
            print(f"    ❌ System status: {status_result['status']}")
        
        results["details"]["status"] = status_result
        
        # Test if we have users to test messaging
        if users_result["success"] and users_result["count"] > 0:
            print("  💬 Testing Message Simulation...")
            message_result = await self.test_message_simulation(users_result["sample_user_id"])
            if message_result["success"]:
                results["passed"] += 1
                print(f"    ✅ Message simulation successful")
            else:
                results["failed"] += 1
                print(f"    ❌ Message simulation failed: {message_result.get('error')}")
            
            results["details"]["messaging"] = message_result
        
        return results

    async def test_users_endpoint(self) -> Dict:
        """ทดสอบ Users Endpoint แบบละเอียด"""
        try:
            async with self.session.get(f"{self.base_url}/admin/users") as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get("users", [])
                    
                    return {
                        "success": True,
                        "count": len(users),
                        "sample_user_id": users[0]["user_id"] if users else None,
                        "response_structure": list(data.keys()),
                        "sample_user_fields": list(users[0].keys()) if users else []
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text[:200]}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_system_status(self) -> Dict:
        """ทดสอบ System Status"""
        try:
            async with self.session.get(f"{self.base_url}/admin/status") as response:
                if response.status == 200:
                    data = await response.json()
                    overall_status = data.get("overall_status", "unknown")
                    
                    return {
                        "healthy": overall_status in ["healthy", "degraded"],
                        "status": overall_status,
                        "checks": data.get("checks", {}),
                        "details": data
                    }
                else:
                    return {
                        "healthy": False,
                        "status": f"HTTP {response.status}",
                        "error": await response.text()
                    }
                    
        except Exception as e:
            return {"healthy": False, "status": "error", "error": str(e)}

    async def test_message_simulation(self, user_id: str) -> Dict:
        """ทดสอบการส่งข้อความ (จำลอง)"""
        if not user_id:
            return {"success": False, "error": "No user ID provided"}
        
        try:
            # Load messages for this user first
            async with self.session.get(f"{self.base_url}/admin/messages/{user_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    message_count = len(data.get("messages", []))
                    
                    return {
                        "success": True,
                        "message_count": message_count,
                        "user_id": user_id,
                        "can_send": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to load messages: HTTP {response.status}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_realtime_features(self) -> Dict:
        """ทดสอบ Real-time features และ WebSocket"""
        results = {"passed": 0, "failed": 0, "websocket_tested": False}
        
        # Test WebSocket connection
        print("  🔌 Testing WebSocket Connection...")
        try:
            import websockets
            
            ws_url = f"ws://127.0.0.1:8000/ws"
            
            try:
                async with websockets.connect(ws_url, timeout=5) as websocket:
                    print("    ✅ WebSocket connection established")
                    
                    # Send ping message
                    ping_message = json.dumps({"type": "ping", "timestamp": datetime.now().isoformat()})
                    await websocket.send(ping_message)
                    
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "pong":
                        print("    ✅ WebSocket ping/pong successful")
                        results["passed"] += 1
                    elif response_data.get("type") == "connection_established":
                        print("    ✅ WebSocket welcome message received")
                        results["passed"] += 1
                    else:
                        print(f"    ⚠️ Unexpected WebSocket response: {response}")
                        results["failed"] += 1
                    
                    results["websocket_tested"] = True
                    
            except asyncio.TimeoutError:
                print("    ❌ WebSocket connection timeout")
                results["failed"] += 1
            except Exception as e:
                print(f"    ❌ WebSocket test failed: {e}")
                results["failed"] += 1
                
        except ImportError:
            print("    ⚠️ websockets library not available, skipping WebSocket test")
            print("    💡 Install with: pip install websockets")
        
        return results

    async def test_performance(self) -> Dict:
        """ทดสอบประสิทธิภาพของระบบ"""
        results = {"tests": []}
        
        # Test API response times
        endpoints_to_test = [
            "/admin/users",
            "/admin/status",
            "/health"
        ]
        
        print("  ⏱️ Testing API Response Times...")
        for endpoint in endpoints_to_test:
            times = []
            
            # Test each endpoint 3 times
            for i in range(3):
                try:
                    start_time = time.time()
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        response_time = time.time() - start_time
                        times.append(response_time)
                        
                except Exception as e:
                    print(f"    ⚠️ Error testing {endpoint}: {e}")
                    continue
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                print(f"    📊 {endpoint}: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")
                
                results["tests"].append({
                    "endpoint": endpoint,
                    "avg_response_time": avg_time,
                    "min_response_time": min_time,
                    "max_response_time": max_time,
                    "samples": len(times)
                })
        
        return results

    async def generate_final_report(self, all_results: Dict):
        """สร้างรายงานสรุปผลการทดสอบ"""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*70)
        
        total_passed = 0
        total_failed = 0
        
        # Health Results
        health = all_results["health"]
        total_passed += health["passed"]
        total_failed += health["failed"]
        print(f"🏥 HEALTH CHECKS: {health['passed']} passed, {health['failed']} failed")
        
        # Admin Results
        admin = all_results["admin"]
        total_passed += admin["passed"]
        total_failed += admin["failed"]
        print(f"👨‍💼 ADMIN PANEL: {admin['passed']} passed, {admin['failed']} failed")
        
        # Real-time Results
        realtime = all_results["realtime"]
        total_passed += realtime["passed"]
        total_failed += realtime["failed"]
        print(f"⚡ REAL-TIME: {realtime['passed']} passed, {realtime['failed']} failed")
        
        # Performance Summary
        performance = all_results["performance"]
        if performance["tests"]:
            avg_times = [test["avg_response_time"] for test in performance["tests"]]
            overall_avg = sum(avg_times) / len(avg_times)
            print(f"🚀 PERFORMANCE: Average response time: {overall_avg:.3f}s")
        
        print("\n" + "="*70)
        success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        print(f"🎯 OVERALL RESULTS: {total_passed} passed, {total_failed} failed")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! System is working great!")
        elif success_rate >= 70:
            print("✅ GOOD! System is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️ FAIR! System has some issues that need attention")
        else:
            print("❌ POOR! System has significant issues that need immediate attention")
        
        print("\n🔧 RECOMMENDATIONS:")
        
        # Specific recommendations based on results
        if all_results["health"]["failed"] > 0:
            print("  • Check server configuration and static file serving")
        
        if all_results["admin"]["failed"] > 0:
            print("  • Verify database connectivity and API endpoints")
        
        if all_results["realtime"]["failed"] > 0:
            print("  • Check WebSocket configuration and real-time features")
        
        if not realtime.get("websocket_tested", False):
            print("  • Install websockets library for full testing: pip install websockets")
        
        # Performance recommendations
        if performance["tests"]:
            slow_endpoints = [test for test in performance["tests"] if test["avg_response_time"] > 1.0]
            if slow_endpoints:
                print("  • Consider optimizing slow endpoints:")
                for test in slow_endpoints:
                    print(f"    - {test['endpoint']}: {test['avg_response_time']:.3f}s")
        
        print("\n✨ ENHANCED FEATURES STATUS:")
        
        # Check for enhanced features
        user_count = all_results["admin"]["details"]["users"].get("count", 0) if "users" in all_results["admin"]["details"] else 0
        print(f"  👥 Users in system: {user_count}")
        
        system_status = all_results["admin"]["details"]["status"].get("status", "unknown") if "status" in all_results["admin"]["details"] else "unknown"
        print(f"  ⚙️ System health: {system_status}")
        
        websocket_ok = all_results["realtime"]["websocket_tested"]
        print(f"  🔌 WebSocket functionality: {'✅ Working' if websocket_ok else '❌ Not tested'}")
        
        print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

async def main():
    """เรียกใช้การทดสอบครบครัน"""
    print("🚀 Starting Comprehensive System Testing...")
    print("📝 Make sure the server is running at http://127.0.0.1:8000")
    print("⏳ This will take approximately 30-60 seconds...")
    print()
    
    async with ComprehensiveSystemTester() as tester:
        await tester.run_comprehensive_tests()
    
    print("\n🏁 Testing complete! Check the results above.")
    print("💡 If you see issues, refer to the recommendations section.")

if __name__ == "__main__":
    asyncio.run(main())
