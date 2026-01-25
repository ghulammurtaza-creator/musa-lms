#!/bin/bash

# Complete startup script - Starts both backend (Docker) and frontend (npm)

echo "🎓 Academy Management System - Complete Startup"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start backend services
echo "🚀 Starting backend services..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start backend services"
    exit 1
fi

echo "✅ Backend services started"
echo ""

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install frontend dependencies"
        exit 1
    fi
    cd ..
fi

# Start frontend
echo "🎨 Starting frontend..."
echo "   Opening a new terminal window for frontend..."
echo ""

# Try different terminal emulators
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd frontend && npm run dev; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "cd frontend && npm run dev; bash" &
elif command -v konsole &> /dev/null; then
    konsole -e "cd frontend && npm run dev; bash" &
else
    # Fallback: run in background and show instructions
    echo "⚠️  Could not find a terminal emulator. Please start the frontend manually:"
    echo "   cd frontend && npm run dev"
    echo ""
fi

echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ All services are starting!"
echo ""
echo "📍 Access points:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API:        http://localhost:8000"
echo "   API Documentation:  http://localhost:8000/docs"
echo "   MinIO Console:      http://localhost:9001"
echo ""
echo "📊 Check backend logs with:"
echo "   docker compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   - Stop frontend with Ctrl+C in its terminal"
echo "   - Run: docker compose down"
echo ""
echo "Happy coding! 🎉"
