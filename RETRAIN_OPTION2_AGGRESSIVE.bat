@echo off
chcp 65001 >nul
title Retrain Model - Aggressive (Rank 80)
cls

echo.
echo ========================================================================
echo   RETRAIN MODEL - AGGRESSIVE
echo ========================================================================
echo.
echo   Parameters:
echo      - Rank: 80 (was 50)
echo      - RegParam: 0.05 (was 0.1)
echo      - Alpha: 50.0 (was 40.0)
echo      - MaxIter: 30 (was 20)
echo.
echo   Expected:
echo      - MAP@500: ~7-8%% (was 5.59%%)
echo      - Train time: ~15 minutes
echo      - May need more RAM
echo.
echo   Note: Will SKIP loading/indexing (fast start!)
echo.
echo ========================================================================
echo.
pause

echo.
echo [1/2] Checking containers...
docker ps --filter "name=namenode" --format "{{.Names}}" | findstr "namenode" >nul
if errorlevel 1 (
    echo.
    echo [X] Containers not running!
    echo    Please start containers first:
    echo    MAIN_MENU.bat -^> [2] START APPLICATION
    pause
    exit /b 1
)

echo    [OK] Containers running
echo.
echo [2/3] Copying Python file to container...
docker cp "code python/spotify_rec_optimized_tangchinhxac.py" gui-docker-spark-worker-1:/tmp/

if errorlevel 1 (
    echo.
    echo [X] Failed to copy file!
    pause
    exit /b 1
)

echo    [OK] File copied
echo.
echo [3/3] Starting Spark job...
echo.
echo    Submitting to Spark Master...
echo.

docker exec -it gui-docker-spark-worker-1 /spark/bin/spark-submit ^
  --master spark://spark-master:7077 ^
  /tmp/spotify_rec_optimized_tangchinhxac.py ^
  --force_retrain ^
  --rank 80 ^
  --regParam 0.05 ^
  --alpha 50.0 ^
  --maxIter 30

echo.
echo ========================================================================
echo   Job finished!
echo ========================================================================
pause

