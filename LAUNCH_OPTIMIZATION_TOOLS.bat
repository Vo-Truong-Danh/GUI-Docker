@echo off
REM ================================================================================
REM Quick Launch - System Optimization Tools
REM Windows Batch Script
REM ================================================================================

setlocal

set "SCRIPT_DIR=%~dp0run_spark_gui"
set "PYTHON=python"

:MENU
cls
echo ================================================================================
echo                    SYSTEM OPTIMIZATION TOOLS
echo                      Quick Launch Menu
echo ================================================================================
echo.
echo Choose an option:
echo.
echo  1. Run Master Optimization Suite (Recommended)
echo  2. System Analysis Only
echo  3. Auto Code Fixer (with backup)
echo  4. Dependency Optimizer
echo  5. Launch Monitoring Dashboard
echo  6. Demo All Features
echo  7. View Documentation
echo  8. View Reports
echo  0. Exit
echo.
echo ================================================================================
echo.

set /p choice="Enter your choice (0-8): "

if "%choice%"=="1" goto MASTER
if "%choice%"=="2" goto ANALYSIS
if "%choice%"=="3" goto FIXER
if "%choice%"=="4" goto DEPENDENCY
if "%choice%"=="5" goto DASHBOARD
if "%choice%"=="6" goto DEMO
if "%choice%"=="7" goto DOCS
if "%choice%"=="8" goto REPORTS
if "%choice%"=="0" goto EXIT

echo Invalid choice!
timeout /t 2 >nul
goto MENU

:MASTER
cls
echo ================================================================================
echo Running Master Optimization Suite...
echo ================================================================================
echo.
cd /d "%SCRIPT_DIR%"
%PYTHON% master_optimization.py
echo.
pause
goto MENU

:ANALYSIS
cls
echo ================================================================================
echo Running System Analysis...
echo ================================================================================
echo.
cd /d "%SCRIPT_DIR%"
%PYTHON% comprehensive_system_analysis.py
echo.
echo Check generated reports:
echo - system_analysis_report_*.json
echo - system_analysis_report_*_summary.txt
echo.
pause
goto MENU

:FIXER
cls
echo ================================================================================
echo Running Auto Code Fixer...
echo WARNING: This will modify code files (backup will be created)
echo ================================================================================
echo.
set /p confirm="Continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    timeout /t 2 >nul
    goto MENU
)
echo.
cd /d "%SCRIPT_DIR%"
%PYTHON% auto_code_fixer.py
echo.
echo Check backups/ directory for original files
echo.
pause
goto MENU

:DEPENDENCY
cls
echo ================================================================================
echo Running Dependency Optimizer...
echo ================================================================================
echo.
cd /d "%SCRIPT_DIR%"
%PYTHON% dependency_optimizer_v2.py
echo.
echo Check generated reports:
echo - dependency_analysis_report.json
echo - dependency_analysis_summary.txt
echo.
pause
goto MENU

:DASHBOARD
cls
echo ================================================================================
echo Launching Monitoring Dashboard...
echo ================================================================================
echo.
cd /d "%SCRIPT_DIR%"
start %PYTHON% realtime_monitoring_dashboard.py
echo.
echo Dashboard launched in separate window
timeout /t 2 >nul
goto MENU

:DEMO
cls
echo ================================================================================
echo Running Demo Script...
echo ================================================================================
echo.
cd /d "%SCRIPT_DIR%"
%PYTHON% demo_optimization_tools.py
echo.
pause
goto MENU

:DOCS
cls
echo ================================================================================
echo DOCUMENTATION
echo ================================================================================
echo.
echo Available documentation:
echo.
if exist "OPTIMIZATION_REPORT.md" (
    echo [FOUND] OPTIMIZATION_REPORT.md
    echo         - Comprehensive optimization report
    echo.
)
if exist "QUICK_START_OPTIMIZATION_TOOLS.md" (
    echo [FOUND] QUICK_START_OPTIMIZATION_TOOLS.md
    echo         - Quick start guide
    echo.
)
if exist "OPTIMIZATION_SUMMARY_FINAL.txt" (
    echo [FOUND] OPTIMIZATION_SUMMARY_FINAL.txt
    echo         - Final summary
    echo.
)
echo.
set /p open="Open documentation? (1=Report, 2=Quick Start, 3=Summary, 0=Back): "
if "%open%"=="1" (
    if exist "OPTIMIZATION_REPORT.md" start notepad "OPTIMIZATION_REPORT.md"
)
if "%open%"=="2" (
    if exist "QUICK_START_OPTIMIZATION_TOOLS.md" start notepad "QUICK_START_OPTIMIZATION_TOOLS.md"
)
if "%open%"=="3" (
    if exist "OPTIMIZATION_SUMMARY_FINAL.txt" start notepad "OPTIMIZATION_SUMMARY_FINAL.txt"
)
timeout /t 2 >nul
goto MENU

:REPORTS
cls
echo ================================================================================
echo GENERATED REPORTS
echo ================================================================================
echo.
cd /d "%SCRIPT_DIR%"
echo System Analysis Reports:
dir /b system_analysis_report_*.json 2>nul
dir /b system_analysis_report_*.txt 2>nul
echo.
echo Auto-Fix Reports:
dir /b auto_fix_report_*.json 2>nul
echo.
echo Dependency Reports:
dir /b dependency_analysis_*.* 2>nul
echo.
echo Monitoring Reports:
dir /b monitoring_report_*.json 2>nul
echo.
echo.
set /p open="Open report directory in Explorer? (y/N): "
if /i "%open%"=="y" (
    explorer "%SCRIPT_DIR%"
)
pause
goto MENU

:EXIT
cls
echo ================================================================================
echo Thank you for using System Optimization Tools!
echo ================================================================================
echo.
echo Generated by: GitHub Copilot
echo Version: 1.0.0
echo Date: October 14, 2025
echo.
echo For more information, see:
echo - OPTIMIZATION_REPORT.md
echo - QUICK_START_OPTIMIZATION_TOOLS.md
echo.
timeout /t 3
exit /b 0
