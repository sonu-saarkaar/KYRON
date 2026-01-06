# Quick Chromium Installation
# Installs only Chromium browser for Playwright

$ErrorActionPreference = "Continue"

Write-Host "🌐 Installing Chromium Browser for Playwright..." -ForegroundColor Cyan
Write-Host "This may take a few minutes (downloads ~150MB)" -ForegroundColor Gray
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

Write-Host "Installing Chromium..." -ForegroundColor Yellow
& $python -m playwright install chromium

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Chromium installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Automation is now ready to use!" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠ Installation may have issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

