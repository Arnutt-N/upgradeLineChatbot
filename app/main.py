# app/main.py
import uvicorn
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import create_db_and_tables
from app.api.routers import webhook, admin, form_admin

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with absolute path
import os
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(current_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"Static files mounted from: {static_dir}")
else:
    print(f"Warning: Static directory not found at {static_dir}")

@app.on_event("startup")
async def on_startup():
    print("Application startup: Initializing database...")
    try:
        await create_db_and_tables()
        print("Database and tables created successfully.")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("Application will start anyway, database will be created on first request.")

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

# Health check endpoint for Render
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "LINE Chatbot Admin System",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "admin": "/admin",
            "dashboard": "/ui/dashboard", 
            "analytics": "/ui/analytics",
            "api": "/api/enhanced",
            "docs": "/docs",
            "health": "/health"
        }
    }

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
