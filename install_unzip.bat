@echo off
REM Install unzip in namenode container
REM Run this script to manually install unzip

echo ============================================================
echo Installing unzip in namenode container...
echo ============================================================
echo.

echo Step 1/3: Checking if container is running...
docker ps -q -f name=namenode >nul 2>&1
if errorlevel 1 (
    echo [ERROR] namenode container is not running!
    echo Please start Docker and namenode container first.
    pause
    exit /b 1
)
echo [OK] Container is running
echo.

echo Step 2/3: Updating package lists...
docker exec -u root namenode apt-get update
if errorlevel 1 (
    echo [WARNING] apt-get update failed, trying to continue...
)
echo.

echo Step 3/3: Installing unzip...
docker exec -u root namenode apt-get install -y unzip
if errorlevel 1 (
    echo [ERROR] Failed to install unzip
    echo.
    echo Possible solutions:
    echo 1. Check internet connection
    echo 2. Try: docker exec -it -u root namenode bash
    echo    Then run: apt-get update ^&^& apt-get install -y unzip
    echo 3. Check if container has enough disk space
    pause
    exit /b 1
)
echo.

echo Step 4/3: Verifying installation...
docker exec namenode which unzip
if errorlevel 1 (
    echo [ERROR] unzip not found after installation
    pause
    exit /b 1
)
echo.

echo ============================================================
echo SUCCESS! unzip has been installed successfully
echo ============================================================
echo.
echo You can now use the auto-extract feature in HDFS Upload Manager.
echo.
pause
