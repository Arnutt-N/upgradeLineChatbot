@echo off
cd /d "D:\hrProject\upgradeLineChatbot"
echo Running avatar backfill script...
echo.
"D:\hrProject\upgradeLineChatbot\env\Scripts\python.exe" backfill_avatars_simple.py
echo.
echo Script completed.
pause
