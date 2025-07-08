import os
import json
import time
import sys
from pathlib import Path
import pandas as pd

# Add the parent directory to the path so we can import the petpoint_image_scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import PETPOINT_CONFIG, IMAGE_CONFIG

# Import the working functions from the original scraper
from petpoint_image_scraper import setup_driver, login_to_petpoint, get_animal_images

class ImageCacheManager:
    def __init__(self):
        self.cache_file = "animal_images_cache.json"
        self.cache_data = {}
        self.scraper = None
        self.load_cache()
    
    def load_cache(self):
        """Load existing cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
                print(f"Loaded {len(self.cache_data)} cached image entries")
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.cache_data = {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2)
            print(f"Saved {len(self.cache_data)} image entries to cache")
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def initialize_scraper(self):
        """Initialize the PetPoint scraper using the working setup_driver function"""
        try:
            # Use the exact working setup_driver function from the original scraper
            self.driver = setup_driver()
            print("✓ Chrome driver initialized using working setup function")
            return True
            
        except ImportError:
            print("✗ Original scraper not available")
            return False
        except Exception as e:
            print(f"✗ Error initializing scraper: {e}")
            return False
    
    def login_to_petpoint(self):
        """Login to PetPoint using the working login function"""
        try:
            # Use the exact working login function from the original scraper
            success = login_to_petpoint(
                self.driver, 
                PETPOINT_CONFIG['shelter_id'], 
                PETPOINT_CONFIG['username'], 
                PETPOINT_CONFIG['password']
            )
            if success:
                print("✓ Login successful using working login function!")
            else:
                print("✗ Login failed using working login function")
            return success
            
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False
    
    def get_animal_images_from_page(self, animal_id):
        """Get images from the animal page using the exact working function"""
        try:
            # Use the exact working get_animal_images function from the original scraper
            image_urls = get_animal_images(self.driver, animal_id)
            return image_urls
            
        except Exception as e:
            print(f"Error getting images for {animal_id}: {str(e)}")
            return []
    
    def get_animal_images(self, animal_id):
        """Get images for a specific animal (from cache only)"""
        animal_id = str(animal_id).strip()
        
        # Check cache first
        if animal_id in self.cache_data:
            return self.cache_data[animal_id]
        
        # Return empty list if not in cache
        return []
    
    def build_cache_from_csv(self, csv_path):
        """Build cache for all animals in the CSV file"""
        print("Building image cache from CSV data...")
        
        # Load CSV data
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} animals from CSV")
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
        
        # Initialize scraper
        if not self.initialize_scraper():
            print("Cannot build cache without scraper")
            return False
        
        # Login once for all animals
        if not self.login_to_petpoint():
            print("Failed to login to PetPoint. Cannot build cache.")
            return False
        
        # Get unique animal IDs
        animal_ids = df['AID'].dropna().unique()
        print(f"Found {len(animal_ids)} unique animal IDs")
        
        # Process each animal
        processed = 0
        cached = 0
        
        for animal_id in animal_ids:
            animal_id = str(animal_id).strip()
            if not animal_id or animal_id == 'nan':
                continue
            
            processed += 1
            
            # Skip if already cached
            if animal_id in self.cache_data:
                cached += 1
                continue
            
            print(f"Processing {processed}/{len(animal_ids)}: Animal {animal_id}")
            
            try:
                image_urls = self.get_animal_images_from_page(animal_id)
                if image_urls:
                    self.cache_data[animal_id] = image_urls
                    cached += 1
                    print(f"  ✓ Found {len(image_urls)} images")
                else:
                    print(f"  - No images found")
                
                # Save cache periodically
                if processed % 10 == 0:
                    self.save_cache()
                
                # Small delay to be nice to the server
                time.sleep(1)
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        # Final save
        self.save_cache()
        
        print(f"\nCache building complete!")
        print(f"Processed: {processed} animals")
        print(f"Cached: {cached} animals with images")
        print(f"Total cache entries: {len(self.cache_data)}")
        
        return True
    
    def get_cache_stats(self):
        """Get statistics about the cache"""
        total_animals = len(self.cache_data)
        animals_with_images = sum(1 for urls in self.cache_data.values() if urls)
        total_images = sum(len(urls) for urls in self.cache_data.values())
        
        return {
            'total_animals': total_animals,
            'animals_with_images': animals_with_images,
            'total_images': total_images,
            'cache_file_size': os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache_data = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("Cache cleared")
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

# Global cache manager instance
cache_manager = None

def get_cache_manager():
    """Get the global cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = ImageCacheManager()
    return cache_manager

def initialize_cache():
    """Initialize the cache during application startup"""
    manager = get_cache_manager()
    
    # Check if cache exists and is recent
    if os.path.exists(manager.cache_file):
        cache_age = time.time() - os.path.getmtime(manager.cache_file)
        cache_age_hours = cache_age / 3600
        
        if cache_age_hours < 24:  # Cache is less than 24 hours old
            print(f"Using existing cache (age: {cache_age_hours:.1f} hours)")
            return True
        else:
            print(f"Cache is old ({cache_age_hours:.1f} hours), rebuilding...")
    
    # Build cache from CSV
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    return manager.build_cache_from_csv(csv_path)

def get_animal_images_cached(animal_id):
    """Get images for an animal from cache"""
    manager = get_cache_manager()
    return manager.get_animal_images(animal_id)

def get_cache_stats():
    """Get cache statistics"""
    manager = get_cache_manager()
    return manager.get_cache_stats()

def cleanup_cache():
    """Clean up cache resources"""
    global cache_manager
    if cache_manager:
        cache_manager.cleanup()
        cache_manager = None 