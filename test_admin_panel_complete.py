#!/usr/bin/env python3
# Test Admin Panel Functionality - ทดสอบระบบแอดมิน

import asyncio
import aiohttp
import json
from datetime import datetime

class AdminPanelTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_admin_endpoints(self):
        """ทดสอบ Admin Endpoints"""
        print("🔍 Testing Admin Panel Endpoints...")
        
        tests = [
            ("GET", "/admin", "Admin HTML Page"),
            ("GET", "/admin/status", "System Status"),
            ("GET", "/admin/users", "Users List"),
            ("GET", "/health", "Health Check")
        ]
        
        results = []
        
        for method, endpoint, description in tests:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"  📡 Testing {description}: {method} {endpoint}")
                
                if method == "GET":
                    async with self.session.get(url) as response:
                        status = response.status
                        content_type = response.headers.get('content-type', '')
                        
                        if status == 200:
                            print(f"    ✅ {description}: OK (Status: {status})")
                            results.append({"endpoint": endpoint, "status": "PASS", "code": status})
                        else:
                            print(f"    ❌ {description}: FAIL (Status: {status})")
                            results.append({"endpoint": endpoint, "status": "FAIL", "code": status})
                            
            except Exception as e:
                print(f"    🚨 {description}: ERROR - {str(e)}")
                results.append({"endpoint": endpoint, "status": "ERROR", "error": str(e)})
        
        return results
    
    async def test_users_endpoint_detail(self):
        """ทดสอบ Users Endpoint แบบละเอียด"""
        print("\n👥 Testing Users Endpoint in Detail...")
        
        try:
            url = f"{self.base_url}/admin/users"
            async with self.session.get(url) as response:
                status = response.status
                print(f"  📊 Status Code: {status}")
                
                if status == 200:
                    data = await response.json()
                    print(f"  📈 Response Structure: {type(data)}")
                    print(f"  👤 Users Count: {len(data.get('users', []))}")
                    
                    if data.get('users'):
                        sample_user = data['users'][0]
                        print(f"  📝 Sample User Fields: {list(sample_user.keys())}")
                        print(f"  🏷️ Sample User ID: {sample_user.get('user_id', 'N/A')}")
                        print(f"  📛 Sample Display Name: {sample_user.get('display_name', 'N/A')}")
                    else:
                        print("  ⚠️ No users found in response")
                        
                    return True
                else:
                    error_text = await response.text()
                    print(f"  ❌ Failed to get users: {error_text[:200]}...")
                    return False
                    
        except Exception as e:
            print(f"  🚨 Error testing users endpoint: {e}")
            return False
    
    async def test_system_status_detail(self):
        """ทดสอบ System Status แบบละเอียด"""
        print("\n⚙️ Testing System Status in Detail...")
        
        try:
            url = f"{self.base_url}/admin/status"
            async with self.session.get(url) as response:
                status = response.status
                print(f"  📊 Status Code: {status}")
                
                if status == 200:
                    data = await response.json()
                    print(f"  🔧 Overall Status: {data.get('overall_status', 'unknown')}")
                    print(f"  ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
                    
                    checks = data.get('checks', {})
                    print(f"  🔍 System Checks:")
                    
                    for check_name, check_data in checks.items():
                        if isinstance(check_data, dict):
                            available = check_data.get('available', check_data.get('configured', False))
                            status_icon = "✅" if available else "❌"
                            print(f"    {status_icon} {check_name}: {'OK' if available else 'FAIL'}")
                            
                            if check_data.get('error'):
                                print(f"      🔸 Error: {check_data['error'][:100]}...")
                            if check_data.get('stats'):
                                stats = check_data['stats']
                                print(f"      📊 Stats: {stats}")
                        else:
                            print(f"    ❓ {check_name}: {check_data}")
                    
                    return data.get('overall_status') in ['healthy', 'degraded']
                else:
                    error_text = await response.text()
                    print(f"  ❌ Failed to get status: {error_text[:200]}...")
                    return False
                    
        except Exception as e:
            print(f"  🚨 Error testing system status: {e}")
            return False

    async def test_loading_scripts(self):
        """ทดสอบการโหลด JavaScript Files"""
        print("\n📜 Testing Loading Animation Scripts...")
        
        scripts = [
            "/static/js/loading-animations.js",
            "/static/js/admin-enhanced.js"
        ]
        
        results = []
        
        for script_path in scripts:
            try:
                url = f"{self.base_url}{script_path}"
                print(f"  📂 Testing: {script_path}")
                
                async with self.session.get(url) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    content_length = len(await response.text())
                    
                    if status == 200:
                        print(f"    ✅ Script OK (Size: {content_length} bytes)")
                        results.append({"script": script_path, "status": "OK", "size": content_length})
                    else:
                        print(f"    ❌ Script FAIL (Status: {status})")
                        results.append({"script": script_path, "status": "FAIL", "code": status})
                        
            except Exception as e:
                print(f"    🚨 Error loading {script_path}: {e}")
                results.append({"script": script_path, "status": "ERROR", "error": str(e)})
        
        return results
    
    async def generate_test_report(self):
        """สร้างรายงานการทดสอบ"""
        print("\n" + "="*60)
        print("🎯 ADMIN PANEL TESTING REPORT")
        print("="*60)
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print()
        
        # ทดสอบ endpoints
        endpoint_results = await self.test_admin_endpoints()
        
        # ทดสอบ users endpoint
        users_ok = await self.test_users_endpoint_detail()
        
        # ทดสอบ system status
        status_ok = await self.test_system_status_detail()
        
        # ทดสอบ loading scripts
        script_results = await self.test_loading_scripts()
        
        # สรุปผล
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_endpoints = len(endpoint_results)
        passed_endpoints = len([r for r in endpoint_results if r['status'] == 'PASS'])
        
        total_scripts = len(script_results)
        passed_scripts = len([r for r in script_results if r['status'] == 'OK'])
        
        print(f"🔗 Endpoints: {passed_endpoints}/{total_endpoints} passed")
        print(f"📜 Scripts: {passed_scripts}/{total_scripts} loaded")
        print(f"👥 Users Endpoint: {'✅ OK' if users_ok else '❌ FAIL'}")
        print(f"⚙️ System Status: {'✅ OK' if status_ok else '❌ FAIL'}")
        
        overall_status = (
            passed_endpoints == total_endpoints and 
            passed_scripts == total_scripts and 
            users_ok and status_ok
        )
        
        print(f"\n🎯 OVERALL STATUS: {'✅ ALL TESTS PASSED' if overall_status else '❌ SOME TESTS FAILED'}")
        
        if not overall_status:
            print("\n🔧 RECOMMENDATIONS:")
            if passed_endpoints < total_endpoints:
                print("  - ตรวจสอบการทำงานของ FastAPI server")
                print("  - ตรวจสอบการกำหนดค่า routes และ endpoints")
            if passed_scripts < total_scripts:
                print("  - ตรวจสอบว่าไฟล์ JavaScript อยู่ในที่ถูกต้อง")
                print("  - ตรวจสอบการ mount static files")
            if not users_ok:
                print("  - ตรวจสอบการเชื่อมต่อฐานข้อมูล")
                print("  - ตรวจสอบ CRUD functions ใน crud_enhanced.py")
            if not status_ok:
                print("  - ตรวจสอบการกำหนดค่าระบบต่าง ๆ")
        
        print("\n" + "="*60)
        return overall_status

async def main():
    """เรียกใช้การทดสอบ"""
    print("🚀 Starting Admin Panel Tests...")
    print("📝 Make sure the server is running at http://127.0.0.1:8000")
    print()
    
    async with AdminPanelTester() as tester:
        success = await tester.generate_test_report()
    
    if success:
        print("\n🎉 All tests passed! Admin Panel is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Please check the recommendations above.")

if __name__ == "__main__":
    asyncio.run(main())
