#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to Google Cloud SQL MySQL
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import pymysql
from datetime import datetime
import time

def load_cloud_config():
    """Load cloud configuration"""
    try:
        with open('cloud_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ cloud_config.json not found!")
        print("💡 Run 'python cloud_migration_setup.py --setup' first")
        return None

def get_sqlite_connection():
    """Get SQLite connection"""
    db_path = 'pathways_database.db'
    if not os.path.exists(db_path):
        print(f"❌ SQLite database not found: {db_path}")
        return None
    return sqlite3.connect(db_path)

def get_mysql_connection(config):
    """Get MySQL connection"""
    try:
        cloud_config = config['cloud_sql']
        
        # SSL configuration (optional)
        ssl_config = {}
        if os.path.exists(cloud_config.get('ssl_ca', '')):
            ssl_config = {
                'ssl': {
                    'ca': cloud_config['ssl_ca'],
                    'cert': cloud_config['ssl_cert'],
                    'key': cloud_config['ssl_key']
                }
            }
        
        connection = pymysql.connect(
            host=cloud_config['host'],
            port=cloud_config['port'],
            user=cloud_config['user'],
            password=cloud_config['password'],
            database=cloud_config['database_name'],
            charset='utf8mb4',
            **ssl_config
        )
        
        print("✅ Connected to Google Cloud SQL")
        return connection
        
    except Exception as e:
        print(f"❌ Failed to connect to MySQL: {e}")
        return None

def create_mysql_tables(mysql_conn):
    """Create MySQL tables"""
    try:
        with mysql_conn.cursor() as cursor:
            # Read and execute schema
            with open('mysql_schema.sql', 'r') as f:
                schema = f.read()
            
            # Split by semicolon and execute each statement
            statements = schema.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
            
            mysql_conn.commit()
            print("✅ MySQL tables created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Failed to create MySQL tables: {e}")
        return False

def migrate_data(sqlite_conn, mysql_conn):
    """Migrate data from SQLite to MySQL"""
    try:
        print("🔄 Starting data migration...")
        
        # Get all tables from SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
        
        for table in tables:
            print(f"\n🔄 Migrating table: {table}")
            
            # Read data from SQLite
            df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
            print(f"   📊 Found {len(df)} records")
            
            if len(df) == 0:
                print(f"   ⚠️  No data in {table}, skipping...")
                continue
            
            # Clean column names (remove spaces and special characters)
            df.columns = [col.replace(' ', '_').replace('(', '').replace(')', '') for col in df.columns]
            
            # Handle date columns
            date_columns = ['Intake_Date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Insert data into MySQL
            with mysql_conn.cursor() as cursor:
                # Create placeholders for INSERT
                columns = ', '.join([f'`{col}`' for col in df.columns])
                placeholders = ', '.join(['%s'] * len(df.columns))
                
                # Prepare INSERT statement
                insert_sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                
                # Convert DataFrame to list of tuples
                data = [tuple(row) for row in df.values]
                
                # Execute batch insert
                cursor.executemany(insert_sql, data)
                
                mysql_conn.commit()
                print(f"   ✅ Migrated {len(df)} records to {table}")
        
        print("\n🎉 Data migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def validate_migration(sqlite_conn, mysql_conn):
    """Validate that migration was successful"""
    print("\n🧪 Validating migration...")
    
    try:
        # Compare record counts
        tables = ['pathways_data', 'animal_inventory', 'metadata']
        
        for table in tables:
            # SQLite count
            sqlite_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", sqlite_conn).iloc[0]['count']
            
            # MySQL count
            mysql_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", mysql_conn).iloc[0]['count']
            
            print(f"   📊 {table}: SQLite={sqlite_count}, MySQL={mysql_count}")
            
            if sqlite_count != mysql_count:
                print(f"   ⚠️  Count mismatch in {table}!")
                return False
        
        print("✅ Migration validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def backup_sqlite():
    """Create backup of SQLite database"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'backups/pathways_database_backup_{timestamp}.db'
        
        # Create backups directory if it doesn't exist
        os.makedirs('backups', exist_ok=True)
        
        # Copy SQLite database
        import shutil
        shutil.copy2('pathways_database.db', backup_path)
        
        print(f"💾 Created backup: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
        return None

def main():
    """Main migration function"""
    print("=" * 60)
    print("SQLite to Google Cloud SQL Migration")
    print("=" * 60)
    
    # Load configuration
    config = load_cloud_config()
    if not config:
        return
    
    # Create backup
    print("💾 Creating backup...")
    backup_path = backup_sqlite()
    
    # Connect to databases
    print("🔌 Connecting to databases...")
    sqlite_conn = get_sqlite_connection()
    if not sqlite_conn:
        return
    
    mysql_conn = get_mysql_connection(config)
    if not mysql_conn:
        sqlite_conn.close()
        return
    
    try:
        # Create MySQL tables
        print("🗄️ Setting up MySQL tables...")
        if not create_mysql_tables(mysql_conn):
            return
        
        # Migrate data
        if not migrate_data(sqlite_conn, mysql_conn):
            return
        
        # Validate migration
        if not validate_migration(sqlite_conn, mysql_conn):
            return
        
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("📝 Next steps:")
        print("   1. Update your application to use MySQL")
        print("   2. Test the new cloud database")
        print("   3. Update cloud_config.json with production settings")
        print("   4. Deploy your application to use the cloud database")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
    finally:
        # Close connections
        sqlite_conn.close()
        mysql_conn.close()
        print("\n🔌 Database connections closed")

if __name__ == "__main__":
    main() 