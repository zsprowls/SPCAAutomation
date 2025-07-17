#!/usr/bin/env python3t CSV data loading from Google Drive

from google_drive_manager import get_gdrive_manager, connect_to_gdrive

def test_csv_data():
    print("=" * 60)
    print("Testing CSV Data Loading)
    print(= * 60)    
    # Connect to Google Drive
    if not connect_to_gdrive(use_service_account=True):
        print("❌ Failed to connect to Google Drive")
        return
    
    # Get manager
    manager = get_gdrive_manager(use_service_account=True)
    
    # Try to read the CSV data
    print("\n📊 Loading CSV data...")
    df = manager.get_pathways_data()
    
    if df is None:
        print("❌ Failed to load CSV data")
        return
    
    print(f"✅ Successfully loaded CSV data")
    print(f"📈 Shape: {df.shape}")
    print(f📋 Columns: {list(df.columns)})    
    if len(df) == 0:
        print("⚠️  CSV file is empty!")
        print("\n💡 You need to add some data to your CSV file.)
        print("   The file should have these columns:)
        print("   AID,Animal Name,Location,SubLocation,Age,Stage,Foster_Attempted,Transfer_Attempted,Communications_Team_Attempted,Welfare_Notes,Image_URLs")
    else:
        print(f"\n📄 First few rows:")
        print(df.head())
        
        print(f"\n📊 Data types:")
        print(df.dtypes)

if __name__ == "__main__":
    test_csv_data() 