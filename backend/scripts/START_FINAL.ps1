# Final Backend Start Script - Guaranteed to Work
# Stops any existing processes and starts fresh

$ErrorActionPreference = "Continue"

Write-Host "🚀 Starting KYRON Backend..." -ForegroundColor Cyan
Write-Host ""

# Stop any existing Python/uvicorn processes
Write-Host "Stopping any existing backend processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Find Python
$python = $null
$venvPython = "..\venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $python = $venvPython
    Write-Host "✓ Using venv Python" -ForegroundColor Green
} else {
    $python = "python"
    Write-Host "✓ Using system Python" -ForegroundColor Green
}

if (-not $python) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Install/Verify dependencies
Write-Host ""
Write-Host "Installing/Verifying dependencies..." -ForegroundColor Yellow
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet passlib[bcrypt] bcrypt fastapi uvicorn[standard] python-jose[cryptography] pymongo

# Verify critical packages
Write-Host "Verifying packages..." -ForegroundColor Gray
$test = & $python -c "import passlib; import fastapi; import uvicorn; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0 -and $test -match "OK") {
    Write-Host "✓ All packages verified" -ForegroundColor Green
} else {
    Write-Host "⚠ Some packages may be missing" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Backend: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server (NO RELOAD - Windows compatible)..." -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop" -ForegroundColor Gray
Write-Host ""

# Start WITHOUT reload (Windows compatible)
& $python -m uvicorn main:app --host 127.0.0.1 --port 8000

