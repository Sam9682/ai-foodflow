# FoodFlow Architecture Guide

## System Architecture Overview

FoodFlow follows a microservices architecture with AI-first design principles, enabling seamless integration with GenAI agents and automated deployment processes.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GenAI Agent   │────│  MCP Server     │────│   FastAPI App   │
│   (Q Chat)      │    │  (AI Bridge)    │    │   (Core Logic)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│  Docker Engine  │──────────────┘
                        │  (Orchestration)│
                        └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │  External APIs  │
│   (Database)    │    │    (Cache)      │    │  (Platforms)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. FastAPI Application Layer
- **Purpose**: REST API endpoints and business logic
- **Location**: `/app` directory
- **Key Features**:
  - Menu management endpoints
  - Platform synchronization logic
  - Image analysis integration
  - Health monitoring

### 2. MCP Server (Model Context Protocol)
- **Purpose**: AI agent communication bridge
- **Location**: `start_mcp.py`
- **Key Features**:
  - Tool registration for AI agents
  - Natural language command processing
  - Structured AI-to-API communication

### 3. Database Layer
- **PostgreSQL**: Primary data storage
- **Redis**: Caching and session management
- **Migrations**: Automated schema management

### 4. External Platform Integration
- **Uber Eats API**: Menu synchronization
- **Deliveroo API**: Order and menu management
- **Just Eat API**: Multi-platform sync

## Standardized Deployment Architecture

### Universal Deployment Process

All applications following this architecture use the same deployment pattern:

```
Application Repository
├── deploy.ini          # Application-specific configuration
├── deploy.sh          # Universal deployment script (identical across apps)
├── docker-compose.yml # Container orchestration
├── Dockerfile         # Application containerization
└── requirements.txt   # Dependencies
```

### 1. deploy.ini Configuration

Each application only needs to customize `deploy.ini`:

```ini
[application]
name=ai-foodflow
port=8000
health_endpoint=/health

[database]
type=postgresql
name=foodflow

[services]
redis=true
nginx=false
celery=false

[ai]
mcp_enabled=true
openai_required=true
```

### 2. Universal deploy.sh Script

The `deploy.sh` script is identical across all applications and handles:

```bash
#!/bin/bash
# Universal deployment script - DO NOT MODIFY
# Reads deploy.ini for application-specific configuration

source deploy.ini

case "$1" in
    "docker")
        docker-compose up -d --build
        ;;
    "local")
        pip install -r requirements.txt
        python main.py
        ;;
    "production")
        docker-compose -f docker-compose.prod.yml up -d
        ;;
esac
```

### 3. Docker Compose Architecture

Standard container orchestration pattern:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "${APP_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## GenAI Agent Integration

### Q Chat Integration Flow

```
1. User Command → Q Chat Agent
2. Agent Analysis → MCP Server
3. Tool Selection → FastAPI Endpoints
4. Database Operations → Response
5. Platform Sync → External APIs
```

### MCP Tool Registration

```python
# Automatic tool discovery and registration
@mcp_tool
async def sync_to_platforms():
    """Sync menu to all delivery platforms"""
    # Implementation handled by FastAPI endpoints

@mcp_tool  
async def add_menu_item(name: str, price: float):
    """Add new menu item with AI validation"""
    # Natural language processing + database operations
```

## Application Evolution Process

### 1. Automated Development Cycle

```
GenAI Agent Request → Code Analysis → Modification → Testing → Deployment
```

### 2. Standardized Modification Points

- **deploy.ini**: Service configuration
- **requirements.txt**: Dependencies
- **app/**: Business logic
- **docker-compose.yml**: Infrastructure needs

### 3. Zero-Touch Deployment

```bash
# Same command for all applications
./deploy.sh docker

# Automatic:
# - Dependency installation
# - Database migration
# - Service orchestration
# - Health verification
```

## Data Flow Architecture

### Request Processing Pipeline

```
External Request → FastAPI Router → Business Logic → Database Layer → Response
                ↓
         AI Processing → MCP Bridge → Tool Execution → Platform APIs
```

### AI-Enhanced Operations

1. **Natural Language Input**: User commands in plain English
2. **Intent Recognition**: MCP server processes and categorizes
3. **Tool Mapping**: Automatic selection of appropriate endpoints
4. **Execution**: Database operations and external API calls
5. **Response Generation**: Human-readable status updates

## Security Architecture

### Authentication Layers
- **API Keys**: Platform-specific credentials
- **Environment Variables**: Secure configuration management
- **Container Isolation**: Service-level security boundaries

### Data Protection
- **Encrypted Storage**: Sensitive credentials in environment files
- **Network Isolation**: Container-to-container communication only
- **Input Validation**: AI-powered request sanitization

## Monitoring and Observability

### Health Check System
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_db_connection(),
        "redis": await check_redis_connection(),
        "external_apis": await check_platform_apis()
    }
```

### Logging Architecture
- **Application Logs**: FastAPI request/response logging
- **AI Interaction Logs**: MCP server communication tracking
- **Platform Sync Logs**: External API call monitoring

## Scalability Considerations

### Horizontal Scaling
- **Stateless Design**: All services can be replicated
- **Database Connection Pooling**: Efficient resource utilization
- **Redis Caching**: Reduced database load

### Performance Optimization
- **Async Operations**: Non-blocking I/O for external APIs
- **Background Tasks**: Queue-based platform synchronization
- **Caching Strategy**: Intelligent data caching with Redis

## Development Guidelines

### Adding New Features
1. Update `deploy.ini` if new services required
2. Implement business logic in `/app`
3. Register MCP tools for AI integration
4. Update docker-compose.yml if infrastructure changes needed
5. Deploy with `./deploy.sh docker`

### AI Agent Enhancement
1. Define new tools in MCP server
2. Implement corresponding FastAPI endpoints
3. Test with natural language commands
4. Deploy automatically via GenAI agent

This architecture ensures consistent, scalable, and AI-enhanced application development with minimal manual intervention.