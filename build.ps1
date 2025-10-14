# Build Script for Spark Runner GUI
# Version: 6.0.1
# Platform: Windows (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Spark Runner GUI - Build Script" -ForegroundColor Cyan
Write-Host "   Version: 6.0.1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_NAME = "SparkRunnerGUI"
$VERSION = "6.0.1"
$DIST_DIR = "dist"
$BUILD_DIR = "build"

# Step 1: Check Python version
Write-Host "[1/7] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "   $pythonVersion" -ForegroundColor Green
Write-Host ""

# Step 2: Check PyInstaller
Write-Host "[2/7] Checking PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = pip show pyinstaller 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install PyInstaller!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "   PyInstaller is ready" -ForegroundColor Green
Write-Host ""

# Step 3: Install dependencies
Write-Host "[3/7] Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Some dependencies failed to install" -ForegroundColor Yellow
        Write-Host "         This is OK if optional packages (AI API) failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "   requirements.txt not found, skipping..." -ForegroundColor Yellow
}
Write-Host "   Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 4: Clean previous build
Write-Host "[4/7] Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path $DIST_DIR) {
    Remove-Item -Path $DIST_DIR -Recurse -Force
    Write-Host "   Removed $DIST_DIR/" -ForegroundColor Green
}
if (Test-Path $BUILD_DIR) {
    Remove-Item -Path $BUILD_DIR -Recurse -Force
    Write-Host "   Removed $BUILD_DIR/" -ForegroundColor Green
}
if (Test-Path "$APP_NAME.spec") {
    Remove-Item -Path "$APP_NAME.spec" -Force
    Write-Host "   Removed old spec file" -ForegroundColor Green
}
Write-Host ""

# Step 5: Build executable
Write-Host "[5/7] Building executable..." -ForegroundColor Yellow
Write-Host "   This may take 2-5 minutes..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "build_config.spec") {
    # Use custom spec file
    pyinstaller build_config.spec --noconfirm
} else {
    # Use command line options
    pyinstaller `
        --name="$APP_NAME" `
        --onefile `
        --windowed `
        --add-data="run_spark_gui;run_spark_gui" `
        --add-data="docker-compose.yml;." `
        --add-data="spark_runner_config.json;." `
        --hidden-import=yaml `
        --hidden-import=tkinter `
        --hidden-import=pandas `
        --exclude-module=matplotlib `
        --exclude-module=numpy `
        --noconfirm `
        "run_spark_gui\main.py"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Write-Host "Check the output above for error details" -ForegroundColor Red
    exit 1
}
Write-Host ""
Write-Host "   Build completed successfully!" -ForegroundColor Green
Write-Host ""

# Step 6: Verify executable
Write-Host "[6/7] Verifying executable..." -ForegroundColor Yellow
$exePath = Join-Path $DIST_DIR "$APP_NAME.exe"
if (Test-Path $exePath) {
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host "   Executable found: $exePath" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "ERROR: Executable not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 7: Create release package
Write-Host "[7/7] Creating release package..." -ForegroundColor Yellow
$releaseName = "${APP_NAME}_v${VERSION}_Windows"
$releaseDir = Join-Path $DIST_DIR $releaseName

# Create release directory
if (Test-Path $releaseDir) {
    Remove-Item -Path $releaseDir -Recurse -Force
}
New-Item -ItemType Directory -Path $releaseDir | Out-Null

# Copy files
Copy-Item $exePath -Destination $releaseDir
Copy-Item "README.md" -Destination $releaseDir -ErrorAction SilentlyContinue
Copy-Item "docker-compose.yml" -Destination $releaseDir -ErrorAction SilentlyContinue
Copy-Item "spark_runner_config.json" -Destination $releaseDir -ErrorAction SilentlyContinue

# Create README for release
$releaseReadme = @"
# Spark Runner GUI v$VERSION

## Quick Start

1. **Start Docker Desktop** (required)
2. **Run SparkRunnerGUI.exe**
3. **Start containers** from Settings tab
4. **Run Spark jobs!**

## Requirements

- Windows 10/11
- Docker Desktop installed and running
- 4GB RAM minimum

## Features

- Spark Job Runner
- HDFS File Upload
- AI Code Generator
- Performance Monitor
- Docker Compose Editor
- Port Configuration

## Support

- Documentation: README.md
- Issues: https://github.com/yourusername/GUI-Docker/issues

## Version: $VERSION ($(Get-Date -Format 'yyyy-MM-dd'))
"@

$releaseReadme | Out-File -FilePath (Join-Path $releaseDir "QUICKSTART.txt") -Encoding UTF8

Write-Host "   Release package created: $releaseDir/" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Executable location:" -ForegroundColor Cyan
Write-Host "   $exePath" -ForegroundColor White
Write-Host ""
Write-Host "Release package:" -ForegroundColor Cyan
Write-Host "   $releaseDir/" -ForegroundColor White
Write-Host ""
Write-Host "To distribute:" -ForegroundColor Cyan
Write-Host "   1. Compress the release folder to ZIP" -ForegroundColor White
Write-Host "   2. Share the ZIP file" -ForegroundColor White
Write-Host "   3. Users just need Docker Desktop + run the EXE" -ForegroundColor White
Write-Host ""
Write-Host "To test now:" -ForegroundColor Cyan
Write-Host "   cd $DIST_DIR" -ForegroundColor White
Write-Host "   .\$APP_NAME.exe" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
