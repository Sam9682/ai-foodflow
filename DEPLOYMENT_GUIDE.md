# FoodFlow Deployment Guide

Complete deployment guide for FoodFlow multi-platform restaurant sync system.

## 🚀 Quick Deployment

### One-Command Deployment
```bash
# Make deploy script executable
chmod +x deploy.sh

# Docker deployment (recommended)
./deploy.sh docker

# Manual deployment
./deploy.sh

# Stop services
./deploy.sh stop
```

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Python**: 3.11 or higher
- **Docker**: 20.10+ (for Docker deployment)
- **Docker Compose**: 2.0+ (for Docker deployment)
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 5GB free space

### Required Services
- **PostgreSQL**: 15+ (included in Docker deployment)
- **Redis**: 7+ (included in Docker deployment)
- **Internet**: For platform API access

## 🐳 Docker Deployment (Recommended)

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd ai-foodflow

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Deploy with Script
```bash
# Automated Docker deployment
./deploy.sh docker
```

### 3. Manual Docker Commands
```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec app python scripts/init_data.py

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Docker Services Overview
| Service | Port | Description |
|---------|------|-------------|
| app | 8000 | Main FastAPI application |
| scheduler | - | Background sync scheduler |
| mcp-server | - | MCP server for AI integration |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| prometheus | 9090 | Metrics collection |
| grafana | 3000 | Monitoring dashboard |

## 🔧 Manual Deployment

### 1. System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip postgresql redis-server

# macOS
brew install python@3.11 postgresql redis

# Windows (WSL2)
sudo apt update
sudo apt install python3.11 python3-pip postgresql redis-server
```

### 2. Database Setup
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE foodflow;
CREATE USER foodflow WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE foodflow TO foodflow;
\q
```

### 3. Redis Setup
```bash
# Start Redis
sudo systemctl start redis-server

# Test Redis connection
redis-cli ping
```

### 4. Application Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://foodflow:password@localhost:5432/foodflow"
export REDIS_URL="redis://localhost:6379/0"

# Initialize database
python scripts/init_data.py
```

### 5. Start Services
```bash
# Option 1: Use deploy script
./deploy.sh

# Option 2: Manual start
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &
python -c "from app.services.scheduler import scheduler; scheduler.start()" &
python start_mcp.py &
```

## 🌐 Environment Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/foodflow
REDIS_URL=redis://localhost:6379/0

# AI Configuration
OPENAI_API_KEY=your_openai_api_key

# Platform APIs
UBER_EATS_CLIENT_ID=your_client_id
UBER_EATS_CLIENT_SECRET=your_client_secret
UBER_EATS_STORE_ID=your_store_id
DELIVEROO_API_KEY=your_api_key
DELIVEROO_RESTAURANT_ID=your_restaurant_id
JUST_EAT_API_KEY=your_api_key
JUST_EAT_TENANT_ID=your_tenant_id

# Application Settings
SECRET_KEY=your_secret_key_here
DEBUG=False
LOG_LEVEL=INFO
RESTAURANT_NAME=Le Bouzou
RESTAURANT_LOCATION=Montpellier/Castelnau-le-Lez
```

### Optional Environment Variables
```bash
# Performance
WORKERS=4
MAX_CONNECTIONS=100
TIMEOUT=30

# Security
CORS_ORIGINS=["http://localhost:3000"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

## 🔍 Verification & Testing

### Health Checks
```bash
# API health check
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/config/status

# MCP server (if running)
python -c "from mcp_server import app; print('MCP OK')"
```

### Service Status
```bash
# Docker deployment
docker-compose ps
docker-compose logs app

# Manual deployment
ps aux | grep uvicorn
ps aux | grep scheduler
netstat -tlnp | grep :8000
```

### Functional Tests
```bash
# Test API endpoints
curl http://localhost:8000/restaurants/
curl http://localhost:8000/menu-items/1

# Test chat interface
# Open chat_demo.html in browser
# Navigate to http://localhost:8000/docs for API documentation
```

## 📊 Monitoring Setup

### Prometheus Configuration
```bash
# Prometheus available at http://localhost:9090
# Metrics endpoint: http://localhost:8000/metrics
```

### Grafana Dashboard
```bash
# Access: http://localhost:3000
# Login: admin/admin
# Import FoodFlow dashboard (if available)
```

### Log Management
```bash
# Docker logs
docker-compose logs -f app
docker-compose logs -f scheduler

# Manual deployment logs
tail -f logs/app.log
tail -f logs/scheduler.log
```

## 🔧 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.api.main:app --port 8001
```

**Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U foodflow -d foodflow

# Reset database
docker-compose down -v
docker-compose up -d db
```

**Redis Connection Failed**
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Restart Redis
sudo systemctl restart redis-server
```

**Permission Denied**
```bash
# Fix file permissions
chmod +x deploy.sh
chmod -R 755 app/

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

### Debug Commands
```bash
# Check environment variables
env | grep -E "(DATABASE|REDIS|OPENAI)"

# Test imports
python -c "from app.api.main import app; print('Import OK')"

# Database migration
python -c "from app.core.db_init import init_db; init_db()"

# Clear Redis cache
redis-cli FLUSHALL
```

## 🔄 Updates & Maintenance

### Updating FoodFlow
```bash
# Pull latest changes
git pull origin main

# Docker deployment
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Manual deployment
pip install -r requirements.txt --upgrade
./deploy.sh stop
./deploy.sh
```

### Database Migrations
```bash
# Backup database
pg_dump -h localhost -U foodflow foodflow > backup.sql

# Run migrations (if available)
python scripts/migrate.py

# Restore from backup (if needed)
psql -h localhost -U foodflow foodflow < backup.sql
```

### Performance Optimization
```bash
# Increase worker processes
export WORKERS=8

# Optimize database
docker-compose exec db psql -U foodflow -d foodflow -c "VACUUM ANALYZE;"

# Clear Redis cache
redis-cli FLUSHALL
```

## 🚀 Production Deployment

### Security Hardening
```bash
# Use strong passwords
# Enable SSL/TLS
# Configure firewall
# Set up monitoring alerts
# Regular security updates
```

### Scaling Considerations
```bash
# Load balancer configuration
# Database replication
# Redis clustering
# Container orchestration (Kubernetes)
# CDN for static assets
```

### Backup Strategy
```bash
# Database backups
# Configuration backups
# Log rotation
# Disaster recovery plan
```

## 📞 Support

For deployment issues:
- Check logs first: `docker-compose logs` or `tail -f logs/app.log`
- Review this guide and README.md
- Contact: lepetre@yahoo.fr

## 🎉 Success Checklist

- [ ] All services running (app, db, redis, scheduler)
- [ ] Health check returns 200 OK
- [ ] Chat interface accessible
- [ ] API documentation available
- [ ] MCP server responding (if using AI)
- [ ] Monitoring dashboards accessible
- [ ] Database initialized with Le Bouzou data
- [ ] Environment variables configured
- [ ] Platform API credentials set
- [ ] Sync scheduler active