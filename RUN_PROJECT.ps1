# KYRON - Complete Project Runner
Write-Host "Starting KYRON Project..." -ForegroundColor Cyan

# Start Backend
Write-Host "Starting Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\backend'; python main.py" -WindowStyle Normal

# Wait a bit for backend to initialize
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Starting Frontend on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\frontend-react'; npm run dev" -WindowStyle Normal

Write-Host "Both services starting in separate windows!" -ForegroundColor Green
Write-Host "Backend API:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Frontend App: http://localhost:3000" -ForegroundColor Cyan
