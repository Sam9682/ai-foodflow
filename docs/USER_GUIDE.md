# FoodFlow User Guide

Complete guide for using FoodFlow's AI-powered restaurant management system.

## 🎯 Overview

FoodFlow provides multiple interfaces for managing your restaurant menu and syncing with delivery platforms:
- **Main Dashboard**: Central hub for all platform functions
- **Web Chat Interface**: Interactive AI assistant with image upload
- **Menu Management**: Visual interface for CRUD operations on menu items
- **Audit Records**: Complete audit trail with filtering and export
- **REST API**: Programmatic access to all features
- **MCP Integration**: Natural language commands via AI clients (Claude, ChatGPT)
- **WebSocket**: Real-time communication

## 🏠 Main Dashboard

### Accessing the Dashboard
1. Ensure FoodFlow is running (`./deploy.sh` or `./deploy.sh docker`)
2. Navigate to http://localhost:8000/main
3. Access all platform features from the central hub

### Dashboard Features
- **System Status**: Real-time API, database, and sync status
- **Quick Actions**: One-click sync, status checks, menu view
- **Feature Cards**: Direct access to all interfaces
- **Navigation**: Links to chat, menu management, audit, and more

## 💬 Web Chat Interface

### Accessing the Chat Interface
1. From main dashboard or direct URL: http://localhost:8000/static/chat_discussion.html
2. Start chatting with the AI assistant

### Chat Features

**Text Commands:**
- "Show me the current menu"
- "Add a new pizza for €12.50"
- "Update item 5's price to €15.00"
- "Sync to Uber Eats and Deliveroo"
- "Check sync status"
- "What's the most expensive item?"

**Image Upload:**
1. Click "📎 Attach Image" button
2. Select menu image from your device
3. Type a message like "Analyze this menu"
4. AI will extract menu items automatically

**Interactive Elements:**
- **Suggestions**: Click suggested commands for quick actions
- **Action Buttons**: Use buttons for common operations
- **Menu Visualization**: View extracted items in formatted cards
- **Sync Results**: See real-time sync status updates

### Example Chat Session
```
You: Show me the current menu

🤖 Assistant: Here's Le Bouzou's current menu:

**Pizzas**
• Pizza Margherita - €12.50
• Pizza Pepperoni - €14.00

**Salads**
• Caesar Salad - €8.50
• Greek Salad - €9.00

Total: 4 items

You: Add a new pasta dish for €11.00

🤖 Assistant: I've added a new pasta dish to your menu:
• Pasta Carbonara - €11.00 (Category: Pasta)

Would you like me to sync this to your delivery platforms?

You: Yes, sync to Uber Eats

🤖 Assistant: Syncing to Uber Eats...

Sync Results:
✅ uber_eats: Success - Menu updated successfully
```

## 🔧 REST API Usage

### Authentication
Most endpoints require restaurant context. Use restaurant ID in URLs.

### Core Endpoints

**Get Menu:**
```bash
curl http://localhost:8000/menu-items/1
```

**Add Menu Item:**
```bash
curl -X POST http://localhost:8000/menu-items/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "name": "Pizza Margherita",
    "description": "Classic tomato and mozzarella",
    "price": 12.50,
    "category": "Pizzas",
    "is_available": true
  }'
```

**Update Menu Item:**
```bash
curl -X PUT http://localhost:8000/menu-items/5 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 15.00,
    "is_available": true
  }'
```

**Sync to Platforms:**
```bash
curl -X POST http://localhost:8000/sync/manual \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "platforms": ["uber_eats", "deliveroo"]
  }'
```

**Delete Menu Item:**
```bash
curl -X DELETE http://localhost:8000/menu-items/5
```

**Upload Menu Image:**
```bash
curl -X POST http://localhost:8000/chat/message-with-image \
  -F "file=@menu.jpg" \
  -F "message=Analyze this menu" \
  -F "restaurant_id=1"
```

## 🍽️ Menu Management Interface

### Accessing Menu Management
- **URL**: http://localhost:8000/menu-management
- **From Dashboard**: Click "Menu Management" card

### Features
- **Visual Grid**: All menu items displayed in organized cards
- **Add Items**: Modal form with validation
- **Edit Items**: Click edit to modify existing items
- **Delete Items**: Remove items with confirmation
- **Categories**: Predefined categories (Pizzas, Salads, etc.)
- **Availability**: Toggle item availability
- **Real-time Updates**: Immediate UI updates

### Usage
1. **Add New Item**: Click "+ Add New Item" button
2. **Fill Form**: Name, price, category, description, availability
3. **Save**: Item appears immediately in grid
4. **Edit**: Click "Edit" on any item card
5. **Delete**: Click "Delete" with confirmation dialog

## 📈 Audit Records Interface

### Accessing Audit Records
- **URL**: http://localhost:8000/audit-page
- **From Dashboard**: Click "Analytics & Audit" card

### Features
- **Complete Audit Trail**: All system operations logged
- **Filtering**: By action type, status, date range
- **Statistics**: Success rates, error counts, daily activity
- **Export**: Download filtered records as CSV
- **Pagination**: Handle large datasets efficiently

### Usage
1. **View Records**: Automatic loading on page access
2. **Filter Data**: Use dropdown filters and apply
3. **Export Data**: Click "Export CSV" for reports
4. **Navigate**: Use pagination for large datasets

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

## 🤖 MCP Integration (AI Clients)

### Setup with Claude Desktop
1. Add FoodFlow to your MCP configuration:
```json
{
  "mcpServers": {
    "foodflow": {
      "command": "python",
      "args": ["start_mcp.py"],
      "cwd": "/path/to/ai-foodflow"
    }
  }
}
```

2. Restart Claude Desktop
3. Use natural language commands

### Natural Language Commands

**Menu Management:**
- "Add a new burger to Le Bouzou's menu for €13.50"
- "Show me all pizzas on the menu"
- "Update the Caesar salad price to €9.50"
- "Remove item 7 from the menu"
- "What's the average price of main courses?"

**Platform Sync:**
- "Sync Le Bouzou's menu to all platforms"
- "Update Uber Eats with the latest menu"
- "Check sync status for restaurant 1"
- "Sync only to Deliveroo and Just Eat"

**Image Analysis:**
- "Analyze this menu image" (with image attachment)
- "Extract items from this restaurant menu"
- "What items can you see in this menu photo?"

**Status & Reporting:**
- "Show me sync history for the last week"
- "What's the current menu status?"
- "Generate a menu report"
- "Check platform connection status"

## 📱 WebSocket Integration

### Connecting to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/chat/ws/1');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.send(JSON.stringify({
    message: "Show me the current menu"
}));
```

### Message Format
```javascript
// Outgoing message
{
    "message": "Add a new pizza for €12.50"
}

// Incoming response
{
    "type": "menu_updated",
    "response": "Added Pizza Margherita to your menu",
    "user_message": "Add a new pizza for €12.50",
    "suggestions": ["Sync to platforms", "Add another item"]
}
```

## 🖼️ Image Analysis Features

### Supported Image Formats
- JPEG, PNG, WebP
- Maximum size: 10MB
- Minimum resolution: 300x300px
- Optimal: High contrast, clear text

### Image Upload Methods

**Web Chat:**
1. Click "📎 Attach Image"
2. Select image file
3. Add description message
4. Send to AI

**API Upload:**
```bash
curl -X POST http://localhost:8000/chat/message-with-image \
  -F "file=@menu.jpg" \
  -F "message=Extract all items with prices" \
  -F "restaurant_id=1"
```

**MCP Integration:**
```
"Analyze this menu image and add all items to Le Bouzou"
```

### AI Analysis Capabilities
- **Item Extraction**: Names, prices, descriptions
- **Category Detection**: Automatic categorization
- **Price Recognition**: Multiple currency formats
- **Language Support**: Multiple languages
- **Layout Understanding**: Columns, sections, headers

### Example Analysis Result
```json
{
  "type": "menu_analyzed",
  "response": "I found 8 menu items in your image",
  "menu_items": [
    {
      "name": "Pizza Margherita",
      "price": 12.50,
      "description": "Tomato, mozzarella, basil",
      "category": "Pizzas"
    },
    {
      "name": "Caesar Salad",
      "price": 8.50,
      "description": "Romaine, parmesan, croutons",
      "category": "Salads"
    }
  ],
  "actions": [
    {"action": "add_items", "text": "Add All Items"},
    {"action": "sync_platforms", "text": "Sync to Platforms"}
  ]
}
```

## 🔄 Platform Synchronization

### Supported Platforms
- **Uber Eats**: Full menu sync, real-time updates
- **Deliveroo**: Menu items, pricing, availability
- **Just Eat**: Product catalog, restaurant info

### Sync Types

**Manual Sync:**
- Triggered via chat, API, or MCP
- Immediate execution
- Full error reporting

**Scheduled Sync:**
- Daily: 2:00 AM (menu items, prices)
- Weekly: Sunday 1:00 AM (restaurant info)
- Hourly: Availability status

**Real-time Sync:**
- Triggered by menu changes
- Platform-specific formatting
- Automatic retry on failure

### Sync Commands

**Chat Interface:**
- "Sync to all platforms"
- "Update Uber Eats only"
- "Check last sync status"

**API:**
```bash
curl -X POST http://localhost:8000/sync/manual \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": 1, "platforms": ["uber_eats"]}'
```

**MCP:**
- "Sync Le Bouzou's menu to Deliveroo"
- "Update all platforms with latest menu"

## 📊 Monitoring & Analytics

### Health Monitoring
- **API Health**: http://localhost:8000/health
- **Database Status**: Connection and query performance
- **Platform Status**: API connectivity and sync success
- **Service Status**: All components running

### Performance Metrics
- **Sync Success Rate**: Platform-specific success rates
- **Response Times**: API and sync operation timing
- **Error Rates**: Failed operations and causes
- **Usage Statistics**: Most used features and commands

### Audit Trail
- **All Operations**: Complete history of actions
- **User Interactions**: Chat messages and API calls
- **Sync History**: Platform synchronization logs
- **Error Tracking**: Detailed error information

### Accessing Metrics
```bash
# API metrics
curl http://localhost:8000/audit/stats

# Sync history
curl http://localhost:8000/audit/history?action_type=platform_sync

# Health status
curl http://localhost:8000/health
```

## 🛠️ Configuration Management

### API Credentials
Update platform credentials via API or environment variables:

```bash
# View current credentials (masked)
curl http://localhost:8000/config/credentials

# Update credentials
curl -X POST http://localhost:8000/config/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "uber_eats_client_id": "new_client_id",
    "uber_eats_client_secret": "new_secret"
  }'
```

### Restaurant Settings
```bash
# Update restaurant info
curl -X PUT http://localhost:8000/restaurants/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Le Bouzou Updated",
    "location": "New Location"
  }'
```

## 🔍 Troubleshooting

### Common Issues

**Dashboard Not Loading:**
1. Check API server: `curl http://localhost:8000/health`
2. Verify main dashboard: `curl http://localhost:8000/main`
3. Restart services: `./deploy.sh stop && ./deploy.sh`

**Chat Not Responding:**
1. Check WebSocket connection in browser console
2. Verify API server is running: `curl http://localhost:8000/health`
3. Restart services: `./deploy.sh stop && ./deploy.sh`

**Menu Management Issues:**
1. Check API endpoints: `curl http://localhost:8000/menu-items/1`
2. Verify database connection
3. Check browser console for JavaScript errors

**Image Upload Failed:**
1. Check image size (max 10MB)
2. Verify supported format (JPEG, PNG, WebP)
3. Ensure OpenAI API key is configured

**Sync Failed:**
1. Check platform credentials: `curl http://localhost:8000/config/status`
2. Verify internet connection
3. Check sync history: `curl http://localhost:8000/audit/history`

**MCP Not Working:**
1. Verify MCP server is running: `python start_mcp.py`
2. Check database connection
3. Restart AI client (Claude Desktop)

### Debug Commands
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f app

# Test database connection
python -c "from app.core.database import engine; print('DB OK')"

# Test AI integration
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "restaurant_id": 1}'
```

## 📞 Support & Resources

### Getting Help
- **Main Dashboard**: http://localhost:8000/main
- **Documentation**: README.md, DEPLOYMENT_GUIDE.md
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Contact**: lepetre@yahoo.fr

### Best Practices
1. **Regular Backups**: Database and configuration
2. **Monitor Sync Status**: Check daily sync results
3. **Update Credentials**: Rotate API keys regularly
4. **Image Quality**: Use high-resolution menu images
5. **Test Changes**: Verify updates before syncing

### Advanced Usage
- **Custom Integrations**: Use REST API for custom apps
- **Bulk Operations**: Upload multiple images at once
- **Automated Workflows**: Combine with external systems
- **Multi-Restaurant**: Scale to multiple locations

## 🎉 Success Tips

1. **Start with Dashboard**: Use http://localhost:8000/main as your starting point
2. **Menu Management**: Use the visual interface for easy menu updates
3. **Use Images**: Upload clear, high-quality menu photos via chat
4. **Regular Sync**: Keep platforms updated daily via dashboard
5. **Monitor Results**: Check audit page for complete activity history
6. **Leverage AI**: Use natural language for complex operations
7. **Stay Updated**: Keep FoodFlow updated to latest version

FoodFlow makes restaurant management simple and efficient. Start with the chat interface, explore the API, and integrate with your favorite AI tools for the best experience!