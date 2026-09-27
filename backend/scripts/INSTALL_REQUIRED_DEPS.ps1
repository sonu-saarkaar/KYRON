# KYRON Backend - Install Required Dependencies
# This script installs all required dependencies for KYRON backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "KYRON Backend - Dependency Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install core dependencies
Write-Host ""
Write-Host "Installing core dependencies..." -ForegroundColor Yellow
python -m pip install fastapi uvicorn[standard] python-multipart pydantic email-validator

# Install authentication dependencies
Write-Host ""
Write-Host "Installing authentication dependencies..." -ForegroundColor Yellow
python -m pip install "python-jose[cryptography]" "passlib[bcrypt]"

# Install database dependencies (optional but recommended)
Write-Host ""
Write-Host "Installing database dependencies (optional)..." -ForegroundColor Yellow
python -m pip install pymongo psycopg2-binary sqlalchemy

# Install all from requirements.txt
Write-Host ""
Write-Host "Installing from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the backend:" -ForegroundColor Yellow
Write-Host "  python -m uvicorn main:app --host 127.0.0.1 --port 8000" -ForegroundColor White
Write-Host ""

