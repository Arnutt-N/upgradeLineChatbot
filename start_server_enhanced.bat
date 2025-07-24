@echo off
cd /d "D:\hrProject\upgradeLineChatbot"

echo ========================================
echo 🚀 Starting HR Project LINE Chatbot
echo ========================================
echo 📍 Project Directory: %CD%
echo ⏰ Start Time: %DATE% %TIME%
echo ========================================

echo.
echo 🔍 Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo.
echo 📦 Installing/Updating dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠️ Warning: Some dependencies might not be installed properly
)

echo.
echo 🗃️ Checking database...
if exist "chatbot.db" (
    echo ✅ Database file found
) else (
    echo ⚠️ Database file not found - will be created on startup
)

echo.
echo 📁 Checking static files...
if exist "static\js\loading-animations.js" (
    echo ✅ Loading animations script found
) else (
    echo ❌ Loading animations script not found!
)

if exist "static\js\admin-enhanced.js" (
    echo ✅ Enhanced admin script found  
) else (
    echo ❌ Enhanced admin script not found!
)

echo.
echo 🌐 Starting FastAPI server...
echo 📱 Admin Panel: http://127.0.0.1:8000/admin
echo 📊 API Docs: http://127.0.0.1:8000/docs  
echo 🔧 Health Check: http://127.0.0.1:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo 🛑 Server stopped
pause
