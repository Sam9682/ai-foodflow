#!/bin/bash

set -e

# Help function
show_help() {
    echo "🚀 FoodFlow Platform Deployment Script"
    echo "======================================"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  docker    Deploy using Docker Compose (recommended)"
    echo "  manual    Deploy manually with local services"
    echo "  stop      Stop all running services"
    echo "  status    Check service status"
    echo "  logs      Show service logs"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 docker    # Start with Docker"
    echo "  $0 manual    # Start manually"
    echo "  $0 stop      # Stop all services"
    echo "  $0 status    # Check status"
    echo ""
    echo "Documentation:"
    echo "  README.md           - Main documentation"
    echo "  DEPLOYMENT_GUIDE.md - Detailed deployment guide"
    echo "  USER_GUIDE.md       - User interface guide"
    echo "  README_MCP.md       - AI integration guide"
    echo ""
    exit 0
}

# Check for help flag
if [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
fi

echo "🚀 FoodFlow Platform Deployment Script"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Setting up environment..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from template"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env with your API credentials:"
        echo "   • OPENAI_API_KEY - Required for AI features"
        echo "   • Platform API credentials (Uber Eats, Deliveroo, Just Eat)"
        echo "   • Database and Redis URLs (if using manual deployment)"
        echo ""
        echo "📖 See DEPLOYMENT_GUIDE.md for credential setup instructions"
        echo "🔧 Run './deploy.sh help' for more options"
        exit 1
    else
        echo "❌ No .env.example found. Please create .env manually"
        echo "📖 Check DEPLOYMENT_GUIDE.md for environment setup"
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
    echo ""
    echo "🌐 Access Points:"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Chat Interface: Open chat_demo.html in browser"
    echo "   • Prometheus: http://localhost:9090"
    echo "   • Grafana: http://localhost:3000 (admin/admin)"
    echo ""
    echo "📖 Next Steps:"
    echo "   • Check USER_GUIDE.md for usage instructions"
    echo "   • Configure platform API credentials in .env"
    echo "   • Test chat interface with menu images"
    
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
    echo ""
    echo "🌐 Access Points:"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Chat Interface: Open chat_demo.html in browser"
    echo ""
    echo "📖 Next Steps:"
    echo "   • Check USER_GUIDE.md for usage instructions"
    echo "   • Configure platform API credentials in .env"
    echo "   • Test chat interface with menu images"
    echo ""
    echo "🛑 To stop: ./deploy.sh stop"
fi

# Handle additional commands
if [ "$1" = "stop" ]; then
    echo "🛑 Stopping FoodFlow services..."
    
    if [ -f docker-compose.yml ]; then
        docker-compose down
        echo "✅ Docker services stopped"
    fi
    
    if [ -f api.pid ]; then
        kill $(cat api.pid) 2>/dev/null || true
        rm -f api.pid
        echo "✅ API server stopped"
    fi
    
    if [ -f scheduler.pid ]; then
        kill $(cat scheduler.pid) 2>/dev/null || true
        rm -f scheduler.pid
        echo "✅ Scheduler stopped"
    fi
    
    echo "🎉 All services stopped"
    exit 0
fi

if [ "$1" = "status" ]; then
    echo "📊 FoodFlow Service Status"
    echo "========================"
    
    if [ -f docker-compose.yml ] && docker-compose ps | grep -q "Up"; then
        echo "🐳 Docker Services:"
        docker-compose ps
    else
        echo "🔧 Manual Services:"
        if [ -f api.pid ] && kill -0 $(cat api.pid) 2>/dev/null; then
            echo "   ✅ API Server: Running (PID: $(cat api.pid))"
        else
            echo "   ❌ API Server: Not running"
        fi
        
        if [ -f scheduler.pid ] && kill -0 $(cat scheduler.pid) 2>/dev/null; then
            echo "   ✅ Scheduler: Running (PID: $(cat scheduler.pid))"
        else
            echo "   ❌ Scheduler: Not running"
        fi
    fi
    
    echo ""
    echo "🌐 Health Check:"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ API: Healthy"
    else
        echo "   ❌ API: Not responding"
    fi
    
    exit 0
fi

if [ "$1" = "logs" ]; then
    echo "📋 FoodFlow Service Logs"
    echo "======================="
    
    if [ -f docker-compose.yml ] && docker-compose ps | grep -q "Up"; then
        echo "🐳 Docker Logs (last 50 lines):"
        docker-compose logs --tail=50 app
    else
        echo "🔧 Manual Deployment Logs:"
        if [ -f logs/app.log ]; then
            echo "📄 API Server Logs (last 20 lines):"
            tail -20 logs/app.log
        else
            echo "   ❌ No log files found"
        fi
    fi
    
    exit 0
fi

echo ""
echo "🎉 FoodFlow is now running!"
echo ""
echo "📚 Documentation:"
echo "   • README.md - Main documentation"
echo "   • USER_GUIDE.md - Usage instructions"
echo "   • DEPLOYMENT_GUIDE.md - Deployment details"
echo "   • README_MCP.md - AI integration"
echo ""
echo "🔧 Management Commands:"
echo "   • ./deploy.sh status - Check service status"
echo "   • ./deploy.sh logs - View service logs"
echo "   • ./deploy.sh stop - Stop all services"
echo "   • ./deploy.sh help - Show help"