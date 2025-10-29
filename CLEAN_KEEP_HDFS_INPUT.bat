@echo off
REM ============================================================================
REM CLEAN DOCKER - Keep HDFS Input Data (No Backup/Restore!)
REM ============================================================================

echo.
echo ========================================================================
echo   CLEAN DOCKER - Keep HDFS Input Data (No Backup/Restore!)
echo ========================================================================
echo.
echo   This will:
echo   [1] Delete stopped containers
echo   [2] Delete unused volumes
echo   [3] Delete unused images
echo   [4] Keep RUNNING containers and /input/data in HDFS
echo   [5] Compact VHDX
echo.
echo   Input data stays in HDFS - NO NEED to re-upload!
echo.
echo   Will free: ~200 GB on C: drive
echo.
echo ========================================================================
choice /C YN /M "Continue? (Y/N): "
if errorlevel 2 exit /b

REM ============================================================================
REM STEP 1: CLEAN DOCKER (keep running containers)
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 1/5: Cleaning Docker (keep running containers)...
echo ========================================================================
echo.
echo   Make sure Docker Desktop is running!
echo   Press any key when ready...
pause

echo.
echo [1.1] Removing stopped containers...
docker container prune -f

echo [1.2] Removing unused volumes...
docker volume prune -f

echo [1.3] Removing dangling images only (keep custom images)...
docker image prune -f

echo [1.4] System prune (keep images)...
docker system prune -f --volumes

echo.
echo [OK] Docker cleaned (running containers kept)
timeout /t 3 /nobreak >nul

REM ============================================================================
REM STEP 2: STOP CONTAINERS
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 2/5: Stopping containers...
echo ========================================================================

docker-compose down
timeout /t 5 /nobreak >nul

echo [OK] Containers stopped

REM ============================================================================
REM STEP 3: STOP DOCKER
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 3/5: Stop Docker Desktop
echo ========================================================================
echo.
echo   1. Right-click Docker icon - Quit Docker Desktop
echo   2. Wait until icon disappears completely
echo   3. Press any key here
echo.
pause

echo Waiting 10 seconds for full shutdown...
timeout /t 10 /nobreak >nul

REM ============================================================================
REM STEP 4: COMPACT VHDX
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 4/5: Compacting VHDX...
echo ========================================================================
echo.
echo   This will take 10-15 minutes. Please wait...
echo.

set VHDX_PATH=C:\Users\Pls\AppData\Local\Docker\wsl\disk\docker_data.vhdx

echo Before:
powershell -Command "Get-Item '%VHDX_PATH%' | Select @{N='Size (GB)';E={[math]::Round($_.Length/1GB,2)}}"
echo.

echo select vdisk file="%VHDX_PATH%" > %TEMP%\compact.txt
echo compact vdisk >> %TEMP%\compact.txt
echo exit >> %TEMP%\compact.txt

diskpart /s %TEMP%\compact.txt

del %TEMP%\compact.txt

echo.
echo After:
powershell -Command "Get-Item '%VHDX_PATH%' | Select @{N='Size (GB)';E={[math]::Round($_.Length/1GB,2)}}"

echo.
echo [OK] VHDX compacted
timeout /t 3 /nobreak >nul

REM ============================================================================
REM STEP 5: RESTART
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 5/5: Restart Docker
echo ========================================================================
echo.
echo   1. Open Docker Desktop from Start Menu
echo   2. Wait for "Engine running"
echo   3. Press any key here
echo.
pause

echo Starting containers...
docker-compose up -d
timeout /t 15 /nobreak >nul

echo.
echo [OK] Containers started

REM ============================================================================
REM VERIFICATION
REM ============================================================================
echo.
echo ========================================================================
echo   VERIFICATION
echo ========================================================================
echo.

echo [1] VHDX size:
powershell -Command "Get-Item '%VHDX_PATH%' | Select @{N='Size (GB)';E={[math]::Round($_.Length/1GB,2)}}"

echo.
echo [2] C: drive free space:
powershell -Command "Get-PSDrive C | Select @{N='Free (GB)';E={[math]::Round($_.Free/1GB,2)}}"

echo.
echo [3] Input data still in HDFS:
docker exec namenode hdfs dfs -du -s -h /input/data/

echo.
echo ========================================================================
echo   [OK] CLEAN COMPLETE!
echo ========================================================================
echo.
echo   If VHDX did NOT shrink much, it means Docker still has data.
echo   Run CHECK_DOCKER_DATA.bat to see what's using space.
echo.
pause

