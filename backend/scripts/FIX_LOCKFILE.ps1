# Fix Playwright Lockfile Issue
# Removes lockfile and installs Chromium

$ErrorActionPreference = "Continue"

Write-Host "🔧 Fixing Playwright Lockfile Issue..." -ForegroundColor Cyan
Write-Host ""

# Remove lockfile
$lockfile = "$env:LOCALAPPDATA\ms-playwright\__dirlock"
if (Test-Path $lockfile) {
    Write-Host "Removing lockfile..." -ForegroundColor Yellow
    Remove-Item -Path $lockfile -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Lockfile removed" -ForegroundColor Green
} else {
    Write-Host "No lockfile found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Installing Chromium browser..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes - downloads ~150MB)" -ForegroundColor Gray
Write-Host ""

# Find Python
$python = $null
$venvPython = "..\venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $python = "python"
}

# Install Chromium
& $python -m playwright install chromium

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Chromium installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Automation is now ready!" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠ Installation may have issues" -ForegroundColor Yellow
    Write-Host "Try running again if needed" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

