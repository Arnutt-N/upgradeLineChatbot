#!/usr/bin/env python3
"""
Quick validation script for refactored project structure
"""

import os
import sys
from pathlib import Path

def check_directories():
    """Check that all required directories exist"""
    required_dirs = [
        "backend/app",
        "frontend/templates", 
        "frontend/static",
        "scripts/database",
        "scripts/testing",
        "config",
        "docs"
    ]
    
    print("Checking directory structure...")
    all_good = True
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"[OK] {directory}")
        else:
            print(f"[MISSING] {directory}")
            all_good = False
    
    return all_good

def check_backend():
    """Check backend functionality"""
    print("\nTesting backend import...")
    
    try:
        # Change to backend directory for testing
        original_cwd = os.getcwd()
        os.chdir("backend")
        
        # Add to Python path
        sys.path.insert(0, ".")
        
        # Try to import the FastAPI app
        from app.main import app
        print("[OK] Backend app imported successfully")
        print(f"[OK] App title: {app.title}")
        print(f"[OK] App version: {app.version}")
        
        # Check if static files path exists
        static_path = Path("../frontend/static")
        if static_path.exists():
            print("[OK] Static files path accessible")
        else:
            print("[WARNING] Static files path not found")
        
        # Check if templates path exists
        templates_path = Path("../frontend/templates")
        if templates_path.exists():
            print("[OK] Templates path accessible")
        else:
            print("[WARNING] Templates path not found")
        
        os.chdir(original_cwd)
        return True
        
    except Exception as e:
        print(f"[ERROR] Backend test failed: {e}")
        os.chdir(original_cwd)
        return False

def check_files():
    """Check that key files exist"""
    key_files = [
        "backend/main.py",
        "backend/app/main.py",
        "backend/requirements.txt",
        "frontend/templates/admin/admin.html",
        "frontend/static/images/avatars/default_user_avatar.png",
        "scripts/database/run_migration.py",
        "config/docker-compose.yml"
    ]
    
    print("\nChecking key files...")
    all_good = True
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path}")
            all_good = False
    
    return all_good

def main():
    """Main validation function"""
    print("=" * 60)
    print("🧪 REFACTORING VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Check directory structure
    results.append(check_directories())
    
    # Check backend functionality
    results.append(check_backend())
    
    # Check key files
    results.append(check_files())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("🎉 ALL CHECKS PASSED!")
        print("\n✅ Your project refactoring is successful!")
        print("\n🚀 Quick start commands:")
        print("   cd backend && python main.py")
        print("   python scripts/database/run_migration.py")
        print("   python scripts/testing/test_enhanced_system.py")
        return True
    else:
        print("⚠️  Some checks failed!")
        print("\n🔧 Please check the issues above and:")
        print("   1. Ensure all files were copied correctly")
        print("   2. Check that paths are properly updated")
        print("   3. Verify directory structure is complete")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)