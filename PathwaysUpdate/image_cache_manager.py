import os
import json
import time
import sys
from pathlib import Path
import pandas as pd

from config import PETPOINT_CONFIG, IMAGE_CONFIG

# Note: The original scraper functions are no longer available
# This version only works with pre-built cache

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
        """Initialize the PetPoint scraper - DISABLED"""
        print("✗ Scraper functionality disabled - using cache only")
        return False
    
    def login_to_petpoint(self):
        """Login to PetPoint - DISABLED"""
        print("✗ Login functionality disabled - using cache only")
        return False
    
    def get_animal_images_from_page(self, animal_id):
        """Get images from the animal page - DISABLED"""
        print(f"✗ Image fetching disabled for {animal_id} - using cache only")
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
        """Build cache for all animals in the CSV file - DISABLED"""
        print("✗ Cache building disabled - scraper functionality removed")
        print("The cache is pre-built and stored in animal_images_cache.json")
        print("To rebuild cache, you would need to restore the scraper functionality")
        return False
    
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
        # No driver to clean up since scraper is disabled
        pass

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