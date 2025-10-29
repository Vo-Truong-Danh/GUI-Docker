@echo off
chcp 65001 >nul
title Retrain Model Menu
cls

:MENU
cls
echo.
echo ========================================================================
echo   RETRAIN MODEL MENU
echo ========================================================================
echo.
echo   Current model: MAP@500 = 5.59%% (Rank 50)
echo.
echo   Choose retrain strategy:
echo.
echo   [1] CONSERVATIVE (Safe - Rank 60)
echo      - MAP@500: ~6-7%%
echo      - Train: ~12 min
echo      - RAM: Safe for 24GB
echo.
echo   [2] AGGRESSIVE (Medium - Rank 80)
echo      - MAP@500: ~7-8%%
echo      - Train: ~15 min
echo      - RAM: May need more
echo.
echo   [3] MAX PERFORMANCE (High - Rank 100)
echo      - MAP@500: ~8-9%%
echo      - Train: ~20 min
echo      - RAM: Risk OOM!
echo.
echo   [4] CUSTOM (Specify your own parameters)
echo.
echo   [0] Back to Main Menu
echo.
echo ========================================================================
echo.
echo   Note: All options will SKIP loading/indexing (fast start!)
echo.
echo ========================================================================

choice /C 12340 /N /M "Select option (1-4, 0=Back): "
set CHOICE=%ERRORLEVEL%

if %CHOICE%==1 goto OPTION1
if %CHOICE%==2 goto OPTION2
if %CHOICE%==3 goto OPTION3
if %CHOICE%==4 goto CUSTOM
if %CHOICE%==5 goto EXIT

:OPTION1
call RETRAIN_OPTION1_CONSERVATIVE.bat
goto MENU

:OPTION2
call RETRAIN_OPTION2_AGGRESSIVE.bat
goto MENU

:OPTION3
call RETRAIN_OPTION3_MAX.bat
goto MENU

:CUSTOM
cls
echo.
echo ========================================================================
echo   CUSTOM RETRAIN PARAMETERS
echo ========================================================================
echo.
echo   Enter your custom parameters (or press Enter for defaults)
echo.

set /p RANK="Rank (default: 50): "
set /p REGPARAM="RegParam (default: 0.1): "
set /p ALPHA="Alpha (default: 40.0): "
set /p MAXITER="MaxIter (default: 20): "

if "%RANK%"=="" set RANK=50
if "%REGPARAM%"=="" set REGPARAM=0.1
if "%ALPHA%"=="" set ALPHA=40.0
if "%MAXITER%"=="" set MAXITER=20

echo.
echo   Selected parameters:
echo      - Rank: %RANK%
echo      - RegParam: %REGPARAM%
echo      - Alpha: %ALPHA%
echo      - MaxIter: %MAXITER%
echo.
pause

echo.
echo [1/2] Checking containers...
docker ps --filter "name=namenode" --format "{{.Names}}" | findstr "namenode" >nul
if errorlevel 1 (
    echo.
    echo [X] Containers not running!
    echo    Please start containers first
    pause
    goto MENU
)

echo    [OK] Containers running
echo.
echo [2/3] Copying Python file to container...
docker cp "code python/spotify_rec_optimized_tangchinhxac.py" gui-docker-spark-worker-1:/tmp/

if errorlevel 1 (
    echo.
    echo [X] Failed to copy file!
    pause
    goto MENU
)

echo    [OK] File copied
echo.
echo [3/3] Starting Spark job...
echo.

docker exec -it gui-docker-spark-worker-1 /spark/bin/spark-submit ^
  --master spark://spark-master:7077 ^
  /tmp/spotify_rec_optimized_tangchinhxac.py ^
  --force_retrain ^
  --rank %RANK% ^
  --regParam %REGPARAM% ^
  --alpha %ALPHA% ^
  --maxIter %MAXITER%

echo.
echo ========================================================================
echo   Job finished!
echo ========================================================================
pause
goto MENU

:EXIT
exit /b 0

