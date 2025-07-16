#!/usr/bin/env python3
"""
Test script to verify database connection with fallback logic
"""

import sys
import os

def test_database_connection():
    """Test database connection with fallback logic"""
    print("Testing database connection with fallback...")
    print("=" * 50)
    
    try:
        # Import required modules
        from cloud_database_manager import connect_to_database, get_database_manager
        
        # Test cloud connection (should fail without credentials)
        print("Testing cloud database connection...")
        cloud_success = connect_to_database(use_cloud=True)
        
        if cloud_success:
            print("✅ Cloud database connection successful")
        else:
            print("⚠️ Cloud database connection failed (expected without credentials)")
            
            # Test local SQLite fallback
            print("Testing local SQLite fallback...")
            local_success = connect_to_database(use_cloud=False)
            
            if local_success:
                print("✅ Local SQLite database connection successful")
                
                # Test data loading
                print("Testing data loading...")
                manager = get_database_manager()
                df = manager.get_pathways_data()
                
                if df is not None and len(df) > 0:
                    print(f"✅ Data loaded successfully: {len(df)} records")
                    print(f"Columns: {list(df.columns)}")
                else:
                    print("❌ No data found in database")
                    return False
            else:
                print("❌ Local SQLite database connection failed")
                return False
        
        print("\n🎉 Database connection test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1) 