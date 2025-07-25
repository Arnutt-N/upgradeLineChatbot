@echo off
echo Starting database migration test...
echo.

cd /d "D:\hrProject\upgradeLineChatbot"
D:\hrProject\upgradeLineChatbot\env\Scripts\python.exe test_db.py

echo.
echo Test completed.
pause
