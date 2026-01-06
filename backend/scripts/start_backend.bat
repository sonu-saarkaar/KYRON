@echo off
echo Starting KYRON Backend Server...
echo.

cd backend

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not found in PATH.
    echo Please install Python or add it to your PATH.
    echo.
    echo Trying python3...
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo Python3 is also not found.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo Using: %PYTHON_CMD%
echo.

REM First, setup admin account if needed
echo Setting up admin account...
%PYTHON_CMD% setup_admin.py
echo.

REM Start the server
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
%PYTHON_CMD% -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause

