# main.py - Entry point สำหรับรันแอปพลิเคชัน
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting LINE Bot Application...")
    print("Press Ctrl+C to stop")
    print("Admin UI: http://localhost:8000/admin")
    print("API Docs: http://localhost:8000/docs")
    print("Auto-reload enabled - files will restart automatically when changed")
    
    uvicorn.run(
        "app.main:app",  # ใช้ string path แทน app object
        host="127.0.0.1",  # เปลี่ยนจาก 0.0.0.0 เป็น localhost
        port=8000,
        reload=True,  # เปิด auto-reload
        reload_dirs=["app"],  # ดู folder app สำหรับการเปลี่ยนแปลง
        log_level="info"
    )
