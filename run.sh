#!/bin/bash

# AutoPost AI - Run Both Backend and Frontend (portable)
# This script finds its project directory dynamically and will create
# a Python venv and install backend/frontend deps if missing.

set -euo pipefail

# Resolve project dir to the script directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 AutoPost AI - Starting Application"
echo "====================================="
echo ""
echo "Project dir: $PROJECT_DIR"
echo "Starting backend at http://localhost:8000"
echo "Starting frontend at http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# --- Backend setup and start ---
cd "$PROJECT_DIR/backend"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
	echo "🛠️  Creating Python virtual environment..."
	python3 -m venv venv
fi

echo "📦 Activating backend venv..."
source venv/bin/activate

# Install requirements if not installed (rudimentary check)
if ! python -c "import uvicorn" >/dev/null 2>&1; then
	echo "📥 Installing Python requirements... (this may take a while)"
	pip install --upgrade pip
	if [ -f requirements.txt ]; then
		pip install -r requirements.txt
	else
		echo "⚠️  requirements.txt not found in backend/ — skipping pip install"
	fi
fi

echo "📦 Starting Backend..."
nohup uvicorn main:app --reload --port 8000 > /tmp/autopost-backend.log 2>&1 &
BACKEND_PID=$!
disown "$BACKEND_PID" 2>/dev/null || true
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 2

# --- Frontend setup and start ---
cd "$PROJECT_DIR/frontend"

# Install npm deps if node_modules missing
if [ ! -d "node_modules" ]; then
	if command -v npm >/dev/null 2>&1; then
		echo "� Installing frontend npm dependencies..."
		npm install
	else
		echo "⚠️  npm not found — frontend dependencies not installed"
	fi
fi

echo "� Starting Frontend..."
if command -v npm >/dev/null 2>&1; then
	nohup npm run dev > /tmp/autopost-frontend.log 2>&1 &
	FRONTEND_PID=$!
	disown "$FRONTEND_PID" 2>/dev/null || true
	echo "✅ Frontend started (PID: $FRONTEND_PID)"
else
	FRONTEND_PID=0
	echo "⚠️  Frontend not started because npm is not available"
fi

echo ""
echo "====================================="
echo "Both services started (if no errors)." 
echo "📖 Open browser: http://localhost:5173"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/autopost-backend.log"
echo "  Frontend: tail -f /tmp/autopost-frontend.log"
echo ""
echo "Press Ctrl+C to stop..."
echo "====================================="

# Handle Ctrl+C (only kill non-zero PIDs)
trap 'if [ "$BACKEND_PID" -ne 0 ]; then kill "$BACKEND_PID" || true; fi; if [ "$FRONTEND_PID" -ne 0 ]; then kill "$FRONTEND_PID" || true; fi; echo ""; echo "Services stopped"; exit' INT

# Wait for both processes (ignore zero PIDs)
if [ "$FRONTEND_PID" -ne 0 ]; then
	wait "$BACKEND_PID" "$FRONTEND_PID"
else
	wait "$BACKEND_PID"
fi
