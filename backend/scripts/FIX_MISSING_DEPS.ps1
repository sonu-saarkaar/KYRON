# Fix Missing Dependencies Script
# Installs all required packages

$ErrorActionPreference = "Continue"

Write-Host "Installing all required dependencies..." -ForegroundColor Cyan
Write-Host ""

# Find Python
$python = $null
$venvPython = "..\venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $python = $venvPython
    Write-Host "Using venv Python" -ForegroundColor Green
} else {
    $python = "python"
    Write-Host "Using system Python" -ForegroundColor Green
}

if (-not $python) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1: Upgrading pip..." -ForegroundColor Yellow
& $python -m pip install --upgrade pip

Write-Host ""
Write-Host "Step 2: Installing from requirements_minimal.txt..." -ForegroundColor Yellow
& $python -m pip install -r requirements_minimal.txt

Write-Host ""
Write-Host "Step 3: Installing critical packages..." -ForegroundColor Yellow
& $python -m pip install passlib[bcrypt] bcrypt python-jose[cryptography] pymongo fastapi uvicorn[standard] python-multipart pydantic email-validator

Write-Host ""
Write-Host "Step 4: Verifying installation..." -ForegroundColor Yellow
$test = & $python -c "import passlib; import fastapi; import uvicorn; import pymongo; print('SUCCESS')" 2>&1

if ($LASTEXITCODE -eq 0 -and $test -match "SUCCESS") {
    Write-Host ""
    Write-Host "✅ All dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run: .\START.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Some packages failed to install" -ForegroundColor Red
    Write-Host "Error: $test" -ForegroundColor Red
}

