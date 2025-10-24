# 🚀 QUICK START - Unified Dashboard (PowerShell)

Write-Host "📊 Big Data Analytics Dashboard - Unified Version" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "unified_dashboard.html")) {
    Write-Host "❌ ERROR: Run this from GUI-Docker directory!" -ForegroundColor Red
    Write-Host "   cd 'd:\BaiTapSinhVien\TH BigData\GUI-Docker'" -ForegroundColor Yellow
    exit 1
}

# Show options
Write-Host "Choose option:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Start GUI (Dashboard + Server)" -ForegroundColor Green
Write-Host "    cd run_spark_gui && python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Start HTTP Server only" -ForegroundColor Green
Write-Host "    python -m http.server 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Generate Real Data (code7.py)" -ForegroundColor Green
Write-Host "    cd run_spark_gui && python code7.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Open Dashboard in Browser" -ForegroundColor Green
Write-Host "    http://localhost:8000/unified_dashboard.html" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🚀 Starting GUI..." -ForegroundColor Cyan
        Push-Location "run_spark_gui"
        python main.py
        Pop-Location
    }
    "2" {
        Write-Host "🚀 Starting HTTP Server..." -ForegroundColor Cyan
        Write-Host "   Access: http://localhost:8000/unified_dashboard.html" -ForegroundColor Green
        python -m http.server 8000
    }
    "3" {
        Write-Host "🚀 Running code7.py..." -ForegroundColor Cyan
        Push-Location "run_spark_gui"
        python code7.py
        Pop-Location
    }
    "4" {
        Write-Host "🚀 Opening Dashboard..." -ForegroundColor Cyan
        start "http://localhost:8000/unified_dashboard.html"
    }
    default {
        Write-Host "❌ Invalid choice!" -ForegroundColor Red
        exit 1
    }
}
