@echo off
REM Scholarix AI Theme - Docker Test Script for Windows

echo 🐳 Starting Scholarix AI Theme Docker Test Environment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose not found. Please install docker-compose.
    pause
    exit /b 1
)

echo ✅ docker-compose is available

REM Clean up any existing containers
echo 🧹 Cleaning up existing containers...
docker-compose down -v

REM Create a placeholder logo if it doesn't exist
if not exist "static\src\img\logo.png" (
    echo 📸 Creating placeholder logo directory...
    if not exist "static\src\img" mkdir static\src\img
    echo. > static\src\img\logo.png
    echo ⚠️  Please place your Scholarix logo at static\src\img\logo.png
)

REM Start the containers
echo 🚀 Starting Odoo 18 with Scholarix Theme...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 >nul

REM Check if containers are running
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ Containers are running!
    echo.
    echo 🌐 Access your Odoo instance at: http://localhost:8069
    echo 📊 Database: postgres
    echo 👤 Default admin user will be created on first access
    echo.
    echo 📋 Next Steps:
    echo 1. Go to http://localhost:8069
    echo 2. Create database or use existing
    echo 3. Login as admin
    echo 4. Go to Apps → Search 'Scholarix' → Install
    echo 5. Go to Website → Settings → Select Theme
    echo.
    echo 🔧 To stop the test environment:
    echo    docker-compose down
    echo.
    echo 📝 To view logs:
    echo    docker-compose logs -f web
    echo.
) else (
    echo ❌ Failed to start containers. Check logs:
    docker-compose logs
    pause
    exit /b 1
)

REM Show container status
echo 📊 Container Status:
docker-compose ps

echo.
echo Press any key to continue...
pause >nul
