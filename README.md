# FoodFlow - Multi-Platform Restaurant Sync System

Automated synchronization platform for Le Bouzou restaurant across Uber Eats, Deliveroo, and Just Eat.

## Features

- **MCP Integration**: Model Context Protocol support for AI systems (Claude, ChatGPT)
- **AI Chat Interface**: Conversational AI assistant for menu management
- **Menu Image Analysis**: Upload menu images for automatic item extraction
- **Centralized Menu Management**: Single source of truth for menu items, prices, and availability
- **Multi-Platform Sync**: Automated synchronization to Uber Eats, Deliveroo, and Just Eat
- **Scheduled Updates**: Daily, weekly, and hourly sync schedules
- **Real-time Monitoring**: Sync status tracking and error handling
- **Configuration Management**: Database-backed credential storage with environment fallback
- **Audit System**: Complete action history and performance tracking
- **REST API**: Complete API for restaurant and menu management

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Server    │    │   FastAPI App    │    │  Platform APIs  │
│                 │    │                  │    │                 │
│ • AI Tools      │◄──►│ • REST Endpoints │◄──►│ • Uber Eats     │
│ • Natural Lang  │    │ • Chat Interface │    │ • Deliveroo     │
│ • Claude/GPT    │    │ • Sync Service   │    │ • Just Eat      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Config & Audit │    │   Redis Cache   │
│                 │    │                  │    │                 │
│ • Restaurants   │    │ • API Credentials│    │ • Sync Queue    │
│ • Menu Items    │    │ • Action History │    │ • Session Data  │
│ • Sync Status   │    │ • Performance    │    │ • Rate Limiting │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start

### 🚀 One-Command Deployment

```bash
# Automated deployment script
./deploy.sh          # Manual deployment
./deploy.sh docker   # Docker deployment
```

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API credentials (see Platform Integration section for how to obtain)
# OPENAI_API_KEY=your_openai_api_key
# DATABASE_URL=postgresql://user:password@localhost:5432/foodflow
# REDIS_URL=redis://localhost:6379/0
# UBER_EATS_CLIENT_ID=your_client_id
# UBER_EATS_CLIENT_SECRET=your_client_secret
# UBER_EATS_STORE_ID=your_store_id
# DELIVEROO_API_KEY=your_api_key
# DELIVEROO_RESTAURANT_ID=your_restaurant_id
# JUST_EAT_API_KEY=your_api_key
# JUST_EAT_TENANT_ID=your_tenant_id
# SECRET_KEY=your_secret_key_here
# RESTAURANT_NAME=Le Bouzou
# RESTAURANT_LOCATION=Montpellier/Castelnau-le-Lez
```

### 2. Docker Deployment (Recommended)

```bash
# Automated Docker deployment
./deploy.sh docker

# Or manual Docker commands:
docker-compose up -d
docker-compose exec app python scripts/init_data.py
```

**Docker Services:**
- **app**: Main FastAPI application
- **scheduler**: Background sync scheduler
- **mcp-server**: MCP server for AI integration
- **db**: PostgreSQL database
- **redis**: Redis cache
- **prometheus**: Metrics collection
- **grafana**: Monitoring dashboard

### 3. Manual Setup

```bash
# Automated manual deployment
./deploy.sh

# Or manual commands:
pip install -r requirements.txt
python scripts/init_data.py
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &
python -c "from app.services.scheduler import scheduler; scheduler.start()" &
```

### 4. Stop Services

```bash
# Docker deployment
docker-compose down

# Manual deployment
./deploy.sh stop
# Or kill processes using saved PIDs
kill $(cat api.pid scheduler.pid)
```

## API Endpoints

### Restaurant Management
- `POST /restaurants/` - Create restaurant
- `GET /restaurants/` - List restaurants
- `GET /restaurants/{id}` - Get restaurant details

### Menu Management
- `POST /menu-items/` - Create menu item
- `GET /menu-items/{restaurant_id}` - Get menu items
- `PUT /menu-items/{item_id}` - Update menu item

### MCP Tools (AI Integration)
- `sync_to_platforms` - Sync menu to delivery platforms
- `add_menu_item` - Add new menu items
- `get_menu` - View current menu
- `update_menu_item` - Update existing items
- `analyze_menu_image` - AI menu analysis
- `get_sync_status` - Check sync status

### AI Chat Interface
- `WebSocket /chat/ws/{restaurant_id}` - Real-time chat with AI
- `POST /chat/message` - Send text message
- `POST /chat/message-with-image` - Send message with image attachment
- `POST /chat/add-items` - Add analyzed menu items
- **Web Interface**: Open `chat_demo.html` in browser for interactive chat

### Configuration Management
- `GET /config/credentials` - View API credentials (masked)
- `POST /config/credentials` - Update API credentials
- `GET /config/status` - Check configuration status

### Audit & Monitoring
- `GET /audit/history` - View action history
- `GET /audit/stats` - Get performance statistics
- `GET /health` - Health check
- `POST /scheduler/start` - Start scheduler
- `POST /scheduler/stop` - Stop scheduler

### Synchronization
- `POST /sync/manual` - Trigger manual sync
- `GET /sync/status/{restaurant_id}` - Get sync status
- `POST /sync/restaurant-info` - Sync restaurant info

## Platform Integration & Credentials

### Uber Eats
**Getting Credentials:**
1. Visit [Uber Eats Developer Portal](https://developer.uber.com/)
2. Create developer account and register your restaurant
3. Apply for Partner API access
4. Get `CLIENT_ID`, `CLIENT_SECRET`, and `STORE_ID`
5. Complete restaurant verification process

**Technical Details:**
- Uses OAuth 2.0 authentication
- JSON format for menu data
- Specific category taxonomy required

### Deliveroo
**Getting Credentials:**
1. Contact Deliveroo Partner Support at [partners@deliveroo.com](mailto:partners@deliveroo.com)
2. Request API access for your restaurant
3. Complete partner onboarding process
4. Receive `API_KEY` and `RESTAURANT_ID`
5. Sign API usage agreement

**Technical Details:**
- Bearer token authentication
- XML/JSON format support
- Different image aspect ratios

### Just Eat
**Getting Credentials:**
1. Visit [Just Eat Partner Centre](https://partners.just-eat.com/)
2. Register as restaurant partner
3. Request API integration through account manager
4. Get `API_KEY` and `TENANT_ID`
5. Complete technical integration review

**Technical Details:**
- API key authentication
- Platform-specific menu structure
- Product-based categorization

**Important Notes:**
- All platforms require active restaurant partnerships
- API access typically requires business verification
- Some platforms have minimum order volume requirements
- Integration approval can take 2-4 weeks

## Sync Schedules

- **Daily Sync**: 2:00 AM - Menu items and prices
- **Weekly Sync**: Sunday 1:00 AM - Full restaurant info
- **Hourly Sync**: Every hour - Availability status

## MCP Integration (AI Systems)

Use FoodFlow with any AI system via Model Context Protocol:

```bash
# Start MCP server
python start_mcp.py

# Configure AI client (Claude, ChatGPT, etc.)
# Add mcp_config.json to client configuration
```

**Natural Language Commands:**
- "Add a new pizza to Le Bouzou's menu for €12.50"
- "Sync the menu to Uber Eats and Deliveroo"
- "Show me the current menu"
- "Update item 5's price to €15.00"
- "Check sync status for restaurant 1"

**Supported AI Clients:**
- Claude Desktop
- ChatGPT (via MCP plugin)
- Custom AI applications
- Any MCP-compatible system

## AI Chat Interface

Access the conversational AI interface:
- **Web Chat Demo**: Open `chat_demo.html` in your browser
- **WebSocket**: ws://localhost:8000/chat/ws/{restaurant_id}
- **Features**: 
  - Natural language menu management
  - Drag & drop image upload and analysis
  - Platform sync commands
  - Real-time responses
  - Interactive suggestions
  - Action buttons for quick operations
  - Menu item visualization
  - Sync result tracking

## Monitoring & Health Checks

Access monitoring dashboards:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Chat Interface**: Open `chat_demo.html` in browser
- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Database**: PostgreSQL on port 5432
- **Redis Cache**: Redis on port 6379

## Development

### Project Structure
```
FoodFlow/
├── app/
│   ├── api/           # FastAPI endpoints (main, chat, config, audit, bot, websocket)
│   ├── core/          # Database configuration & initialization
│   ├── models/        # SQLAlchemy models (restaurant, config, audit)
│   ├── services/      # Business logic (sync, AI, config, audit, menu_scanner)
│   └── utils/         # Utilities (image processing)
├── config/            # Configuration files (prometheus.yml)
├── scripts/           # Initialization scripts (init_data.py)
├── deploy.sh          # Automated deployment script
├── docker-compose.yml # Multi-service Docker configuration
├── Dockerfile         # Main application container
├── Dockerfile.mcp     # MCP server container
├── mcp_server.py      # MCP server for AI integration
├── start_mcp.py       # MCP server startup script
├── mcp_config.json    # MCP client configuration
├── chat_demo.html     # Interactive web chat interface
├── .env.example       # Environment template
├── README_MCP.md      # MCP integration guide
└── requirements.txt   # Python dependencies
```

### Adding New Platforms

1. Create adapter in `app/services/platform_adapters.py`
2. Implement `PlatformAdapter` interface
3. Add to `SyncService.platforms` dictionary
4. Update environment variables

## Configuration Management

FoodFlow automatically manages API credentials:

**Priority System:**
1. Environment variables (highest priority)
2. Database storage (fallback)

**Features:**
- Automatic sync of env vars to database on startup
- Secure credential storage with masking
- Configuration API for runtime updates
- Fallback system ensures availability

## Audit System

Complete tracking of all platform operations:

**Tracked Actions:**
- Platform synchronizations (success/failure)
- Menu operations (add, update, delete)
- Configuration changes
- AI interactions and image analysis
- System events and errors

**Query Examples:**
```bash
# Get sync history
GET /audit/history?action_type=platform_sync&days=7

# Get performance stats
GET /audit/stats?days=30
```

## Success Metrics

- ✅ Sync accuracy rate >99%
- ✅ Automated daily updates
- ✅ Error rate <1%
- ✅ Platform consistency
- ✅ Real-time monitoring
- ✅ MCP AI integration
- ✅ Complete audit trail
- ✅ Secure credential management
- ✅ Natural language interface
- ✅ One-command deployment
- ✅ Multi-container architecture
- ✅ Interactive web chat
- ✅ Image upload & analysis
- ✅ Health checks & metrics
- ✅ Redis caching
- ✅ Background scheduling

## Support

For support:
- Email: lepetre@yahoo.fr
- Phone: +33 6 XX XX XX XX
- Location: Montpellier