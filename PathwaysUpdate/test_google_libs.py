#!/usr/bin/env python3
"""
Test script to check if Google Drive API libraries are installed
"""

import streamlit as st

def main():
    st.title("🔍 Google Drive API Libraries Test")
    
    st.write("Testing if Google Drive API libraries are available...")
    
    # Test imports
    try:
        st.write("📦 Testing imports...")
        
        # Test google-auth-oauthlib
        try:
            import google.auth.oauthlib
            st.success("✅ google-auth-oauthlib imported successfully")
        except ImportError as e:
            st.error(f"❌ google-auth-oauthlib import failed: {e}")
        
        # Test google-auth-httplib2
        try:
            import google.auth.httplib2
            st.success("✅ google-auth-httplib2 imported successfully")
        except ImportError as e:
            st.error(f"❌ google-auth-httplib2 import failed: {e}")
        
        # Test google-api-python-client
        try:
            import googleapiclient
            st.success("✅ google-api-python-client imported successfully")
        except ImportError as e:
            st.error(f"❌ google-api-python-client import failed: {e}")
        
        # Test specific modules
        try:
            from google.oauth2 import service_account
            st.success("✅ google.oauth2.service_account imported successfully")
        except ImportError as e:
            st.error(f"❌ google.oauth2.service_account import failed: {e}")
        
        try:
            from googleapiclient.discovery import build
            st.success("✅ googleapiclient.discovery.build imported successfully")
        except ImportError as e:
            st.error(f"❌ googleapiclient.discovery.build import failed: {e}")
        
        # Test if we can create credentials
        st.write("🔐 Testing credential creation...")
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            # Test with dummy data
            dummy_sa_info = {
                "type": "service_account",
                "project_id": "test",
                "private_key_id": "test",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
                "client_email": "test@test.iam.gserviceaccount.com",
                "client_id": "test",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test.iam.gserviceaccount.com"
            }
            
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            credentials = service_account.Credentials.from_service_account_info(dummy_sa_info, scopes=SCOPES)
            st.success("✅ Service account credentials created successfully")
            
        except Exception as e:
            st.error(f"❌ Credential creation failed: {e}")
        
    except Exception as e:
        st.error(f"❌ General import error: {e}")
    
    # Check installed packages
    st.write("---")
    st.write("## 📋 Installed Packages")
    
    try:
        import pkg_resources
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        
        google_packages = [pkg for pkg in installed_packages if 'google' in pkg.lower()]
        st.write(f"**Google-related packages:** {google_packages}")
        
        if not google_packages:
            st.error("❌ No Google packages found!")
        else:
            st.success(f"✅ Found {len(google_packages)} Google packages")
            
    except Exception as e:
        st.error(f"❌ Error checking installed packages: {e}")
    
    # Instructions
    st.write("---")
    st.write("## 🔧 If Google libraries are missing:")
    st.write("1. Check that requirements.txt includes:")
    st.code("""
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
""")
    st.write("2. Redeploy your app to force dependency reinstallation")
    st.write("3. Check Streamlit Cloud logs for any installation errors")

if __name__ == "__main__":
    main() 