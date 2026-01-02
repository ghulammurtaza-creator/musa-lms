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

echo 🚀 Starting services...
echo.

REM Start Docker Compose
docker-compose up -d

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ✅ All services are running!
    echo.
    echo 📍 Access points:
    echo    Frontend Dashboard: http://localhost:3000
    echo    Backend API:        http://localhost:8000
    echo    API Documentation:  http://localhost:8000/api/docs
    echo.
    echo 📊 Check logs with:
    echo    docker-compose logs -f
    echo.
    echo 🛑 Stop services with:
    echo    docker-compose down
    echo.
    echo Happy coding! 🎉
) else (
    echo.
    echo ❌ Some services failed to start. Check logs with:
    echo    docker-compose logs
)

pause
