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

### 1. Install MCP Dependencies
```bash
pip install mcp==1.0.0
```

### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
# Add your API credentials
```

### 3. Start MCP Server
```bash
# Option 1: Direct start
python mcp_server.py

# Option 2: With environment loader
python start_mcp.py
```

### 4. Configure AI Client
Add to your AI client's MCP configuration:
```json
{
  "mcpServers": {
    "foodflow": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/FoodFlow",
      "env": {
        "DATABASE_URL": "postgresql://foodflow:password@localhost:5432/foodflow"
      }
    }
  }
}
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

## Security Notes

- MCP server runs locally with database access
- API credentials managed through secure config system
- All operations logged in audit trail
- Environment variables for sensitive data

The MCP integration makes FoodFlow accessible to any generative AI system, enabling natural language restaurant management and platform synchronization.