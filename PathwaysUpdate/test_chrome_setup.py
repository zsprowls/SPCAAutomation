#!/usr/bin/env python3
"""
Test script to verify Chrome and ChromeDriver setup for SPCA Automation
"""

import sys
import os

def test_chrome_setup():
    """Test if Chrome and ChromeDriver can be set up successfully"""
    print("Testing Chrome setup for SPCA Automation...")
    print("=" * 50)
    
    try:
        # Import required modules
        from image_cache_manager import get_cache_manager
        
        # Get cache manager
        manager = get_cache_manager()
        
        # Test driver setup
        print("Setting up Chrome driver...")
        driver = manager.setup_driver()
        
        if driver is None:
            print("❌ Chrome driver setup failed!")
            print("\nPossible solutions:")
            print("1. Run: sudo ./install_chrome_deps.sh")
            print("2. Use Docker: docker build -t spca-automation .")
            print("3. Check the CHROME_SETUP_GUIDE.md for detailed instructions")
            return False
        
        print("✅ Chrome driver setup successful!")
        
        # Test basic functionality
        print("Testing basic Chrome functionality...")
        try:
            driver.get("https://www.google.com")
            title = driver.title
            print(f"✅ Successfully loaded Google (title: {title})")
        except Exception as e:
            print(f"❌ Failed to load test page: {e}")
            driver.quit()
            return False
        
        # Clean up
        driver.quit()
        print("✅ Chrome test completed successfully!")
        print("\nYour Chrome setup is working correctly.")
        print("The SPCA Automation application should now work with image scraping.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the PathwaysUpdate directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_chrome_setup()
    sys.exit(0 if success else 1) 