@echo off
echo ================================================
echo QUICK FIX: Show Buttons - Restart GUI
echo ================================================
echo.
echo Closing GUI...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Spark Runner*" 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

echo.
echo Starting GUI with fixed layout...
cd run_spark_gui
start python main.py

echo.
echo ================================================
echo DONE!
echo ================================================
echo.
echo Buttons should now be visible at bottom!
echo.
echo Layout:
echo   - Output area: 20 lines (fixed height)
echo   - Buttons: [Copy] [Save] [Run] [Clear]
echo   - Always visible, no scrolling needed
echo.
pause
