@echo off
echo ================================================
echo RESTART GUI - V8.3 Enhanced with Buttons
echo ================================================
echo.
echo Closing any running Python GUI...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting GUI...
cd run_spark_gui
start python main.py

echo.
echo ================================================
echo GUI Started!
echo ================================================
echo.
echo Check for buttons:
echo   [Copy Code] [Save to File] [Run Code] [Clear]
echo.
echo If buttons still not visible:
echo   1. Generate some code first
echo   2. Scroll down in output area
echo   3. Resize window to see bottom
echo.
pause
