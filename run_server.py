#!/usr/bin/env python3
"""
Simple script to run the HR Project LINE Chatbot server
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    from app.core.config import settings
    
    print(f"Starting HR Project LINE Chatbot")
    print(f"Port: {settings.PORT}")
    print(f"Dashboard: http://localhost:{settings.PORT}/ui/dashboard")
    print(f"Analytics: http://localhost:{settings.PORT}/ui/analytics")
    print(f"Admin: http://localhost:{settings.PORT}/admin")
    print(f"Form Admin: http://localhost:{settings.PORT}/form-admin")
    print(f"API Docs: http://localhost:{settings.PORT}/docs")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        access_log=True
    )