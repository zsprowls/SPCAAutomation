import sqlite3
import pandas as pd

def check_database():
    """Check database structure and data"""
    conn = sqlite3.connect('pathways_database.db')
    cursor = conn.cursor()
    
    print("🔍 Checking database structure...")
    
    # Get table info
    cursor.execute('PRAGMA table_info(pathways_data)')
    columns = cursor.fetchall()
    
    print("\n📋 Column names in database:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check sample data
    print("\n📊 Sample data:")
    cursor.execute('SELECT * FROM pathways_data LIMIT 3')
    rows = cursor.fetchall()
    
    for i, row in enumerate(rows):
        print(f"\nRecord {i+1}:")
        for j, col in enumerate(columns):
            print(f"  {col[1]}: {row[j]}")
    
    # Test queries
    print("\n🧪 Testing queries...")
    
    # Test welfare notes query
    try:
        cursor.execute('SELECT "Welfare Notes" FROM pathways_data WHERE AID = ?', ('57975287',))
        result = cursor.fetchone()
        print(f"✅ Welfare notes query works: {result[0] if result else 'No data'}")
    except Exception as e:
        print(f"❌ Welfare notes query failed: {e}")
    
    # Test update query
    try:
        cursor.execute('''
            UPDATE pathways_data 
            SET "Foster Attempted" = "Test"
            WHERE AID = ?
        ''', ('57975287',))
        print("✅ Update query works")
        conn.rollback()  # Rollback test change
    except Exception as e:
        print(f"❌ Update query failed: {e}")
    
    conn.close()
    
    print("\n✅ Database check complete!")

if __name__ == "__main__":
    check_database() 