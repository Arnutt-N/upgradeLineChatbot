@echo off
echo ==========================================
echo     LINE Bot Friend List Checker
echo ==========================================
echo.

echo Starting friend list recheck...
python recheck_friends.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Friend check failed!
    pause
    exit /b 1
)

echo.
echo ✅ Friend check completed successfully!
echo.
echo Sending current status report...
python check_current_friends.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Status report failed but friend check was successful
) else (
    echo ✅ Status report sent!
)

echo.
echo ==========================================
echo All tasks completed!
echo ==========================================
pause