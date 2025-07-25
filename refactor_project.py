#!/usr/bin/env python3
"""
Project Structure Refactoring Script
Reorganizes the LINE Bot chatbot project into frontend/backend separation
"""

import os
import shutil
from pathlib import Path
import argparse

def create_directory_structure():
    """Create the new directory structure"""
    print("Creating new directory structure...")
    
    directories = [
        # Backend structure
        "backend/app/core",
        "backend/app/api/routers", 
        "backend/app/services",
        "backend/app/db",
        "backend/app/schemas",
        "backend/app/auth",
        "backend/app/utils",
        "backend/migrations",
        
        # Frontend structure
        "frontend/templates/admin",
        "frontend/templates/form_admin",
        "frontend/templates/dashboard", 
        "frontend/templates/history",
        "frontend/static/css",
        "frontend/static/js",
        "frontend/static/images/avatars",
        "frontend/assets",
        
        # Scripts structure
        "scripts/database",
        "scripts/testing",
        "scripts/deployment",
        "scripts/batch",
        
        # Config, docs, tests, tools
        "config",
        "docs/guides",
        "tests/test_api",
        "tests/test_services", 
        "tests/test_db",
        "tools"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created: {directory}")

def move_backend_files():
    """Move backend application files"""
    print("\n🔧 Moving backend files...")
    
    backend_moves = [
        # Main app structure (keep existing app/ for now, copy to backend/)
        ("app", "backend/app_new"),
        ("migrations", "backend/migrations"),
    ]
    
    for src, dst in backend_moves:
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"✅ Copied: {src} → {dst}")

def move_frontend_files():
    """Move frontend files"""
    print("\n🎨 Moving frontend files...")
    
    # Templates
    template_moves = [
        ("templates/admin.html", "frontend/templates/admin/admin.html"),
        ("templates/dashboard", "frontend/templates/dashboard"),
        ("templates/history", "frontend/templates/history"),
        ("app/templates/form_admin", "frontend/templates/form_admin"),
    ]
    
    for src, dst in template_moves:
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"✅ Moved: {src} → {dst}")
    
    # Static files
    static_moves = [
        ("static/enhanced/dashboard.css", "frontend/static/css/dashboard.css"),
        ("static/images", "frontend/static/images"),
        ("static/test.html", "frontend/static/test.html"),
    ]
    
    for src, dst in static_moves:
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"✅ Moved: {src} → {dst}")

def move_scripts():
    """Move utility scripts"""
    print("\n🔧 Moving scripts...")
    
    # Database scripts
    db_scripts = [
        "run_migration.py",
        "check_database.py", 
        "create_sample_data.py",
        "backfill_avatars_simple.py",
        "test_db.py",
        "simple_migrate.py",
        "migrate_add_display_name.py",
        "migrate_add_picture_url.py"
    ]
    
    for script in db_scripts:
        if os.path.exists(script):
            shutil.copy2(script, f"scripts/database/{script}")
            print(f"✅ Moved: {script} → scripts/database/{script}")
    
    # Testing scripts  
    test_scripts = [
        "test_enhanced_system.py",
        "test_avatar_system.py",
        "check_users.py",
        "test_ui_enhancement.py",
        "test_complete_flow.py",
        "test_websocket.py"
    ]
    
    for script in test_scripts:
        if os.path.exists(script):
            shutil.copy2(script, f"scripts/testing/{script}")
            print(f"✅ Moved: {script} → scripts/testing/{script}")
    
    # Deployment scripts
    if os.path.exists("deployment"):
        shutil.copytree("deployment", "scripts/deployment", dirs_exist_ok=True)
        print("✅ Moved: deployment → scripts/deployment")
    
    # Batch files
    batch_files = [f for f in os.listdir(".") if f.endswith(".bat")]
    for batch_file in batch_files:
        shutil.copy2(batch_file, f"scripts/batch/{batch_file}")
        print(f"✅ Moved: {batch_file} → scripts/batch/{batch_file}")

def move_config_and_docs():
    """Move configuration and documentation files"""
    print("\n⚙️  Moving configuration and documentation...")
    
    # Configuration files
    config_files = [
        ("docker-compose.yml", "config/docker-compose.yml"),
        ("Dockerfile", "config/Dockerfile"),
        ("render.yaml", "config/render.yaml"),
        ("vercel.json", "config/vercel.json"),
        ("runtime.txt", "config/runtime.txt")
    ]
    
    for src, dst in config_files:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ Moved: {src} → {dst}")
    
    # Documentation files
    doc_files = [
        "CLAUDE.md",
        "DEPLOYMENT_GUIDE.md", 
        "SECURITY.md",
        "DATABASE_ANALYSIS.md",
        "ARCHITECTURE.md"
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            shutil.copy2(doc_file, f"docs/{doc_file}")
            print(f"✅ Moved: {doc_file} → docs/{doc_file}")
    
    # Guide files
    guide_files = [
        "POSTGRESQL_MIGRATION_GUIDE.md",
        "SUPABASE_RENDER_SETUP_GUIDE.md", 
        "QUICK_START_POSTGRESQL.md"
    ]
    
    for guide_file in guide_files:
        if os.path.exists(guide_file):
            shutil.copy2(guide_file, f"docs/guides/{guide_file}")
            print(f"✅ Moved: {guide_file} → docs/guides/{guide_file}")

def move_tools():
    """Move development tools"""
    print("\n🛠️  Moving development tools...")
    
    tool_dirs = ["vscode-mcp-server", "ai-agent-jetpack"]
    
    for tool_dir in tool_dirs:
        if os.path.exists(tool_dir):
            shutil.copytree(tool_dir, f"tools/{tool_dir}", dirs_exist_ok=True)
            print(f"✅ Moved: {tool_dir} → tools/{tool_dir}")

def create_new_main_files():
    """Create new main entry points and configuration files"""
    print("\n📝 Creating new configuration files...")
    
    # New main.py for backend
    backend_main = '''# backend/main.py
"""
FastAPI Backend Application Entry Point
"""
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
'''
    
    with open("backend/main.py", "w", encoding="utf-8") as f:
        f.write(backend_main)
    print("✅ Created: backend/main.py")
    
    # New requirements.txt for backend
    if os.path.exists("requirements.txt"):
        shutil.copy2("requirements.txt", "backend/requirements.txt")
        print("✅ Created: backend/requirements.txt")
    
    # Project-level pyproject.toml
    pyproject_content = '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "line-chatbot-admin"
version = "1.3.0"
description = "LINE Bot with Admin Panel and Form Management"
readme = "README.md"
requires-python = ">=3.9"
keywords = ["line", "chatbot", "admin", "fastapi"]
authors = [
    {name = "Development Team"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

[project.urls]
Homepage = "https://github.com/yourusername/line-chatbot-admin"
Documentation = "https://github.com/yourusername/line-chatbot-admin/docs"
Repository = "https://github.com/yourusername/line-chatbot-admin"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\\.pyi?$'
extend-exclude = """
(
  # directories
  \\.eggs
  | \\.git
  | \\.venv
  | env
  | venv
)
"""

[tool.isort]
profile = "black"
multi_line_output = 3
'''
    
    with open("pyproject.toml", "w", encoding="utf-8") as f:
        f.write(pyproject_content)
    print("✅ Created: pyproject.toml")

def create_readme():
    """Create main README.md"""
    readme_content = '''# LINE Bot Chatbot with Admin Panel

A comprehensive LINE Bot application with dual admin systems, real-time chat capabilities, and advanced analytics.

## 🏗️ Project Structure

```
upgradeLineChatbot/
├── backend/          # FastAPI Backend Application
├── frontend/         # Templates & Static Assets  
├── scripts/          # Utility Scripts
├── config/           # Configuration Files
├── docs/             # Documentation
├── tests/            # Test Files
└── tools/            # Development Tools
```

## 🚀 Quick Start

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
python main.py
```

### Production Deployment
```bash
# Using Docker
docker-compose -f config/docker-compose.yml up --build

# Using Python directly
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)  
- [Security Guide](docs/SECURITY.md)
- [Database Guide](docs/DATABASE_ANALYSIS.md)

## 🔧 Development Scripts

- Database: `scripts/database/`
- Testing: `scripts/testing/`
- Deployment: `scripts/deployment/`
- Batch Operations: `scripts/batch/`

## 🎯 Features

- **LINE Bot Integration**: Real-time webhook processing
- **Dual Admin Systems**: Live chat + Form management
- **Analytics Dashboard**: Real-time data visualization
- **Telegram Integration**: Admin notifications
- **AI-Powered Responses**: Gemini AI integration

## 📊 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: HTML5, CSS3, JavaScript, WebSocket
- **AI**: Google Gemini API
- **Deployment**: Docker, Render, Vercel
- **Database**: PostgreSQL (production), SQLite (development)

## 🤝 Contributing

Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details on our code of conduct and development process.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
'''
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Created: README.md")

def main():
    """Main refactoring function"""
    parser = argparse.ArgumentParser(description="Refactor project structure")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without making changes")
    parser.add_argument("--skip-backup", action="store_true",
                       help="Skip creating backup of current structure")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        return
    
    print("🏗️  Starting project structure refactoring...")
    print("=" * 60)
    
    # Create backup if requested
    if not args.skip_backup:
        print("💾 Creating backup...")
        if os.path.exists("backup_before_refactor"):
            shutil.rmtree("backup_before_refactor")
        
        # Backup key directories
        backup_dirs = ["app", "templates", "static", "migrations"]
        for backup_dir in backup_dirs:
            if os.path.exists(backup_dir):
                shutil.copytree(backup_dir, f"backup_before_refactor/{backup_dir}")
        print("✅ Backup created in: backup_before_refactor/")
    
    try:
        # Execute refactoring steps
        create_directory_structure()
        move_backend_files()
        move_frontend_files()
        move_scripts()
        move_config_and_docs()
        move_tools()
        create_new_main_files()
        create_readme()
        
        print("\n" + "=" * 60)
        print("🎉 Project refactoring completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Update import statements in backend/app_new/")
        print("2. Test the new structure: cd backend && python main.py")
        print("3. Verify all functionality works correctly")
        print("4. Remove old files after verification")
        print("5. Update deployment configurations")
        
        print("\n🔧 Quick Test Commands:")
        print("cd backend && python main.py")
        print("cd scripts/testing && python test_enhanced_system.py")
        
    except Exception as e:
        print(f"\n❌ Error during refactoring: {e}")
        print("💾 Restore from backup_before_refactor/ if needed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())