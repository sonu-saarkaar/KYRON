@echo off
echo ========================================
echo    KYRON Backend - Quick Start
echo ========================================
echo.

cd /d "%~dp0"

REM Check for venv Python
if exist "..\venv\Scripts\python.exe" (
    echo Using venv Python...
    echo.
    echo Installing dependencies...
    ..\venv\Scripts\python.exe -m pip install --quiet --upgrade pip
    ..\venv\Scripts\python.exe -m pip install -r requirements_minimal.txt
    echo.
    echo Starting backend...
    echo Backend: http://127.0.0.1:8000
    echo API Docs: http://127.0.0.1:8000/docs
    echo.
    ..\venv\Scripts\python.exe run.py
) else (
    echo Checking system Python...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python not found!
        echo Please install Python from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo.
    echo Installing dependencies...
    python -m pip install --quiet --upgrade pip
    python -m pip install -r requirements_minimal.txt
    echo.
    echo Starting backend...
    echo Backend: http://127.0.0.1:8000
    echo API Docs: http://127.0.0.1:8000/docs
    echo.
    python run.py
)

pause

