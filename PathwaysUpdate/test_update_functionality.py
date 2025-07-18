#!/usr/bin/env python3
"""
Test script to diagnose Google Sheets update functionality
"""

import os
import sys
import traceback
from google_drive_manager import get_gdrive_manager

def test_service_account_setup():
    """Test service account authentication and permissions"""
    print("🔧 Testing Service Account Setup...")
    
    try:
        # Get the manager
        manager = get_gdrive_manager(use_service_account=True)
        
        # Test authentication
        print("📋 Testing authentication...")
        if not manager.authenticate():
            print("❌ Authentication failed")
            return False
        print("✅ Authentication successful")
        
        # Test reading data
        print("📖 Testing data reading...")
        df = manager.read_from_sheets_with_service_account()
        if df is None:
            print("❌ Failed to read data")
            return False
        print(f"✅ Successfully read {len(df)} records")
        
        # Test getting sheet metadata
        print("📊 Testing sheet metadata access...")
        try:
            from googleapiclient.discovery import build
            sheets_service = build('sheets', 'v4', credentials=manager.credentials)
            
            # Get sheet metadata
            sheet_metadata = sheets_service.spreadsheets().get(
                spreadsheetId="1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ"
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            if sheets:
                sheet_id = sheets[0]['properties']['sheetId']
                print(f"✅ Found sheet with ID: {sheet_id}")
                print(f"✅ Sheet name: {sheets[0]['properties']['title']}")
            else:
                print("❌ No sheets found")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing sheet metadata: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return False
        
        # Test a simple update (we'll use a test animal if available)
        print("✏️ Testing update functionality...")
        if len(df) > 0:
            test_aid = str(df.iloc[0]['AID'])
            print(f"Testing with animal AID: {test_aid}")
            
            # Try to update the test animal
            success = manager.update_animal_record_with_api_key(
                aid=test_aid,
                foster_value="Test",
                transfer_value="Test", 
                communications_value="Test",
                new_note="Test update from service account"
            )
            
            if success:
                print("✅ Update test successful!")
                return True
            else:
                print("❌ Update test failed")
                return False
        else:
            print("⚠️ No data to test with")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def check_service_account_permissions():
    """Check if service account has proper permissions"""
    print("\n🔐 Checking Service Account Permissions...")
    
    try:
        manager = get_gdrive_manager(use_service_account=True)
        
        if not manager.authenticate():
            print("❌ Cannot authenticate to check permissions")
            return False
            
        # Get service account email
        if hasattr(manager.credentials, 'service_account_email'):
            service_account_email = manager.credentials.service_account_email
            print(f"📧 Service Account Email: {service_account_email}")
        else:
            print("⚠️ Could not determine service account email")
            
        # Test file access
        print("📁 Testing file access...")
        try:
            from googleapiclient.discovery import build
            drive_service = build('drive', 'v3', credentials=manager.credentials)
            
            # Try to get file metadata
            file_metadata = drive_service.files().get(
                fileId="1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ"
            ).execute()
            
            print(f"✅ File access successful")
            print(f"📄 File name: {file_metadata.get('name', 'Unknown')}")
            print(f"🔗 File ID: {file_metadata.get('id', 'Unknown')}")
            
            # Check permissions
            permissions = drive_service.permissions().list(
                fileId="1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ"
            ).execute()
            
            print("📋 File permissions:")
            for perm in permissions.get('permissions', []):
                email = perm.get('emailAddress', 'Unknown')
                role = perm.get('role', 'Unknown')
                print(f"  - {email}: {role}")
                
        except Exception as e:
            print(f"❌ Error checking permissions: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Google Sheets Update Functionality Test")
    print("=" * 50)
    
    # Check if service account key exists
    if not os.path.exists('service_account_key.json'):
        print("❌ service_account_key.json not found")
        print("Please create a service account and download the key file")
        return
    
    print("✅ service_account_key.json found")
    
    # Test permissions
    if not check_service_account_permissions():
        print("❌ Permission check failed")
        return
    
    # Test update functionality
    if test_service_account_setup():
        print("\n🎉 All tests passed! Update functionality should work.")
    else:
        print("\n❌ Update functionality test failed")
        print("\n📋 Troubleshooting steps:")
        print("1. Make sure the Google Sheet is shared with the service account email")
        print("2. Give the service account 'Editor' permissions (not just Viewer)")
        print("3. Check that Google Sheets API is enabled in your Google Cloud project")
        print("4. Verify the service account key is valid and not expired")

if __name__ == "__main__":
    main() 