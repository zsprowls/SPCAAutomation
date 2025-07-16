#!/usr/bin/env python3
"""
Update cloud_config.json with environment variables
"""

import os
import json

def update_cloud_config():
    """Update cloud_config.json with environment variables"""
    
    # Load existing config
    try:
        with open('cloud_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ cloud_config.json not found!")
        return False
    
    # Get environment variables
    cloud_config = {
        'instance_name': os.getenv('CLOUD_SQL_INSTANCE_NAME', 'your-project:your-region:your-instance'),
        'database_name': os.getenv('CLOUD_SQL_DATABASE_NAME', 'pathways_care'),
        'user': os.getenv('CLOUD_SQL_USER', 'pathways_user'),
        'password': os.getenv('CLOUD_SQL_PASSWORD', 'your-secure-password'),
        'host': os.getenv('CLOUD_SQL_HOST', 'your-instance-ip'),
        'port': int(os.getenv('CLOUD_SQL_PORT', '3306')),
        'ssl_ca': os.getenv('CLOUD_SQL_SSL_CA', 'server-ca.pem'),
        'ssl_cert': os.getenv('CLOUD_SQL_SSL_CERT', 'client-cert.pem'),
        'ssl_key': os.getenv('CLOUD_SQL_SSL_KEY', 'client-key.pem')
    }
    
    # Update config
    config['cloud_sql'] = cloud_config
    
    # Save updated config
    with open('cloud_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Updated cloud_config.json with environment variables")
    print("📋 Configuration:")
    for key, value in cloud_config.items():
        if key == 'password':
            print(f"   {key}: {'*' * len(str(value))}")
        else:
            print(f"   {key}: {value}")
    
    return True

if __name__ == "__main__":
    update_cloud_config() 