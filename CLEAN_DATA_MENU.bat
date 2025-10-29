@echo off
REM ============================================================================
REM CLEAN DATA - MENU WITH 3 OPTIONS
REM ============================================================================
setlocal enabledelayedexpansion

:MENU
cls
echo.
echo ========================================================================
echo   CLEAN DATA - MENU
echo ========================================================================
echo.
echo   Choose cleanup level:
echo.
echo   [1] XOA HET - Delete EVERYTHING
echo       - Delete ALL data, volumes, images, containers
echo       - Fresh start, need to re-upload 31.2 GB data
echo       - Need to rebuild custom images
echo       - Free: Maximum space (~200 GB)
echo.
echo   [2] GIU CUSTOM IMAGES - Keep Custom Images Only
echo       - Delete: Data, checkpoints, outputs, old volumes
echo       - KEEP: Custom Docker images (libraries)
echo       - Need to re-upload 31.2 GB input data
echo       - Free: ~180 GB
echo.
echo   [3] GIU INPUT + IMAGES - Keep Input Data and Custom Images
echo       - Delete: Only checkpoints, outputs, old volumes
echo       - KEEP: Input 31.2 GB + Custom images
echo       - No re-upload needed
echo       - Free: ~100 GB
echo.
echo   [4] Exit
echo.
echo ========================================================================

choice /C 1234 /N /M "Select option (1-4): "
set CHOICE=%ERRORLEVEL%

if %CHOICE%==1 goto OPTION1
if %CHOICE%==2 goto OPTION2
if %CHOICE%==3 goto OPTION3
if %CHOICE%==4 goto EXIT

:OPTION1
cls
echo.
echo ========================================================================
echo   [1] XOA HET - DELETE EVERYTHING
echo ========================================================================
echo.
echo   WARNING: This will DELETE EVERYTHING!
echo.
echo   Will delete:
echo      - ALL Docker containers
echo      - ALL Docker volumes (including input 31.2 GB)
echo      - ALL Custom images (need rebuild)
echo      - ALL HDFS data
echo.
echo   Result:
echo      - Need to re-upload 31.2 GB data
echo      - Need to rebuild custom images (~30 min)
echo      - Maximum disk space freed (~200 GB)
echo.
echo ========================================================================
choice /C YN /M "Are you SURE you want to delete EVERYTHING? (Y/N)"
if errorlevel 2 goto MENU

echo.
echo [1/4] Stopping all containers...
docker-compose down

echo.
echo [2/4] Removing ALL volumes...
docker volume prune -a -f

echo.
echo [3/4] Removing ALL images...
docker image prune -a -f
docker rmi $(docker images -q) -f 2>nul

echo.
echo [4/4] Cleaning Docker system...
docker system prune -a --volumes -f

echo.
echo [OK] EVERYTHING DELETED!
echo.
echo Next steps:
echo    1. Rebuild images: docker-compose build
echo    2. Re-upload 31.2 GB input data
echo    3. Start fresh: docker-compose up -d
echo.
pause
goto MENU

:OPTION2
cls
echo.
echo ========================================================================
echo   [2] GIU CUSTOM IMAGES - Keep Custom Images Only
echo ========================================================================
echo.
echo   Will delete:
echo      - HDFS data (including /input/)
echo      - All checkpoints, outputs, logs
echo      - All Docker volumes
echo.
echo   Will KEEP:
echo      - Custom Docker images [OK]
echo      - Libraries in images [OK]
echo.
echo   Result:
echo      - Need to re-upload 31.2 GB input data
echo      - No need to rebuild images
echo      - Free: ~180 GB
echo.
echo ========================================================================
pause

echo.
echo [1/5] Stopping containers...
docker-compose down

echo.
echo [2/5] Removing ALL volumes (will delete input data)...
docker volume prune -a -f

echo.
echo [3/5] Cleaning dangling images only...
docker image prune -f

echo.
echo [4/5] Cleaning build cache...
docker builder prune -f

echo.
echo [5/5] Restarting containers...
docker-compose up -d
timeout /t 15 /nobreak >nul

echo.
echo [OK] CLEANUP COMPLETE - Custom images preserved!
echo.
echo Next steps:
echo    1. Upload 31.2 GB input data to HDFS
echo    2. Ready to run Spark jobs
echo.
pause
goto MENU

:OPTION3
cls
echo.
echo ========================================================================
echo   [3] GIU INPUT + IMAGES - Keep Input Data and Custom Images
echo ========================================================================
echo.
echo   Will delete:
echo      - HDFS checkpoints, outputs, logs
echo      - Old Docker volumes (not gui-docker_*)
echo      - Docker cache
echo.
echo   Will KEEP:
echo      - Input data 31.2 GB [OK]
echo      - Custom Docker images [OK]
echo.
echo   Result:
echo      - No re-upload needed [OK]
echo      - Ready to run immediately
echo      - Free: ~100 GB
echo.
echo ========================================================================
pause

echo.
echo [1/7] Cleaning HDFS (keeping /input/data/)...
docker exec namenode hdfs dfs -rm -r -f /tmp/checkpoints 2>nul
docker exec namenode hdfs dfs -rm -r -f /checkpoints 2>nul
docker exec namenode hdfs dfs -rm -r -f /output 2>nul
docker exec namenode hdfs dfs -rm -r -f /spark-events 2>nul
echo    [OK] HDFS cleaned

echo.
echo [2/7] Verifying input data...
docker exec namenode hdfs dfs -du -s -h /input/data/
echo    [OK] Input verified

echo.
echo [3/7] Cleaning container logs...
docker exec spark-master sh -c "rm -rf /spark/logs/*" 2>nul
docker exec gui-docker-spark-worker-1 sh -c "rm -rf /spark/logs/* /tmp/*.log /tmp/progress.json" 2>nul
echo    [OK] Logs cleaned

echo.
echo [4/7] Stopping containers...
docker-compose down
timeout /t 3 /nobreak >nul
echo    [OK] Stopped

echo.
echo [5/7] Removing OLD volumes...
for /f "tokens=2" %%V in ('docker volume ls -q ^| findstr /V "gui-docker"') do (
    docker volume rm %%V 2>nul
)
echo    [OK] Old volumes removed

echo.
echo [6/7] Cleaning cache...
docker image prune -f
docker builder prune -f
echo    [OK] Cache cleaned

echo.
echo [7/7] Restarting containers...
docker-compose up -d
timeout /t 15 /nobreak >nul
echo    [OK] Restarted

echo.
echo ========================================================================
echo   [OK] CLEANUP COMPLETE!
echo ========================================================================
echo.
docker exec namenode hdfs dfs -du -s -h /input/data/
echo.
docker images --format "{{.Repository}}:{{.Tag}} - {{.Size}}" | findstr "my-spark-worker bde2020"
echo.
echo ========================================================================
pause
goto MENU

:EXIT
echo.
echo Exiting...
exit /b 0
