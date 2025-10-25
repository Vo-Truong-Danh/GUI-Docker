@echo off
echo ============================================
echo   Dashboard 3D - Quick Start Script
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/3] Starting HTTP Server...
echo Dashboard URL: http://localhost:8000/unified_dashboard_3d.html
echo.
echo Press Ctrl+C to stop server
echo.

python -m http.server 8000

pause
