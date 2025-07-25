#!/usr/bin/env python3
"""
Test script for refactored project structure
Verifies that all components work correctly after refactoring
"""

import os
import sys
from pathlib import Path
import importlib.util
import subprocess

def test_directory_structure():
    """Test that all required directories exist"""
    print("🏗️  Testing directory structure...")
    
    required_dirs = [
        "backend/app_new",
        "backend/migrations", 
        "frontend/templates",
        "frontend/static",
        "scripts/database",
        "scripts/testing",
        "config",
        "docs"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
        else:
            print(f"✅ Found: {directory}")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ All required directories exist")
    return True

def test_backend_structure():
    """Test backend application structure"""
    print("\n🔧 Testing backend structure...")
    
    backend_files = [
        "backend/app_new/main.py",
        "backend/app_new/core/config.py",
        "backend/app_new/api/routers/webhook.py",
        "backend/app_new/api/routers/admin.py",
        "backend/app_new/services/line_handler_enhanced.py",
        "backend/app_new/db/models.py",
        "backend/requirements.txt"
    ]
    
    missing_files = []
    for file_path in backend_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print(f"❌ Missing backend files: {missing_files}")
        return False
    
    print("✅ Backend structure is correct")
    return True

def test_frontend_structure():
    """Test frontend structure"""
    print("\n🎨 Testing frontend structure...")
    
    frontend_files = [
        "frontend/templates/admin",
        "frontend/templates/form_admin", 
        "frontend/static/css",
        "frontend/static/js",
        "frontend/static/images/avatars"
    ]
    
    missing_items = []
    for item_path in frontend_files:
        if not Path(item_path).exists():
            missing_items.append(item_path)
        else:
            print(f"✅ Found: {item_path}")
    
    if missing_items:
        print(f"❌ Missing frontend items: {missing_items}")
        return False
    
    print("✅ Frontend structure is correct")
    return True

def test_import_statements():
    """Test that Python imports work correctly"""
    print("\n📦 Testing import statements...")
    
    # Add backend to Python path
    backend_path = Path("backend").absolute()
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    try:
        # Test importing main modules
        spec = importlib.util.spec_from_file_location(
            "config", "backend/app_new/core/config.py"
        )
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        print("✅ Successfully imported config module")
        
        # Test settings access
        if hasattr(config_module, 'settings'):
            print("✅ Settings object is available")
        else:
            print("❌ Settings object not found")
            return False
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    print("✅ Import statements are working")
    return True

def test_static_files():
    """Test that static files are properly organized"""
    print("\n📁 Testing static file organization...")
    
    static_items = [
        "frontend/static/images/avatars/default_user_avatar.png",
        "frontend/static/images/avatars/default_admin_avatar.png",
        "frontend/static/images/avatars/default_bot_avatar.png"
    ]
    
    found_items = []
    for item in static_items:
        if Path(item).exists():
            found_items.append(item)
            print(f"✅ Found: {item}")
        else:
            print(f"ℹ️  Missing (optional): {item}")
    
    if found_items:
        print("✅ Static files are organized")
        return True
    else:
        print("⚠️  No static files found, but this may be OK")
        return True

def test_configuration_files():
    """Test configuration files"""
    print("\n⚙️  Testing configuration files...")
    
    config_files = [
        "config/docker-compose.yml",
        "config/Dockerfile",
        ".env.example",
        "pyproject.toml"
    ]
    
    found_configs = []
    for config_file in config_files:
        if Path(config_file).exists():
            found_configs.append(config_file)
            print(f"✅ Found: {config_file}")
        else:
            print(f"ℹ️  Missing: {config_file}")
    
    if found_configs:
        print("✅ Configuration files are present")
        return True
    else:
        print("❌ No configuration files found")
        return False

def test_scripts():
    """Test utility scripts"""
    print("\n🔧 Testing utility scripts...")
    
    script_dirs = [
        "scripts/database",
        "scripts/testing",
        "scripts/batch"
    ]
    
    found_scripts = 0
    for script_dir in script_dirs:
        if Path(script_dir).exists():
            scripts = list(Path(script_dir).glob("*.py")) + list(Path(script_dir).glob("*.bat"))
            if scripts:
                found_scripts += len(scripts)
                print(f"✅ Found {len(scripts)} scripts in: {script_dir}")
            else:
                print(f"ℹ️  Empty directory: {script_dir}")
        else:
            print(f"ℹ️  Missing directory: {script_dir}")
    
    if found_scripts > 0:
        print(f"✅ Found {found_scripts} utility scripts")
        return True
    else:
        print("⚠️  No utility scripts found")
        return True

def test_backend_startup():
    """Test that backend can start without errors"""
    print("\n🚀 Testing backend startup...")
    
    try:
        # Change to backend directory
        backend_dir = Path("backend").absolute()
        
        # Test syntax by importing main module
        spec = importlib.util.spec_from_file_location(
            "main", backend_dir / "app_new" / "main.py"
        )
        
        if spec is None:
            print("❌ Could not load main.py spec")
            return False
            
        main_module = importlib.util.module_from_spec(spec)
        
        # Add backend to path temporarily
        old_path = sys.path.copy()
        sys.path.insert(0, str(backend_dir / "app_new"))
        
        try:
            spec.loader.exec_module(main_module)
            if hasattr(main_module, 'app'):
                print("✅ FastAPI app object created successfully")
                return True
            else:
                print("❌ FastAPI app object not found")
                return False
        finally:
            sys.path = old_path
            
    except Exception as e:
        print(f"❌ Backend startup test failed: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "=" * 60)
    print("📊 REFACTORING TEST REPORT")
    print("=" * 60)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Backend Structure", test_backend_structure),
        ("Frontend Structure", test_frontend_structure),
        ("Import Statements", test_import_statements),
        ("Static Files", test_static_files),
        ("Configuration Files", test_configuration_files),
        ("Utility Scripts", test_scripts),
        ("Backend Startup", test_backend_startup)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactoring was successful.")
        print("\n📋 Next Steps:")
        print("1. cd backend && python main.py")
        print("2. Open http://localhost:8000 to test the application")
        print("3. Run: python scripts/testing/test_enhanced_system.py")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you ran: python refactor_project.py")
        print("2. Then ran: python update_imports.py")
        print("3. Check that all files were copied correctly")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Refactored Project Structure")
    print("=" * 60)
    
    success = generate_test_report()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())