@echo off
echo ========================================
echo    KYRON Backend - No Reload (Windows)
echo ========================================
echo.

cd /d "%~dp0"

REM Check for venv Python
if exist "..\venv\Scripts\python.exe" (
    echo Using venv Python...
    echo.
    echo Installing/Verifying dependencies...
    ..\venv\Scripts\python.exe -m pip install --quiet --upgrade pip
    ..\venv\Scripts\python.exe -m pip install --quiet passlib[bcrypt] bcrypt fastapi uvicorn
    echo.
    echo Starting backend (no reload)...
    echo Backend: http://127.0.0.1:8000
    echo API Docs: http://127.0.0.1:8000/docs
    echo.
    ..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
) else (
    echo Checking system Python...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python not found!
        pause
        exit /b 1
    )
    echo.
    echo Installing/Verifying dependencies...
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet passlib[bcrypt] bcrypt fastapi uvicorn
    echo.
    echo Starting backend (no reload)...
    echo Backend: http://127.0.0.1:8000
    echo API Docs: http://127.0.0.1:8000/docs
    echo.
    python -m uvicorn main:app --host 127.0.0.1 --port 8000
)

pause

