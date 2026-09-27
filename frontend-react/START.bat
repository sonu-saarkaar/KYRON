@echo off
echo ========================================
echo    KYRON React Frontend - Quick Start
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
call npm install

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Frontend: http://localhost:3000
echo  Backend: http://127.0.0.1:8000
echo ========================================
echo.
echo Starting development server...
echo.

call npm run dev

pause

