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
        
        # Try different methods to find images
        print("\nTrying to find images...")
        
        # Method 1: Original XPath
        try:
            print("Method 1: Trying original XPath...")
            image_xpath = "/html/body/div[1]/div/section/div/div[4]/div[2]/div[2]/div/div/div[2]/div/div/div[1]/div[1]/img"
            images = driver.find_elements(By.XPATH, image_xpath)
            print(f"Found {len(images)} images with original XPath")
        except Exception as e:
            print(f"Method 1 failed: {str(e)}")
            images = []
        
        # Method 2: Find all images in the page
        if not images:
            try:
                print("\nMethod 2: Trying to find all images...")
                images = driver.find_elements(By.TAG_NAME, "img")
                print(f"Found {len(images)} total images on page")
                
                # Filter for animal images (you might need to adjust this filter)
                animal_images = []
                for img in images:
                    src = img.get_attribute('src')
                    if src and ('animal' in src.lower() or 'pet' in src.lower()):
                        animal_images.append(img)
                print(f"Found {len(animal_images)} potential animal images")
                images = animal_images
            except Exception as e:
                print(f"Method 2 failed: {str(e)}")
        
        # Method 3: Try finding images in specific containers
        if not images:
            try:
                print("\nMethod 3: Looking in specific containers...")
                # Try to find image containers
                containers = driver.find_elements(By.CLASS_NAME, "animal-image")
                if not containers:
                    containers = driver.find_elements(By.CLASS_NAME, "pet-image")
                if not containers:
                    containers = driver.find_elements(By.CLASS_NAME, "image-container")
                
                print(f"Found {len(containers)} potential image containers")
                
                # Look for images in these containers
                for container in containers:
                    container_images = container.find_elements(By.TAG_NAME, "img")
                    if container_images:
                        images.extend(container_images)
                
                print(f"Found {len(images)} images in containers")
            except Exception as e:
                print(f"Method 3 failed: {str(e)}")
        
        # Extract image URLs
        image_urls = []
        for img in images:
            try:
                src = img.get_attribute('src')
                if src:
                    print(f"Found image URL: {src}")
                    image_urls.append(src)
            except Exception as e:
                print(f"Error getting image source: {str(e)}")
        
        print(f"\nTotal images found: {len(image_urls)}")
        return image_urls
    
    except Exception as e:
        print(f"Error scraping images for animal {animal_id}: {str(e)}")
        print("Current URL:", driver.current_url)
        print("Page source:", driver.page_source[:1000])
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
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape images from PetPoint for given animal IDs')
    parser.add_argument('--animal-id', help='Single animal ID to process')
    parser.add_argument('--input-file', help='Text file containing animal IDs (one per line)')
    parser.add_argument('--output-dir', default='animal_images', help='Directory to save images (default: animal_images)')
    args = parser.parse_args()

    # Login credentials
    SHELTER_ID = "USNY9"
    USERNAME = "zaks"
    PASSWORD = "Gillian666!"
    
    # Get animal IDs to process
    animal_ids = []
    if args.animal_id:
        animal_ids.append(args.animal_id)
    elif args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                animal_ids = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: Input file '{args.input_file}' not found.")
            return
    else:
        # If no arguments provided, ask for input
        print("Enter animal IDs (one per line, press Enter twice to finish):")
        while True:
            animal_id = input().strip()
            if not animal_id:
                break
            animal_ids.append(animal_id)
    
    if not animal_ids:
        print("No animal IDs provided. Exiting.")
        return

    # Setup driver and login
    driver = setup_driver()
    try:
        if login_to_petpoint(driver, SHELTER_ID, USERNAME, PASSWORD):
            print("Successfully logged in.")
            
            # Process each animal ID
            for animal_id in animal_ids:
                print(f"\nProcessing animal {animal_id}...")
                image_urls = get_animal_images(driver, animal_id)
                
                if image_urls:
                    print(f"Found {len(image_urls)} images")
                    download_images(image_urls, args.output_dir, animal_id)
                else:
                    print("No images found")
        else:
            print("Failed to log in. Please check your credentials.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 