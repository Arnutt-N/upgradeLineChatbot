#!/usr/bin/env python3
"""
Simple UI Test - Check if files exist
"""

import os
from pathlib import Path

def test_ui_files():
    """Test if UI files exist"""
    
    print("Testing UI Enhancement Files...")
    print("=" * 50)
    
    base_path = Path("D:/hrProject/upgradeLineChatbot")
    
    # Required files
    required_files = [
        "templates/history/chat_history.html",
        "templates/dashboard/overview.html", 
        "app/api/routers/ui_router.py",
        "static/enhanced/dashboard.css",
        "static/enhanced/dashboard.js"
    ]
    
    print("Checking required files:")
    all_exist = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  OK: {file_path} ({size:,} bytes)")
        else:
            print(f"  MISSING: {file_path}")
            all_exist = False
    
    print("\nChecking directories:")
    
    required_dirs = [
        "templates/history",
        "templates/dashboard", 
        "static/enhanced"
    ]
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists() and full_path.is_dir():
            file_count = len(list(full_path.glob("*")))
            print(f"  OK: {dir_path}/ ({file_count} files)")
        else:
            print(f"  MISSING: {dir_path}/")
            all_exist = False
    
    print("\nChecking admin.html modifications:")
    
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
            status = "OK" if result else "MISSING"
            print(f"  {status}: {check_name}")
            if not result:
                all_exist = False
    else:
        print("  MISSING: admin.html")
        all_exist = False
    
    print("\n" + "=" * 50)
    
    if all_exist:
        print("SUCCESS: All UI Enhancement files are ready!")
        print("\nNext steps:")
        print("1. Start server: python main.py")
        print("2. Test URLs:")
        print("   - http://localhost:8000/ui/dashboard")
        print("   - http://localhost:8000/ui/analytics")
        print("   - http://localhost:8000/admin (enhanced)")
        print("3. Test APIs:")
        print("   - http://localhost:8000/api/enhanced/dashboard/summary")
        
    else:
        print("ERROR: Some UI Enhancement files are missing!")
    
    return all_exist

if __name__ == "__main__":
    try:
        result = test_ui_files()
        
        if result:
            print("\nPhase C: UI Enhancement - COMPLETED!")
        else:
            print("\nPhase C: UI Enhancement - NEEDS ATTENTION!")
            
    except Exception as e:
        print(f"Test failed: {e}")
