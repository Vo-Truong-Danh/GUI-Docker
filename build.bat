@echo off
REM ========================================
REM   Spark Runner GUI - Simple Build
REM   Version: 6.0.1
REM ========================================

echo.
echo ========================================
echo    Spark Runner GUI - Build Tool
echo    Version: 6.0.1
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

REM Install PyInstaller
echo [2/5] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller already installed
)
echo.

REM Create icon if not exists
echo [3/5] Checking icon...
if not exist icon.ico (
    echo Creating application icon...
    pip install Pillow >nul 2>&1
    python create_icon.py
    if %errorlevel% neq 0 (
        echo Warning: Could not create icon automatically
        echo You can create icon.ico manually later
    )
) else (
    echo Icon found: icon.ico
)
echo.

REM Clean previous build
echo [4/5] Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist SparkRunnerGUI.spec del /q SparkRunnerGUI.spec
echo Cleaned
echo.

REM Build
echo [5/5] Building executable...
echo This may take 2-5 minutes...
echo.

REM Check if icon exists and add to build command
set ICON_PARAM=
if exist icon.ico (
    set ICON_PARAM=--icon=icon.ico
    echo Building with icon...
) else (
    echo Building without icon...
)

REM Prefer using custom spec for lean build
if exist build_config.spec (
    pyinstaller build_config.spec --noconfirm
    goto :postbuild
)

pyinstaller ^
    --name=SparkRunnerGUI ^
    --onefile ^
    --windowed ^
    %ICON_PARAM% ^
    --add-data=docker-compose.yml;. ^
    --add-data=spark_runner_config.json;. ^
    --hidden-import=yaml ^
    --hidden-import=tkinter ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --noconfirm ^
    run_spark_gui\main.py

:postbuild

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [6/6] Copying tmp folder (images + JSON data)...
if exist tmp (
    if not exist dist\tmp (
        mkdir dist\tmp
    )
    xcopy tmp dist\tmp /s /y /i
    echo Copied: tmp folder with all ML analysis results ✓
) else (
    echo Info: tmp folder not found (will be created when running analysis)
)

echo.
echo [7/7] Verifying...
if exist dist\SparkRunnerGUI.exe (
    echo.
    echo ========================================
    echo    BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable: dist\SparkRunnerGUI.exe
    echo Data Folder: dist\tmp (with ML analysis results)
    echo.
    for %%A in (dist\SparkRunnerGUI.exe) do echo Size: %%~zA bytes
    echo.
    if exist icon.ico (
        echo Icon: Included ✓
    ) else (
        echo Icon: Not included
    )
    echo.
    echo To test: cd dist ^& SparkRunnerGUI.exe
    echo.
) else (
    echo ERROR: Executable not found!
)

pause
