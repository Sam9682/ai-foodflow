import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

def create_database_if_not_exists():
    """Create PostgreSQL database if it doesn't exist"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Parse database URL
    parsed = urlparse(database_url)
    db_name = parsed.path[1:]  # Remove leading slash
    
    # Connection without database name
    admin_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(admin_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"✅ Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False