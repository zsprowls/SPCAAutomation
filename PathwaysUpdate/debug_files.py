#!/usr/bin/env python3
debug script to list accessible Google Drive files
from google_drive_manager import GoogleDriveManager

def main():
    print("🔍 Debugging Google Drive access...")
    
    # Initialize manager
    manager = GoogleDriveManager(use_service_account=True)
    
    if not manager.authenticate():
        print("❌ Authentication failed")
        return
    
    try:
        # List all files the service account can access
        print("\n📁 Listing accessible files:)
        results = manager.service.files().list(
            pageSize=50,
            fields=files(id, name, mimeType, owners, sharedWithMe)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("❌ No files found")
            return
        
        print(f"✅ Found {len(files)} accessible files:")
        for file in files:
            print(f"  📄 [object Object]file['name]} (ID: [object Object]file['id]}, Type:[object Object]file['mimeType']})")
            
        # Look for CSV files specifically
        print("\n🔍 Looking for CSV files:")
        csv_files = [f for f in files if f[mimeType] == xt/csv']
        
        if csv_files:
            print(✅ Found CSV files:)          for file in csv_files:
                print(f"  📊 [object Object]file[name]} (ID: {file['id']})")
        else:
            print("❌ No CSV files found")
            
    except Exception as e:
        print(f"❌ Error listing files: {e})if __name__ == "__main__":
    main() 