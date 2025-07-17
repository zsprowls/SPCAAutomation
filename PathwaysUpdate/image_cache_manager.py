import os
import json
import time
import sys
from pathlib import Path
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedImageCacheManager:
    def __init__(self):
        # Use absolute path to cache file relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_file = os.path.join(script_dir, "animal_images_cache.json")
        self.cache_data = {}
        self.load_cache()
        
    def load_cache(self):
        """Load existing cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
                logger.info(f"Loaded {len(self.cache_data)} cached image entries")
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                self.cache_data = {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2)
            logger.info(f"Saved {len(self.cache_data)} image entries to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def get_animal_images(self, animal_id):
        """Get images for a specific animal (from cache only)"""
        animal_id = str(animal_id).strip()
        
        # Check cache first
        if animal_id in self.cache_data:
            return self.cache_data[animal_id]
        
        # Return empty list if not in cache
        return []
    
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
    
    def cleanup(self):
        """Cleanup resources"""
        pass  # No cleanup needed for cache-only manager

# Global cache manager instance
_cache_manager = None

def get_cache_manager():
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = OptimizedImageCacheManager()
    return _cache_manager

def initialize_cache():
    """Initialize the image cache"""
    try:
    manager = get_cache_manager()
        stats = manager.get_cache_stats()
        
        if stats['total_animals'] > 0:
            logger.info(f"Cache contains {stats['total_animals']} animals with {stats['total_images']} total images")
            return True
        else:
            logger.warning("No animals found in cache")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing cache: {e}")
        return False

def get_animal_images_cached(animal_id):
    """Get cached images for an animal"""
    try:
    manager = get_cache_manager()
    return manager.get_animal_images(animal_id)
    except Exception as e:
        logger.error(f"Error getting cached images for {animal_id}: {e}")
        return []

def get_cache_stats():
    """Get cache statistics"""
    try:
    manager = get_cache_manager()
    return manager.get_cache_stats()
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {}

def cleanup_cache():
    """Cleanup cache resources"""
    try:
        global _cache_manager
        if _cache_manager:
            _cache_manager.cleanup()
            _cache_manager = None
    except Exception as e:
        logger.error(f"Error cleaning up cache: {e}") 