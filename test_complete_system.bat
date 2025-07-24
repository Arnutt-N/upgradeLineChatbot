@echo off
cd /d "D:\hrProject\upgradeLineChatbot"

echo ========================================
echo 🧪 Complete System Testing
echo ========================================
echo 📍 Project Directory: %CD%
echo ⏰ Test Time: %DATE% %TIME%
echo ========================================

echo.
echo 🔍 Pre-test Checks...
echo   • Checking if server is running...
curl -s http://127.0.0.1:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Server is running
) else (
    echo     ❌ Server not running!
    echo     💡 Please start server with: .\start_enhanced_system.bat
    echo     🔄 Testing will continue anyway...
)

echo   • Installing test dependencies...
pip install websockets aiohttp --quiet > nul 2>&1

echo.
echo 🧪 Running Comprehensive Tests...
echo ========================================
python test_complete_system.py

echo.
echo ========================================
echo 🏁 Testing Complete
echo ========================================
echo 📊 Review the results above for system health
echo 💡 Check recommendations if any tests failed
echo ✨ Your Enhanced Admin Panel should now work perfectly!
echo.
pause
