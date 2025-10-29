@echo off
chcp 65001 >nul
title TRAIN MODEL ONLY - OPTIMIZED

echo.
echo ========================================================================
echo   TRAIN MODEL ONLY - SKIP LOAD ^& INDEX
echo ========================================================================
echo.
echo   Strategy:
echo      - Load indexed_df from checkpoint (instant!)
echo      - Train model with NEW parameters
echo      - Generate submission
echo.
echo   Time: ~15-20 minutes (no data loading!)
echo ========================================================================
echo.

echo [1/3] Checking workers...
docker ps --filter "name=spark-worker" --filter "status=running" >nul 2>&1
if errorlevel 1 (
    echo    [X] Workers not running! Run MAIN_MENU.bat ^> [1] START first
    pause
    exit /b 1
)
echo    [OK] Workers ready

echo.
echo [2/3] Copying Python file...
docker cp "code python/spotify_rec_optimized_tangchinhxac.py" gui-docker-spark-worker-1:/tmp/
if errorlevel 1 (
    echo    [X] Failed to copy file
    pause
    exit /b 1
)
echo    [OK] File copied

echo.
echo [3/3] Starting TRAIN-ONLY job...
echo.
echo    Loading indexed_df from checkpoint...
echo    Training with YOUR NEW parameters...
echo.

docker exec -it gui-docker-spark-worker-1 /spark/bin/spark-submit ^
    --master spark://spark-master:7077 ^
    /tmp/spotify_rec_optimized_tangchinhxac.py ^
    --checkpoint_dir hdfs://namenode:8020/checkpoints/ ^
    --model_path hdfs://namenode:8020/output/model/als_model ^
    --submission_path hdfs://namenode:8020/output/submissions/submission_optimized.csv

echo.
echo ========================================================================
echo   Job finished!
echo ========================================================================
pause



