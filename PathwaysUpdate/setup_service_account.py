#!/usr/bin/env python3
"""
Setup script for Google Service Account configuration
This script helps you set up the service account key file safely.
"""

import os
import json
import shutil

def setup_service_account():
    """Guide user through service account setup"""
    print("=" * 60)
    print("Google Service Account Setup")
    print("=" * 60)
    
    # Check if service account key already exists
    if os.path.exists('service_account_key.json'):
        print("✅ service_account_key.json already exists")
        response = input("Do you want to replace it? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return True
    
    print("\n📋 To set up your service account:")
    print("1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts")
    print("2. Create a new service account or select existing one")
    print("3. Create a new JSON key file")
    print("4. Download the JSON file")
    print("5. Place it in this directory as 'service_account_key.json'")
    
    print("\n🔧 Required permissions for the service account:")
    print("- Google Drive API: Enabled")
    print("- Google Sheets API: Enabled")
    print("- Role: Editor (for the project)")
    
    print("\n📄 Required sharing:")
    print("- Share your Google Sheet with the service account email")
    print("- Give it 'Editor' permissions")
    
    # Check if the file exists after instructions
    if os.path.exists('service_account_key.json'):
        print("\n✅ service_account_key.json found!")
        
        # Validate the JSON structure
        try:
            with open('service_account_key.json', 'r') as f:
                key_data = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in key_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print("✅ Service account key file is valid!")
            print(f"📧 Service account email: {key_data.get('client_email', 'Not found')}")
            return True
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON file")
            return False
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    else:
        print("\n❌ service_account_key.json not found")
        print("Please download your service account key and place it in this directory.")
        return False

def test_connection():
    """Test the service account connection"""
    print("\n" + "=" * 60)
    print("Testing Service Account Connection")
    print("=" * 60)
    
    try:
        from google_drive_manager import get_gdrive_manager
        
        # Test authentication
        manager = get_gdrive_manager(use_service_account=True)
        if manager.authenticate():
            print("✅ Service account authentication successful!")
            
            # Test reading from sheets
            df = manager.read_from_sheets_with_api_key()
            if df is not None:
                print(f"✅ Successfully read {len(df)} records from Google Sheets")
                return True
            else:
                print("❌ Failed to read from Google Sheets")
                return False
        else:
            print("❌ Service account authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Google Service Account for Pathways for Care")
    
    # Setup service account
    if setup_service_account():
        # Test connection
        if test_connection():
            print("\n🎉 Setup complete! Your service account is ready to use.")
            print("\nYou can now run:")
            print("streamlit run streamlit_gdrive_app.py")
        else:
            print("\n❌ Connection test failed. Please check your setup.")
    else:
        print("\n❌ Setup failed. Please try again.") 