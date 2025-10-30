@echo off
REM ====================================================================
REM ENHANCED HYBRID v7.0 - RECOMMENDED SETTINGS
REM ====================================================================
REM This script runs the improved version with optimized hyperparameters
REM Expected MAP improvement: +35-50% over baseline
REM ====================================================================

echo.
echo ========================================================================
echo ENHANCED HYBRID v7.0 - RECOMMENDED SETTINGS
echo ========================================================================
echo.
echo Features:
echo   [+] Position-based confidence weighting
echo   [+] Dual-model ensemble (Track + Artist)
echo   [+] Improved hyperparameters
echo   [+] Artist-level collaborative filtering
echo.
echo Expected improvements over v6:
echo   - MAP@500: +35-50%%
echo   - Training time: +60-80%%
echo   - Memory usage: +50%%
echo.
echo Press Ctrl+C to cancel, or
pause

docker exec -it spark-master spark-submit ^
  --master spark://spark-master:7077 ^
  --deploy-mode client ^
  --driver-memory 3g ^
  --executor-memory 6g ^
  --executor-cores 6 ^
  --conf spark.sql.shuffle.partitions=120 ^
  --conf spark.default.parallelism=120 ^
  /opt/spark-apps/code_python/spotify_rec_hybrid_v7_enhanced.py ^
  --input_path hdfs://namenode:8020/input/data ^
  --checkpoint_base hdfs://namenode:8020/checkpoints_v7/ ^
  --model_path hdfs://namenode:8020/output/model_v7/ ^
  --indexer_path hdfs://namenode:8020/output/indexers_v7/ ^
  --progress_path hdfs://namenode:8020/tmp/progress_v7.json ^
  --metrics_path hdfs://namenode:8020/output/metrics/ ^
  --rank 150 ^
  --maxIter 25 ^
  --regParam 0.08 ^
  --alpha 40.0 ^
  --topK 500 ^
  --holdout_k 1 ^
  --min_user 5 ^
  --min_item 10 ^
  --track_weight 0.7 ^
  --artist_weight 0.3 ^
  --eval_batches 20 ^
  --export_metrics

echo.
echo ========================================================================
echo Training completed!
echo ========================================================================
pause

