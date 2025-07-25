@echo off
cd /d "D:\hrProject\upgradeLineChatbot"
echo Running comprehensive avatar system test...
echo.
"D:\hrProject\upgradeLineChatbot\env\Scripts\python.exe" test_complete_avatar_system.py
echo.
echo Test completed.
pause
