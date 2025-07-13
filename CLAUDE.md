# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Claude Code Guidelines for HR LINE Chatbot System

This document provides essential guidance for Claude Code when working with this repository, including development commands, architecture overview, and **critical instructions for using Gemini CLI for large codebase analysis**.

---

## 🤖 **CRITICAL: Gemini CLI Integration for Large Codebase Analysis**

**When Claude Code needs to gather information about large parts of the codebase that exceed its context window, it MUST use Gemini CLI in non-interactive mode with the `-p` parameter to get comprehensive analysis.**

### **When to Use Gemini CLI:**
- Analyzing entire directories or multiple large files
- Understanding architecture patterns across the codebase
- Checking implementation status of features across multiple files
- Comparing code patterns between different modules
- Gathering comprehensive project overview
- Any task requiring analysis of >100KB of code

### **Gemini CLI Non-Interactive Mode Syntax:**

**Basic Pattern:**
```bash
gemini -p "@path/to/files PROMPT_HERE"
```

**Key Examples for This Project:**

**1. Architecture Overview:**
```bash
gemini -p "@app/ @static/ @templates/ Provide a comprehensive architecture overview of this HR LINE Chatbot system. Include main components, data flow, and key technologies used."
```

**2. Feature Implementation Check:**
```bash
gemini -p "@app/ Check if authentication system is fully implemented. Show all auth-related files, functions, and security measures."
```

**3. Database Schema Analysis:**
```bash
gemini -p "@app/db/ @migrations/ Analyze the complete database schema. List all tables, relationships, and migration history."
```

**4. API Endpoints Inventory:**
```bash
gemini -p "@app/api/ List all API endpoints in this system. Group by router and include HTTP methods, paths, and purposes."
```

**5. Forms System Analysis:**
```bash
gemini -p "@app/api/routers/form_admin.py @templates/form_admin/ @static/form_admin/ Analyze the complete Forms Admin system implementation including frontend and backend components."
```

**6. LINE Bot Integration Check:**
```bash
gemini -p "@app/api/routers/webhook.py @app/services/ Check LINE Bot integration implementation. Show webhook handling, message processing, and admin features."
```

**7. Security Implementation Review:**
```bash
gemini -p "@app/ @deployment/ Review all security implementations including authentication, session management, environment variables, and production configurations."
```

**8. Deployment Configuration Analysis:**
```bash
gemini -p "@render.yaml @Dockerfile @deployment/ @.env.* Analyze all deployment configurations for Render.com, Docker, and environment setups."
```

**9. Testing Coverage Check:**
```bash
gemini -p "@test*.py @*test*.py @app/ Analyze testing coverage. List all test files and what components they cover."
```

**10. Documentation Completeness:**
```bash
gemini -p "@*.md @deployment/ Check documentation completeness. List all phases, guides, and missing documentation areas."
```

### **Mandatory Usage Scenarios:**

**Claude Code MUST use Gemini CLI when:**
- User asks about overall system architecture
- Need to check implementation across multiple files/directories  
- Analyzing feature completeness or gaps
- Comparing patterns between different modules
- Gathering comprehensive project status
- Creating summaries of large codebases
- Checking security implementations across the system
- Analyzing deployment readiness

### **Command Template for Claude Code:**
```bash
# Always use this pattern when analysis exceeds context limits
gemini -p "@relevant/paths SPECIFIC_ANALYSIS_QUESTION"
```

**Example Usage in Practice:**
When user asks: "Is the authentication system complete?"
Claude should run:
```bash
gemini -p "@app/ Check authentication system completeness. Show all auth files, session management, login/logout flows, and security measures implemented."
```

---

## 🏗️ **Project Architecture Overview**

### **HR LINE Chatbot System Components:**

**Main Application Structure:**
```
🚀 HR LINE Chatbot System
├── 📱 LINE Bot Integration (/webhook)
├── 👥 LINE Admin Interface (/admin) 
├── 📋 Forms Admin System (/form-admin)
├── 🗄️ Database Layer (SQLite/PostgreSQL)
├── 🔐 Authentication System
└── 🚀 Deployment Configuration
```

**Key Technologies:**
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Uvicorn
- **Frontend:** Jinja2 templates, Vanilla JS, Modern CSS
- **Database:** SQLite (dev), PostgreSQL (production ready)
- **Deployment:** Render.com, Docker support
- **Integrations:** LINE Messaging API, Telegram Bot API

**Development Status:**
- ✅ All Phases (0-4 + D) completed
- ✅ Production deployment ready
- ✅ Authentication system implemented
- ✅ Forms management functional
- ✅ Database migrations complete

---

## 💻 **Development Commands**

### **Application Startup:**
```bash
# Development server with auto-reload
python main.py

# Production server  
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker deployment
docker-compose up --build
```

### **Database Management:**
```bash
# Run database migrations
python run_migration.py

# Check database status
python check_database.py

# Create sample data
python create_sample_data.py

# Test database connection
python test_db.py

# Backfill user avatars
python backfill_avatars_simple.py
```

### **Testing & Validation:**
```bash
# Run complete test suite
python test_enhanced_system.py

# Test avatar system
python test_avatar_system.py

# Check user data
python check_users.py

# Test UI enhancements
python test_ui_enhancement.py
```

### **Windows Batch Operations:**
```bash
run_test.bat          # Test database migration
run_migration.bat     # Run database migration  
run_backfill.bat      # Run avatar backfill
run_check_users.bat   # Check user status
```

---

## 🗄️ **Database Architecture**

### **Core Tables:**
- **user_status** - LINE user profiles with avatars and display names
- **chat_messages** - Chat history with admin/user/bot messages  
- **form_submissions** - Form requests (KP7, ID cards) with workflow status
- **admin_users** - Authentication system for forms admin
- **shared_notifications** - Cross-system notifications
- **shared_audit_logs** - System audit trail

### **Advanced Tracking Tables:**
- **chat_history** - Detailed chat analytics
- **friend_activities** - Follow/unfollow tracking
- **telegram_notifications** - Notification queue and status
- **system_logs** - System monitoring and logs
- **telegram_settings** - Dynamic configuration

---

## 🔐 **Security Implementation**

### **Authentication System:**
- Session-based authentication for Forms Admin
- Role-based access control (Admin/Officer/Viewer)
- Secure password hashing
- Session timeout and cleanup
- CSRF protection

### **API Security:**
- LINE webhook signature validation
- Environment variable protection
- Input validation via FastAPI
- SQL injection prevention
- XSS protection headers

---

## 🚀 **Deployment Configuration**

### **Production Ready:**
- ✅ Render.com configuration (render.yaml)
- ✅ Docker support (Dockerfile)
- ✅ Environment templates (.env.render)
- ✅ Database migrations (deployment/migrate_production.py)
- ✅ Health checks and monitoring
- ✅ SSL/HTTPS ready

### **Deployment Files:**
- **render.yaml** - Render.com service configuration
- **Dockerfile** - Container deployment
- **.env.render** - Production environment template
- **DEPLOYMENT_CHECKLIST.md** - Step-by-step deployment guide

---

## 📋 **Current Project Status**

### **Completed Phases:**
```
✅ Phase 0: Backup & Safety
✅ Phase 1: Forms Admin Structure  
✅ Phase 2: Database Migration
✅ Phase 3: Forms Admin Development
✅ Phase 4: Integration & Testing
✅ Phase D: Deployment Configuration
```

### **System URLs:**
```
👥 LINE Admin: http://localhost:8001/admin
📋 Forms Admin: http://localhost:8001/form-admin  
🔗 LINE Webhook: http://localhost:8001/webhook
📚 API Docs: http://localhost:8001/docs
❤️ Health Check: http://localhost:8001/health
```

### **Ready for Production:**
- All core features implemented
- Authentication system complete
- Database migrations ready
- Deployment configuration prepared
- Testing completed successfully

---

**🎯 This system is production-ready and can be deployed immediately to Render.com or other platforms.**