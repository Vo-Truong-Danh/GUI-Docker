@echo off
REM ====================================================================
REM ENHANCED HYBRID v7.0 - HIGH ACCURACY SETTINGS
REM ====================================================================
REM Maximum accuracy mode - slower but best results
REM Use this for final submission / production models
REM ====================================================================

echo.
echo ========================================================================
echo ENHANCED HYBRID v7.0 - HIGH ACCURACY MODE
echo ========================================================================
echo.
echo Settings:
echo   - Rank: 200 (HIGH - more latent features)
echo   - MaxIter: 30 (more training iterations)
echo   - RegParam: 0.1 (higher regularization)
echo   - Alpha: 35.0 (optimized for implicit feedback)
echo.
echo Expected:
echo   - Best possible MAP@500
echo   - Training time: ~2-3x longer than recommended
echo   - Memory usage: ~2x baseline
echo.
echo WARNING: This will take significantly longer!
echo Press Ctrl+C to cancel, or
pause

docker exec -it spark-master spark-submit ^
  --master spark://spark-master:7077 ^
  --deploy-mode client ^
  --driver-memory 4g ^
  --executor-memory 8g ^
  --executor-cores 6 ^
  --conf spark.sql.shuffle.partitions=160 ^
  --conf spark.default.parallelism=160 ^
  /opt/spark-apps/code_python/spotify_rec_hybrid_v7_enhanced.py ^
  --input_path hdfs://namenode:8020/input/data ^
  --checkpoint_base hdfs://namenode:8020/checkpoints_v7/ ^
  --model_path hdfs://namenode:8020/output/model_v7_high/ ^
  --indexer_path hdfs://namenode:8020/output/indexers_v7/ ^
  --progress_path hdfs://namenode:8020/tmp/progress_v7_high.json ^
  --metrics_path hdfs://namenode:8020/output/metrics/ ^
  --rank 200 ^
  --maxIter 30 ^
  --regParam 0.1 ^
  --alpha 35.0 ^
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
echo High accuracy training completed!
echo ========================================================================
pause

