#!/usr/bin/env python3
"""
Startup script for the Pathways for Care Viewer application.
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import dash
        import pandas
        import dash_bootstrap_components
        print("✓ All required Python packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_csv_file():
    """Check if the CSV file exists"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    if os.path.exists(csv_path):
        print("✓ CSV file found")
        return True
    else:
        print(f"✗ CSV file not found at: {csv_path}")
        print("Please ensure the CSV file is in the correct location")
        return False

def check_cache_status():
    """Check the status of the image cache"""
    try:
        from image_cache_manager import get_cache_stats
        stats = get_cache_stats()
        if stats['total_animals'] > 0:
            print(f"✓ Image cache found: {stats['animals_with_images']} animals with images")
            return True
        else:
            print("⚠ No image cache found. Run 'python build_cache.py' to build cache.")
            return False
    except ImportError:
        print("⚠ Image cache system not available")
        return False

def main():
    print("=" * 50)
    print("Pathways for Care Viewer")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check CSV file
    if not check_csv_file():
        return
    
    # Check cache status
    check_cache_status()
    
    print("\nStarting application...")
    print("The application will open in your default web browser.")
    print("Press Ctrl+C to stop the application.\n")
    
    try:
        # Start the application
        from pathways_viewer import app
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:8050')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the app
        app.run(debug=False, host='0.0.0.0', port=8050)
        
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user.")
    except Exception as e:
        print(f"\nError starting application: {e}")
        print("Please check the error message above and try again.")

if __name__ == "__main__":
    main() 