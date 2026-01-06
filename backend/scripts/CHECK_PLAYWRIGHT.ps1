# Check Playwright Installation
# Verifies if Playwright is properly installed

$ErrorActionPreference = "Continue"

Write-Host "🔍 Checking Playwright Installation..." -ForegroundColor Cyan
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
Write-Host "Step 1: Checking Playwright package..." -ForegroundColor Yellow
$test1 = & $python -c "import playwright; print('OK')" 2>&1

if ($LASTEXITCODE -eq 0 -and $test1 -match "OK") {
    Write-Host "✓ Playwright package installed" -ForegroundColor Green
} else {
    Write-Host "✗ Playwright package NOT installed" -ForegroundColor Red
    Write-Host "  Installing..." -ForegroundColor Yellow
    & $python -m pip install playwright
}

Write-Host ""
Write-Host "Step 2: Checking Chromium browser..." -ForegroundColor Yellow
$test2 = & $python -m playwright install --dry-run chromium 2>&1

if ($test2 -match "chromium" -or $test2 -match "already installed") {
    Write-Host "✓ Chromium browser available" -ForegroundColor Green
} else {
    Write-Host "✗ Chromium browser NOT installed" -ForegroundColor Red
    Write-Host "  Installing Chromium (this may take a few minutes)..." -ForegroundColor Yellow
    & $python -m playwright install chromium
}

Write-Host ""
Write-Host "Step 3: Testing Playwright..." -ForegroundColor Yellow
$test3 = & $python -c "import asyncio; from playwright.async_api import async_playwright; async def test(): p = await async_playwright().start(); b = await p.chromium.launch(); await b.close(); await p.stop(); print('OK'); asyncio.run(test())" 2>&1

if ($LASTEXITCODE -eq 0 -and $test3 -match "OK") {
    Write-Host "✓ Playwright test successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Playwright is properly installed and working!" -ForegroundColor Green
} else {
    Write-Host "✗ Playwright test failed" -ForegroundColor Red
    Write-Host "Error: $test3" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try reinstalling:" -ForegroundColor Yellow
    Write-Host "  .\INSTALL_PLAYWRIGHT.ps1" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

