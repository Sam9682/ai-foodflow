# FoodFlow MCP Integration

FoodFlow now supports Model Context Protocol (MCP) for seamless integration with generative AI systems like Claude, ChatGPT, and other AI assistants.

## MCP Tools Available

### 1. **sync_to_platforms**
Sync restaurant menu to delivery platforms
```
Parameters:
- restaurant_id (required): Restaurant ID
- platforms (optional): Array of platforms ["uber_eats", "deliveroo", "just_eat"]
```

### 2. **add_menu_item**
Add new menu item to restaurant
```
Parameters:
- restaurant_id (required): Restaurant ID
- name (required): Item name
- description: Item description
- price (required): Item price
- category (required): Item category
- is_available: Item availability (default: true)
```

### 3. **get_menu**
Get current menu for restaurant
```
Parameters:
- restaurant_id (required): Restaurant ID
```

### 4. **update_menu_item**
Update existing menu item
```
Parameters:
- item_id (required): Menu item ID
- name: Item name
- description: Item description
- price: Item price
- category: Item category
- is_available: Item availability
```

### 5. **analyze_menu_image**
Analyze menu image using AI
```
Parameters:
- restaurant_id (required): Restaurant ID
- image_data (required): Base64 encoded image
- message: Description message (default: "Analyze this menu")
```

### 6. **get_sync_status**
Get synchronization status for platforms
```
Parameters:
- restaurant_id (required): Restaurant ID
```

## Setup Instructions

### 🚀 Quick Start with Deploy Script
```bash
# Automated deployment (includes MCP server)
./deploy.sh docker   # Docker deployment with MCP service
./deploy.sh          # Manual deployment
```

### 1. Install Dependencies
```bash
# Install all dependencies (including MCP)
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
# Add your API credentials and database URL
```

### 3. Start MCP Server

**Docker Deployment (Recommended):**
```bash
# MCP server runs automatically in Docker
docker-compose up -d mcp-server
```

**Manual Deployment:**
```bash
# Option 1: Direct start
python mcp_server.py

# Option 2: With environment loader
python start_mcp.py

# Option 3: Via deploy script
./deploy.sh  # Includes MCP server setup
```

### 4. Configure AI Client

**For Docker Deployment:**
```json
{
  "mcpServers": {
    "foodflow": {
      "command": "docker",
      "args": ["exec", "-i", "ai-foodflow-mcp-server-1", "python", "start_mcp.py"],
      "cwd": "/path/to/ai-foodflow"
    }
  }
}
```

**For Manual Deployment:**
```json
{
  "mcpServers": {
    "foodflow": {
      "command": "python",
      "args": ["start_mcp.py"],
      "cwd": "/path/to/ai-foodflow",
      "env": {
        "DATABASE_URL": "postgresql://foodflow:password@localhost:5432/foodflow",
        "OPENAI_API_KEY": "your_openai_api_key"
      }
    }
  }
}
```

**Alternative Configuration (using mcp_config.json):**
```bash
# Copy the provided configuration
cp mcp_config.json ~/.config/ai-client/mcp_servers.json
# Edit paths and credentials as needed
```

## Usage Examples

### Natural Language Commands via AI:

**"Add a new pizza to Le Bouzou's menu"**
```
AI will use: add_menu_item
Parameters: restaurant_id=1, name="Pizza Margherita", price=12.50, category="Pizzas"
```

**"Sync Le Bouzou's menu to Uber Eats"**
```
AI will use: sync_to_platforms
Parameters: restaurant_id=1, platforms=["uber_eats"]
```

**"Show me the current menu for restaurant 1"**
```
AI will use: get_menu
Parameters: restaurant_id=1
```

**"Update the price of menu item 5 to €15.00"**
```
AI will use: update_menu_item
Parameters: item_id=5, price=15.00
```

**"Check sync status for Le Bouzou"**
```
AI will use: get_sync_status
Parameters: restaurant_id=1
```

## Integration Benefits

✅ **Natural Language Interface**: Use plain English to manage restaurant data  
✅ **AI-Powered**: Leverage generative AI for complex operations  
✅ **Standardized Protocol**: MCP ensures compatibility across AI systems  
✅ **Real-time Operations**: Direct database and API integration  
✅ **Error Handling**: Comprehensive error reporting and validation  
✅ **Audit Trail**: All MCP operations are logged in audit system  

## Supported AI Clients

- **Claude Desktop**: Add FoodFlow to MCP servers
- **ChatGPT**: Via MCP plugin
- **Custom AI Applications**: Any MCP-compatible system
- **Development Tools**: IDEs with MCP support

## Docker Integration

FoodFlow includes a dedicated MCP server container:

**Docker Services:**
- `mcp-server`: Dedicated MCP server container
- `app`: Main FastAPI application
- `db`: PostgreSQL database
- `redis`: Redis cache

**Container Features:**
- Isolated MCP server environment
- Shared database access with main app
- Environment variable injection
- Health checks and monitoring
- Automatic restart on failure

## Monitoring MCP Server

```bash
# Check MCP server status (Docker)
docker-compose logs mcp-server
docker-compose exec mcp-server python -c "print('MCP Server is running')"

# Check MCP server status (Manual)
ps aux | grep mcp_server
tail -f logs/mcp_server.log
```

## Security Notes

- MCP server runs locally with database access
- API credentials managed through secure config system
- All operations logged in audit trail
- Environment variables for sensitive data
- Docker isolation for enhanced security
- Network-level access controls

## Troubleshooting

**Common Issues:**
- **Connection refused**: Ensure database is running and accessible
- **Permission denied**: Check file permissions and Docker access
- **Module not found**: Verify all dependencies are installed
- **Database connection**: Check DATABASE_URL in environment

**Debug Commands:**
```bash
# Test MCP server connection
python -c "from mcp_server import app; print('MCP server imports successfully')"

# Check database connection
python -c "from app.core.database import engine; print('Database connected')"

# Verify environment variables
python -c "import os; print('DB:', os.getenv('DATABASE_URL'))"
```

The MCP integration makes FoodFlow accessible to any generative AI system, enabling natural language restaurant management and platform synchronization with enterprise-grade deployment options.