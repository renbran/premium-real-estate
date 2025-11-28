#!/bin/bash
# Scholarix AI Theme - Docker Test Script

echo "🐳 Starting Scholarix AI Theme Docker Test Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "✅ docker-compose is available"

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down -v

# Create a placeholder logo if it doesn't exist
if [ ! -f "static/src/img/logo.png" ]; then
    echo "📸 Creating placeholder logo..."
    mkdir -p static/src/img
    # Create a simple placeholder image using ImageMagick if available
    if command -v convert > /dev/null 2>&1; then
        convert -size 200x200 xc:transparent -fill "#00E5FF" -draw "circle 100,100 100,50" -pointsize 24 -fill white -gravity center -annotate +0+0 "SCHOLARIX" static/src/img/logo.png
    else
        echo "⚠️  ImageMagick not found. Please place your logo at static/src/img/logo.png manually"
        touch static/src/img/logo.png
    fi
fi

# Start the containers
echo "🚀 Starting Odoo 18 with Scholarix Theme..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Containers are running!"
    echo ""
    echo "🌐 Access your Odoo instance at: http://localhost:8069"
    echo "📊 Database: postgres"
    echo "👤 Default admin user will be created on first access"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Go to http://localhost:8069"
    echo "2. Create database or use existing"
    echo "3. Login as admin"
    echo "4. Go to Apps → Search 'Scholarix' → Install"
    echo "5. Go to Website → Settings → Select Theme"
    echo ""
    echo "🔧 To stop the test environment:"
    echo "   docker-compose down"
    echo ""
    echo "📝 To view logs:"
    echo "   docker-compose logs -f web"
else
    echo "❌ Failed to start containers. Check logs:"
    docker-compose logs
    exit 1
fi

# Show container status
echo "📊 Container Status:"
docker-compose ps
