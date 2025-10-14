@echo off
REM Restart GUI with AI Engine V8.3

echo ========================================
echo   Restarting GUI with AI Engine V8.3
echo ========================================
echo.

REM Kill existing Python GUI processes
echo Stopping existing GUI processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Spark*" 2>nul
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq Spark*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting GUI with AI Engine V8.3...
echo.

REM Start GUI
cd /d "%~dp0run_spark_gui"
start "Spark Runner GUI V8.3" python main.py

echo.
echo ✅ GUI started successfully!
echo.
echo Tab "AI Engine V8.3" should now be visible.
echo.
pause
