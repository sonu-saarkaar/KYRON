@echo off
echo ========================================
echo KYRON Backend - Quick Dependency Fix
echo ========================================
echo.

cd /d "%~dp0"

echo Installing required dependencies...
echo.

venv\Scripts\python.exe -m pip install email-validator "python-jose[cryptography]" "passlib[bcrypt]" --quiet

echo.
echo ========================================
echo ✅ Dependencies installed!
echo ========================================
echo.
echo Starting backend...
echo.

venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000

pause

