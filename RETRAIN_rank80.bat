@echo off
chcp 65001 >nul
title RETRAIN - Rank 80 (Aggressive)

echo.
echo ========================================================================
echo   QUICK RETRAIN - Rank 80 (High Performance)
echo ========================================================================
echo.
echo   Parameters:
echo      - Rank: 80 (was 50)
echo      - Alpha: 50.0 (was 40.0)
echo      - RegParam: 0.05 (was 0.1)
echo      - MaxIter: 30 (was 20)
echo.
echo   Expected MAP: ~7.0-7.5%%
echo   Time: ~20-25 minutes (NO data loading!)
echo   RAM: May use more memory
echo ========================================================================
echo.

echo [1/2] Deleting old model...
docker exec namenode hdfs dfs -rm -r /output/model/als_model
echo    [OK] Model deleted

echo.
echo [2/2] Training with new parameters...
echo.

docker exec -it gui-docker-spark-worker-1 /spark/bin/spark-submit ^
    --master spark://spark-master:7077 ^
    /tmp/spotify_rec_optimized_tangchinhxac.py ^
    --rank 80 ^
    --alpha 50.0 ^
    --regParam 0.05 ^
    --maxIter 30

echo.
echo ========================================================================
echo   Training finished! Check MAP score above
echo ========================================================================
pause



