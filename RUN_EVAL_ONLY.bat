@echo off
chcp 65001 >nul
echo ========================================
echo     EVALUATION ONLY (Skip Training)
echo ========================================
echo.
echo Chay MAP evaluation voi model da train
echo.

docker exec gui-docker-spark-worker-2 /spark/bin/spark-submit ^
  --master spark://spark-master:7077 ^
  --deploy-mode client ^
  /tmp/spotify_rec_ULTRA_LOW_DISK.py ^
  --skip_training

echo.
echo ========================================
echo     HOAN THANH!
echo ========================================
pause



