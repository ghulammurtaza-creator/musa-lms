#!/bin/bash

# Academy Management System - Startup Script
# This script helps you get started quickly

echo "🎓 Academy Management System - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env file with your configuration before proceeding"
    echo "   At minimum, update:"
    echo "   - SECRET_KEY (generate with: openssl rand -hex 32)"
    echo "   - GEMINI_API_KEY (get from https://makersuite.google.com/)"
    echo ""
    read -p "Press Enter after updating .env file..." 
fi

echo "🚀 Starting services..."
echo ""

# Start Docker Compose
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ All services are running!"
    echo ""
    echo "📍 Access points:"
    echo "   Frontend Dashboard: http://localhost:3000"
    echo "   Backend API:        http://localhost:8000"
    echo "   API Documentation:  http://localhost:8000/api/docs"
    echo ""
    echo "📊 Check logs with:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop services with:"
    echo "   docker-compose down"
    echo ""
    echo "Happy coding! 🎉"
else
    echo ""
    echo "❌ Some services failed to start. Check logs with:"
    echo "   docker-compose logs"
fi
