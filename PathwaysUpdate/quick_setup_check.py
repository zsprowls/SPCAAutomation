#!/usr/bin/env python3
"""
Quick setup check for Google Service Account
Run this after setting up your service account to verify everything works.
"""

import os
import json

def check_service_account_file():
    """Check if service account key file exists and is valid"""
    print("🔍 Checking service account key file...")
    
    if not os.path.exists('service_account_key.json'):
        print("❌ service_account_key.json not found")
        print("📋 Please download your service account key and place it in this directory")
        return False
    
    try:
        with open('service_account_key.json', 'r') as f:
            key_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in key_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print("✅ service_account_key.json found and valid")
        print(f"📧 Service account email: {key_data.get('client_email', 'Not found')}")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def check_google_apis():
    """Check if Google APIs are available"""
    print("\n🔍 Checking Google APIs...")
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
        print("✅ Google APIs available")
        return True
    except ImportError as e:
        print(f"❌ Google APIs not available: {e}")
        print("📋 Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False

def get_service_account_email():
    """Get the service account email from the key file"""
    try:
        with open('service_account_key.json', 'r') as f:
            key_data = json.load(f)
        return key_data.get('client_email', '')
    except:
        return ''

def main():
    """Main check function"""
    print("🔧 Quick Service Account Setup Check")
    print("=" * 40)
    
    # Check service account file
    if not check_service_account_file():
        return
    
    # Check Google APIs
    if not check_google_apis():
        return
    
    # Get service account email
    service_account_email = get_service_account_email()
    
    print("\n📋 Next Steps:")
    print("1. Go to your Google Sheet:")
    print("   https://docs.google.com/spreadsheets/d/1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ")
    print("2. Click 'Share' (top right)")
    print(f"3. Add this email: {service_account_email}")
    print("4. Set permission to 'Editor'")
    print("5. Uncheck 'Notify people'")
    print("6. Click 'Send'")
    print("\n7. Test the setup:")
    print("   python3 test_update_functionality.py")
    
    print("\n✅ Setup check complete!")

if __name__ == "__main__":
    main() 