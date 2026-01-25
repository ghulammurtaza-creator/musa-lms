@echo off
REM Academy Management System - Startup Script (Windows)
REM This script helps you get started quickly

echo.
echo 🎓 Academy Management System - Quick Start
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo Visit: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed
echo.

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Please edit .env file with your configuration before proceeding
    echo    At minimum, update:
    echo    - SECRET_KEY (generate with: openssl rand -hex 32^)
    echo    - GEMINI_API_KEY (get from https://makersuite.google.com/^)
    echo.
    pause
)

echo 🚀 Starting backend services (Database, API, MinIO)...
echo    Frontend will need to be started separately with: npm run dev
echo.

REM Start Docker Compose (backend only)
docker compose up -d

echo.
echo ⏳ Waiting for backend services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker compose ps | findstr "Up" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ✅ Backend services are running!
    echo.
    echo 📍 Backend access points:
    echo    Backend API:        http://localhost:8000
    echo    API Documentation:  http://localhost:8000/docs
    echo    MinIO Console:      http://localhost:9001
    echo.
    echo 🎨 To start the frontend:
    echo    1. Open a new terminal
    echo    2. cd frontend
    echo    3. npm install (first time only)
    echo    4. npm run dev
    echo    5. Visit http://localhost:3000
    echo.
    echo 📊 Check backend logs with:
    echo    docker compose logs -f
    echo.
    echo 🛑 Stop backend services with:
    echo    docker compose down
    echo.
    echo Happy coding! 🎉
) else (
    echo.
    echo ❌ Some services failed to start. Check logs with:
    echo    docker compose logs
)

pause
