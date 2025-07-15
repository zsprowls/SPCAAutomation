#!/usr/bin/env python3
"""
Google Cloud SQL Migration Setup for Pathways for Care Viewer
This script helps migrate from SQLite to Google Cloud SQL (MySQL)
"""

import os
import sys
import json
import subprocess
import pandas as pd
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'pymysql',
        'cryptography'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def create_cloud_config():
    """Create cloud configuration file"""
    config = {
        'cloud_sql': {
            'instance_name': 'your-project:your-region:your-instance',
            'database_name': 'pathways_care',
            'user': 'pathways_user',
            'password': 'your-secure-password',
            'host': 'your-instance-ip',
            'port': 3306,
            'ssl_ca': 'server-ca.pem',  # Download from Google Cloud Console
            'ssl_cert': 'client-cert.pem',  # Download from Google Cloud Console
            'ssl_key': 'client-key.pem'  # Download from Google Cloud Console
        },
        'local_backup': {
            'enabled': True,
            'backup_path': './backups/'
        }
    }
    
    with open('cloud_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("📝 Created cloud_config.json template")
    print("⚠️  Please update the configuration with your actual Google Cloud SQL details")

def generate_setup_instructions():
    """Generate setup instructions"""
    instructions = """
# Google Cloud SQL Setup Instructions

## 1. Create Google Cloud SQL Instance

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Navigate to SQL > Instances
3. Click "Create Instance"
4. Choose MySQL 8.0
5. Configure:
   - Instance ID: pathways-care-db
   - Password: (create a strong password)
   - Region: Choose closest to you
   - Machine type: db-f1-micro (free tier) or db-n1-standard-1
   - Storage: 10GB minimum

## 2. Create Database and User

1. Go to your SQL instance
2. Click "Databases" tab
3. Create database: `pathways_care`
4. Click "Users" tab
5. Create user: `pathways_user` with password
6. Grant privileges: SELECT, INSERT, UPDATE, DELETE, CREATE, DROP

## 3. Configure Network Access

1. Go to "Connections" tab
2. Add your IP address to "Authorized networks"
3. Or use "Public IP" for development (not recommended for production)

## 4. Download SSL Certificates (Optional but Recommended)

1. Go to "Connections" tab
2. Download SSL certificates:
   - Server CA certificate
   - Client certificate
   - Client private key

## 5. Update Configuration

1. Edit `cloud_config.json`
2. Update with your actual instance details
3. Set secure passwords

## 6. Run Migration

```bash
python cloud_migration_setup.py --migrate
```

## 7. Test Connection

```bash
python cloud_migration_setup.py --test
```
"""
    
    with open('CLOUD_SETUP_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print("📖 Created CLOUD_SETUP_INSTRUCTIONS.md with detailed setup steps")

def create_mysql_schema():
    """Create MySQL schema equivalent to SQLite"""
    schema = """
-- MySQL Schema for Pathways for Care Database

CREATE DATABASE IF NOT EXISTS pathways_care;
USE pathways_care;

-- Main pathways data table
CREATE TABLE IF NOT EXISTS pathways_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    AID VARCHAR(50) NOT NULL,
    Name VARCHAR(255),
    Species VARCHAR(100),
    Breed VARCHAR(255),
    Color VARCHAR(255),
    Sex VARCHAR(50),
    Age VARCHAR(100),
    Weight VARCHAR(100),
    `Intake Date` DATE,
    `Days in System` INT,
    `Location ` VARCHAR(255),
    `Foster Attempted` VARCHAR(10),
    `Transfer Attempted` VARCHAR(10),
    `Communications Team Attempted` VARCHAR(10),
    `Welfare Notes` TEXT,
    `Medical Notes` TEXT,
    `Behavior Notes` TEXT,
    `Adoption Notes` TEXT,
    `Transfer Notes` TEXT,
    `Foster Notes` TEXT,
    `Return Notes` TEXT,
    `Euthanasia Notes` TEXT,
    `Other Notes` TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_aid (AID),
    INDEX idx_name (Name),
    INDEX idx_species (Species),
    INDEX idx_intake_date (`Intake Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Animal inventory table
CREATE TABLE IF NOT EXISTS animal_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    AnimalNumber VARCHAR(50),
    Location VARCHAR(255),
    SubLocation VARCHAR(255),
    Status VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_animal_number (AnimalNumber),
    INDEX idx_location (Location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Metadata table
CREATE TABLE IF NOT EXISTS metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Image cache table
CREATE TABLE IF NOT EXISTS image_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id VARCHAR(50) NOT NULL,
    image_urls JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_animal_id (animal_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert initial metadata
INSERT IGNORE INTO metadata (`key`, value) VALUES 
('last_updated', NOW()),
('database_version', '2.0'),
('migration_date', NOW());
"""
    
    with open('mysql_schema.sql', 'w') as f:
        f.write(schema)
    
    print("🗄️ Created mysql_schema.sql with MySQL table definitions")

def main():
    """Main function"""
    print("=" * 60)
    print("Google Cloud SQL Migration Setup")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--check':
            check_dependencies()
        elif command == '--setup':
            create_cloud_config()
            generate_setup_instructions()
            create_mysql_schema()
        elif command == '--migrate':
            print("🚀 Starting migration...")
            # This will be implemented in a separate migration script
            print("📝 Run 'python migrate_to_cloud.py' to perform the actual migration")
        elif command == '--test':
            print("🧪 Testing connection...")
            # This will be implemented in a separate test script
            print("📝 Run 'python test_cloud_connection.py' to test the connection")
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: --check, --setup, --migrate, --test")
    else:
        print("📋 Available commands:")
        print("  --check   : Check if required packages are installed")
        print("  --setup   : Create configuration files and setup instructions")
        print("  --migrate : Start migration process")
        print("  --test    : Test cloud connection")
        print("\n💡 Start with: python cloud_migration_setup.py --setup")

if __name__ == "__main__":
    main() 