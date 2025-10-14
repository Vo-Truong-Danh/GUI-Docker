@echo off
echo ================================================
echo COMPACT UI - More Space for Output
echo ================================================
echo.
echo Changes:
echo - Removed "Your Question" section with examples
echo - Input and Generate button in ONE line
echo - More space for output area (25 lines)
echo - Buttons always visible at bottom
echo.
echo Closing GUI...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Spark Runner*" 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

echo.
echo Starting compact GUI...
cd run_spark_gui
start python main.py

echo.
echo ================================================
echo DONE!
echo ================================================
echo.
echo New layout:
echo   [Input field..................] [Generate]
echo   Output area: 25 lines (scrollable)
echo   [Copy] [Save] [Run] [Clear] - Always visible
echo.
pause
