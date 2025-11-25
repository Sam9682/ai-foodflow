# FoodFlow - AI-Powered Restaurant Menu Sync

## Objective

FoodFlow automates restaurant menu synchronization across multiple delivery platforms (Uber Eats, Deliveroo, Just Eat) using AI-powered natural language processing. It provides:

- **AI Menu Management**: Natural language commands for menu operations
- **Image Analysis**: Automatic menu extraction from uploaded images
- **Multi-Platform Sync**: Automated synchronization to delivery platforms
- **MCP Integration**: Model Context Protocol for AI agent interaction

## Installation & Configuration

### Automated Installation (GenAI Agent Compatible)

```bash
# 1. Clone and setup
git clone <repository_url> ai-foodflow
cd ai-foodflow

# 2. One-command deployment
./deploy.sh docker

# 3. Verify installation
curl http://localhost:8000/health
```

### Environment Configuration

Create `.env` file with required credentials:

```bash
# Required for AI functionality
OPENAI_API_KEY=your_openai_api_key

# Database (auto-configured in Docker)
DATABASE_URL=postgresql://user:password@db:5432/foodflow
REDIS_URL=redis://redis:6379/0

# Platform API credentials (obtain from respective platforms)
UBER_EATS_CLIENT_ID=your_client_id
UBER_EATS_CLIENT_SECRET=your_client_secret
UBER_EATS_STORE_ID=your_store_id
DELIVEROO_API_KEY=your_api_key
DELIVEROO_RESTAURANT_ID=your_restaurant_id
JUST_EAT_API_KEY=your_api_key
JUST_EAT_TENANT_ID=your_tenant_id

# System configuration
SECRET_KEY=generate_random_secret_key
RESTAURANT_NAME=Your_Restaurant_Name
RESTAURANT_LOCATION=Your_Location
```

### Service Endpoints

- **API**: http://localhost:8000
- **AI Chat**: http://localhost:8000/static/chat_discussion.html
- **Menu Management**: http://localhost:8000/menu-management
- **Health Check**: http://localhost:8000/health

## AI Agent Integration

### MCP Server (Model Context Protocol)

```bash
# Start MCP server for AI integration
python start_mcp.py
```

### Available AI Tools

- `sync_to_platforms` - Sync menu to delivery platforms
- `add_menu_item` - Add new menu items
- `get_menu` - View current menu
- `update_menu_item` - Update existing items
- `analyze_menu_image` - AI menu analysis from images
- `get_sync_status` - Check synchronization status

### Natural Language Commands

```
"Add pizza margherita for €12.50 to the menu"
"Sync menu to all platforms"
"Update item 5 price to €15.00"
"Analyze this menu image"
"Show current menu status"
```

## Platform Credentials Setup

### Required API Credentials

**Uber Eats**: [developer.uber.com](https://developer.uber.com/)
- `UBER_EATS_CLIENT_ID`
- `UBER_EATS_CLIENT_SECRET` 
- `UBER_EATS_STORE_ID`

**Deliveroo**: Contact partners@deliveroo.com
- `DELIVEROO_API_KEY`
- `DELIVEROO_RESTAURANT_ID`

**Just Eat**: [partners.just-eat.com](https://partners.just-eat.com/)
- `JUST_EAT_API_KEY`
- `JUST_EAT_TENANT_ID`

### Verification Commands

```bash
# Check system health
curl http://localhost:8000/health

# Verify AI integration
curl http://localhost:8000/config/status

# Test MCP server
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

## Troubleshooting

```bash
# View logs
docker-compose logs app

# Restart services
docker-compose restart

# Reset database
docker-compose down -v && docker-compose up -d
```