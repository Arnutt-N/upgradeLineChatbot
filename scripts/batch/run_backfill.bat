@echo off
cd /d "D:\hrProject\upgradeLineChatbot"
echo Backfilling user avatars...
echo.
"D:\hrProject\upgradeLineChatbot\env\Scripts\python.exe" backfill_user_avatars.py
echo.
echo Backfill completed.
pause
