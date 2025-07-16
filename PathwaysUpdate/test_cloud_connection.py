#!/usr/bin/env python3
"""
Test script to verify Google Cloud SQL connection
"""

import os
import json
import pymysql
from datetime import datetime

def load_cloud_config():
    """Load cloud configuration"""
    try:
        with open('cloud_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ cloud_config.json not found!")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in cloud_config.json!")
        return None

def test_connection():
    """Test the cloud database connection"""
    print("=" * 60)
    print("Testing Google Cloud SQL Connection")
    print("=" * 60)
    
    # Load configuration
    config = load_cloud_config()
    if not config:
        return False
    
    try:
        cloud_config = config['cloud_sql']
        
        print(f"🔌 Connecting to: {cloud_config['host']}:{cloud_config['port']}")
        print(f"📊 Database: {cloud_config['database_name']}")
        print(f"👤 User: {cloud_config['user']}")
        
        # SSL configuration (optional)
        ssl_config = {}
        if cloud_config.get('ssl_ca') and os.path.exists(cloud_config['ssl_ca']):
            ssl_config = {
                'ssl': {
                    'ca': cloud_config['ssl_ca'],
                    'cert': cloud_config['ssl_cert'],
                    'key': cloud_config['ssl_key']
                }
            }
            print("🔒 Using SSL connection")
        else:
            print("⚠️  No SSL certificates found, using unencrypted connection")
        
        # Attempt connection
        connection = pymysql.connect(
            host=cloud_config['host'],
            port=cloud_config['port'],
            user=cloud_config['user'],
            password=cloud_config['password'],
            database=cloud_config['database_name'],
            charset='utf8mb4',
            **ssl_config
        )
        
        print("✅ Successfully connected to Google Cloud SQL!")
        
        # Test a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📋 MySQL Version: {version[0]}")
            
            # Check if tables exist
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
            
            # Check record counts
            if tables:
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()
                    print(f"   📈 {table_name}: {count[0]} records")
        
        connection.close()
        print("\n🎉 Connection test successful!")
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 