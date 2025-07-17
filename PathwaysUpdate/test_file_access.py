#!/usr/bin/env python3est script to find accessible Google Drive files
from google_drive_manager import GoogleDriveManager

def main():
    print(🔍 Testing Google Drive file access...")
    
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
            
        # Look for CSV or spreadsheet files
        print("\n🔍 Looking for CSV/Spreadsheet files:")
        csv_files = [f for f in files if f['mimeType] in ['text/csv', 'application/vnd.google-apps.spreadsheet']]
        
        if csv_files:
            print("✅ Found CSV/Spreadsheet files:)          for file in csv_files:
                print(f"  📊 [object Object]file['name]} (ID: [object Object]file['id]}, Type:[object Object]file['mimeType']})")
        else:
            print("❌ No CSV or spreadsheet files found")
            
    except Exception as e:
        print(f"❌ Error listing files: {e})if __name__ == "__main__":
    main() 