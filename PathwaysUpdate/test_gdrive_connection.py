#!/usr/bin/env python3
"""
Test Google Drive Connection
"""

import os
import sys

def test_gdrive_setup():
    """Test Google Drive setup"""
    print("=" * 60)
    print("Testing Google Drive Setup")
    print("=" * 60)
    
    # Check if credentials file exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found")
        print("\n📋 To set up Google Drive access:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Drive API")
        print("4. Create credentials (OAuth 2.0 Client ID)")
        print("5. Download credentials.json to this directory")
        return False
    
    print("✅ credentials.json found")
    
    # Test imports
    try:
        from google_drive_manager import test_gdrive_connection
        print("✅ Google Drive manager imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n📋 Install dependencies with:")
        print("pip install -r requirements_gdrive.txt")
        return False
    
    # Test connection
    print("\n🔌 Testing Google Drive connection...")
    success = test_gdrive_connection()
    
    if success:
        print("✅ Google Drive connection successful!")
        print("\n🎉 Setup complete! You can now run:")
        print("streamlit run streamlit_gdrive_app.py")
        return True
    else:
        print("❌ Google Drive connection failed")
        return False

if __name__ == "__main__":
    test_gdrive_setup() 