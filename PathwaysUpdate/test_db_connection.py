#!/usr/bin/env python3
"""
Test database connection from local machine
"""

import os
import pymysql
from dotenv import load_dotenv

def test_db_connection():
    """Test if we can connect to the database"""
    print("Testing database connection...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get database credentials
    host = os.getenv('CLOUD_SQL_HOST', '34.162.59.3')
    port = int(os.getenv('CLOUD_SQL_PORT', '3306'))
    user = os.getenv('CLOUD_SQL_USER', 'pathways_user')
    password = os.getenv('CLOUD_SQL_PASSWORD', 'Pathways01')
    database = os.getenv('CLOUD_SQL_DATABASE_NAME', 'pathways_care')
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {database}")
    
    try:
        # Try to connect
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ Database connection successful!")
        
        # Test a simple query
        with connection.cursor() as cursor:
            # Check what tables exist
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Tables in database: {[table[0] for table in tables]}")
            
            # Try to get record count from first table
            if tables:
                first_table = tables[0][0]
                cursor.execute(f"SELECT COUNT(*) FROM {first_table}")
                result = cursor.fetchone()
                print(f"✅ Query successful! Found {result[0]} records in {first_table} table")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_db_connection() 