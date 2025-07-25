#!/usr/bin/env python3
"""
Import Update Script
Updates import statements after project structure refactoring
"""

import os
import re
from pathlib import Path

def update_backend_imports():
    """Update import statements in backend files"""
    print("🔧 Updating backend import statements...")
    
    backend_files = []
    backend_dir = Path("backend/app_new")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found. Run refactor_project.py first.")
        return
    
    # Find all Python files in backend
    for py_file in backend_dir.rglob("*.py"):
        backend_files.append(py_file)
    
    import_updates = {
        # Update app imports to use relative imports
        r'from app\.': 'from .',
        r'import app\.': 'import .',
        
        # Update specific common imports
        r'from app import': 'from . import',
        r'from app/': 'from ./',
        
        # Static file paths
        r'"/static"': '"/frontend/static"',
        r"'/static'": "'/frontend/static'",
        
        # Template paths
        r'"templates"': '"../frontend/templates"',
        r"'templates'": "'../frontend/templates'",
        
        # Configuration updates
        r'StaticFiles\(directory="static"\)': 'StaticFiles(directory="../frontend/static")',
        r'templates = Jinja2Templates\(directory="templates"\)': 'templates = Jinja2Templates(directory="../frontend/templates")',
    }
    
    for py_file in backend_files:
        print(f"📝 Updating: {py_file}")
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply import updates
            for pattern, replacement in import_updates.items():
                content = re.sub(pattern, replacement, content)
            
            # Only write if changes were made
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated imports in: {py_file}")
            else:
                print(f"ℹ️  No changes needed: {py_file}")
                
        except Exception as e:
            print(f"❌ Error updating {py_file}: {e}")

def create_updated_main_py():
    """Create updated main.py with correct paths"""
    print("\n📝 Creating updated main.py...")
    
    main_content = '''# backend/app_new/main.py
import uvicorn
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.database import create_db_and_tables
from .api.routers import webhook, admin, form_admin

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

# Mount static files with correct path
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

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
from .api.routers import enhanced_api, ui_router
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
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
'''
    
    backend_main_file = Path("backend/app_new/main.py")
    if backend_main_file.exists():
        with open(backend_main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
        print("✅ Updated: backend/app_new/main.py")

def create_template_config():
    """Create template configuration file for UI router"""
    print("\n📝 Creating template configuration...")
    
    ui_router_update = '''# backend/app_new/api/routers/ui_router.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Template directory path (relative to backend)
templates_dir = os.path.join(os.path.dirname(__file__), "../../../frontend/templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/ui/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard UI endpoint"""
    return templates.TemplateResponse("dashboard/overview.html", {"request": request})

@router.get("/ui/analytics", response_class=HTMLResponse)  
async def analytics(request: Request):
    """Analytics UI endpoint"""
    return templates.TemplateResponse("admin/admin.html", {"request": request})

@router.get("/ui/chat-history", response_class=HTMLResponse)
async def chat_history(request: Request):
    """Chat history UI endpoint"""
    return templates.TemplateResponse("history/chat_history.html", {"request": request})
'''
    
    ui_router_file = Path("backend/app_new/api/routers/ui_router.py")
    if ui_router_file.exists():
        with open(ui_router_file, 'w', encoding='utf-8') as f:
            f.write(ui_router_update)
        print("✅ Updated: UI router with correct template paths")

def update_docker_compose():
    """Update docker-compose.yml with new structure"""
    print("\n🐳 Updating Docker configuration...")
    
    docker_compose_content = '''version: '3.8'

services:
  web:
    build: 
      context: ..
      dockerfile: config/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./chatbot.db
      - ENVIRONMENT=production
    volumes:
      - ../backend:/app
      - ../frontend:/frontend
    working_dir: /app
    command: python main.py

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: chatbot
      POSTGRES_USER: postgres  
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
    
    docker_compose_file = Path("config/docker-compose.yml")
    if docker_compose_file.exists():
        with open(docker_compose_file, 'w', encoding='utf-8') as f:
            f.write(docker_compose_content)
        print("✅ Updated: config/docker-compose.yml")

def create_dockerfile():
    """Create updated Dockerfile"""
    print("\n🐳 Creating updated Dockerfile...")
    
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ .

# Copy frontend assets
COPY frontend/ /frontend/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Run the application
CMD ["python", "main.py"]
'''
    
    dockerfile_path = Path("config/Dockerfile")
    if dockerfile_path.exists():
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        print("✅ Updated: config/Dockerfile")

def create_env_example():
    """Create .env.example file"""
    print("\n📝 Creating .env.example...")
    
    env_example_content = '''# LINE Bot Configuration
LINE_CHANNEL_SECRET=your_line_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token_here

# Telegram Bot Configuration (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1000
GEMINI_ENABLE_SAFETY=false

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db
# For PostgreSQL: DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Application Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true
ENVIRONMENT=development
DEBUG=false

# Security (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your_secret_key_here
'''
    
    with open(".env.example", 'w', encoding='utf-8') as f:
        f.write(env_example_content)
    print("✅ Created: .env.example")

def main():
    """Main function to update all imports and configurations"""
    print("🔧 Starting import and configuration updates...")
    print("=" * 60)
    
    try:
        update_backend_imports()
        create_updated_main_py()
        create_template_config()
        update_docker_compose()
        create_dockerfile() 
        create_env_example()
        
        print("\n" + "=" * 60)
        print("🎉 Import and configuration updates completed!")
        print("\n📋 Next Steps:")
        print("1. Copy your .env file or rename .env.example to .env")
        print("2. Test the backend: cd backend && python main.py")
        print("3. Verify templates are loading correctly")
        print("4. Test Docker build: docker-compose -f config/docker-compose.yml up")
        
    except Exception as e:
        print(f"\n❌ Error during updates: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())