@echo off
REM ========================================
REM   Copy ML Analysis Results to dist
REM   Purpose: Copy tmp folder with all images and JSON data
REM ========================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    Copy ML Analysis Results
echo ========================================
echo.

REM Check if tmp folder exists
if not exist tmp (
    echo ERROR: tmp folder not found!
    echo Please run code7.py first to generate ML analysis results
    echo.
    pause
    exit /b 1
)

REM Check if dist folder exists
if not exist dist (
    echo ERROR: dist folder not found!
    echo Please build the application first with build.bat or build.ps1
    echo.
    pause
    exit /b 1
)

echo [1/3] Analyzing tmp folder...

REM Count PNG files
for /f %%A in ('dir /b /a-d tmp\*.png 2^>nul ^| find /c /v ""') do set PNG_COUNT=%%A
echo    PNG files found: %PNG_COUNT%

REM Count JSON files
for /f %%A in ('dir /b /a-d tmp\*.json 2^>nul ^| find /c /v ""') do set JSON_COUNT=%%A
echo    JSON files found: %JSON_COUNT%

echo    Files ready to copy
echo.

echo [2/3] Copying to dist folder...

REM Remove old dist\tmp if exists
if exist dist\tmp (
    echo    Removing old dist\tmp folder...
    rmdir /s /q dist\tmp
)

REM Create dist\tmp
mkdir dist\tmp >nul 2>&1

REM Copy tmp folder
echo    Copying tmp folder to dist...
xcopy tmp dist\tmp /s /y /i >nul 2>&1

if %errorlevel% equ 0 (
    echo    Copy completed successfully!
) else (
    echo    ERROR: Copy failed!
    pause
    exit /b 1
)
echo.

echo [3/3] Verifying files...

REM Verify
for /f %%A in ('dir /b /a-d dist\tmp\*.png 2^>nul ^| find /c /v ""') do set DIST_PNG=%%A
for /f %%A in ('dir /b /a-d dist\tmp\*.json 2^>nul ^| find /c /v ""') do set DIST_JSON=%%A

echo    PNG files in dist: !DIST_PNG!
echo    JSON files in dist: !DIST_JSON!

echo.
echo ========================================
echo    COPY SUCCESSFUL!
echo ========================================
echo.
echo Files copied to: dist\tmp\
echo.
echo Next steps:
echo    1. Open: dist\unified_dashboard.html
echo    2. The dashboard will automatically load the JSON data
echo    3. All ML visualizations will be displayed
echo.

pause
