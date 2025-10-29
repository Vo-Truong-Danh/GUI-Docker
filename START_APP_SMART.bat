@echo off
REM ============================================================================
REM SMART START - Check images, build if needed, scale workers
REM ============================================================================
setlocal enabledelayedexpansion

cls
echo.
echo ========================================================================
echo   SMART START APPLICATION
echo ========================================================================
echo.
echo   Checking system status...
echo.

REM ============================================================================
REM STEP 1: Check if custom images exist
REM ============================================================================
echo [1/4] Checking custom Docker images...
docker images my-spark-worker:latest -q >nul 2>&1
if %errorlevel% neq 0 (
    echo    [X] Custom image 'my-spark-worker' NOT FOUND
    goto BUILD_IMAGES
) else (
    echo    [OK] Custom image 'my-spark-worker' exists
)

docker images bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8 -q >nul 2>&1
if %errorlevel% neq 0 (
    echo    [X] Base image 'bde2020/hadoop-namenode' NOT FOUND
    goto BUILD_IMAGES
) else (
    echo    [OK] Base image 'bde2020/hadoop-namenode' exists
)

echo.
echo    [OK] All required images found!
goto CHECK_CONTAINERS

:BUILD_IMAGES
echo.
echo ========================================================================
echo   BUILDING CUSTOM IMAGES
echo ========================================================================
echo.
echo   Images not found. Will build now...
echo   This will take ~20-30 minutes (one-time setup)
echo.
pause

echo.
echo Building custom Spark worker image...
docker-compose build

if %errorlevel% neq 0 (
    echo.
    echo [X] BUILD FAILED!
    echo    Check docker-compose.yml and Dockerfile.spark-worker
    pause
    exit /b 1
)

echo.
echo [OK] Images built successfully!
echo.
pause

REM ============================================================================
REM STEP 2: Check if containers are running
REM ============================================================================
:CHECK_CONTAINERS
echo.
echo [2/4] Checking containers...
docker ps -q --filter "name=namenode" >nul 2>&1
if %errorlevel% neq 0 (
    echo    [!] Containers not running
    goto START_CONTAINERS
) else (
    echo    [OK] Containers already running
    goto SCALE_WORKERS
)

:START_CONTAINERS
echo.
echo ========================================================================
echo   STARTING CONTAINERS
echo ========================================================================
echo.

REM ============================================================================
REM STEP 3: Ask how many workers
REM ============================================================================
:SCALE_WORKERS
echo.
echo [3/4] Worker scaling...
echo.
echo    Current workers: 2 (default)
echo.
echo    How many Spark workers do you want?
echo.
echo    [1] Keep 2 workers (Default - 24 GB total)
echo    [2] Scale to 1 worker (Single - 12 GB)
echo    [3] Scale to 3 workers (High - 36 GB)
echo    [4] Scale to 4 workers (Max - 48 GB)
echo    [5] Custom number
echo.

choice /C 12345 /N /M "Select option (1-5): "
set WORKER_CHOICE=%ERRORLEVEL%

if %WORKER_CHOICE%==1 set WORKERS=2
if %WORKER_CHOICE%==2 set WORKERS=1
if %WORKER_CHOICE%==3 set WORKERS=3
if %WORKER_CHOICE%==4 set WORKERS=4
if %WORKER_CHOICE%==5 (
    set /p WORKERS="Enter number of workers (1-10): "
)

echo.
echo    Selected: %WORKERS% worker(s)
echo.

REM Check if already running
docker ps -q --filter "name=namenode" >nul 2>&1
if %errorlevel% equ 0 (
    echo    Stopping current containers...
    docker-compose down
    timeout /t 3 /nobreak >nul
)

echo    Starting containers with %WORKERS% worker(s)...
docker-compose up -d --scale spark-worker=%WORKERS%

echo.
echo    Waiting for containers to be ready...
timeout /t 15 /nobreak >nul

REM ============================================================================
REM STEP 4: Verify everything
REM ============================================================================
echo.
echo [4/4] Verifying setup...
echo.
echo    Containers:
docker ps --format "table {{.Names}}\t{{.Status}}"

echo.
echo    Checking HDFS...
docker exec namenode hdfs dfs -ls / 2>nul
if %errorlevel% neq 0 (
    echo    [!] HDFS not ready yet, wait a bit longer...
) else (
    echo    [OK] HDFS is ready
    docker exec namenode hdfs dfs -du -s -h /input/data/ 2>nul
)

echo.
echo ========================================================================
echo   [OK] APPLICATION STARTED!
echo ========================================================================
echo.
echo   System Status:
echo      - Workers: %WORKERS%
echo      - Spark Master UI: http://localhost:8080
echo      - Spark Job UI: http://localhost:4040 (when job runs)
echo      - HDFS Web UI: http://localhost:9870
echo      - Datanode UI: http://localhost:9864
echo.
echo   Next steps:
echo      1. Check input data: docker exec namenode hdfs dfs -ls /input/data/
echo      2. Run Spark job: Use MAIN_MENU option 3
echo      3. Monitor job: MONITOR_SPARK_JOB.bat
echo.
echo   Management:
echo      - Stop all: docker-compose down
echo      - Scale workers: docker-compose up -d --scale spark-worker=N
echo      - View logs: docker logs -f [container-name]
echo.
echo ========================================================================
pause
