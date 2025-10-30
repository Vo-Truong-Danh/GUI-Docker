@echo off
REM ====================================================================
REM COMPARE v6 vs v7 PERFORMANCE
REM ====================================================================
REM This script trains both v6 and v7 with same settings for comparison
REM ====================================================================

echo.
echo ========================================================================
echo COMPARE v6 vs v7 PERFORMANCE
echo ========================================================================
echo.
echo This will:
echo   1. Train v6 (baseline) with standard settings
echo   2. Train v7 (enhanced) with same base settings
echo   3. Compare MAP scores
echo.
echo Total time: ~2-3 hours (depending on data size)
echo.
pause

echo.
echo ========================================================================
echo [1/2] Training v6 BASELINE...
echo ========================================================================
echo.

docker exec -it spark-master spark-submit ^
  --master spark://spark-master:7077 ^
  --deploy-mode client ^
  --driver-memory 3g ^
  --executor-memory 6g ^
  --executor-cores 6 ^
  /opt/spark-apps/code_python/spotify_rec_hybrid_v6.py ^
  --input_path hdfs://namenode:8020/input/data ^
  --checkpoint_base hdfs://namenode:8020/checkpoints_v6_compare/ ^
  --model_path hdfs://namenode:8020/output/model_v6_compare/als_model ^
  --rank 100 ^
  --maxIter 25 ^
  --regParam 0.05 ^
  --alpha 50.0 ^
  --topK 500 ^
  --export_metrics

echo.
echo ========================================================================
echo [2/2] Training v7 ENHANCED...
echo ========================================================================
echo.

docker exec -it spark-master spark-submit ^
  --master spark://spark-master:7077 ^
  --deploy-mode client ^
  --driver-memory 3g ^
  --executor-memory 6g ^
  --executor-cores 6 ^
  /opt/spark-apps/code_python/spotify_rec_hybrid_v7_enhanced.py ^
  --input_path hdfs://namenode:8020/input/data ^
  --checkpoint_base hdfs://namenode:8020/checkpoints_v7_compare/ ^
  --model_path hdfs://namenode:8020/output/model_v7_compare/ ^
  --rank 100 ^
  --maxIter 25 ^
  --regParam 0.08 ^
  --alpha 40.0 ^
  --topK 500 ^
  --track_weight 0.7 ^
  --artist_weight 0.3 ^
  --export_metrics

echo.
echo ========================================================================
echo COMPARISON COMPLETE!
echo ========================================================================
echo.
echo Check metrics at: hdfs://namenode:8020/output/metrics/
echo.
echo To view metrics:
echo   docker exec -it namenode hdfs dfs -ls /output/metrics/
echo   docker exec -it namenode hdfs dfs -cat /output/metrics/metrics_*.json
echo.
pause

