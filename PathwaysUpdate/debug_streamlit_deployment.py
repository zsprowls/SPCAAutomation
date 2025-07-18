#!/usr/bin/env python3
"""
Debug script for Streamlit deployment with Google Sheets update functionality
This will help diagnose issues with service account authentication and permissions.
"""

import streamlit as st
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_streamlit_secrets():
    """Test Streamlit secrets configuration"""
    st.write("## 🔐 Testing Streamlit Secrets")
    
    try:
        if hasattr(st, 'secrets'):
            st.success("✅ st.secrets is available")
            
            # Show available keys
            keys = list(st.secrets.keys())
            st.write(f"**Available secret keys:** {keys}")
            
            if 'service_account' in st.secrets:
                st.success("✅ 'service_account' key found")
                
                sa_info = st.secrets['service_account']
                sa_keys = list(sa_info.keys())
                st.write(f"**Service account fields:** {sa_keys}")
                
                # Check required fields
                required_fields = ['type', 'project_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if field not in sa_keys]
                
                if missing_fields:
                    st.error(f"❌ Missing required fields: {missing_fields}")
                    return False
                else:
                    st.success("✅ All required service account fields present")
                    
                    # Show service account email (for sharing)
                    email = sa_info.get('client_email', 'Not found')
                    st.info(f"**Service Account Email:** {email}")
                    st.write("📋 **Make sure to share your Google Sheet with this email and give it Editor permissions!**")
                    return True
            else:
                st.error("❌ 'service_account' key not found in secrets")
                st.write("📋 **To fix this:**")
                st.write("1. Go to your Streamlit Cloud dashboard")
                st.write("2. Navigate to your app settings")
                st.write("3. Add a secret with key 'service_account'")
                st.write("4. Paste the entire JSON content of your service account key")
                return False
        else:
            st.error("❌ st.secrets not available")
            return False
            
    except Exception as e:
        st.error(f"❌ Error testing secrets: {e}")
        st.code(traceback.format_exc())
        return False

def test_google_drive_connection():
    """Test Google Drive connection using secrets"""
    st.write("## 🔗 Testing Google Drive Connection")
    
    try:
        from google_drive_manager import get_gdrive_manager
        
        # Get manager with service account
        manager = get_gdrive_manager(use_service_account=True)
        
        # Test authentication
        st.write("📋 Testing authentication...")
        if manager.authenticate():
            st.success("✅ Service account authentication successful")
        else:
            st.error("❌ Service account authentication failed")
            return False
        
        # Test reading data
        st.write("📖 Testing data reading...")
        df = manager.read_from_sheets_with_service_account()
        if df is not None:
            st.success(f"✅ Successfully read {len(df)} records from Google Sheets")
            
            # Show sample data
            if len(df) > 0:
                st.write("📋 **Sample data:**")
                st.dataframe(df.head(3))
                
                # Show available columns
                st.write("📋 **Available columns:**")
                st.write(list(df.columns))
            return True
        else:
            st.error("❌ Failed to read data from Google Sheets")
            return False
            
    except Exception as e:
        st.error(f"❌ Error testing Google Drive connection: {e}")
        st.code(traceback.format_exc())
        return False

def test_update_functionality():
    """Test update functionality"""
    st.write("## ✏️ Testing Update Functionality")
    
    try:
        from google_drive_manager import get_gdrive_manager
        
        manager = get_gdrive_manager(use_service_account=True)
        
        if not manager.authenticate():
            st.error("❌ Cannot test updates - authentication failed")
            return False
        
        # Read data to find a test animal
        df = manager.read_from_sheets_with_service_account()
        if df is None or len(df) == 0:
            st.error("❌ No data available for testing")
            return False
        
        # Use first animal for testing
        test_aid = str(df.iloc[0]['AID'])
        st.write(f"🧪 Testing with animal AID: {test_aid}")
        
        # Try to update
        st.write("📝 Attempting update...")
        success = manager.update_animal_record_with_api_key(
            aid=test_aid,
            foster_value="Test",
            transfer_value="Test",
            communications_value="Test",
            new_note="Test update from Streamlit deployment"
        )
        
        if success:
            st.success("✅ Update test successful!")
            
            # Verify the update
            st.write("🔍 Verifying update...")
            df_updated = manager.read_from_sheets_with_service_account()
            if df_updated is not None:
                updated_row = df_updated[df_updated['AID'] == test_aid]
                if len(updated_row) > 0:
                    st.success("✅ Update verified in Google Sheets!")
                    return True
                else:
                    st.warning("⚠️ Could not find updated record")
                    return False
            else:
                st.error("❌ Could not verify update")
                return False
        else:
            st.error("❌ Update test failed")
            return False
            
    except Exception as e:
        st.error(f"❌ Error testing update functionality: {e}")
        st.code(traceback.format_exc())
        return False

def check_permissions():
    """Check if service account has proper permissions"""
    st.write("## 🔐 Checking Permissions")
    
    try:
        from google_drive_manager import get_gdrive_manager
        from googleapiclient.discovery import build
        
        manager = get_gdrive_manager(use_service_account=True)
        
        if not manager.authenticate():
            st.error("❌ Cannot check permissions - authentication failed")
            return False
        
        # Get service account email
        if hasattr(manager.credentials, 'service_account_email'):
            service_account_email = manager.credentials.service_account_email
            st.info(f"📧 **Service Account Email:** {service_account_email}")
        else:
            st.warning("⚠️ Could not determine service account email")
            return False
        
        # Test file access
        st.write("📁 Testing file access...")
        try:
            drive_service = build('drive', 'v3', credentials=manager.credentials)
            
            # Try to get file metadata
            file_metadata = drive_service.files().get(
                fileId="1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ"
            ).execute()
            
            st.success("✅ File access successful")
            st.write(f"📄 **File name:** {file_metadata.get('name', 'Unknown')}")
            
            # Check permissions
            permissions = drive_service.permissions().list(
                fileId="1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ"
            ).execute()
            
            st.write("📋 **File permissions:**")
            found_service_account = False
            for perm in permissions.get('permissions', []):
                email = perm.get('emailAddress', 'Unknown')
                role = perm.get('role', 'Unknown')
                st.write(f"  - {email}: {role}")
                
                if email == service_account_email:
                    found_service_account = True
                    if role == 'writer' or role == 'owner':
                        st.success(f"✅ Service account has {role} permissions")
                    else:
                        st.error(f"❌ Service account only has {role} permissions (needs 'writer')")
            
            if not found_service_account:
                st.error("❌ Service account not found in file permissions")
                st.write("📋 **To fix this:**")
                st.write(f"1. Go to your Google Sheet")
                st.write(f"2. Click 'Share' and add: {service_account_email}")
                st.write(f"3. Give it 'Editor' permissions")
                return False
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error checking permissions: {e}")
            return False
            
    except Exception as e:
        st.error(f"❌ Error in permission check: {e}")
        return False

def main():
    """Main debug function"""
    st.title("🔧 Streamlit Deployment Debug Tool")
    st.write("This tool will help diagnose issues with your Google Sheets update functionality.")
    
    # Test secrets
    secrets_ok = test_streamlit_secrets()
    
    if secrets_ok:
        # Test connection
        connection_ok = test_google_drive_connection()
        
        if connection_ok:
            # Check permissions
            permissions_ok = check_permissions()
            
            if permissions_ok:
                # Test updates
                update_ok = test_update_functionality()
                
                if update_ok:
                    st.success("🎉 All tests passed! Your update functionality should work.")
                else:
                    st.error("❌ Update functionality failed. Check the error messages above.")
            else:
                st.error("❌ Permission issues detected. Fix the sharing permissions first.")
        else:
            st.error("❌ Connection issues detected. Check your service account setup.")
    else:
        st.error("❌ Secrets configuration issues detected. Fix your Streamlit secrets first.")
    
    # Summary
    st.write("---")
    st.write("## 📋 Summary")
    st.write("If you're having issues:")
    st.write("1. **Check Streamlit secrets** - Make sure 'service_account' key exists with full JSON")
    st.write("2. **Check file sharing** - Share your Google Sheet with the service account email")
    st.write("3. **Check permissions** - Give the service account 'Editor' permissions")
    st.write("4. **Check APIs** - Enable Google Drive API and Google Sheets API in your project")

if __name__ == "__main__":
    main() 