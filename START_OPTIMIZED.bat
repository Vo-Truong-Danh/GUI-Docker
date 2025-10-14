@echo off
REM ========================================
REM Spark Runner GUI - Quick Start Script
REM With Enhanced System Optimization
REM ========================================

echo.
echo ================================================
echo   SPARK RUNNER GUI - QUICK START
echo   With System Optimization
echo ================================================
echo.

cd /d "%~dp0run_spark_gui"

REM Check if system analysis should run
set /p ANALYZE="Run system analysis first? (y/n): "

if /i "%ANALYZE%"=="y" (
    echo.
    echo [1/3] Running System Analysis...
    python analyze_system.py
    
    echo.
    echo Press any key to continue to health dashboard...
    pause >nul
)

REM Ask if health monitoring dashboard should be shown
set /p DASHBOARD="Open Health Monitoring Dashboard? (y/n): "

if /i "%DASHBOARD%"=="y" (
    echo.
    echo [2/3] Starting Health Monitoring Dashboard...
    start python health_monitoring_dashboard.py
    
    timeout /t 2 >nul
)

REM Start main GUI
echo.
echo [3/3] Starting Main Application...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to start application
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Check if Python is installed
    echo 2. Check if all dependencies are installed
    echo 3. Run: pip install -r requirements.txt
    echo 4. Check logs in: run_spark_gui/logs/
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo Application closed successfully
    echo ========================================
)

echo.
pause
