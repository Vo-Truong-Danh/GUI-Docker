# PowerShell task runner for GUI-Docker
param(
    [ValidateSet('run','deps','clean','audit-unused','help')]
    [string]$Task = 'help'
)

$ErrorActionPreference = 'Stop'

function Show-Help {
    Write-Host "Tasks:" -ForegroundColor Cyan
    Write-Host "  run   : Start GUI (python run_spark_gui/main.py)"
    Write-Host "  deps  : Install dependencies from run_spark_gui/requirements.txt if present"
    Write-Host "  clean : Remove __pycache__ and backups folder"
    Write-Host "  audit-unused : Dry-run list of unused files via cleanup_unused_files.py"
    Write-Host "  help  : Show this help"
}

function Start-Gui {
    Set-Location -Path "$PSScriptRoot/run_spark_gui"
    python main.py
}

function Install-Dependencies {
    $req = Join-Path "$PSScriptRoot/run_spark_gui" 'requirements.txt'
    if (Test-Path $req) {
        pip install -r $req
    } else {
        Write-Host "No requirements.txt found at run_spark_gui/" -ForegroundColor Yellow
    }
}

function Clear-Workspace {
    Get-ChildItem -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $bk = Join-Path "$PSScriptRoot" 'backups'
    if (Test-Path $bk) { Remove-Item -Recurse -Force $bk }
    Write-Host "Clean complete." -ForegroundColor Green
}

function Test-AuditUnusedFiles {
    $script = Join-Path "$PSScriptRoot/run_spark_gui" 'cleanup_unused_files.py'
    if (Test-Path $script) {
        python $script --root "$PSScriptRoot" --entry run_spark_gui/main.py --include-md --dry-run
    } else {
        Write-Host "cleanup_unused_files.py not found" -ForegroundColor Yellow
    }
}

switch ($Task) {
    'run'           { Start-Gui }
    'deps'          { Install-Dependencies }
    'clean'         { Clear-Workspace }
    'audit-unused'  { Test-AuditUnusedFiles }
    default { Show-Help }
}
