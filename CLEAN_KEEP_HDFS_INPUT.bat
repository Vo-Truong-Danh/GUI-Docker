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
echo   Forcefully stopping all Docker processes...
echo.

REM Stop Docker Desktop service
net stop com.docker.service 2>nul

REM Kill all Docker-related processes
echo   [3.1] Stopping Docker Desktop...
taskkill /F /IM "Docker Desktop.exe" 2>nul
timeout /t 3 /nobreak >nul

echo   [3.2] Stopping Docker backend services...
taskkill /F /IM com.docker.backend.exe 2>nul
taskkill /F /IM com.docker.vpnkit.exe 2>nul
taskkill /F /IM com.docker.proxy.exe 2>nul
timeout /t 3 /nobreak >nul

echo   [3.3] Stopping WSL Docker processes...
wsl --shutdown
timeout /t 5 /nobreak >nul

echo   [3.4] Verifying all processes stopped...
timeout /t 10 /nobreak >nul

REM Double-check critical processes are gone
tasklist /FI "IMAGENAME eq com.docker.backend.exe" 2>NUL | find /I /N "com.docker.backend.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo   WARNING: Docker backend still running, waiting 10 more seconds...
    timeout /t 10 /nobreak >nul
)

echo.
echo   [OK] Docker fully stopped

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

REM Verify VHDX file exists
if not exist "%VHDX_PATH%" (
    echo   ERROR: VHDX file not found at: %VHDX_PATH%
    echo   Please check your Docker Desktop installation.
    pause
    exit /b 1
)

REM Get size before compaction
echo Before:
for /f "tokens=*" %%a in ('powershell -Command "[math]::Round((Get-Item '%VHDX_PATH%').Length/1GB,2)"') do set SIZE_BEFORE=%%a
echo   Size: %SIZE_BEFORE% GB
echo.

REM Create DiskPart script
echo select vdisk file="%VHDX_PATH%" > %TEMP%\compact.txt
echo compact vdisk >> %TEMP%\compact.txt
echo exit >> %TEMP%\compact.txt

echo   Running DiskPart (this takes 10-15 minutes)...
echo.
diskpart /s %TEMP%\compact.txt

REM Check if DiskPart succeeded
if errorlevel 1 (
    echo.
    echo   ================================================================
    echo   ERROR: VHDX compaction FAILED!
    echo   ================================================================
    echo.
    echo   Possible causes:
    echo   1. Docker processes still running (check Task Manager)
    echo   2. VHDX file is locked by another process
    echo   3. Insufficient permissions
    echo.
    echo   What to do:
    echo   1. Open Task Manager
    echo   2. Kill all "Docker" and "com.docker.*" processes
    echo   3. Run: wsl --shutdown
    echo   4. Wait 30 seconds
    echo   5. Try running this script again
    echo.
    del %TEMP%\compact.txt
    pause
    exit /b 1
)

del %TEMP%\compact.txt

REM Get size after compaction
echo.
echo After:
for /f "tokens=*" %%a in ('powershell -Command "[math]::Round((Get-Item '%VHDX_PATH%').Length/1GB,2)"') do set SIZE_AFTER=%%a
echo   Size: %SIZE_AFTER% GB
echo.

REM Calculate space saved
powershell -Command "$before=%SIZE_BEFORE%; $after=%SIZE_AFTER%; $saved=[math]::Round($before-$after,2); Write-Host '  Space Saved:' $saved 'GB'"

echo.
echo [OK] VHDX compacted successfully!
timeout /t 3 /nobreak >nul

REM ============================================================================
REM STEP 5: RESTART
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 5/5: Restart Docker
echo ========================================================================
echo.
echo   [5.1] Starting Docker Desktop...
echo.

REM Start Docker Desktop
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo   Waiting for Docker to initialize (this takes 30-60 seconds)...
timeout /t 30 /nobreak >nul

REM Wait for Docker to be ready (check every 5 seconds, max 2 minutes)
set DOCKER_WAIT=0
:DOCKER_WAIT_LOOP
docker info >nul 2>&1
if errorlevel 1 (
    if %DOCKER_WAIT% GEQ 24 (
        echo.
        echo   WARNING: Docker not responding after 2 minutes!
        echo   Please check Docker Desktop manually.
        pause
        goto DOCKER_READY
    )
    echo   Still waiting... (%DOCKER_WAIT%/24 checks^)
    timeout /t 5 /nobreak >nul
    set /a DOCKER_WAIT+=1
    goto DOCKER_WAIT_LOOP
)

:DOCKER_READY
echo.
echo   [OK] Docker is running!
echo.

echo   [5.2] Starting containers...
docker-compose up -d
timeout /t 15 /nobreak >nul

echo.
echo   [OK] Containers started

REM ============================================================================
REM VERIFICATION
REM ============================================================================
echo.
echo ========================================================================
echo   VERIFICATION
echo ========================================================================
echo.

echo [1] VHDX final size:
for /f "tokens=*" %%a in ('powershell -Command "[math]::Round((Get-Item '%VHDX_PATH%').Length/1GB,2)"') do set SIZE_FINAL=%%a
echo   %SIZE_FINAL% GB

echo.
echo [2] C: drive status:
powershell -Command "Get-PSDrive C | Format-Table @{N='Used (GB)';E={[math]::Round($_.Used/1GB,2)}}, @{N='Free (GB)';E={[math]::Round($_.Free/1GB,2)}}, @{N='Total (GB)';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}} -AutoSize"

echo.
echo [3] Docker system status:
docker system df

echo.
echo [4] Containers running:
docker ps --format "table {{.Names}}\t{{.Status}}"

echo.
echo [5] HDFS input data:
docker exec namenode hdfs dfs -du -s -h /input/data/ 2>nul
if errorlevel 1 (
    echo   ⚠️ Cannot check HDFS - namenode might still be starting
    echo   Wait 1-2 minutes and run: docker exec namenode hdfs dfs -ls /input/data/
)

echo.
echo ========================================================================
echo   COMPACTION SUMMARY
echo ========================================================================
echo.
powershell -Command "$before=%SIZE_BEFORE%; $after=%SIZE_FINAL%; $saved=[math]::Round($before-$after,2); Write-Host '  Before:' $before 'GB'; Write-Host '  After: ' $after 'GB'; Write-Host '  Saved: ' $saved 'GB'; Write-Host ''; if ($saved -lt 50) { Write-Host '  ⚠️ WARNING: Less than 50 GB saved!' -ForegroundColor Yellow; Write-Host '  Docker may still have data. Run: docker system df -v' -ForegroundColor Yellow } else { Write-Host '  ✅ SUCCESS! Freed significant space!' -ForegroundColor Green }"

echo.
echo ========================================================================
echo   [OK] CLEAN COMPLETE!
echo ========================================================================
echo.
echo   Next steps:
echo   - Verify your Spark jobs still work
echo   - Check HDFS data: MAIN_MENU.bat - Option 8 (System Info)
echo.
echo   Troubleshooting:
echo   - If VHDX didn't shrink: See COMPACT_DISK_TROUBLESHOOTING.md
echo   - Check what's using space: docker system df -v
echo.
pause

