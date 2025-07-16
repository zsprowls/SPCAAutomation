#!/usr/bin/env python3
"""
Simple Migration script to transfer data from SQLite to Google Cloud SQL MySQL
"""

import os
import sys
import json
import sqlite3
import pandas as pd
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
        
        connection = pymysql.connect(
            host=cloud_config['host'],
            port=cloud_config['port'],
            user=cloud_config['user'],
            password=cloud_config['password'],
            database=cloud_config['database_name'],
            charset='utf8mb4'
        )
        
        print("✅ Connected to Google Cloud SQL")
        return connection
        
    except Exception as e:
        print(f"❌ Failed to connect to MySQL: {e}")
        return None

def create_table_from_dataframe(mysql_conn, table_name, df):
    """Create MySQL table based on DataFrame structure"""
    try:
        with mysql_conn.cursor() as cursor:
            # Drop table if exists
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # Create table with proper column types
            columns = []
            for col in df.columns:
                col_clean = col.replace(' ', '_').replace('(', '').replace(')', '')
                if df[col].dtype == 'object':
                    # Check if it's a date column
                    if 'date' in col.lower() or 'Date' in col:
                        columns.append(f"`{col}` DATE")
                    else:
                        # Use TEXT for long strings, VARCHAR for shorter ones
                        max_length = df[col].astype(str).str.len().max()
                        if max_length > 255 or pd.isna(max_length):
                            columns.append(f"`{col}` TEXT")
                        else:
                            columns.append(f"`{col}` VARCHAR({max_length + 50})")
                elif df[col].dtype == 'int64':
                    columns.append(f"`{col}` INT")
                elif df[col].dtype == 'float64':
                    columns.append(f"`{col}` FLOAT")
                else:
                    columns.append(f"`{col}` TEXT")
            
            # Add id column
            columns.insert(0, "id INT AUTO_INCREMENT PRIMARY KEY")
            
            # Create table
            create_sql = f"""
                CREATE TABLE {table_name} (
                    {', '.join(columns)},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_sql)
            mysql_conn.commit()
            print(f"   ✅ Created table {table_name}")
            return True
            
    except Exception as e:
        print(f"   ❌ Failed to create table {table_name}: {e}")
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
            
            # Create table structure
            if not create_table_from_dataframe(mysql_conn, table, df):
                continue
            
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
        # Get tables from both databases
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SHOW TABLES")
        mysql_tables = [row[0] for row in mysql_cursor.fetchall()]
        
        print(f"📊 SQLite tables: {', '.join(sqlite_tables)}")
        print(f"📊 MySQL tables: {', '.join(mysql_tables)}")
        
        # Compare record counts for each table
        for table in sqlite_tables:
            if table in mysql_tables:
                # SQLite count
                sqlite_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", sqlite_conn).iloc[0]['count']
                
                # MySQL count
                mysql_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", mysql_conn).iloc[0]['count']
                
                print(f"   📈 {table}: SQLite={sqlite_count}, MySQL={mysql_count}")
                
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
    print("SQLite to Google Cloud SQL Migration (Simple)")
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
        print("   1. Your data is now in Google Cloud SQL!")
        print("   2. You can update your app to use the cloud database")
        print("   3. Test the cloud database with your application")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
    finally:
        # Close connections
        sqlite_conn.close()
        mysql_conn.close()
        print("\n🔌 Database connections closed")

if __name__ == "__main__":
    main() 