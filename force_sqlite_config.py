# force_sqlite_config.py
"""
Force SQLite configuration for production deployment
"""
import os
import sys
from pathlib import Path

def force_sqlite_environment():
    """Force environment to use SQLite"""
    print("🔧 Forcing SQLite configuration...")
    
    # Override environment variables for SQLite
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./chatbot.db"
    os.environ["DB_TYPE"] = "sqlite"
    
    # Remove PostgreSQL configs if they exist
    postgres_keys = ["SUPABASE_URL", "POSTGRES_URL", "DATABASE_URL_POSTGRES"]
    for key in postgres_keys:
        if key in os.environ:
            del os.environ[key]
    
    print("✅ Environment configured for SQLite")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"DB_TYPE: {os.environ.get('DB_TYPE')}")

if __name__ == "__main__":
    force_sqlite_environment()
