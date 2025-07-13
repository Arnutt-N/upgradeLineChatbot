# app/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.database import create_db_and_tables
from app.api.routers import webhook, admin, form_admin

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
app.include_router(form_admin.router)
app.include_router(webhook.router)

# Import enhanced API and UI
from app.api.routers import enhanced_api, ui_router
app.include_router(enhanced_api.router)
app.include_router(ui_router.router)

# Development endpoint for testing static files
@app.get("/test-static")
async def test_static():
    """Test endpoint to verify static files are working"""
    return {
        "status": "ok",
        "message": "Static files test endpoint",
        "static_urls": {
            "test_page": "/static/test.html",
            "user_avatar": "/static/images/avatars/default_user_avatar.png",
            "admin_avatar": "/static/images/avatars/default_admin_avatar.png", 
            "bot_avatar": "/static/images/avatars/default_bot_avatar.png"
        },
        "instructions": "Visit the URLs above to test static file serving"
    }

if __name__ == "__main__":
    print("Starting server...")
    print(f"Admin Live Chat UI available at http://127.0.0.1:{settings.PORT}/admin")
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD
    )
