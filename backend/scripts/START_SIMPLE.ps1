# Simple Backend Starter - Activates venv and runs uvicorn directly
# Use this if START.ps1 has issues

$ErrorActionPreference = "Continue"

# Get backend directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Split-Path -Parent $scriptDir
Set-Location $backendDir

Write-Host "🚀 Starting KYRON Backend (Simple Mode)..." -ForegroundColor Cyan
Write-Host ""

# Activate venv
$venvActivate = Join-Path $backendDir "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
    & $venvActivate
} else {
    Write-Host "⚠️  Virtual environment not found at: $venvActivate" -ForegroundColor Yellow
    Write-Host "   Using system Python instead..." -ForegroundColor Yellow
}

# Verify Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Backend: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server... (Press CTRL+C to stop)" -ForegroundColor Yellow
Write-Host ""

# Run uvicorn directly
python -m uvicorn main:app --host 127.0.0.1 --port 8000
