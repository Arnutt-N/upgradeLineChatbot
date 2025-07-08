# app/main.py
import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.db.database import create_db_and_tables
from app.api.routers import webhook, admin

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION
)

@app.on_event("startup")
async def on_startup():
    print("Application startup: Creating database and tables...")
    await create_db_and_tables()
    print("Database and tables created successfully.")

@app.on_event("shutdown")
async def on_shutdown():
    print("Application shutdown: Cleaning up resources...")
    # ปิด database connections และ cleanup resources อื่นๆ
    print("Application shutdown complete.")

# Include routers
app.include_router(admin.router)
app.include_router(webhook.router)

if __name__ == "__main__":
    print("Starting server...")
    print(f"Admin Live Chat UI available at http://127.0.0.1:{settings.PORT}/admin")
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD
    )
