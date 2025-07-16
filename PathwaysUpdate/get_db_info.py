#!/usr/bin/env python3
"""
Get database connection information from environment variables
"""

import os

def get_db_info():
    """Get database connection info from environment variables"""
    
    print("🔍 Checking for database environment variables...")
    print()
    
    # Check for environment variables
    env_vars = {
        'CLOUD_SQL_INSTANCE_NAME': os.getenv('CLOUD_SQL_INSTANCE_NAME'),
        'CLOUD_SQL_DATABASE_NAME': os.getenv('CLOUD_SQL_DATABASE_NAME'),
        'CLOUD_SQL_USER': os.getenv('CLOUD_SQL_USER'),
        'CLOUD_SQL_PASSWORD': os.getenv('CLOUD_SQL_PASSWORD'),
        'CLOUD_SQL_HOST': os.getenv('CLOUD_SQL_HOST'),
        'CLOUD_SQL_PORT': os.getenv('CLOUD_SQL_PORT'),
    }
    
    found_vars = []
    missing_vars = []
    
    for var, value in env_vars.items():
        if value:
            found_vars.append((var, value))
            if var == 'CLOUD_SQL_PASSWORD':
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
    
    print()
    
    if found_vars:
        print("📋 To update your cloud_config.json, use these values:")
        print()
        print("Host:", env_vars.get('CLOUD_SQL_HOST', 'NOT_FOUND'))
        print("Database:", env_vars.get('CLOUD_SQL_DATABASE_NAME', 'NOT_FOUND'))
        print("User:", env_vars.get('CLOUD_SQL_USER', 'NOT_FOUND'))
        print("Password:", env_vars.get('CLOUD_SQL_PASSWORD', 'NOT_FOUND'))
        print("Port:", env_vars.get('CLOUD_SQL_PORT', '3306'))
        
        print()
        print("💡 Update your cloud_config.json with these values!")
    else:
        print("❌ No database environment variables found!")
        print("💡 Make sure you're running this in the same environment as your Streamlit app")

if __name__ == "__main__":
    get_db_info() 