@echo off
chcp 65001 >nul
title FORCE RETRAIN - Skip Load Model

echo.
echo ========================================================================
echo   FORCE RETRAIN MODEL - NEW PARAMETERS
echo ========================================================================
echo.
echo   This will:
echo      - Load indexed_df from checkpoint (fast!)
echo      - FORCE retrain model (skip loading old model)
echo      - Use NEW parameters you edited in the code
echo.
echo ========================================================================
echo.

echo [1/2] Copying Python file...
docker cp "code python/spotify_rec_optimized_tangchinhxac.py" gui-docker-spark-worker-2:/tmp/
if errorlevel 1 (
    echo [X] Failed to copy file
    pause
    exit /b 1
)
echo [OK] File copied

echo.
echo [2/2] Submitting job with --force_retrain flag...
echo.

docker exec -it gui-docker-spark-worker-2 /spark/bin/spark-submit ^
    --master spark://spark-master:7077 ^
    /tmp/spotify_rec_optimized_tangchinhxac.py ^
    --force_retrain

echo.
echo ========================================================================
echo   Job finished!
echo ========================================================================
pause

