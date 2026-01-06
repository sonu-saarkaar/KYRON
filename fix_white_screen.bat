@echo off
echo ===================================
echo KYRON White Screen Fix
echo ===================================
echo.

echo Checking if services are running...
echo.

REM Check backend
echo [1/4] Testing Backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Backend is running on port 8000
) else (
    echo ✗ Backend is NOT running!
    echo   Please start backend first:
    echo   cd backend
    echo   python main.py
    echo.
    pause
    exit /b 1
)

REM Check frontend
echo [2/4] Testing Frontend...
netstat -an | findstr :3000 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Frontend is running on port 3000
) else (
    echo ✗ Frontend is NOT running!
    echo   Please start frontend:
    echo   cd frontend-react
    echo   npm run dev
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Clearing browser cache...
echo Please do this manually:
echo 1. Open http://localhost:3000/login
echo 2. Press F12 to open DevTools
echo 3. Press Ctrl+Shift+R to hard refresh
echo 4. Look for RED errors in Console tab
echo.

echo [4/4] Opening browser...
start http://localhost:3000/login

echo.
echo ===================================
echo Diagnostic Complete!
echo ===================================
echo.
echo If you see a white screen:
echo 1. Press F12 in browser
echo 2. Click Console tab
echo 3. Look for any RED errors
echo 4. Share those errors
echo.
echo Common fixes:
echo - Hard refresh: Ctrl+Shift+R
echo - Clear cache: Ctrl+Shift+Delete
echo - Restart both backend and frontend
echo.
pause

