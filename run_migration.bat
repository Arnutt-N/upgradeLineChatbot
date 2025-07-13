@echo off
echo =====================================
echo Database Migration Script
echo =====================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)

echo Python found!
echo.

echo Current directory: %CD%
echo.

echo Do you want to create a backup before migration? (y/n)
set /p backup_choice="Enter choice: "

if /i "%backup_choice%"=="y" (
    echo Running migration with backup...
    python run_migration.py --backup
) else (
    echo Running migration without backup...
    python run_migration.py
)

echo.
echo =====================================
if errorlevel 1 (
    echo Migration FAILED!
    echo Please check the error messages above.
) else (
    echo Migration COMPLETED successfully!
    echo Your database has been upgraded.
)
echo =====================================
echo.
pause
