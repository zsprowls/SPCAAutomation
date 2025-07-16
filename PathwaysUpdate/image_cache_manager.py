import os
import json
import time
import sys
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import threading
from queue import Queue
import logging

# PetPoint config no longer needed since we only read from cache
# from config import PETPOINT_CONFIG, IMAGE_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedImageCacheManager:
    def __init__(self):
        # Use absolute path to cache file relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_file = os.path.join(script_dir, "animal_images_cache.json")
        self.cache_data = {}
        self.driver = None
        self.last_login_time = None
        self.login_timeout = 1800  # 30 minutes
        self.session_lock = threading.Lock()
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
    
    def setup_driver(self):
        """Set up and return a configured Chrome WebDriver with headless mode"""
        try:
            chrome_options = Options()
            
            # Headless mode for faster processing
            # if IMAGE_CONFIG.get('headless_browser', True):
            chrome_options.add_argument("--headless")
            
            # Cloud environment specific options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Don't load images for faster page loads
            chrome_options.add_argument("--disable-javascript")  # Disable JS for faster loads
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Add additional preferences for faster loading
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,  # Block images
            })
            
            # Try to setup Chrome driver with better error handling
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as chrome_error:
                logger.error(f"Chrome driver setup failed: {chrome_error}")
                
                # Check if we're in a cloud environment and try alternative approaches
                if os.path.exists('/home/appuser') or os.path.exists('/app'):
                    logger.info("Detected cloud environment, trying alternative Chrome setup...")
                    
                    # Try with system Chrome if available
                    try:
                        chrome_options.binary_location = "/usr/bin/google-chrome"
                        service = Service(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                        logger.info("Successfully setup Chrome with system binary")
                    except Exception as system_chrome_error:
                        logger.error(f"System Chrome setup failed: {system_chrome_error}")
                        
                        # Try with chromium if available
                        try:
                            chrome_options.binary_location = "/usr/bin/chromium-browser"
                            service = Service(ChromeDriverManager().install())
                            driver = webdriver.Chrome(service=service, options=chrome_options)
                            logger.info("Successfully setup Chrome with Chromium binary")
                        except Exception as chromium_error:
                            logger.error(f"Chromium setup failed: {chromium_error}")
                            logger.error("All Chrome driver attempts failed. Image scraping will be disabled.")
                            return None
                else:
                    # Not in cloud environment, re-raise the original error
                    raise chrome_error
            
            # Execute CDP commands to prevent detection
            try:
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    '''
                })
            except Exception as cdp_error:
                logger.warning(f"CDP commands failed (non-critical): {cdp_error}")
            
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return None
    
    def ensure_valid_session(self):
        """Ensure we have a valid login session - DISABLED since we only read from cache"""
        # with self.session_lock:
        #     current_time = time.time()
        #     if (self.last_login_time is None or 
        #         current_time - self.last_login_time > self.login_timeout):
        #         self.login_to_petpoint()
        pass  # No login needed when reading from cache
    
    def login_to_petpoint(self):
        """Login to PetPoint - DISABLED since we only read from cache"""
        logger.info("PetPoint login disabled - using cache only")
        return False
    
    def get_animal_images_from_page(self, animal_id):
        """Get images for a specific animal from PetPoint - DISABLED since we only read from cache"""
        logger.info(f"Image scraping disabled for animal {animal_id} - using cache only")
        return []
    
    def process_animal_batch(self, animal_ids, progress_queue):
        """Process a batch of animals concurrently"""
        results = {}
        
        for i, animal_id in enumerate(animal_ids):
            try:
                animal_id_str = str(animal_id).strip()
                
                # Skip if already in cache
                if animal_id_str in self.cache_data:
                    logger.info(f"Animal {animal_id_str} already in cache, skipping...")
                    continue
                
                # Get images for this animal
                image_urls = self.get_animal_images_from_page(animal_id_str)
                results[animal_id_str] = image_urls
                
                # Update progress
                progress_queue.put(('processed', animal_id_str, len(image_urls)))
                
            except Exception as e:
                logger.error(f"Error processing animal {animal_id}: {str(e)}")
                results[str(animal_id).strip()] = []
                progress_queue.put(('error', str(animal_id).strip(), str(e)))
        
        return results
    
    def build_cache_from_csv(self, csv_path):
        """Build cache for all animals in the CSV file with concurrent processing"""
        try:
            if not os.path.exists(csv_path):
                logger.error(f"CSV file not found: {csv_path}")
                return False
            
            # Load CSV data
            logger.info(f"Loading data from {csv_path}...")
            df = pd.read_csv(csv_path)
            
            # Get animal IDs (assuming there's an ID column)
            id_columns = ['Animal ID', 'AnimalID', 'ID', 'id', 'AID']
            animal_id_col = None
            
            for col in id_columns:
                if col in df.columns:
                    animal_id_col = col
                    break
            
            if animal_id_col is None:
                logger.error("No animal ID column found in CSV")
                return False
            
            animal_ids = df[animal_id_col].dropna().unique().tolist()
            total_animals = len(animal_ids)
            
            logger.info(f"Found {total_animals} unique animals to process")
            
            # Initialize progress tracking
            progress_queue = Queue()
            processed_count = 0
            start_time = time.time()
            
            # Process animals in batches for better performance
            batch_size = 10  # Process 10 animals at a time
            all_results = {}
            
            for i in range(0, len(animal_ids), batch_size):
                batch = animal_ids[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(animal_ids) + batch_size - 1)//batch_size}")
                
                # Process this batch
                batch_results = self.process_animal_batch(batch, progress_queue)
                all_results.update(batch_results)
                
                # Update cache with batch results
                self.cache_data.update(batch_results)
                
                # Save cache periodically
                if (i + batch_size) % 50 == 0:
                    self.save_cache()
                    logger.info(f"Saved cache after processing {i + batch_size} animals")
                
                # Small delay between batches to avoid overwhelming the server
                time.sleep(1)
            
            # Save final cache
            self.save_cache()
            
            # Calculate final stats
            elapsed_time = time.time() - start_time
            minutes = elapsed_time / 60
            
            logger.info(f"Cache build completed in {minutes:.1f} minutes")
            logger.info(f"Processed {len(all_results)} animals")
            
            return True
            
        except Exception as e:
            logger.error(f"Error building cache: {str(e)}")
            return False
    
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
        logger.info("Cache cleared")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

# Global cache manager instance
cache_manager = None

def get_cache_manager():
    """Get the global cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = OptimizedImageCacheManager()
    return cache_manager

def initialize_cache():
    """Initialize the cache during application startup - READ ONLY MODE"""
    manager = get_cache_manager()
    
    # Debug: Log the cache file path
    logger.info(f"Looking for cache file at: {manager.cache_file}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Check if cache exists
    if os.path.exists(manager.cache_file):
        cache_age = time.time() - os.path.getmtime(manager.cache_file)
        cache_age_hours = cache_age / 3600
        
        logger.info(f"Using existing cache (age: {cache_age_hours:.1f} hours)")
        
        # Get cache stats for logging
        stats = manager.get_cache_stats()
        logger.info(f"Cache contains {stats['total_animals']} animals with {stats['total_images']} total images")
        
        return True
    else:
        logger.warning("No cache file found. Images will not be available.")
        logger.info("To enable images, build the cache locally using build_cache.py and push the animal_images_cache.json file")
        return False

def get_animal_images_cached(animal_id):
    """Get images for an animal from cache"""
    try:
        manager = get_cache_manager()
        return manager.get_animal_images(animal_id)
    except Exception as e:
        logger.error(f"Error getting cached images for {animal_id}: {e}")
        return []

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