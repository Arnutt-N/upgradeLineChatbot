@echo off
cd /d "D:\hrProject\upgradeLineChatbot"

echo ========================================
echo 🧪 Testing Enhanced Admin Panel
echo ========================================
echo 📍 Project Directory: %CD%
echo ⏰ Test Time: %DATE% %TIME%  
echo ========================================

echo.
echo 🔍 Checking if server is running...
timeout /t 2 /nobreak > nul

python test_admin_panel_complete.py

echo.
echo ========================================
echo 🏁 Test completed
echo ========================================
pause
