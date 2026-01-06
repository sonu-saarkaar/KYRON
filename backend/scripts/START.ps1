# Quick Start Script - Just run this!
# Automatically installs dependencies and starts backend

$ErrorActionPreference = "Continue"

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Split-Path -Parent $scriptDir
Set-Location $backendDir

Write-Host "Starting KYRON Backend..." -ForegroundColor Cyan
Write-Host "Working Directory: $backendDir" -ForegroundColor Gray
Write-Host ""

# Find Python - Check venv first
$python = $null
$venvPython = Join-Path $backendDir "venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $python = $venvPython
    Write-Host "Using venv Python: $venvPython" -ForegroundColor Green
    
    # Verify venv is valid
    $venvCfg = Join-Path $backendDir "venv\pyvenv.cfg"
    if (-not (Test-Path $venvCfg)) {
        Write-Host "Warning: venv\pyvenv.cfg not found. Recreating venv..." -ForegroundColor Yellow
        $systemPython = (Get-Command python -ErrorAction SilentlyContinue).Source
        if ($systemPython) {
            & $systemPython -m venv "venv"
            $python = $venvPython
            Write-Host "Venv recreated" -ForegroundColor Green
        }
    }
} else {
    # Try to find system Python
    try {
        $systemPython = (Get-Command python -ErrorAction SilentlyContinue).Source
        if ($systemPython) {
            $python = $systemPython
            $ver = & $python --version 2>&1
            Write-Host "Using system Python: $ver" -ForegroundColor Yellow
            Write-Host "Note: Consider using venv for better dependency management" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Python not found!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

if (-not $python) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Install dependencies
Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $python -m pip install --quiet --upgrade pip

Write-Host "Installing dependencies from requirements_minimal.txt..." -ForegroundColor Yellow
& $python -m pip install -r requirements_minimal.txt

# Always ensure passlib is installed (critical for auth)
Write-Host "Ensuring critical packages (passlib, bcrypt)..." -ForegroundColor Gray
& $python -m pip install passlib[bcrypt] bcrypt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Some packages may have failed" -ForegroundColor Yellow
    Write-Host "Installing critical packages individually..." -ForegroundColor Yellow
    & $python -m pip install passlib[bcrypt] bcrypt python-jose[cryptography] pymongo fastapi uvicorn
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server... (Press CTRL+C to stop)" -ForegroundColor Yellow
Write-Host ""

# Start backend using run.py (which handles imports properly)
& $python run.py
