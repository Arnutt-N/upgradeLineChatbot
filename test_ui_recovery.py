#!/usr/bin/env python3
# Quick UI Test - ทดสอบ UI ที่กู้คืนแล้ว

import asyncio
import aiohttp
from datetime import datetime

class QuickUITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        
    async def test_ui_recovery(self):
        """ทดสอบว่า UI กลับมาใช้งานได้หรือไม่"""
        print("🔍 QUICK UI RECOVERY TEST")
        print("="*50)
        print(f"🌐 Testing URL: {self.base_url}")
        print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test Admin Panel Access
                print("\n📱 Testing Admin Panel Access...")
                async with session.get(f"{self.base_url}/admin") as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for critical elements
                        checks = {
                            "HTML Structure": "<html" in content,
                            "JavaScript": "<script>" in content,
                            "CSS Styles": "<style>" in content,
                            "Title": "Admin Live Chat" in content,
                            "Loading Scripts": "loading-animations.js" in content,
                            "Enhanced Scripts": "admin-enhanced.js" in content,
                            "No Merge Conflicts": "<<<<<<< HEAD" not in content and "=======" not in content
                        }
                        
                        print("  🔍 UI Elements Check:")
                        all_good = True
                        for check, passed in checks.items():
                            status = "✅" if passed else "❌"
                            print(f"    {status} {check}")
                            if not passed:
                                all_good = False
                        
                        if all_good:
                            print("\n  🎉 SUCCESS! UI is recovered and should work properly!")
                            print("    • No merge conflicts found")
                            print("    • All essential scripts are loaded")
                            print("    • HTML structure is intact")
                        else:
                            print("\n  ⚠️ WARNING! Some UI elements may have issues")
                            
                    else:
                        print(f"  ❌ Admin Panel not accessible: HTTP {response.status}")
                        return False
                
                # Test Essential Endpoints
                print("\n🔧 Testing Essential Endpoints...")
                endpoints = [
                    ("/admin/users", "Users Data"),
                    ("/admin/status", "System Status"),
                    ("/static/js/loading-animations.js", "Loading Animations"),
                    ("/static/js/admin-enhanced.js", "Enhanced Features")
                ]
                
                for endpoint, description in endpoints:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}") as resp:
                            if resp.status == 200:
                                print(f"  ✅ {description}: OK")
                            else:
                                print(f"  ⚠️ {description}: HTTP {resp.status}")
                    except Exception as e:
                        print(f"  ❌ {description}: Error - {e}")
                
                print("\n" + "="*50)
                print("🎯 UI RECOVERY TEST COMPLETE")
                print("="*50)
                print("\n💡 NEXT STEPS:")
                print("  1. Open browser: http://127.0.0.1:8000/admin")
                print("  2. Check if UI looks the same as before")
                print("  3. Test loading animations and basic functions")
                print("  4. Report any remaining UI issues")
                
                return True
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("\n💡 Make sure the server is running:")
            print("  .\start_enhanced_system.bat")
            return False

async def main():
    tester = QuickUITester()
    await tester.test_ui_recovery()

if __name__ == "__main__":
    asyncio.run(main())
