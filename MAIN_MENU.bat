@echo off
REM ============================================================================
REM MAIN MENU - Central Control for All Operations
REM ============================================================================
setlocal enabledelayedexpansion

:MAIN
cls
echo.
echo ========================================================================
echo   SPARK DOCKER MANAGEMENT - MAIN MENU
echo ========================================================================
echo.
echo   [1] CLEAN DATA (3 options: Xoa het/Giu images/Giu input+images)
echo.
echo   [2] START APPLICATION (Auto build, scale workers)
echo.
echo   [3] OPEN GUI APPLICATION (run_spark_gui/main.py)
echo.
echo   [4] RUN SPARK JOB (Fixed script)
echo.
echo   [R] RETRAIN MODEL (Skip load/index, fast retrain!)
echo.
echo   [5] MONITOR SPARK JOB (Auto-refresh)
echo.
echo   [6] STOP ALL CONTAINERS
echo.
echo   [7] COMPACT DOCKER DISK (Free ~180 GB, need Admin) [v2.0]
echo.
echo   [8] SYSTEM INFO (Disk, containers, images, volumes)
echo.
echo   [9] ADVANCED MENU (More options)
echo.
echo   [0] EXIT
echo.
echo ========================================================================

choice /C 1234R567890 /N /M "Select option (1-4, R, 5-9, 0=Exit): "
set CHOICE=%ERRORLEVEL%

if %CHOICE%==1 goto CLEAN_DATA
if %CHOICE%==2 goto START_APP
if %CHOICE%==3 goto OPEN_GUI
if %CHOICE%==4 goto RUN_JOB
if %CHOICE%==5 goto RETRAIN
if %CHOICE%==6 goto MONITOR_JOB
if %CHOICE%==7 goto STOP_ALL
if %CHOICE%==8 goto COMPACT_DISK
if %CHOICE%==9 goto SYSTEM_INFO
if %CHOICE%==10 goto ADVANCED_MENU
if %CHOICE%==11 goto EXIT

:CLEAN_DATA
call "%~dp0CLEAN_DATA_MENU.bat"
goto MAIN

:START_APP
call "%~dp0START_APP_SMART.bat"
goto MAIN

:OPEN_GUI
cls
echo.
echo ========================================================================
echo   OPENING GUI APPLICATION
echo ========================================================================
echo.
echo   Starting run_spark_gui/main.py...
echo.

cd run_spark_gui
start "" python main.py
cd ..

timeout /t 2 /nobreak >nul
echo.
echo   [OK] GUI Application started!
echo.
pause
goto MAIN

:RETRAIN
call "%~dp0RETRAIN_MENU.bat"
goto MAIN

:RUN_JOB
cls
echo.
echo ========================================================================
echo   RUNNING SPARK JOB
echo ========================================================================
echo.
echo   Copying fixed script and starting Spark job...
echo.

docker cp "code python/spotify_rec_optimized_tangchinhxac.py" gui-docker-spark-worker-1:/tmp/

docker exec -d gui-docker-spark-worker-1 bash -c "/spark/bin/spark-submit --master spark://spark-master:7077 /tmp/spotify_rec_optimized_tangchinhxac.py --reset_progress > /tmp/spark_job.log 2>&1"

timeout /t 5 /nobreak >nul

echo.
echo   [OK] Job submitted!
echo.
echo   View logs:
docker exec gui-docker-spark-worker-1 tail -30 /tmp/spark_job.log

echo.
echo   Monitor: MONITOR_SPARK_JOB.bat
echo   Spark UI: http://localhost:4040
echo.
pause
goto MAIN

:MONITOR_JOB
call "%~dp0MONITOR_SPARK_JOB.bat"
goto MAIN

:STOP_ALL
cls
echo.
echo ========================================================================
echo   STOPPING ALL CONTAINERS
echo ========================================================================
echo.

docker-compose down

echo.
echo   [OK] All containers stopped
echo.
pause
goto MAIN

:COMPACT_DISK
cls
echo.
echo ========================================================================
echo   COMPACT DOCKER DISK - Free 200GB on C: [v2.0 - FULLY AUTOMATIC]
echo ========================================================================
echo.
echo   This will:
echo   [1] Clean Docker (delete stopped containers, unused volumes/images)
echo   [2] Keep HDFS input data (NO need to re-upload!)
echo   [3] Auto-stop Docker (kills all processes automatically)
echo   [4] Compact VHDX (244GB ??? ~40GB)
echo   [5] Auto-restart Docker (starts and waits for ready)
echo.
echo   NEW in v2.0:
echo   ✅ Automatic process killing (no manual quit needed!)
echo   ✅ Verifies processes stopped before compaction
echo   ✅ Better error messages if compaction fails
echo   ✅ Shows space saved at the end
echo.
echo   Will free: ~200 GB on C: drive
echo   Time: 15-20 minutes
echo.
echo   WARNING: Requires ADMINISTRATOR privileges!
echo.
choice /C YN /M "Continue? (Y/N): "
if errorlevel 2 goto MAIN

REM Check if running as admin
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo ================================================================
    echo   NOT RUNNING AS ADMINISTRATOR
    echo ================================================================
    echo.
    echo   Please run as Administrator!
    echo   Right-click MAIN_MENU.bat - "Run as Administrator"
    echo.
    pause
    goto MAIN
)

call "%~dp0CLEAN_KEEP_HDFS_INPUT.bat"
goto MAIN

:SYSTEM_INFO
cls
echo.
echo ========================================================================
echo   SYSTEM INFORMATION
echo ========================================================================
echo.

echo   [1] C: Drive Status:
powershell -Command "Get-PSDrive C | Select-Object @{N='Used (GB)';E={[math]::Round($_.Used/1GB,2)}}, @{N='Free (GB)';E={[math]::Round($_.Free/1GB,2)}}"

echo.
echo   [2] Docker System:
docker system df

echo.
echo   [3] Containers:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

echo.
echo   [4] Images:
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"

echo.
echo   [5] Volumes:
docker volume ls

echo.
echo   [6] Input Data:
docker exec namenode hdfs dfs -du -s -h /input/data/ 2>nul

echo.
pause
goto MAIN

:ADVANCED_MENU
cls
echo.
echo ========================================================================
echo   ADVANCED MENU
echo ========================================================================
echo.
echo   [1] Verify Input Data (detailed check)
echo   [2] Clean HDFS Only (keep containers)
echo   [3] Rebuild Custom Images
echo   [4] Export/Import Images
echo   [5] View All Logs
echo   [6] Docker Prune (clean unused)
echo   [7] Reset Docker (nuclear option)
echo   [0] Back to Main Menu
echo.
echo ========================================================================

choice /C 12345670 /N /M "Select option (1-7, 0=Back): "
set ADV_CHOICE=%ERRORLEVEL%

if %ADV_CHOICE%==1 goto VERIFY_DATA
if %ADV_CHOICE%==2 goto CLEAN_HDFS_ONLY
if %ADV_CHOICE%==3 goto REBUILD_IMAGES
if %ADV_CHOICE%==4 goto EXPORT_IMPORT
if %ADV_CHOICE%==5 goto VIEW_LOGS
if %ADV_CHOICE%==6 goto DOCKER_PRUNE
if %ADV_CHOICE%==7 goto RESET_DOCKER
if %ADV_CHOICE%==8 goto MAIN
goto MAIN

:VERIFY_DATA
cls
echo.
echo   Verifying input data...
echo.
docker exec namenode hdfs dfs -ls /input/data/ | findstr "mpd.slice" | measure-object -line
docker exec namenode hdfs dfs -du -s -h /input/data/
echo.
pause
goto ADVANCED_MENU

:CLEAN_HDFS_ONLY
cls
echo.
echo   Cleaning HDFS (keeping /input/)...
echo.
docker exec namenode hdfs dfs -rm -r -f /checkpoints /output /spark-events /tmp/checkpoints
echo.
echo   [OK] Done
pause
goto ADVANCED_MENU

:REBUILD_IMAGES
cls
echo.
echo   Rebuilding custom images...
echo.
docker-compose build --no-cache
echo.
pause
goto ADVANCED_MENU

:EXPORT_IMPORT
cls
echo.
echo   Export/Import Images
echo.
echo   [1] Export my-spark-worker to file
echo   [2] Import from file
echo   [3] Back
echo.
choice /C 123 /N /M "Select: "
if errorlevel 3 goto ADVANCED_MENU
if errorlevel 2 goto IMPORT_IMAGE
if errorlevel 1 goto EXPORT_IMAGE

:EXPORT_IMAGE
set /p FILENAME="Enter filename (e.g. my-spark-worker.tar): "
docker save my-spark-worker:latest -o %FILENAME%
echo [OK] Exported to %FILENAME%
pause
goto ADVANCED_MENU

:IMPORT_IMAGE
set /p FILENAME="Enter filename to import: "
docker load -i %FILENAME%
echo [OK] Imported
pause
goto ADVANCED_MENU

:VIEW_LOGS
cls
echo.
echo   [1] Namenode logs
echo   [2] Spark Master logs
echo   [3] Spark Worker logs
echo   [4] Spark Job logs
echo   [5] Back
echo.
choice /C 12345 /N /M "Select: "
if errorlevel 5 goto ADVANCED_MENU
if errorlevel 4 docker exec gui-docker-spark-worker-1 cat /tmp/spark_job.log
if errorlevel 3 docker logs gui-docker-spark-worker-1
if errorlevel 2 docker logs spark-master
if errorlevel 1 docker logs namenode
pause
goto ADVANCED_MENU

:DOCKER_PRUNE
cls
echo.
echo   Docker system prune...
echo.
docker system prune -f
echo.
echo   [OK] Done
pause
goto ADVANCED_MENU

:RESET_DOCKER
cls
echo.
echo   !!! NUCLEAR OPTION !!!
echo.
echo   This will DELETE EVERYTHING!
echo.
choice /C YN /M "Are you ABSOLUTELY SURE?"
if errorlevel 2 goto ADVANCED_MENU

docker-compose down
docker system prune -a --volumes -f
docker volume prune -a -f

echo.
echo   [OK] Everything deleted. Start fresh with option 2.
pause
goto MAIN

:EXIT
cls
echo.
echo   Goodbye!
echo.
exit /b 0
