# Script to copy ML analysis results to dist folder
# Purpose: Copy tmp folder with all images and JSON data to distribution folder

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Copy ML Analysis Results" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if tmp folder exists
if (-not (Test-Path "tmp")) {
    Write-Host "❌ ERROR: tmp folder not found!" -ForegroundColor Red
    Write-Host "   Please run code7.py first to generate ML analysis results" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if dist folder exists
if (-not (Test-Path "dist")) {
    Write-Host "❌ ERROR: dist folder not found!" -ForegroundColor Red
    Write-Host "   Please build the application first with build.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "[1/3] Analyzing tmp folder..." -ForegroundColor Yellow

# Count files
$pngFiles = @(Get-ChildItem "tmp" -Filter "*.png" -ErrorAction SilentlyContinue)
$jsonFiles = @(Get-ChildItem "tmp" -Filter "*.json" -ErrorAction SilentlyContinue)

Write-Host "   📊 PNG files found: $($pngFiles.Count)" -ForegroundColor Green
Write-Host "   📋 JSON files found: $($jsonFiles.Count)" -ForegroundColor Green

# Calculate size
$tmpSize = (Get-ChildItem -Path "tmp" -Recurse | Measure-Object -Property Length -Sum).Sum
$sizeInMB = [math]::Round($tmpSize / 1MB, 2)
Write-Host "   💾 Total size: $sizeInMB MB" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Copying to dist folder..." -ForegroundColor Yellow

# Create dist/tmp if not exists
$destPath = "dist\tmp"
if (Test-Path $destPath) {
    Write-Host "   ✓ Removing old dist/tmp folder..." -ForegroundColor Cyan
    Remove-Item -Path $destPath -Recurse -Force
}

# Copy entire tmp folder
Write-Host "   ✓ Copying tmp folder to dist..." -ForegroundColor Cyan
Copy-Item -Path "tmp" -Destination $destPath -Recurse -Force

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Copy completed successfully!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Copy failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[3/3] Verifying files..." -ForegroundColor Yellow

# Verify files in dist
$distPngFiles = @(Get-ChildItem "$destPath" -Filter "*.png" -ErrorAction SilentlyContinue)
$distJsonFiles = @(Get-ChildItem "$destPath" -Filter "*.json" -ErrorAction SilentlyContinue)

Write-Host "   ✓ PNG files in dist: $($distPngFiles.Count)" -ForegroundColor Green
Write-Host "   ✓ JSON files in dist: $($distJsonFiles.Count)" -ForegroundColor Green

# List JSON files
if ($distJsonFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "   JSON files:" -ForegroundColor Cyan
    $distJsonFiles | ForEach-Object {
        Write-Host "      • $($_.Name)" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ✅ COPY SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Files copied to: dist\tmp\" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Open: dist\unified_dashboard.html" -ForegroundColor White
Write-Host "   2. The dashboard will automatically load the JSON data" -ForegroundColor White
Write-Host "   3. All ML visualizations will be displayed" -ForegroundColor White
Write-Host ""
