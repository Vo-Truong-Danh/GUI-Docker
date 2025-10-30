@echo off
REM ====================================================================
REM ENHANCED HYBRID v7.0 - FAST TEST MODE
REM ====================================================================
REM Quick testing mode for development / debugging
REM Lower accuracy but much faster
REM ====================================================================

echo.
echo ========================================================================
echo ENHANCED HYBRID v7.0 - FAST TEST MODE
echo ========================================================================
echo.
echo Settings:
echo   - Rank: 80 (LOW - for speed)
echo   - MaxIter: 12 (fewer iterations)
echo   - Quick evaluation
echo.
echo Use this for:
echo   - Testing code changes
echo   - Quick iterations
echo   - Debugging
echo.
echo NOT for final submission!
echo Press Ctrl+C to cancel, or
pause

docker exec -it spark-master spark-submit ^
  --master spark://spark-master:7077 ^
  --deploy-mode client ^
  --driver-memory 3g ^
  --executor-memory 6g ^
  --executor-cores 6 ^
  --conf spark.sql.shuffle.partitions=80 ^
  --conf spark.default.parallelism=80 ^
  /opt/spark-apps/code_python/spotify_rec_hybrid_v7_enhanced.py ^
  --input_path hdfs://namenode:8020/input/data ^
  --checkpoint_base hdfs://namenode:8020/checkpoints_v7_test/ ^
  --model_path hdfs://namenode:8020/output/model_v7_test/ ^
  --indexer_path hdfs://namenode:8020/output/indexers_v7_test/ ^
  --progress_path hdfs://namenode:8020/tmp/progress_v7_test.json ^
  --metrics_path hdfs://namenode:8020/output/metrics/ ^
  --rank 80 ^
  --maxIter 12 ^
  --regParam 0.08 ^
  --alpha 40.0 ^
  --topK 500 ^
  --holdout_k 1 ^
  --min_user 5 ^
  --min_item 10 ^
  --track_weight 0.7 ^
  --artist_weight 0.3 ^
  --eval_batches 10 ^
  --export_metrics

echo.
echo ========================================================================
echo Fast test completed!
echo ========================================================================
pause

