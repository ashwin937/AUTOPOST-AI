#!/bin/bash

# AutoPost AI - Quick Setup Script

echo "🚀 AutoPost AI - Project Setup"
echo "================================"

# Backend Setup
echo ""
echo "📦 Setting up Backend..."
cd backend || exit 1

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet

echo "✅ Backend ready!"

# Frontend Setup
cd ../frontend || exit 1

echo ""
echo "📦 Setting up Frontend..."

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install --silent
else
    echo "Node modules already installed"
fi

echo "✅ Frontend ready!"

echo ""
echo "================================"
echo "✨ Setup Complete!"
echo ""
echo "To run the project:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:5173 in your browser"
echo "================================"
