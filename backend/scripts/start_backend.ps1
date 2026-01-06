# KYRON - One-Click Backend Start
# Run this script to automatically setup and start the backend

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     KYRON Backend Auto-Start         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptPath = $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$backendPath = Join-Path $projectRoot "backend"

# Check if backend directory exists
if (-not (Test-Path $backendPath)) {
    Write-Host "ERROR: Backend directory not found!" -ForegroundColor Red
    Write-Host "Expected: $backendPath" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the auto setup script
$autoSetupScript = Join-Path $backendPath "auto_setup_and_run.ps1"

if (Test-Path $autoSetupScript) {
    Write-Host "Starting auto-setup..." -ForegroundColor Green
    Write-Host ""
    & $autoSetupScript
} else {
    Write-Host "Auto-setup script not found. Running manual setup..." -ForegroundColor Yellow
    Write-Host ""
    
    Set-Location $backendPath
    
    # Try to find and run Python
    $pythonFound = $false
    
    # Check venv
    $venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        Write-Host "Using Python from venv..." -ForegroundColor Green
        & $venvPython -m pip install -r requirements_minimal.txt
        & $venvPython run.py
        $pythonFound = $true
    }
    
    # Check system Python
    if (-not $pythonFound) {
        try {
            $pythonVersion = python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Using system Python: $pythonVersion" -ForegroundColor Green
                python -m pip install -r requirements_minimal.txt
                python run.py
                $pythonFound = $true
            }
        } catch {
            # Try py launcher
            try {
                $pythonVersion = py --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Using Python launcher: $pythonVersion" -ForegroundColor Green
                    py -m pip install -r requirements_minimal.txt
                    py run.py
                    $pythonFound = $true
                }
            } catch {
                Write-Host "ERROR: Python not found!" -ForegroundColor Red
                Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
    }
}
