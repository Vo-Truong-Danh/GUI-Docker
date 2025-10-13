@echo off
REM Safe Start Script for Spark Runner GUI (Windows)
REM Author: System
REM Version: 4.4.3

echo ================================================================================
echo    SPARK RUNNER GUI - SAFE START (Windows)
echo ================================================================================
echo.

REM Check Python installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
python --version

REM Change to script directory
cd /d "%~dp0"

echo.
echo [INFO] Running pre-flight checks...
echo.

REM Run safe start script
python safe_start.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Pre-flight checks failed
    echo.
    pause
    exit /b 1
)

REM If we get here, app should be running
echo.
echo [INFO] Application started successfully
echo.
pause
