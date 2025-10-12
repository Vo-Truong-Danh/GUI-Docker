@echo off
REM Spark Runner GUI - Quick Launcher
REM Double-click this file to run the application

echo ========================================
echo  Spark Runner GUI - Enhanced
echo ========================================
echo.
echo Starting application...
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application!
    echo.
    echo Possible reasons:
    echo - Python is not installed or not in PATH
    echo - Tkinter module is missing
    echo.
    echo Please check your Python installation.
    pause
)
