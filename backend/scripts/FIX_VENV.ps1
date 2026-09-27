# Fix Virtual Environment Issues
# Run this if you get "No pyvenv.cfg file" error

$ErrorActionPreference = "Continue"

# Get backend directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Split-Path -Parent $scriptDir
Set-Location $backendDir

Write-Host "🔧 Fixing Virtual Environment..." -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
$venvPath = Join-Path $backendDir "venv"
$venvCfg = Join-Path $venvPath "pyvenv.cfg"

if (Test-Path $venvCfg) {
    Write-Host "✓ pyvenv.cfg found" -ForegroundColor Green
    Get-Content $venvCfg
} else {
    Write-Host "⚠️  pyvenv.cfg not found!" -ForegroundColor Yellow
    Write-Host ""
    
    # Check if venv directory exists
    if (Test-Path $venvPath) {
        Write-Host "⚠️  Venv directory exists but pyvenv.cfg is missing" -ForegroundColor Yellow
        Write-Host "   This might be a corrupted venv. Recreating..." -ForegroundColor Yellow
        Write-Host ""
        
        # Remove old venv
        Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Find system Python
    $systemPython = $null
    try {
        $cmd = Get-Command python -ErrorAction SilentlyContinue
        if ($cmd) {
            $systemPython = $cmd.Source
        }
    } catch {
        # Try python3
        try {
            $cmd = Get-Command python3 -ErrorAction SilentlyContinue
            if ($cmd) {
                $systemPython = $cmd.Source
            }
        } catch {
            Write-Host "✗ System Python not found!" -ForegroundColor Red
            exit 1
        }
    }
    
    if ($systemPython) {
        Write-Host "✓ Found system Python: $systemPython" -ForegroundColor Green
        $version = & $systemPython --version 2>&1
        Write-Host "  Version: $version" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
        
        # Create new venv
        & $systemPython -m venv $venvPath
        
        if (Test-Path $venvCfg) {
            Write-Host "✓ Virtual environment created successfully!" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✗ Cannot find Python to create venv!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Virtual environment is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  3. Run backend: python run.py" -ForegroundColor White
Write-Host ""
