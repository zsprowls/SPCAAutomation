#!/usr/bin/env python3
"""
Test script to verify the app works without Selenium dependencies
"""

import sys
import os

def test_app_no_selenium():
    """Test if the app can run without Selenium"""
    print("Testing SPCA Automation app without Selenium...")
    print("=" * 50)
    
    try:
        # Test imports
        print("Testing imports...")
        import streamlit as st
        import pandas as pd
        from image_cache_manager import get_cache_manager, initialize_cache, get_animal_images_cached
        
        print("✅ All imports successful")
        
        # Test cache manager
        print("Testing cache manager...")
        manager = get_cache_manager()
        print("✅ Cache manager created")
        
        # Test cache initialization (should not try to scrape)
        print("Testing cache initialization...")
        cache_success = initialize_cache()
        
        if cache_success:
            print("✅ Cache loaded successfully")
            
            # Test getting images from cache
            print("Testing image retrieval from cache...")
            test_images = get_animal_images_cached("12345")  # Test with dummy ID
            print(f"✅ Image retrieval works (returned {len(test_images)} images)")
            
        else:
            print("⚠️ No cache file found (this is expected if you haven't built the cache yet)")
        
        print("\n🎉 App is ready to run without Selenium!")
        print("To run the app:")
        print("  streamlit run streamlit_cloud_app.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_app_no_selenium()
    sys.exit(0 if success else 1) 