#!/usr/bin/env python3
"""
Standalone script to build the image cache for the Pathways for Care Viewer.
This can be run independently to pre-populate the cache.
"""

import os
import sys
import time

def main():
    print("=" * 60)
    print("Pathways for Care - Image Cache Builder")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('config.py'):
        print("Error: Please run this script from the PathwaysUpdate directory")
        return
    
    # Import the cache manager
    try:
        from image_cache_manager import initialize_cache, get_cache_stats, cleanup_cache
    except ImportError as e:
        print(f"Error importing cache manager: {e}")
        return
    
    print("\nStarting cache build process...")
    print("This will take several minutes as it processes all animals.")
    print("You can stop at any time with Ctrl+C and resume later.\n")
    
    start_time = time.time()
    
    try:
        # Initialize and build cache
        success = initialize_cache()
        
        if success:
            # Get and display stats
            stats = get_cache_stats()
            
            elapsed_time = time.time() - start_time
            minutes = elapsed_time / 60
            
            print("\n" + "=" * 60)
            print("CACHE BUILD COMPLETE!")
            print("=" * 60)
            print(f"Total time: {minutes:.1f} minutes")
            print(f"Animals processed: {stats['total_animals']}")
            print(f"Animals with images: {stats['animals_with_images']}")
            print(f"Total images cached: {stats['total_images']}")
            print(f"Cache file size: {stats['cache_file_size'] / 1024:.1f} KB")
            print("\nThe cache is now ready for the web application!")
            
        else:
            print("\nCache build failed. Check the error messages above.")
            
    except KeyboardInterrupt:
        print("\n\nCache build interrupted by user.")
        print("Partial cache has been saved and can be used.")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        
    finally:
        # Clean up
        cleanup_cache()

if __name__ == "__main__":
    main() 