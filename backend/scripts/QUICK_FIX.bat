@echo off
REM Quick fix for "No pyvenv.cfg file" error

cd /d "%~dp0.."
echo 🔧 Fixing Virtual Environment...
echo.

REM Check if pyvenv.cfg exists
if exist "venv\pyvenv.cfg" (
    echo ✓ pyvenv.cfg found
    type venv\pyvenv.cfg
) else (
    echo ⚠️  pyvenv.cfg not found!
    echo.
    echo Creating new virtual environment...
    python -m venv venv
    if exist "venv\pyvenv.cfg" (
        echo ✓ Virtual environment created successfully!
    ) else (
        echo ✗ Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo.
echo ✅ Virtual environment is ready!
echo.
echo Next steps:
echo   1. Activate venv: venv\Scripts\activate.bat
echo   2. Install dependencies: pip install -r requirements.txt
echo   3. Run backend: python run.py
echo.
pause

