@echo off
chcp 65001 >nul
title START FRESH - Train from Scratch

echo.
echo ========================================================================
echo   START FRESH TRAINING - Clean Slate
echo ========================================================================
echo.
echo   This will:
echo      - Keep input data (33GB)
echo      - Keep checkpoints (raw_data, indexed_data) for fast loading
echo      - DELETE old model
echo      - DELETE progress tracker
echo      - Train NEW model with parameters below
echo.
echo   Default Parameters:
echo      - Rank: 50
echo      - Alpha: 40.0
echo      - RegParam: 0.1
echo      - MaxIter: 20
echo.
echo   Result: Only MAP score (no submission file)
echo   Time: ~2min load + ~15-20min train = ~20min total
echo ========================================================================
echo.
pause

echo.
echo [1/4] Deleting old model...
docker exec namenode hdfs dfs -rm -r /output/model/als_model 2>nul
if errorlevel 1 (
    echo    [i] No old model found - OK
) else (
    echo    [OK] Model deleted
)

echo.
echo [2/4] Clearing progress tracker...
docker exec gui-docker-spark-worker-1 rm -f /tmp/progress.json 2>nul
docker exec gui-docker-spark-worker-2 rm -f /tmp/progress.json 2>nul
echo    [OK] Progress cleared

echo.
echo [3/4] Copying latest code...
docker cp "code python/spotify_rec_optimized_tangchinhxac.py" gui-docker-spark-worker-1:/tmp/
if errorlevel 1 (
    echo    [X] Failed to copy
    pause
    exit /b 1
)
echo    [OK] Code updated

echo.
echo [4/4] Starting training...
echo    Loading data from checkpoints (fast)...
echo    Training with default params...
echo.
echo ========================================================================

docker exec -it gui-docker-spark-worker-1 /spark/bin/spark-submit ^
    --master spark://spark-master:7077 ^
    /tmp/spotify_rec_optimized_tangchinhxac.py

echo.
echo ========================================================================
echo   Training finished!
echo   Check MAP score above
echo ========================================================================
echo.
echo   To retrain with DIFFERENT parameters, run:
echo      - RETRAIN_rank60.bat  (moderate)
echo      - RETRAIN_rank80.bat  (aggressive)
echo      - RETRAIN_rank100.bat (maximum)
echo.
pause



