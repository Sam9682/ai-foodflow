#!/usr/bin/env python3
"""Start FoodFlow MCP Server"""

import subprocess
import sys
import os
from dotenv import load_dotenv

def main():
    """Start MCP server with environment"""
    load_dotenv()
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://foodflow:password@localhost:5432/foodflow"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "UBER_EATS_CLIENT_ID": os.getenv("UBER_EATS_CLIENT_ID", ""),
        "UBER_EATS_CLIENT_SECRET": os.getenv("UBER_EATS_CLIENT_SECRET", ""),
        "UBER_EATS_STORE_ID": os.getenv("UBER_EATS_STORE_ID", ""),
        "DELIVEROO_API_KEY": os.getenv("DELIVEROO_API_KEY", ""),
        "DELIVEROO_RESTAURANT_ID": os.getenv("DELIVEROO_RESTAURANT_ID", ""),
        "JUST_EAT_API_KEY": os.getenv("JUST_EAT_API_KEY", ""),
        "JUST_EAT_TENANT_ID": os.getenv("JUST_EAT_TENANT_ID", "")
    })
    
    # Start MCP server
    try:
        subprocess.run([sys.executable, "mcp_server.py"], env=env, check=True)
    except KeyboardInterrupt:
        print("\nMCP server stopped")
    except Exception as e:
        print(f"Error starting MCP server: {e}")

if __name__ == "__main__":
    main()