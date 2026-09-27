# Install Playwright for Automation
# This is required for the automation feature to work

$ErrorActionPreference = "Continue"

Write-Host "🎭 Installing Playwright for Automation..." -ForegroundColor Cyan
Write-Host ""

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

Write-Host ""
Write-Host "Step 1: Installing Playwright package..." -ForegroundColor Yellow
& $python -m pip install playwright

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Playwright package installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Playwright" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Installing Chromium browser..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
& $python -m playwright install chromium

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Playwright installation complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Automation feature is now ready to use!" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠ Installation may have issues, but you can try automation anyway" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

