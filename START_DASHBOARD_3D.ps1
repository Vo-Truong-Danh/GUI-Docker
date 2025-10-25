# ============================================
# Dashboard 3D - Quick Start Script (PowerShell)
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Dashboard 3D - Quick Start Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check Python
Write-Host "[1/3] Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "[2/3] Starting HTTP Server..." -ForegroundColor Yellow
Write-Host "Dashboard URL: " -NoNewline
Write-Host "http://localhost:8000/unified_dashboard_3d.html" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop server" -ForegroundColor Cyan
Write-Host ""

# Start server
python -m http.server 8000
