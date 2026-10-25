#!/usr/bin/env bash
# KYRON Backend Runner
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements_minimal.txt
fi

echo "Starting KYRON Backend on http://127.0.0.1:8000..."
./venv/bin/python main.py
