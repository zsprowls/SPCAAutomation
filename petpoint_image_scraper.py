from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import time
import requests
import argparse
from urllib.parse import urljoin

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add additional preferences
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Additional CDP commands to prevent detection
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver

def wait_for_element(driver, by, value, timeout=20, description="element"):
    """Wait for an element to be present and visible."""
    print(f"Waiting for {description}...")
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        print(f"Found {description}")
        return element
    except Exception as e:
        print(f"Error waiting for {description}: {str(e)}")
        print("Current page source:", driver.page_source[:1000])
        raise

def login_to_petpoint(driver, shelter_id, username, password):
    """
    Log in to PetPoint with the provided credentials.
    """
    try:
        print("Navigating to login page...")
        driver.get("https://sms.petpoint.com/sms3/forms/signinout.aspx")
        time.sleep(5)
        
        # Wait for page to be fully loaded
        print("Waiting for page to be fully loaded...")
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Get and print the current page title
        print(f"Page title: {driver.title}")
        
        # First, let's check if we need to handle any iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"Found {len(iframes)} iframes, switching to first one...")
            driver.switch_to.frame(iframes[0])
        
        # Try to find the shelter ID input
        print("Looking for shelter ID input...")
        shelter_id_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "LoginShelterId"))
        )
        print("Found shelter ID input")
        
        # Clear and enter shelter ID
        shelter_id_input.clear()
        shelter_id_input.send_keys(shelter_id)
        time.sleep(2)
        
        # Try to find the continue button
        print("Looking for continue button...")
        try:
            continue_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            print("Found continue button, clicking...")
            continue_button.click()
        except Exception as e:
            print(f"Could not find or click continue button: {str(e)}")
            print("Trying to press Enter key...")
            # Try pressing Enter key
            shelter_id_input.send_keys(Keys.RETURN)
        
        time.sleep(5)
        
        # Switch back to default content if we were in an iframe
        if iframes:
            driver.switch_to.default_content()
            # Switch to the iframe again for the next step
            driver.switch_to.frame(iframes[0])
        
        # Wait for username input
        print("Looking for username input...")
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "LoginUsername"))
        )
        print("Found username input")
        
        # Enter username
        username_input.clear()
        username_input.send_keys(username)
        time.sleep(2)
        
        # Wait for password input
        print("Looking for password input...")
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "LoginPassword"))
        )
        print("Found password input")
        
        # Enter password
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(2)
        
        # Try to find and click login button
        print("Looking for login button...")
        try:
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
            )
            print("Found login button, clicking...")
            login_button.click()
        except Exception as e:
            print(f"Could not find or click login button: {str(e)}")
            print("Trying to press Enter key...")
            # Try pressing Enter key
            password_input.send_keys(Keys.RETURN)
        
        # Wait for successful login
        time.sleep(5)
        
        # Switch back to default content
        if iframes:
            driver.switch_to.default_content()
        
        # Check if login was successful
        current_url = driver.current_url.lower()
        print(f"Current URL after login attempt: {current_url}")
        
        if "signinout.aspx" in current_url:
            print("Login failed - still on login page")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error during login: {str(e)}")
        print("Current URL:", driver.current_url)
        print("Page source:", driver.page_source[:1000])
        return False

def get_animal_images(driver, animal_id):
    """
    Scrape images for a given animal ID from PetPoint.
    
    Args:
        driver: Selenium WebDriver instance
        animal_id (str): The 8-digit animal ID
        
    Returns:
        list: List of image URLs found for the animal
    """
    # Extract last 8 digits if full ID is provided
    if len(animal_id) > 8:
        animal_id = animal_id[-8:]
    
    url = f"https://sms.petpoint.com/sms3/enhanced/animal/{animal_id}"
    print(f"\nNavigating to animal page: {url}")
    
    try:
        driver.get(url)
        time.sleep(5)  # Give page time to load
        
        # Wait for page to be fully loaded
        print("Waiting for page to be fully loaded...")
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Print page title for debugging
        print(f"Page title: {driver.title}")
        
        # Try to close any popup overlays
        try:
            overlay = driver.find_element(By.CLASS_NAME, "k-overlay")
            if overlay:
                print("Found overlay, trying to close it...")
                # Try to click outside the overlay
                ActionChains(driver).move_by_offset(0, 0).click().perform()
                time.sleep(2)
        except:
            print("No overlay found or couldn't close it")
        
        # Navigate to Photos/Video tab
        print("\nNavigating to Photos/Video tab...")
        try:
            # Wait for and click the Photos/Video tab
            photo_tab = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@id='AnimalImageGalleryTabLink']"))
            )
            # Try to click the tab
            try:
                photo_tab.click()
            except:
                # If click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", photo_tab)
            print("Clicked Photos/Video tab")
            time.sleep(3)  # Wait for tab content to load
            
            # Try multiple selectors to find images
            image_urls = []
            
            # Method 1: Try finding images in the gallery container
            try:
                print("Method 1: Looking for images in gallery container...")
                gallery_images = driver.find_elements(By.CSS_SELECTOR, "#ImageGallery img")
                if gallery_images:
                    print(f"Found {len(gallery_images)} images in gallery container")
                    for img in gallery_images:
                        src = img.get_attribute('src')
                        if src:
                            image_urls.append(src)
                            print(f"Found image URL: {src}")
            except Exception as e:
                print(f"Method 1 failed: {str(e)}")
            
            # Method 2: Try finding all images in the tab content
            if not image_urls:
                try:
                    print("\nMethod 2: Looking for all images in tab content...")
                    tab_images = driver.find_elements(By.CSS_SELECTOR, "#ImageGallery .tab-content img")
                    if tab_images:
                        print(f"Found {len(tab_images)} images in tab content")
                        for img in tab_images:
                            src = img.get_attribute('src')
                            if src:
                                image_urls.append(src)
                                print(f"Found image URL: {src}")
                except Exception as e:
                    print(f"Method 2 failed: {str(e)}")
            
            # Method 3: Try finding images with specific classes
            if not image_urls:
                try:
                    print("\nMethod 3: Looking for images with specific classes...")
                    class_images = driver.find_elements(By.CSS_SELECTOR, ".animal-image, .pet-image, .gallery-image")
                    if class_images:
                        print(f"Found {len(class_images)} images with specific classes")
                        for img in class_images:
                            src = img.get_attribute('src')
                            if src:
                                image_urls.append(src)
                                print(f"Found image URL: {src}")
                except Exception as e:
                    print(f"Method 3 failed: {str(e)}")
            
            # Print the page source for debugging if no images found
            if not image_urls:
                print("\nNo images found. Current page source:")
                print(driver.page_source[:2000])  # Print first 2000 chars for debugging
            
            return image_urls
            
        except Exception as e:
            print(f"Error navigating to Photos/Video tab: {str(e)}")
            return []
            
    except Exception as e:
        print(f"Error accessing animal page: {str(e)}")
        return []

def download_images(image_urls, output_dir, animal_id):
    """
    Download images to the specified directory.
    
    Args:
        image_urls (list): List of image URLs to download
        output_dir (str): Directory to save images to
        animal_id (str): Animal ID for naming files
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Save image with animal ID and index
                filename = f"{animal_id}_image_{i+1}.jpg"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download image {i+1} for animal {animal_id}")
        except Exception as e:
            print(f"Error downloading image {i+1} for animal {animal_id}: {str(e)}")

def main():
    # List of animal IDs to process
    animal_ids = [
        "57711591",
        "58332064",
        "58349243",
        "58467665",
        "58480470"
    ]
    
    # Setup driver and login
    driver = setup_driver()
    try:
        if login_to_petpoint(driver, "USNY9", "zaks", "Gillian666!"):
            print("Successfully logged in.")
            
            # Process each animal ID
            for animal_id in animal_ids:
                print(f"\nProcessing animal {animal_id}...")
                image_urls = get_animal_images(driver, animal_id)
                
                if image_urls:
                    print(f"Found {len(image_urls)} images")
                    print("First image URL:", image_urls[0])
                else:
                    print("No images found")
        else:
            print("Failed to log in. Please check your credentials.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

class PetPointImageScraper:
    def __init__(self):
        self.driver = None
        self.last_login_time = None
        self.login_timeout = 1800  # 30 minutes in seconds
        
    def ensure_valid_session(self):
        current_time = time.time()
        if (self.last_login_time is None or 
            current_time - self.last_login_time > self.login_timeout):
            self.login()
            
    def login(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
                
        self.driver = webdriver.Chrome()
        self.driver.get("https://sms.petpoint.com/sms3/enhanced/")
        
        # Wait for login form and enter credentials
        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = self.driver.find_element(By.ID, "password")
        
        username_field.send_keys("zsprowls")
        password_field.send_keys("Zaksprowls1!")
        
        # Click login button
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Wait for login to complete
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "k-widget"))
        )
        
        self.last_login_time = time.time()
        
    def get_animal_images(self, animal_id):
        try:
            self.ensure_valid_session()
            
            # Navigate to animal page
            url = f"https://sms.petpoint.com/sms3/enhanced/animal/{animal_id}"
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "k-widget"))
            )
            
            # Try to close any overlay
            try:
                overlay = self.driver.find_element(By.CLASS_NAME, "k-overlay")
                if overlay.is_displayed():
                    close_button = self.driver.find_element(By.CLASS_NAME, "k-window-titlebar-close")
                    close_button.click()
            except:
                pass
            
            # Click Photos/Video tab
            try:
                photos_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Photos/Video')]"))
                )
                photos_tab.click()
            except:
                print("Could not click Photos/Video tab")
                return []
            
            # Wait for images to load
            time.sleep(2)
            
            # Find all images
            images = []
            try:
                # Method 1: Look for images in gallery container
                gallery = self.driver.find_element(By.CLASS_NAME, "k-gallery")
                img_elements = gallery.find_elements(By.TAG_NAME, "img")
                
                for img in img_elements:
                    src = img.get_attribute("src")
                    if src and "petango.com" in src:
                        images.append(src)
                        
            except:
                print("No images found in gallery container")
                
            return images
            
        except Exception as e:
            print(f"Error accessing animal page: {str(e)}")
            return []
            
    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass 