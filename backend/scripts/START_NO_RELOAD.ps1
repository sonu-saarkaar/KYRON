# Start Backend Without Reload (Fixes subprocess import issues)
# Use this if you get import errors with reload enabled

$ErrorActionPreference = "Continue"

Write-Host "🚀 Starting KYRON Backend (No Reload)..." -ForegroundColor Cyan
Write-Host ""

# Find Python
$python = $null
$venvPython = "..\venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $python = $venvPython
    Write-Host "✓ Using venv Python" -ForegroundColor Green
} else {
    try {
        $ver = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $python = "python"
            Write-Host "✓ Using system Python: $ver" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ Python not found!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

if (-not $python) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Install dependencies
& $python -m pip install --quiet --upgrade pip
& $python -m pip install -r requirements_minimal.txt

# Ensure passlib is installed
& $python -m pip install passlib[bcrypt] bcrypt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some packages may have failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Backend: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server (no reload)... (Press CTRL+C to stop)" -ForegroundColor Yellow
Write-Host ""

# Start backend without reload
& $python -m uvicorn main:app --host 127.0.0.1 --port 8000

