# KYRON Backend - Auto Setup and Run Script
# Automatically detects Python, installs dependencies, and runs backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   KYRON Backend - Auto Setup & Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir

# Step 1: Find Python
Write-Host "[1/4] Detecting Python..." -ForegroundColor Yellow

$pythonCmd = $null
$pipCmd = $null

# Check for Python in venv first (project root venv)
$projectRoot = Split-Path -Parent $scriptDir
$venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"
$venvPip = Join-Path $projectRoot "venv\Scripts\pip.exe"

if (Test-Path $venvPython) {
    Write-Host "  ✓ Found Python in venv" -ForegroundColor Green
    $pythonCmd = $venvPython
    $pipCmd = $venvPip
    $useVenv = $true
} else {
    $useVenv = $false
    # Check for Python in PATH
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Found Python in PATH: $pythonVersion" -ForegroundColor Green
            $pythonCmd = "python"
            $pipCmd = "pip"
        }
    } catch {
        # Try python3
        try {
            $pythonVersion = python3 --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  Found Python3 in PATH: $pythonVersion" -ForegroundColor Green
                $pythonCmd = "python3"
                $pipCmd = "pip3"
            }
        } catch {
            Write-Host "  Python not found in PATH" -ForegroundColor Yellow
        }
    }
    
    # Try py launcher (Windows)
    if (-not $pythonCmd) {
        try {
            $pythonVersion = py --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  Found Python via py launcher: $pythonVersion" -ForegroundColor Green
                $pythonCmd = "py"
                $pipCmd = "py -m pip"
            }
        } catch {
            Write-Host "  Python launcher not found" -ForegroundColor Yellow
        }
    }
}

if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11+ from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "During installation, make sure to:" -ForegroundColor Yellow
    Write-Host "  ✓ Check 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "  ✓ Check 'Install pip'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "  Using: $pythonCmd" -ForegroundColor Green
Write-Host ""

# Step 2: Check/Install pip
Write-Host "[2/4] Checking pip..." -ForegroundColor Yellow

if ($pipCmd -eq "py -m pip") {
    $pipCheck = & py -m pip --version 2>&1
} else {
    $pipCheck = & $pipCmd --version 2>&1
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "  pip not found, installing..." -ForegroundColor Yellow
    & $pythonCmd -m ensurepip --upgrade
} else {
    Write-Host "  pip found: $pipCheck" -ForegroundColor Green
}

Write-Host ""

# Step 3: Install Dependencies
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

$requirementsFile = Join-Path $scriptDir "requirements_minimal.txt"
if (-not (Test-Path $requirementsFile)) {
    $requirementsFile = Join-Path $scriptDir "requirements.txt"
}

if (Test-Path $requirementsFile) {
    Write-Host "  Installing from: $requirementsFile" -ForegroundColor Gray
    
    if ($useVenv) {
        # Use venv pip directly
        Write-Host "  Using venv pip..." -ForegroundColor Gray
        & $venvPip install --upgrade pip --quiet
        & $venvPip install -r $requirementsFile
    } elseif ($pipCmd -eq "py -m pip") {
        & py -m pip install --upgrade pip --quiet
        & py -m pip install -r $requirementsFile
    } else {
        & $pipCmd install --upgrade pip --quiet
        & $pipCmd install -r $requirementsFile
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "WARNING: Some dependencies may have failed to install" -ForegroundColor Yellow
        Write-Host "The backend may still work with core dependencies" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "  Dependencies installed successfully!" -ForegroundColor Green
    }
} else {
    Write-Host "  WARNING: requirements.txt not found!" -ForegroundColor Yellow
    Write-Host "  Installing core dependencies manually..." -ForegroundColor Yellow
    
    $corePackages = @("fastapi", "uvicorn[standard]", "python-multipart", "pydantic", "python-jose[cryptography]", "passlib[bcrypt]", "email-validator")
    
    foreach ($package in $corePackages) {
        Write-Host "    Installing $package..." -ForegroundColor Gray
        if ($pipCmd -eq "py -m pip") {
            & py -m pip install $package
        } else {
            & $pipCmd install $package
        }
    }
}

Write-Host ""

# Step 4: Run Backend
Write-Host "[4/4] Starting KYRON Backend..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend will be available at:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Documentation:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the backend
$runScript = Join-Path $scriptDir "run.py"
if (Test-Path $runScript) {
    Write-Host "Starting backend with: $pythonCmd" -ForegroundColor Gray
    & $pythonCmd $runScript
} else {
    # Fallback: run uvicorn directly
    Write-Host "Running uvicorn directly..." -ForegroundColor Yellow
    if ($useVenv) {
        & $venvPython -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    } elseif ($pythonCmd -eq "py") {
        & py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    } else {
        & $pythonCmd -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    }
}

Write-Host ""
Write-Host "Backend stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"

