# FoodFlow Quick Reference

## 🚀 Quick Start Commands

```bash
# Deploy with Docker (recommended)
./deploy.sh docker

# Deploy manually
./deploy.sh

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Stop services
./deploy.sh stop

# Get help
./deploy.sh help
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Health Check | http://localhost:8000/health | Service health status |
| Chat Interface | `chat_demo.html` | AI chat interface (open in browser) |
| Prometheus | http://localhost:9090 | Metrics and monitoring |
| Grafana | http://localhost:3000 | Dashboard (admin/admin) |

## 💬 Chat Commands

| Command | Example | Description |
|---------|---------|-------------|
| Show menu | "Show me the current menu" | Display all menu items |
| Add item | "Add a new pizza for €12.50" | Add menu item with price |
| Update price | "Update item 5's price to €15.00" | Change item price |
| Sync platforms | "Sync to Uber Eats and Deliveroo" | Sync to delivery platforms |
| Check status | "Check sync status" | View sync status |
| Upload image | Attach image + "Analyze this menu" | Extract items from menu image |

## 🔧 API Endpoints

### Menu Management
```bash
# Get menu
curl http://localhost:8000/menu-items/1

# Add item
curl -X POST http://localhost:8000/menu-items/ \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id":1,"name":"Pizza","price":12.50,"category":"Pizzas"}'

# Update item
curl -X PUT http://localhost:8000/menu-items/5 \
  -H "Content-Type: application/json" \
  -d '{"price":15.00}'
```

### Platform Sync
```bash
# Manual sync
curl -X POST http://localhost:8000/sync/manual \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id":1,"platforms":["uber_eats"]}'

# Check sync status
curl http://localhost:8000/sync/status/1
```

### Image Analysis
```bash
# Upload menu image
curl -X POST http://localhost:8000/chat/message-with-image \
  -F "file=@menu.jpg" \
  -F "message=Analyze this menu" \
  -F "restaurant_id=1"
```

## 🤖 MCP Commands (AI Clients)

| Natural Language | MCP Tool | Parameters |
|------------------|----------|------------|
| "Add pizza for €12.50" | add_menu_item | restaurant_id, name, price, category |
| "Show current menu" | get_menu | restaurant_id |
| "Update item 5 price to €15" | update_menu_item | item_id, price |
| "Sync to Uber Eats" | sync_to_platforms | restaurant_id, platforms |
| "Check sync status" | get_sync_status | restaurant_id |
| "Analyze menu image" | analyze_menu_image | restaurant_id, image_data |

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Initialize database
docker-compose exec app python scripts/init_data.py
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Database connection failed | Check PostgreSQL: `docker-compose logs db` |
| Chat not responding | Check WebSocket in browser console |
| Image upload failed | Verify OpenAI API key in .env |
| Sync failed | Check platform credentials: `curl localhost:8000/config/status` |
| MCP not working | Restart MCP server: `python start_mcp.py` |

## 📁 File Structure

```
ai-foodflow/
├── deploy.sh              # Deployment script
├── docker-compose.yml     # Docker services
├── chat_demo.html         # Web chat interface
├── .env.example          # Environment template
├── README.md             # Main documentation
├── USER_GUIDE.md         # Usage guide
├── DEPLOYMENT_GUIDE.md   # Deployment details
├── README_MCP.md         # AI integration
└── QUICK_REFERENCE.md    # This file
```

## 🔑 Environment Variables

### Required
```bash
DATABASE_URL=postgresql://user:pass@host:5432/foodflow
OPENAI_API_KEY=your_openai_key
```

### Platform APIs
```bash
UBER_EATS_CLIENT_ID=your_client_id
UBER_EATS_CLIENT_SECRET=your_secret
DELIVEROO_API_KEY=your_api_key
JUST_EAT_API_KEY=your_api_key
```

### Optional
```bash
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key
DEBUG=False
LOG_LEVEL=INFO
```

## 📊 Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database status
curl http://localhost:8000/config/status

# Service status
./deploy.sh status

# View metrics
curl http://localhost:8000/audit/stats
```

## 🔄 Common Workflows

### 1. Add New Menu Items
1. Open `chat_demo.html`
2. Upload menu image or type: "Add new pizza for €12.50"
3. Confirm items
4. Sync: "Sync to all platforms"

### 2. Update Prices
1. Chat: "Update item 5's price to €15.00"
2. Or API: `curl -X PUT localhost:8000/menu-items/5 -d '{"price":15.00}'`
3. Sync: "Sync to platforms"

### 3. Bulk Menu Upload
1. Upload high-quality menu image
2. Chat: "Analyze this menu and add all items"
3. Review extracted items
4. Click "Add All Items"
5. Sync to platforms

### 4. Monitor Sync Status
1. Chat: "Check sync status"
2. Or API: `curl localhost:8000/sync/status/1`
3. View Grafana dashboard: http://localhost:3000

## 📞 Support

- **Documentation**: README.md, USER_GUIDE.md, DEPLOYMENT_GUIDE.md
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Contact**: lepetre@yahoo.fr
- **Help**: `./deploy.sh help`

## 🎯 Pro Tips

1. **Use Docker**: Recommended for production deployment
2. **High-Quality Images**: Better OCR results with clear menu photos
3. **Regular Sync**: Keep platforms updated with scheduled sync
4. **Monitor Health**: Check health endpoint regularly
5. **Backup Database**: Regular PostgreSQL backups
6. **Update Credentials**: Rotate API keys periodically
7. **Use MCP**: Natural language commands via Claude/ChatGPT
8. **Check Logs**: Use `./deploy.sh logs` for debugging