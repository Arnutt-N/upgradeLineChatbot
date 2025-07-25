@echo off
cd /d "D:\hrProject\upgradeLineChatbot"
echo Checking current users in database...
echo.
"D:\hrProject\upgradeLineChatbot\env\Scripts\python.exe" check_users.py
echo.
pause
