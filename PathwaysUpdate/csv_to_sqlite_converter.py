import pandas as pd
import sqlite3
import os
from datetime import datetime

def convert_csv_to_sqlite():
    """Convert CSV files to SQLite database"""
    
    # Paths
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    inventory_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'AnimalInventory.csv')
    db_path = 'pathways_database.db'
    
    print("🔄 Converting CSV to SQLite database...")
    
    # Create/connect to SQLite database
    conn = sqlite3.connect(db_path)
    
    # Load Pathways for Care data
    print("📊 Loading Pathways for Care data...")
    df_pathways = pd.read_csv(csv_path)
    
    # Load Animal Inventory data
    print("📊 Loading Animal Inventory data...")
    try:
        df_inventory = pd.read_csv(inventory_path, skiprows=2)
        print(f"✅ Loaded {len(df_inventory)} inventory records")
    except Exception as e:
        print(f"⚠️ Warning: Could not load inventory data: {e}")
        df_inventory = None
    
    # Create tables
    print("🗄️ Creating database tables...")
    
    # Main pathways table
    df_pathways.to_sql('pathways_data', conn, if_exists='replace', index=False)
    print(f"✅ Created pathways_data table with {len(df_pathways)} records")
    
    # Inventory table (if available)
    if df_inventory is not None:
        df_inventory.to_sql('animal_inventory', conn, if_exists='replace', index=False)
        print(f"✅ Created animal_inventory table with {len(df_inventory)} records")
    
    # Create indexes for better performance
    print("⚡ Creating database indexes...")
    conn.execute('CREATE INDEX IF NOT EXISTS idx_aid ON pathways_data(AID)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_name ON pathways_data(Name)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_species ON pathways_data(Species)')
    
    # Add metadata table
    metadata = pd.DataFrame({
        'key': ['last_updated', 'total_records', 'source_files'],
        'value': [
            datetime.now().isoformat(),
            str(len(df_pathways)),
            'Pathways for Care.csv, AnimalInventory.csv'
        ]
    })
    metadata.to_sql('metadata', conn, if_exists='replace', index=False)
    
    conn.close()
    
    print(f"🎉 Database created successfully: {db_path}")
    print(f"📁 Database size: {os.path.getsize(db_path) / 1024:.1f} KB")
    
    return db_path

def test_database(db_path):
    """Test the database by running some queries"""
    print("\n🧪 Testing database...")
    
    conn = sqlite3.connect(db_path)
    
    # Test basic queries
    queries = [
        ("Total records", "SELECT COUNT(*) FROM pathways_data"),
        ("Species count", "SELECT Species, COUNT(*) FROM pathways_data GROUP BY Species"),
        ("Sample records", "SELECT AID, Name, Species FROM pathways_data LIMIT 5")
    ]
    
    for name, query in queries:
        print(f"\n📋 {name}:")
        result = conn.execute(query).fetchall()
        for row in result:
            print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    # Convert CSV to SQLite
    db_path = convert_csv_to_sqlite()
    
    # Test the database
    test_database(db_path)
    
    print("\n✅ Conversion complete! You can now use the database instead of CSV files.")
    print("📝 Next steps:")
    print("   1. Update your app to use the database")
    print("   2. Test the new database functionality")
    print("   3. Consider backing up your original CSV files") 