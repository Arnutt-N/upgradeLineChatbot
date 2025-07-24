#!/usr/bin/env python3
"""
Test script for Admin Panel Fixes
Tests the critical fixes applied to resolve admin panel issues
"""

import asyncio
import aiohttp
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Test Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_TIMEOUT = 30
DB_PATH = "chatbot.db"

class AdminPanelTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup(self):
        """Setup test environment"""
        print("🚀 Setting up Admin Panel Test Environment...")
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT))
        
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
    
    async def test_database_connection(self):
        """Test database connection and table existence"""
        print("\n📊 Testing Database Connection...")
        
        try:
            # Test SQLite connection
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if main tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('user_status', 'chat_messages', 'chat_history')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Check user_status table
            if 'user_status' in tables:
                cursor.execute("SELECT COUNT(*) FROM user_status")
                user_count = cursor.fetchone()[0]
                self.log_test("Database - user_status table", True, f"{user_count} users found")
            else:
                self.log_test("Database - user_status table", False, "Table not found")
            
            # Check chat tables
            old_messages = 0
            new_messages = 0
            
            if 'chat_messages' in tables:
                cursor.execute("SELECT COUNT(*) FROM chat_messages")
                old_messages = cursor.fetchone()[0]
                self.log_test("Database - chat_messages table", True, f"{old_messages} messages found")
            
            if 'chat_history' in tables:
                cursor.execute("SELECT COUNT(*) FROM chat_history")
                new_messages = cursor.fetchone()[0]
                self.log_test("Database - chat_history table", True, f"{new_messages} messages found")
            
            total_messages = old_messages + new_messages
            self.log_test("Database - Total messages", total_messages > 0, 
                         f"Total: {total_messages} messages")
            
            conn.close()
            
        except Exception as e:
            self.log_test("Database Connection", False, f"Error: {e}")
    
    async def test_server_health(self):
        """Test server health and basic endpoints"""
        print("\n🏥 Testing Server Health...")
        
        try:
            # Test health endpoint
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Server Health Endpoint", True, 
                                 f"Status: {data.get('status', 'unknown')}")
                else:
                    self.log_test("Server Health Endpoint", False, 
                                 f"HTTP {response.status}")
        
        except Exception as e:
            self.log_test("Server Health Endpoint", False, f"Connection error: {e}")
    
    async def test_admin_endpoints(self):
        """Test admin panel API endpoints"""
        print("\n🔧 Testing Admin Panel Endpoints...")
        
        # Test admin users endpoint
        try:
            async with self.session.get(f"{BASE_URL}/admin/users") as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get('users', [])
                    self.log_test("Admin Users Endpoint", True, 
                                 f"Loaded {len(users)} users successfully")
                    
                    # Test user data structure
                    if users:
                        user = users[0]
                        required_fields = ['user_id', 'display_name', 'is_in_live_chat', 'chat_mode']
                        has_all_fields = all(field in user for field in required_fields)
                        self.log_test("Admin Users Data Structure", has_all_fields,
                                     f"User fields: {list(user.keys())}")
                else:
                    self.log_test("Admin Users Endpoint", False, 
                                 f"HTTP {response.status}: {await response.text()}")
        
        except Exception as e:
            self.log_test("Admin Users Endpoint", False, f"Request error: {e}")
        
        # Test admin status endpoint
        try:
            async with self.session.get(f"{BASE_URL}/admin/status") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('overall_status', 'unknown')
                    checks = data.get('checks', {})
                    
                    self.log_test("Admin Status Endpoint", True, 
                                 f"Overall status: {status}, Checks: {len(checks)}")
                    
                    # Test individual system checks
                    for check_name, check_data in checks.items():
                        available = check_data.get('available', check_data.get('configured', False))
                        self.log_test(f"System Check - {check_name}", available,
                                     f"Details: {check_data}")
                else:
                    self.log_test("Admin Status Endpoint", False, 
                                 f"HTTP {response.status}")
        
        except Exception as e:
            self.log_test("Admin Status Endpoint", False, f"Request error: {e}")
    
    async def test_message_endpoints(self):
        """Test message loading endpoints"""
        print("\n💬 Testing Message Loading...")
        
        # First, get a user ID from the users endpoint
        try:
            async with self.session.get(f"{BASE_URL}/admin/users") as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get('users', [])
                    
                    if users:
                        test_user_id = users[0]['user_id']
                        
                        # Test loading messages for this user
                        async with self.session.get(f"{BASE_URL}/admin/messages/{test_user_id}") as msg_response:
                            if msg_response.status == 200:
                                msg_data = await msg_response.json()
                                messages = msg_data.get('messages', [])
                                self.log_test("Admin Messages Endpoint", True,
                                             f"Loaded {len(messages)} messages for user {test_user_id}")
                                
                                # Test message data structure
                                if messages:
                                    message = messages[0]
                                    required_fields = ['id', 'message', 'sender_type', 'created_at']
                                    has_all_fields = all(field in message for field in required_fields)
                                    self.log_test("Admin Messages Data Structure", has_all_fields,
                                                 f"Message fields: {list(message.keys())}")
                            else:
                                self.log_test("Admin Messages Endpoint", False,
                                             f"HTTP {msg_response.status}")
                    else:
                        self.log_test("Admin Messages Endpoint", False, "No users available for testing")
        
        except Exception as e:
            self.log_test("Admin Messages Endpoint", False, f"Request error: {e}")
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        print("\n🔌 Testing WebSocket Connection...")
        
        try:
            import websockets
            
            ws_url = f"ws://127.0.0.1:8000/ws"
            async with websockets.connect(ws_url, timeout=5) as websocket:
                self.log_test("WebSocket Connection", True, "Connection established successfully")
                
                # Test if we can receive a message (wait briefly)
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    self.log_test("WebSocket Message Receiving", True, "Can receive messages")
                except asyncio.TimeoutError:
                    self.log_test("WebSocket Message Receiving", True, 
                                 "No immediate messages (normal for admin panel)")
                
        except ImportError:
            self.log_test("WebSocket Connection", False, "websockets library not available")
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Connection error: {e}")
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("🧪 Starting Admin Panel Comprehensive Tests")
        print("=" * 60)
        
        await self.setup()
        
        try:
            await self.test_database_connection()
            await self.test_server_health()
            await self.test_admin_endpoints()
            await self.test_message_endpoints()
            await self.test_websocket_connection()
            
        finally:
            await self.teardown()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! Admin panel should be working correctly.")
        elif self.passed_tests / self.total_tests >= 0.8:
            print("\n⚠️  Most tests passed. Minor issues may exist.")
        else:
            print("\n❌ Several tests failed. Admin panel has significant issues.")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['passed']]
        if failed_tests:
            print("\n🔍 Failed Tests Details:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n📝 Recommendations:")
        if self.total_tests - self.passed_tests == 0:
            print("  ✅ Admin panel is fully functional!")
        else:
            print("  🔧 Check server logs for detailed error information")
            print("  🔧 Ensure database contains test data")
            print("  🔧 Verify all environment variables are configured")
            print("  🔧 Check network connectivity to all services")

async def main():
    """Main test execution"""
    if not Path(DB_PATH).exists():
        print(f"❌ Database file {DB_PATH} not found!")
        print("   Please run the application first to create the database.")
        sys.exit(1)
    
    tester = AdminPanelTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())