@echo off
REM Complete startup script - Starts both backend (Docker) and frontend (npm)

echo.
echo 🎓 Academy Management System - Complete Startup
echo ================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Start backend services
echo 🚀 Starting backend services...
cd /d "%~dp0"
docker compose up -d

if errorlevel 1 (
    echo ❌ Failed to start backend services
    pause
    exit /b 1
)

echo ✅ Backend services started
echo.

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules\" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install frontend dependencies
        pause
        exit /b 1
    )
    cd ..
)

REM Start frontend in a new window
echo 🎨 Starting frontend...
start "Academy Frontend - npm run dev" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 5 /nobreak >nul

echo.
echo ✅ All services are starting!
echo.
echo 📍 Access points:
echo    Frontend Dashboard: http://localhost:3000
echo    Backend API:        http://localhost:8000
echo    API Documentation:  http://localhost:8000/docs
echo    MinIO Console:      http://localhost:9001
echo.
echo 📊 Check backend logs with:
echo    docker compose logs -f
echo.
echo 🛑 Stop services:
echo    - Close the frontend terminal window
echo    - Run: docker compose down
echo.
echo Happy coding! 🎉
echo.

pause
