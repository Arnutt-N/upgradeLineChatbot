# main.py - Entry point สำหรับรันแอปพลิเคชัน
import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Get environment settings
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    print("Starting LINE Bot Application...")
    print(f"Environment: {environment}")
    print(f"Host: {host}:{port}")
    
    if environment == "production":
        print("Admin UI: https://your-app.onrender.com/admin")
        print("API Docs: https://your-app.onrender.com/docs")
    else:
        print(f"Admin UI: http://localhost:{port}/admin")
        print(f"API Docs: http://localhost:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=(environment != "production"),  # ปิด reload ใน production
        log_level="info"
    )
