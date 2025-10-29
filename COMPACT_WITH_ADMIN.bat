@echo off
REM ============================================================================
REM COMPACT DOCKER VHDX - Wrapper Script
REM ============================================================================
REM This script calls CLEAN_KEEP_HDFS_INPUT.bat (keeps HDFS input data!)
REM ============================================================================

echo.
echo ========================================================================
echo   COMPACT DOCKER VHDX - Keep Input Data
echo ========================================================================
echo.
echo   This will run: CLEAN_KEEP_HDFS_INPUT.bat
echo.
echo   - Keep HDFS input data (NO need to re-upload!)
echo   - Clean unused Docker data
echo   - You manually close/open Docker Desktop when asked
echo.
echo   Will free: ~200 GB on C: drive
echo.
echo ========================================================================
pause

call CLEAN_KEEP_HDFS_INPUT.bat

