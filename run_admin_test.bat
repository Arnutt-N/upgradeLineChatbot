@echo off
echo ========================================
echo Admin Panel Fixes Test Runner
echo ========================================
echo.

echo Checking if server is running...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/health > temp_status.txt
set /p STATUS=<temp_status.txt
del temp_status.txt

if "%STATUS%"=="200" (
    echo ✅ Server is running at http://127.0.0.1:8000
    echo.
    echo Starting admin panel tests...
    echo.
    python test_admin_panel_fixes.py
) else (
    echo ❌ Server is not running at http://127.0.0.1:8000
    echo.
    echo Please start the server first:
    echo   python app/main.py
    echo.
    echo Or:
    echo   python run_server.py
    echo.
    pause
)

echo.
echo Test completed. Press any key to exit...
pause > nul