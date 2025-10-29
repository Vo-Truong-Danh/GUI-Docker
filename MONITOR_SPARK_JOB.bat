@echo off
REM ================================================================
REM MONITOR SPARK JOB PROGRESS
REM ================================================================

:LOOP
cls
echo ================================================================
echo  📊 SPARK JOB MONITOR - %date% %time%
echo ================================================================
echo.

REM Check if job is still running
docker exec gui-docker-spark-worker-1 sh -c "ps aux | grep -E 'spark-submit|SpotifyRecs' | grep -v grep" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Spark job is NOT running!
    echo.
    echo Last 30 lines of log:
    docker exec gui-docker-spark-worker-1 tail -30 /tmp/spark_job.log
    pause
    exit /b 1
)

echo ✅ Spark job is RUNNING
echo.

REM Show last 25 lines of log
echo ================================================================
echo  📝 RECENT LOG OUTPUT:
echo ================================================================
docker exec gui-docker-spark-worker-1 tail -25 /tmp/spark_job.log
echo.

echo ================================================================
echo  💡 Commands:
echo     - Open Spark UI: http://localhost:4041
echo     - Full log: docker exec gui-docker-spark-worker-1 cat /tmp/spark_job.log
echo     - Press Ctrl+C to exit monitor
echo ================================================================
echo.
echo Auto-refreshing in 30 seconds...
timeout /t 30 /nobreak
goto LOOP


