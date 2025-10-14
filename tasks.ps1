# PowerShell task runner for GUI-Docker
param(
    [ValidateSet('run','deps','clean','help')]
    [string]$Task = 'help'
)

$ErrorActionPreference = 'Stop'

function Show-Help {
    Write-Host "Tasks:" -ForegroundColor Cyan
    Write-Host "  run   : Start GUI (python run_spark_gui/main.py)"
    Write-Host "  deps  : Install dependencies from run_spark_gui/requirements.txt if present"
    Write-Host "  clean : Remove __pycache__ and backups folder"
    Write-Host "  help  : Show this help"
}

function Task-Run {
    Set-Location -Path "$PSScriptRoot/run_spark_gui"
    python main.py
}

function Task-Deps {
    $req = Join-Path "$PSScriptRoot/run_spark_gui" 'requirements.txt'
    if (Test-Path $req) {
        pip install -r $req
    } else {
        Write-Host "No requirements.txt found at run_spark_gui/" -ForegroundColor Yellow
    }
}

function Task-Clean {
    Get-ChildItem -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $bk = Join-Path "$PSScriptRoot" 'backups'
    if (Test-Path $bk) { Remove-Item -Recurse -Force $bk }
    Write-Host "Clean complete." -ForegroundColor Green
}

switch ($Task) {
    'run'   { Task-Run }
    'deps'  { Task-Deps }
    'clean' { Task-Clean }
    default { Show-Help }
}
