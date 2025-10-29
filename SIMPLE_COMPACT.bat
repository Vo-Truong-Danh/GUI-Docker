@echo off
chcp 65001 >nul
REM ============================================================================
REM SIMPLE COMPACT - Manual Docker stop
REM ============================================================================

echo.
echo ========================================================================
echo   SIMPLE COMPACT PROCESS
echo ========================================================================
echo.
echo   STEP 1: Delete HDFS data
echo   STEP 2: YOU manually close Docker Desktop
echo   STEP 3: Script compacts VHDX
echo   STEP 4: YOU manually restart Docker Desktop
echo.
echo ========================================================================
pause

REM ============================================================================
REM STEP 1: DELETE DATA
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 1: Deleting HDFS data...
echo ========================================================================

docker exec namenode hdfs dfs -rm -r -f -skipTrash /checkpoints/ 2>nul
docker exec namenode hdfs dfs -rm -r -f -skipTrash /tmp/checkpoints/ 2>nul
docker exec namenode hdfs dfs -rm -r -f -skipTrash /output/ 2>nul
docker exec namenode hdfs dfs -rm -r -f -skipTrash /tmp/spark* 2>nul
docker exec namenode hdfs dfs -expunge 2>nul

echo.
echo ✓ Data deleted (kept /input/data/)
timeout /t 3 /nobreak >nul

REM ============================================================================
REM STEP 2: MANUAL DOCKER STOP
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 2: CLOSE DOCKER DESKTOP NOW!
echo ========================================================================
echo.
echo   1. Right-click Docker icon in system tray
echo   2. Click "Quit Docker Desktop"
echo   3. Wait until Docker icon disappears completely (30-60 seconds)
echo   4. Come back here and press any key
echo.
echo ========================================================================
pause

echo.
echo Waiting 10 more seconds to ensure Docker is fully stopped...
timeout /t 10 /nobreak

REM ============================================================================
REM STEP 3: COMPACT
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 3: Compacting VHDX...
echo ========================================================================
echo.
echo   This will take 10-15 minutes. Please wait...
echo.

set VHDX_PATH=C:\Users\Pls\AppData\Local\Docker\wsl\disk\docker_data.vhdx

echo Before:
powershell -Command "Get-Item '%VHDX_PATH%' | Select @{N='Size (GB)';E={[math]::Round($_.Length/1GB,2)}}"
echo.

REM Create DiskPart script
echo select vdisk file="%VHDX_PATH%" > %TEMP%\compact.txt
echo compact vdisk >> %TEMP%\compact.txt
echo exit >> %TEMP%\compact.txt

REM Run DiskPart
diskpart /s %TEMP%\compact.txt

del %TEMP%\compact.txt

echo.
echo After:
powershell -Command "Get-Item '%VHDX_PATH%' | Select @{N='Size (GB)';E={[math]::Round($_.Length/1GB,2)}}"

echo.
echo ✓ Compact complete!

REM ============================================================================
REM STEP 4: MANUAL RESTART
REM ============================================================================
echo.
echo ========================================================================
echo   STEP 4: START DOCKER DESKTOP NOW!
echo ========================================================================
echo.
echo   1. Open Docker Desktop from Start Menu
echo   2. Wait for "Engine running" status
echo   3. Run: docker-compose up -d
echo   4. Verify: docker exec namenode hdfs dfs -du -s -h /input/data/
echo.
echo ========================================================================
pause

echo.
echo Check C: drive free space:
powershell -Command "Get-PSDrive C | Select @{N='Free (GB)';E={[math]::Round($_.Free/1GB,2)}}"

echo.
echo ========================================================================
echo   DONE!
echo ========================================================================
pause


