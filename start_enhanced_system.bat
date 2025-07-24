@echo off
cd /d "D:\hrProject\upgradeLineChatbot"

echo ========================================
echo 🚀 Enhanced HR Chatbot System Startup
echo ========================================
echo 📍 Project Directory: %CD%
echo ⏰ Start Time: %DATE% %TIME%
echo 🎯 Version: Enhanced with Loading Animations
echo ========================================

echo.
echo 🔍 System Diagnostics...
echo   • Python Version:
python --version 2>nul || (echo     ❌ Python not found! && pause && exit /b 1)
echo   • Current Directory: %CD%
echo   • Database Status:
if exist "chatbot.db" (
    echo     ✅ Database file found
) else (
    echo     ⚠️ Database will be created on startup
)

echo.
echo 📦 Enhanced Features Check...
if exist "static\js\loading-animations.js" (
    echo   ✅ Loading Animation System
) else (
    echo   ❌ Loading Animation System MISSING!
)

if exist "static\js\admin-enhanced.js" (
    echo   ✅ Enhanced Admin Panel
) else (
    echo   ❌ Enhanced Admin Panel MISSING!
)

if exist "app\services\fast_gemini_service.py" (
    echo   ✅ Fast Gemini AI Service
) else (
    echo   ❌ Fast Gemini AI Service MISSING!
)

if exist "app\services\enhanced_ws_manager.py" (
    echo   ✅ Enhanced WebSocket Manager
) else (
    echo   ❌ Enhanced WebSocket Manager MISSING!
)

if exist "app\services\line_loading_helper.py" (
    echo   ✅ LINE Loading Animation Helper
) else (
    echo   ❌ LINE Loading Animation Helper MISSING!
)

echo.
echo 📋 Installing/Updating dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ⚠️ Some dependencies might not be installed properly
    echo 🔧 Consider running: pip install --upgrade -r requirements.txt
)

echo.
echo 🌐 Server Configuration...
echo   📱 Admin Panel: http://127.0.0.1:8000/admin
echo   📊 API Documentation: http://127.0.0.1:8000/docs  
echo   🔧 Health Check: http://127.0.0.1:8000/health
echo   📈 System Status: http://127.0.0.1:8000/admin/status
echo   🔌 WebSocket: ws://127.0.0.1:8000/ws

echo.
echo 🎨 Enhanced Features Available:
echo   🔄 Loading Animations in Admin Panel
echo   ⚡ Real-time Updates via WebSocket
echo   🚀 Fast Gemini AI Responses
echo   💬 LINE Chat Loading Indicators
echo   📊 Performance Monitoring
echo   🔧 Auto Error Recovery

echo.
echo ========================================
echo 🚀 Starting Enhanced FastAPI Server...
echo ========================================
echo 💡 Press Ctrl+C to stop the server
echo 🧪 In another terminal, run: .\test_complete_system.bat
echo ========================================

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info

echo.
echo 🛑 Server stopped at %DATE% %TIME%
echo ✨ Thank you for using Enhanced HR Chatbot System!
pause
