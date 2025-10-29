@echo off
chcp 65001 >nul
title Stop Spark Job
cls

echo.
echo ========================================================================
echo   STOP SPARK JOB
echo ========================================================================
echo.
echo   This will stop the currently running Spark job
echo.
echo   WARNING: Job progress will be lost!
echo   (But checkpoint data is saved every batch)
echo.
echo ========================================================================
echo.
pause

echo.
echo [1/3] Finding Spark driver process...
docker exec gui-docker-spark-worker-1 ps aux | findstr "spark-submit" >nul
if errorlevel 1 (
    echo    [!] No Spark job running
    pause
    exit /b 0
)

echo    [OK] Found Spark job
echo.
echo [2/3] Sending SIGTERM (graceful shutdown)...
docker exec gui-docker-spark-worker-1 pkill -TERM -f "spark-submit"
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Checking if stopped...
docker exec gui-docker-spark-worker-1 ps aux | findstr "spark-submit" >nul
if errorlevel 1 (
    echo    [OK] Job stopped gracefully
) else (
    echo    [!] Job still running, forcing kill...
    docker exec gui-docker-spark-worker-1 pkill -KILL -f "spark-submit"
    timeout /t 2 /nobreak >nul
    echo    [OK] Job killed
)

echo.
echo ========================================================================
echo   Job stopped successfully
echo ========================================================================
pause




