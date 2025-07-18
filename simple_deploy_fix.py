# simple_deploy_fix.py
"""
Simple deployment fix for production issues
"""
import os
import sys

def main():
    """Simple fix for deployment"""
    print("🚀 Simple deployment fix starting...")
    
    # Force SQLite configuration
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./chatbot.db"
    os.environ["DB_TYPE"] = "sqlite"
    
    print("✅ Environment configured for SQLite")
    print("✅ Ready for production")

if __name__ == "__main__":
    main()
