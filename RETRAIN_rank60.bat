@echo off
chcp 65001 >nul
title RETRAIN - Rank 60 (Moderate)

echo.
echo ========================================================================
echo   QUICK RETRAIN - Rank 60 (Moderate Performance)
echo ========================================================================
echo.
echo   Parameters:
echo      - Rank: 60 (was 50)
echo      - Alpha: 45.0 (was 40.0)
echo      - RegParam: 0.08 (was 0.1)
echo      - MaxIter: 25 (was 20)
echo.
echo   Expected MAP: ~6.0-6.5%%
echo   Time: ~15-18 minutes (NO data loading!)
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
    --rank 60 ^
    --alpha 45.0 ^
    --regParam 0.08 ^
    --maxIter 25

echo.
echo ========================================================================
echo   Training finished! Check MAP score above
echo ========================================================================
pause



