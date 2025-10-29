@echo off
chcp 65001 >nul
title RETRAIN - Rank 100 (Maximum)

echo.
echo ========================================================================
echo   QUICK RETRAIN - Rank 100 (Maximum Performance)
echo ========================================================================
echo.
echo   Parameters:
echo      - Rank: 100 (was 50)
echo      - Alpha: 60.0 (was 40.0)
echo      - RegParam: 0.03 (was 0.1)
echo      - MaxIter: 35 (was 20)
echo.
echo   Expected MAP: ~8.0-8.5%%
echo   Time: ~25-30 minutes (NO data loading!)
echo   RAM: High memory usage - may crash if insufficient RAM
echo ========================================================================
echo.
echo   WARNING: This uses maximum resources!
echo            Monitor RAM usage carefully.
echo.
pause

echo [1/2] Deleting old model...
docker exec namenode hdfs dfs -rm -r /output/model/als_model
echo    [OK] Model deleted

echo.
echo [2/2] Training with new parameters...
echo.

docker exec -it gui-docker-spark-worker-1 /spark/bin/spark-submit ^
    --master spark://spark-master:7077 ^
    /tmp/spotify_rec_optimized_tangchinhxac.py ^
    --rank 100 ^
    --alpha 60.0 ^
    --regParam 0.03 ^
    --maxIter 35

echo.
echo ========================================================================
echo   Training finished! Check MAP score above
echo ========================================================================
pause



