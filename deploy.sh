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
    echo "  start     Deploy using Docker Compose (recommended)"
    echo "  manual    Deploy manually with local scripts"
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

# Handle special commands first
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
    echo "📊 FoodFlow Application Status"
    echo "=============================="
    
    # Check Docker vs Manual deployment
    if [ -f docker-compose.yml ] && docker-compose ps | grep -q "Up"; then
        echo "🐳 Docker Services:"
        docker-compose ps
        echo ""
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
        echo ""
    fi
    
    # Test API Health
    echo "🌐 API Health Tests:"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Health Endpoint: Responding"
        
        # Test main endpoints
        if curl -s http://localhost:8000/main > /dev/null 2>&1; then
            echo "   ✅ Main Dashboard: Accessible"
        else
            echo "   ❌ Main Dashboard: Not accessible"
        fi
        
        if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
            echo "   ✅ API Documentation: Accessible"
        else
            echo "   ❌ API Documentation: Not accessible"
        fi
        
        # Test database connection
        if curl -s http://localhost:8000/config/status > /dev/null 2>&1; then
            echo "   ✅ Database: Connected"
        else
            echo "   ❌ Database: Connection failed"
        fi
        
        # Test menu API
        if curl -s http://localhost:8000/menu-items/1 > /dev/null 2>&1; then
            echo "   ✅ Menu API: Functional"
        else
            echo "   ❌ Menu API: Not responding"
        fi
        
    else
        echo "   ❌ API Server: Not responding"
        echo "   ❌ All dependent services: Unavailable"
    fi
    
    echo ""
    echo "🔗 Service Ports:"
    if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
        echo "   ✅ Port 8000 (API): In use"
    else
        echo "   ❌ Port 8000 (API): Not listening"
    fi
    
    if netstat -tlnp 2>/dev/null | grep -q ":5432"; then
        echo "   ✅ Port 5432 (PostgreSQL): In use"
    else
        echo "   ❌ Port 5432 (PostgreSQL): Not listening"
    fi
    
    if netstat -tlnp 2>/dev/null | grep -q ":6379"; then
        echo "   ✅ Port 6379 (Redis): In use"
    else
        echo "   ❌ Port 6379 (Redis): Not listening"
    fi
    
    echo ""
    echo "📋 Overall Status:"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ FoodFlow: RUNNING"
        echo "   🌐 Access: http://localhost:8000/main"
    else
        echo "   ❌ FoodFlow: NOT RUNNING"
        echo "   🔧 Run: ./deploy.sh to start services"
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

# Check if .env exists for deployment commands
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

# Set default deployment method to manual if no parameter provided
DEPLOY_METHOD="${1:-manual}"

# Check deployment method
if [ "$DEPLOY_METHOD" = "start" ]; then
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
    echo "   • Main Dashboard: http://localhost:8000/main"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Chat Interface: http://localhost:8000/static/chat_discussion.html"
    echo "   • Menu Management: http://localhost:8000/menu-management"
    echo "   • Audit Records: http://localhost:8000/audit-page"
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
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    python scripts/init_data.py
    
    # Start API server in background
    echo "🚀 Starting API server..."
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    
    # Start scheduler in background
    echo "⏰ Starting scheduler..."
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    python -c "from app.services.scheduler import scheduler; scheduler.start()" &
    SCHEDULER_PID=$!
    
    # Save PIDs for cleanup
    echo $API_PID > api.pid
    echo $SCHEDULER_PID > scheduler.pid
    
    echo "✅ Manual deployment complete!"
    echo ""
    echo "🌐 Access Points:"
    echo "   • Main Dashboard: http://localhost:8000/main"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Chat Interface: http://localhost:8000/static/chat_discussion.html"
    echo "   • Menu Management: http://localhost:8000/menu-management"
    echo "   • Audit Records: http://localhost:8000/audit-page"
    echo ""
    echo "📖 Next Steps:"
    echo "   • Check USER_GUIDE.md for usage instructions"
    echo "   • Configure platform API credentials in .env"
    echo "   • Test chat interface with menu images"
    echo ""
    echo "🛑 To stop: ./deploy.sh stop"
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