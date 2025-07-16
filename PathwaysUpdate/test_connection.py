#!/usr/bin/env python3
"""
Test database connection using the same logic as the working app
"""

import os
import pymysql
from cloud_database_manager import get_database_manager, connect_to_database

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    print()
    
    # Try to connect using the same logic as the app
    try:
        manager = get_database_manager()
        print(f"✅ Got database manager: {manager}")
        
        # Try to connect to cloud database
        success = connect_to_database(use_cloud=True)
        
        if success:
            print("✅ Successfully connected to cloud database!")
            print(f"📋 Database type: {manager.db_type}")
            print(f"📋 Connection status: {manager.connection is not None}")
            
            # Test a simple query
            if manager.connection:
                with manager.connection.cursor() as cursor:
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchone()
                    print(f"✅ Test query successful: {result}")
            
            return True
        else:
            print("❌ Failed to connect to cloud database")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection() 