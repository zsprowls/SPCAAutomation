#!/usr/bin/env python3
"""
Cloud Database Manager for Pathways for Care Viewer
Supports both SQLite (local) and MySQL (cloud) databases
"""

import os
import json
import sqlite3
import pandas as pd
import pymysql
from datetime import datetime
from typing import Optional, Dict, Any, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system environment variables

# Import SQLAlchemy for better pandas compatibility
try:
    from sqlalchemy import create_engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

class DatabaseManager:
    def __init__(self, config_path: str = 'cloud_config.json'):
        """
        Initialize database manager
        
        Args:
            config_path: Path to configuration file (for non-sensitive config only)
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.connection = None
        self.engine = None
        self.db_type = None
        
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from environment variables and file"""
        try:
            # Load sensitive data from environment variables
            cloud_config = {
                'instance_name': os.getenv('CLOUD_SQL_INSTANCE_NAME'),
                'database_name': os.getenv('CLOUD_SQL_DATABASE_NAME'),
                'user': os.getenv('CLOUD_SQL_USER'),
                'password': os.getenv('CLOUD_SQL_PASSWORD'),
                'host': os.getenv('CLOUD_SQL_HOST'),
                'port': int(os.getenv('CLOUD_SQL_PORT', '3306'))
            }
            
            # Check if all required environment variables are set
            missing_vars = [key for key, value in cloud_config.items() if not value]
            if missing_vars:
                print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
                print("Please set the following environment variables:")
                for var in missing_vars:
                    print(f"  - {var.upper()}")
                return None
            
            # Load non-sensitive config from file if it exists
            file_config = {}
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, 'r') as f:
                        file_config = json.load(f)
                except Exception as e:
                    print(f"⚠️  Error loading config file: {e}")
            
            # Merge configurations
            config = {
                'cloud_sql': cloud_config,
                'local_backup': file_config.get('local_backup', {
                    'enabled': True,
                    'backup_path': './backups/'
                })
            }
            
            return config
            
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return None
    
    def connect(self, use_cloud: bool = False) -> bool:
        """
        Connect to database
        
        Args:
            use_cloud: If True, connect to cloud MySQL, otherwise use local SQLite
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if use_cloud and self.config:
                # Connect to cloud MySQL
                cloud_config = self.config['cloud_sql']
                
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
                
                # Create pymysql connection for updates
                self.connection = pymysql.connect(
                    host=cloud_config['host'],
                    port=cloud_config['port'],
                    user=cloud_config['user'],
                    password=cloud_config['password'],
                    database=cloud_config['database_name'],
                    charset='utf8mb4',
                    **ssl_config
                )
                
                # Create SQLAlchemy engine for pandas queries
                if SQLALCHEMY_AVAILABLE:
                    connection_string = f"mysql+pymysql://{cloud_config['user']}:{cloud_config['password']}@{cloud_config['host']}:{cloud_config['port']}/{cloud_config['database_name']}"
                    self.engine = create_engine(connection_string)
                
                self.db_type = 'mysql'
                print("✅ Connected to Google Cloud SQL (MySQL)")
                
            else:
                # Connect to local SQLite
                db_path = 'pathways_database.db'
                if not os.path.exists(db_path):
                    print(f"❌ SQLite database not found: {db_path}")
                    return False
                
                self.connection = sqlite3.connect(db_path)
                self.db_type = 'sqlite'
                print("✅ Connected to local SQLite database")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
        
        if self.engine:
            self.engine.dispose()
            self.engine = None
            
        self.db_type = None
        print("🔌 Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[pd.DataFrame]:
        """
        Execute a query and return results as DataFrame
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            DataFrame with results or None if error
        """
        try:
            if not self.connection:
                return None
            
            # Use SQLAlchemy engine if available for better pandas compatibility
            if SQLALCHEMY_AVAILABLE and self.engine:
                if params:
                    df = pd.read_sql_query(query, self.engine, params=params)
                else:
                    df = pd.read_sql_query(query, self.engine)
            else:
                # Fallback to direct connection
                if params:
                    df = pd.read_sql_query(query, self.connection, params=params)
                else:
                    df = pd.read_sql_query(query, self.connection)
            
            return df
            
        except Exception as e:
            return None
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """
        Execute an UPDATE/INSERT/DELETE query
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.connection:
                return False
            
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                rows_affected = cursor.rowcount
                self.connection.commit()
                return True
                
        except Exception as e:
            return False
    
    def get_pathways_data(self) -> Optional[pd.DataFrame]:
        """Get all pathways data"""
        query = "SELECT * FROM pathways_data"
        return self.execute_query(query)
    
    def get_animal_by_id(self, aid: str) -> Optional[pd.DataFrame]:
        """Get animal by AID"""
        try:
            if self.db_type == 'mysql':
                query = "SELECT * FROM pathways_data WHERE AID = %s"
            else:
                query = "SELECT * FROM pathways_data WHERE AID = ?"
            
            result = self.execute_query(query, (aid,))
            return result
                
        except Exception as e:
            return None
    
    def update_animal_record(self, aid: str, foster_value: str, transfer_value: str, 
                           communications_value: str, new_note: str) -> bool:
        """Update animal record"""
        try:
            # Check connection
            if not self.connection:
                return False
            
            # Get current welfare notes
            current_df = self.get_animal_by_id(aid)
            if current_df is None or len(current_df) == 0:
                return False
            
            # Handle different column names for welfare notes
            welfare_col = None
            for col in ['Welfare Notes', 'Welfare_Notes', 'welfare_notes']:
                if col in current_df.columns:
                    welfare_col = col
                    break
            
            if not welfare_col:
                return False
            
            current_notes = current_df.iloc[0][welfare_col] if current_df.iloc[0][welfare_col] else ""
            
            # Add new note if provided
            if new_note and new_note.strip():
                if current_notes:
                    new_welfare_notes = f"{current_notes}\n\n{new_note.strip()}"
                else:
                    new_welfare_notes = new_note.strip()
            else:
                new_welfare_notes = current_notes
            
            # Update the record - handle different database types
            if self.db_type == 'mysql':
                query = """
                    UPDATE pathways_data 
                    SET Foster_Attempted = %s, Transfer_Attempted = %s, 
                        Communications_Team_Attempted = %s, Welfare_Notes = %s
                    WHERE AID = %s
                """
            else:
                query = """
                    UPDATE pathways_data 
                    SET Foster_Attempted = ?, Transfer_Attempted = ?, 
                        Communications_Team_Attempted = ?, Welfare_Notes = ?
                    WHERE AID = ?
                """
            
            success = self.execute_update(query, (foster_value, transfer_value, 
                                                 communications_value, new_welfare_notes, aid))
            
            return success
            
        except Exception as e:
            return False
    
    def get_inventory_data(self) -> Optional[pd.DataFrame]:
        """Get animal inventory data"""
        query = "SELECT * FROM animal_inventory"
        return self.execute_query(query)
    
    def get_metadata(self) -> Optional[pd.DataFrame]:
        """Get metadata"""
        query = "SELECT * FROM metadata"
        return self.execute_query(query)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        try:
            # Count records in each table
            tables = ['pathways_data', 'animal_inventory', 'metadata']
            for table in tables:
                count_df = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                if count_df is not None:
                    stats[table] = count_df.iloc[0]['count']
            
            # Get database type
            stats['database_type'] = self.db_type
            
            # Get last update time
            metadata_df = self.get_metadata()
            if metadata_df is not None:
                last_updated = metadata_df[metadata_df['key'] == 'last_updated']
                if len(last_updated) > 0:
                    stats['last_updated'] = last_updated.iloc[0]['value']
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
        
        return stats
    
    def export_to_csv(self, filename: str = None) -> Optional[str]:
        """Export pathways data to CSV"""
        try:
            df = self.get_pathways_data()
            if df is None:
                return None
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"Pathways_Data_Export_{timestamp}.csv"
            
            df.to_csv(filename, index=False)
            print(f"✅ Data exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.connection:
                return False
            
            # Simple test query
            test_df = self.execute_query("SELECT 1 as test")
            return test_df is not None and len(test_df) > 0
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

# Global database manager instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def connect_to_database(use_cloud: bool = False) -> bool:
    """Connect to database (local or cloud)"""
    manager = get_database_manager()
    return manager.connect(use_cloud)

def disconnect_database():
    """Disconnect from database"""
    global _db_manager
    if _db_manager:
        _db_manager.disconnect()
        _db_manager = None 