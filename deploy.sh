#!/bin/bash

set -e

echo "🚀 FoodFlow Platform Deployment Script"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Setting up environment..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from template"
        echo "⚠️  Please edit .env with your API credentials before continuing"
        exit 1
    else
        echo "❌ No .env.example found. Please create .env manually"
        exit 1
    fi
fi

# Check deployment method
if [ "$1" = "docker" ] || [ -f docker-compose.yml ]; then
    echo "🐳 Starting Docker deployment..."
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Initialize data
    echo "📊 Initializing Le Bouzou data..."
    docker-compose exec app python scripts/init_data.py
    
    echo "✅ Docker deployment complete!"
    echo "🌐 API: http://localhost:8000"
    echo "📊 Prometheus: http://localhost:9090"
    echo "📈 Grafana: http://localhost:3000 (admin/admin)"
    
else
    echo "🔧 Starting manual deployment..."
    
    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    # Initialize database
    echo "🗄️ Initializing database..."
    python scripts/init_data.py
    
    # Start API server in background
    echo "🚀 Starting API server..."
    uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    
    # Start scheduler in background
    echo "⏰ Starting scheduler..."
    python -c "from app.services.scheduler import scheduler; scheduler.start()" &
    SCHEDULER_PID=$!
    
    # Save PIDs for cleanup
    echo $API_PID > api.pid
    echo $SCHEDULER_PID > scheduler.pid
    
    echo "✅ Manual deployment complete!"
    echo "🌐 API: http://localhost:8000"
    echo "💬 Chat Demo: Open chat_demo.html in browser"
    echo "🛑 To stop: ./deploy.sh stop"
fi

echo ""
echo "🎉 FoodFlow is now running!"
echo "📖 Check README.md for API endpoints and usage"