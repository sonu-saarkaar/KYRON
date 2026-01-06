# KYRON Backend - Simple Auto Run Script
# This script automatically finds Python, installs dependencies, and runs backend

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   KYRON Backend Auto Setup & Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get project root
$projectRoot = $PSScriptRoot
$backendPath = Join-Path $projectRoot "backend"
$venvPath = Join-Path $projectRoot "venv"

# Change to backend directory
if (-not (Test-Path $backendPath)) {
    Write-Host "ERROR: Backend folder not found!" -ForegroundColor Red
    Write-Host "Expected: $backendPath" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location $backendPath
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Step 1: Find Python
Write-Host "[1/4] Finding Python..." -ForegroundColor Yellow

$pythonExe = $null
$pipExe = $null

# Priority 1: Check venv
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"

if (Test-Path $venvPython) {
    Write-Host "  ✓ Found Python in venv" -ForegroundColor Green
    $pythonExe = $venvPython
    $pipExe = $venvPip
    $pythonVersion = & $pythonExe --version 2>&1
    Write-Host "    Version: $pythonVersion" -ForegroundColor Gray
} else {
    # Priority 2: Check system Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0 -or $pythonVersion -match "Python") {
            Write-Host "  ✓ Found system Python: $pythonVersion" -ForegroundColor Green
            $pythonExe = "python"
            $pipExe = "pip"
        }
    } catch {
        # Priority 3: Try py launcher
        try {
            $pythonVersion = py --version 2>&1
            if ($LASTEXITCODE -eq 0 -or $pythonVersion -match "Python") {
                Write-Host "  ✓ Found Python launcher: $pythonVersion" -ForegroundColor Green
                $pythonExe = "py"
                $pipExe = "py -m pip"
            }
        } catch {
            Write-Host "  ✗ Python not found!" -ForegroundColor Red
        }
    }
}

if (-not $pythonExe) {
    Write-Host ""
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11+ from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "During installation:" -ForegroundColor Yellow
    Write-Host "  ✓ Check 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "  ✓ Check 'Install pip'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 2: Check pip
Write-Host "[2/4] Checking pip..." -ForegroundColor Yellow

if ($pipExe -eq "py -m pip") {
    $pipCheck = & py -m pip --version 2>&1
} else {
    $pipCheck = & $pipExe --version 2>&1
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing pip..." -ForegroundColor Yellow
    & $pythonExe -m ensurepip --upgrade
} else {
    Write-Host "  ✓ pip found" -ForegroundColor Green
}

Write-Host ""

# Step 3: Install Dependencies
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

$requirementsFile = "requirements_minimal.txt"
if (-not (Test-Path $requirementsFile)) {
    $requirementsFile = "requirements.txt"
}

if (Test-Path $requirementsFile) {
    Write-Host "  Installing from: $requirementsFile" -ForegroundColor Gray
    
    # Upgrade pip first
    if ($pipExe -eq "py -m pip") {
        & py -m pip install --upgrade pip --quiet 2>&1 | Out-Null
        Write-Host "  Installing packages..." -ForegroundColor Gray
        & py -m pip install -r $requirementsFile
    } elseif ($pipExe -eq "pip") {
        & pip install --upgrade pip --quiet 2>&1 | Out-Null
        Write-Host "  Installing packages..." -ForegroundColor Gray
        & pip install -r $requirementsFile
    } else {
        & $pipExe install --upgrade pip --quiet 2>&1 | Out-Null
        Write-Host "  Installing packages..." -ForegroundColor Gray
        & $pipExe install -r $requirementsFile
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Dependencies installed!" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Some packages may have failed (continuing anyway)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ requirements.txt not found, installing core packages..." -ForegroundColor Yellow
    $corePackages = @("fastapi", "uvicorn[standard]", "python-multipart", "pydantic")
    
    foreach ($package in $corePackages) {
        if ($pipExe -eq "py -m pip") {
            & py -m pip install $package --quiet
        } elseif ($pipExe -eq "pip") {
            & pip install $package --quiet
        } else {
            & $pipExe install $package --quiet
        }
    }
}

Write-Host ""

# Step 4: Run Backend
Write-Host "[4/4] Starting KYRON Backend..." -ForegroundColor Yellow
Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Backend URL: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  API Docs:    http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run backend
$runScript = "run.py"
if (Test-Path $runScript) {
    & $pythonExe $runScript
} else {
    # Fallback
    Write-Host "Running uvicorn directly..." -ForegroundColor Yellow
    if ($pythonExe -eq "py") {
        & py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    } else {
        & $pythonExe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    }
}

Write-Host ""
Write-Host "Backend stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"

