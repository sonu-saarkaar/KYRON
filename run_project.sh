#!/usr/bin/env bash
# KYRON - Complete Project Runner for macOS & Linux

# Ensure user local bin and node bin are in PATH
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Starting KYRON Project from $DIR..."

# 1. Start Backend in background
echo "Starting Backend on http://127.0.0.1:8000..."
cd "$DIR/backend"
if [ ! -d "venv" ]; then
    echo "Creating virtualenv..."
    python3 -m venv venv
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements_minimal.txt httpx croniter openai pytest playwright
fi
./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait 2 seconds
sleep 2

# 2. Start Frontend in background
echo "Starting Frontend on http://localhost:3000..."
cd "$DIR/frontend-react"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo " KYRON Services are Running!"
echo " Backend API:   http://127.0.0.1:8000"
echo " Swagger Docs:  http://127.0.0.1:8000/docs"
echo " Frontend App:  http://localhost:3000"
echo " Admin Panel:   $DIR/admin_panel/dashboard.html"
echo "=========================================="
echo "Press Ctrl+C to stop all services."

cleanup() {
    echo "Stopping KYRON services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM
wait
