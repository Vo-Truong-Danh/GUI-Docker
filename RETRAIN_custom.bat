@echo off
chcp 65001 >nul
title RETRAIN - Custom Parameters

echo.
echo ========================================================================
echo   QUICK RETRAIN - Custom Parameters
echo ========================================================================
echo.
echo   Enter your parameters below:
echo   (Press Enter to use default values)
echo.

set /p RANK="Rank [default: 50]: "
if "%RANK%"=="" set RANK=50

set /p ALPHA="Alpha [default: 40.0]: "
if "%ALPHA%"=="" set ALPHA=40.0

set /p REGPARAM="RegParam [default: 0.1]: "
if "%REGPARAM%"=="" set REGPARAM=0.1

set /p MAXITER="MaxIter [default: 20]: "
if "%MAXITER%"=="" set MAXITER=20

echo.
echo ========================================================================
echo   Your Parameters:
echo      - Rank: %RANK%
echo      - Alpha: %ALPHA%
echo      - RegParam: %REGPARAM%
echo      - MaxIter: %MAXITER%
echo ========================================================================
echo.
pause

echo [1/2] Deleting old model...
docker exec namenode hdfs dfs -rm -r /output/model/als_model
echo    [OK] Model deleted

echo.
echo [2/2] Training with your parameters...
echo.

docker exec -it gui-docker-spark-worker-1 /spark/bin/spark-submit ^
    --master spark://spark-master:7077 ^
    /tmp/spotify_rec_optimized_tangchinhxac.py ^
    --rank %RANK% ^
    --alpha %ALPHA% ^
    --regParam %REGPARAM% ^
    --maxIter %MAXITER%

echo.
echo ========================================================================
echo   Training finished! Check MAP score above
echo ========================================================================
pause



