#!/bin/bash

# TradeFly Backend Deployment Script
# Run this on your EC2 instance to deploy/update the backend

set -e

echo "🚀 TradeFly Backend Deployment"
echo "=============================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please don't run as root. Run as your normal user."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please create .env file from .env.example:"
    echo "   cp .env.example .env"
    echo "   nano .env  # Edit with your keys"
    exit 1
fi

# Pull latest changes (if in git repo)
if [ -d .git ]; then
    echo "📥 Pulling latest changes from GitHub..."
    git pull origin main || echo "⚠️  Git pull failed, continuing with local files"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Build new image
echo "🔨 Building Docker image..."
docker-compose build --no-cache

# Start containers
echo "▶️  Starting TradeFly Backend..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for service to be healthy..."
sleep 10

# Check if container is running
if docker ps | grep -q tradefly-backend; then
    echo "✅ TradeFly Backend is running!"
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "📝 Logs (last 20 lines):"
    docker-compose logs --tail=20
    echo ""
    echo "🌐 Service should be available at:"
    echo "   http://localhost:8000"
    echo "   http://$(curl -s ifconfig.me):8000"
    echo ""
    echo "📚 Useful commands:"
    echo "   View logs:    docker-compose logs -f"
    echo "   Restart:      docker-compose restart"
    echo "   Stop:         docker-compose down"
    echo "   Shell access: docker-compose exec tradefly-backend bash"
else
    echo "❌ Container failed to start!"
    echo "📝 Checking logs..."
    docker-compose logs --tail=50
    exit 1
fi
