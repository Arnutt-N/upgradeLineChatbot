#!/usr/bin/env python3
"""
Test UI Enhancement Components
ทดสอบส่วนประกอบ UI ที่ปรับปรุงแล้ว
"""

import os
from pathlib import Path

def test_ui_files():
    """ทดสอบว่าไฟล์ UI ถูกสร้างครบถ้วน"""
    
    print("🎨 Testing UI Enhancement Files...")
    print("=" * 50)
    
    base_path = Path("D:/hrProject/upgradeLineChatbot")
    
    # ไฟล์ที่ควรมี
    required_files = [
        "templates/history/chat_history.html",
        "templates/dashboard/overview.html", 
        "app/api/routers/ui_router.py",
        "static/enhanced/dashboard.css",
        "static/enhanced/dashboard.js"
    ]
    
    print("📁 Checking required files:")
    all_exist = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path} - NOT FOUND")
            all_exist = False
    
    print("\n" + "=" * 50)
    
    # ตรวจสอบโครงสร้างไดเรกทอรี
    print("📂 Checking directory structure:")
    
    required_dirs = [
        "templates/history",
        "templates/dashboard",
        "static/enhanced"
    ]
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists() and full_path.is_dir():
            file_count = len(list(full_path.glob("*")))
            print(f"  ✅ {dir_path}/ ({file_count} files)")
        else:
            print(f"  ❌ {dir_path}/ - NOT FOUND")
            all_exist = False
    
    print("\n" + "=" * 50)
    
    # ตรวจสอบการแก้ไข admin.html
    print("🔧 Checking admin.html modifications:")
    
    admin_file = base_path / "templates/admin.html"
    if admin_file.exists():
        content = admin_file.read_text(encoding='utf-8')
        
        checks = [
            ("Enhanced navigation", "enhanced-nav" in content),
            ("Dashboard link", "/ui/dashboard" in content),
            ("Analytics link", "/ui/analytics" in content),
            ("Enhanced button styles", "enhanced-btn" in content)
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_exist = False
    else:
        print("  ❌ admin.html not found")
        all_exist = False
    
    print("\n" + "=" * 50)
    
    # สรุปผล
    if all_exist:
        print("🎉 All UI Enhancement files are ready!")
        
        print("\n📋 Next steps:")
        print("1. Start the server: python main.py")
        print("2. Test URLs:")
        print("   - http://localhost:8000/ui/dashboard")
        print("   - http://localhost:8000/ui/analytics") 
        print("   - http://localhost:8000/admin (with enhanced buttons)")
        print("3. Check API endpoints:")
        print("   - http://localhost:8000/api/enhanced/dashboard/summary")
        
    else:
        print("❌ Some UI Enhancement files are missing!")
        print("Please check the missing files and create them.")
    
    return all_exist

def test_ui_routes():
    """ทดสอบ UI routes"""
    
    print("\n🌐 Testing UI Routes Configuration...")
    print("=" * 50)
    
    try:
        # ทดสอบ import ui_router
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app.api.routers.ui_router import router
        print("✅ UI Router imported successfully")
        
        # ตรวจสอบ routes
        routes = router.routes
        print(f"✅ UI Router has {len(routes)} routes")
        
        for route in routes:
            print(f"  📄 {route.methods} {route.path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import UI Router: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing UI routes: {e}")
        return False

def generate_test_report():
    """สร้างรายงานการทดสอบ"""
    
    print("\n📊 Generating Test Report...")
    print("=" * 50)
    
    files_test = test_ui_files()
    routes_test = test_ui_routes()
    
    report = f"""
# UI Enhancement Test Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results

### File Structure Test
**Status:** {'✅ PASSED' if files_test else '❌ FAILED'}

### Routes Configuration Test  
**Status:** {'✅ PASSED' if routes_test else '❌ FAILED'}

### Overall Status
**Phase C UI Enhancement:** {'✅ READY' if files_test and routes_test else '❌ NEEDS WORK'}

## Available URLs (when server is running)
- **Enhanced Dashboard:** http://localhost:8000/ui/dashboard
- **Analytics Dashboard:** http://localhost:8000/ui/analytics
- **Original Admin:** http://localhost:8000/admin (with enhanced navigation)
- **API Endpoints:** http://localhost:8000/api/enhanced/*

## Features Added
1. ✅ History Dashboard with charts and analytics
2. ✅ Enhanced Admin Dashboard with modern UI
3. ✅ UI Router for serving HTML templates
4. ✅ Enhanced CSS and JavaScript framework
5. ✅ Integration with existing admin interface

## Recommendations
{'All UI components are ready for testing!' if files_test and routes_test else 'Please fix missing components before proceeding.'}
    """
    
    # บันทึกรายงาน
    try:
        with open("UI_ENHANCEMENT_REPORT.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("✅ Test report saved to UI_ENHANCEMENT_REPORT.md")
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
    
    return files_test and routes_test

if __name__ == "__main__":
    try:
        from datetime import datetime
        result = generate_test_report()
        
        if result:
            print("\n🚀 Phase C: UI Enhancement - COMPLETED!")
        else:
            print("\n⚠️ Phase C: UI Enhancement - NEEDS ATTENTION!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
