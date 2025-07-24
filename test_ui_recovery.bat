@echo off
cd /d "D:\hrProject\upgradeLineChatbot"

echo ========================================
echo 🔧 UI Recovery Test
echo ========================================
echo 📍 Project Directory: %CD%
echo ⏰ Test Time: %DATE% %TIME%
echo ========================================

echo.
echo 🔍 Testing UI Recovery...
python test_ui_recovery.py

echo.
echo ========================================
echo 🏁 UI Recovery Test Complete
echo ========================================
pause
