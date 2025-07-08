import sys
import os
import time
from functools import lru_cache

# Add the parent directory to the path so we can import the petpoint_image_scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import configuration
from config import PETPOINT_CONFIG, IMAGE_CONFIG

try:
    from petpoint_image_scraper import PetPointImageScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    print("Warning: petpoint_image_scraper not available. Images will not be loaded.")
    SCRAPER_AVAILABLE = False

# Global scraper instance
scraper = None

def initialize_scraper():
    """Initialize the PetPoint scraper if available"""
    global scraper
    if SCRAPER_AVAILABLE and scraper is None:
        try:
            scraper = PetPointImageScraper()
            return True
        except Exception as e:
            print(f"Error initializing scraper: {e}")
            return False
    return SCRAPER_AVAILABLE

@lru_cache(maxsize=IMAGE_CONFIG['image_cache_size'])
def get_animal_images(animal_id):
    """
    Get images for an animal using the PetPoint scraper.
    
    Args:
        animal_id (str): The animal ID to get images for
        
    Returns:
        list: List of image URLs
    """
    if not SCRAPER_AVAILABLE:
        return []
    
    if scraper is None:
        if not initialize_scraper():
            return []
    
    try:
        # Clean the animal ID
        animal_id = str(animal_id).strip()
        if not animal_id or animal_id == 'nan':
            return []
        
        # Get images using the scraper
        image_urls = scraper.get_animal_images(animal_id)
        
        # Filter out any None or empty URLs
        if image_urls:
            image_urls = [url for url in image_urls if url and url.strip()]
        
        return image_urls
        
    except Exception as e:
        print(f"Error getting images for animal {animal_id}: {e}")
        return []

def cleanup_scraper():
    """Clean up the scraper resources"""
    global scraper
    if scraper:
        try:
            scraper.cleanup()
        except:
            pass
        scraper = None

# Alternative implementation using the function-based approach
def get_animal_images_alternative(animal_id):
    """
    Alternative implementation using the function-based approach from the original script.
    This requires setting up the driver and login each time.
    """
    if not SCRAPER_AVAILABLE:
        return []
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        
        # Setup driver
        chrome_options = Options()
        if IMAGE_CONFIG['headless_browser']:
            chrome_options.add_argument("--headless")  # Run headless for web app
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Login to PetPoint
            if not login_to_petpoint(driver, PETPOINT_CONFIG['shelter_id'], PETPOINT_CONFIG['username'], PETPOINT_CONFIG['password']):
                return []
            
            # Get images
            image_urls = get_animal_images_from_page(driver, animal_id)
            return image_urls
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error in alternative image fetching: {e}")
        return []

def login_to_petpoint(driver, shelter_id, username, password):
    """Login to PetPoint - simplified version"""
    try:
        driver.get("https://sms.petpoint.com/sms3/forms/signinout.aspx")
        time.sleep(3)
        
        # Handle iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
        
        # Enter shelter ID
        shelter_id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "LoginShelterId"))
        )
        shelter_id_input.clear()
        shelter_id_input.send_keys(shelter_id)
        shelter_id_input.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Switch back and forth for iframe
        if iframes:
            driver.switch_to.default_content()
            driver.switch_to.frame(iframes[0])
        
        # Enter username
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "LoginUsername"))
        )
        username_input.clear()
        username_input.send_keys(username)
        
        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "LoginPassword"))
        )
        password_input.clear()
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        
        time.sleep(5)
        
        # Check if login was successful
        if "signinout.aspx" in driver.current_url.lower():
            return False
            
        return True
        
    except Exception as e:
        print(f"Login error: {e}")
        return False

def get_animal_images_from_page(driver, animal_id):
    """Get images from the animal page"""
    try:
        url = f"https://sms.petpoint.com/sms3/enhanced/animal/{animal_id}"
        driver.get(url)
        time.sleep(3)
        
        # Click Photos/Video tab
        try:
            photo_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@id='AnimalImageGalleryTabLink']"))
            )
            driver.execute_script("arguments[0].click();", photo_tab)
            time.sleep(2)
        except:
            return []
        
        # Find images
        image_urls = []
        try:
            gallery_images = driver.find_elements(By.CSS_SELECTOR, "#ImageGallery img")
            for img in gallery_images:
                src = img.get_attribute('src')
                if src:
                    image_urls.append(src)
        except:
            pass
        
        return image_urls
        
    except Exception as e:
        print(f"Error getting images from page: {e}")
        return [] 