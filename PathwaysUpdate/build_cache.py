#!/usr/bin/env python3
"""
Standalone script to build the image cache for the Pathways for Care Viewer.
This can be run independently to pre-populate the cache.
"""

import os
import sys
import time
import json
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

# Import credentials from config.py
try:
    from config import PETPOINT_SHELTER_ID, PETPOINT_USERNAME, PETPOINT_PASSWORD
except ImportError:
    print("Error: config.py with PetPoint credentials is missing.")
    sys.exit(1)

# Use absolute paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SCRIPT_DIR, "animal_images_cache.json")
INVENTORY_CSV = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '__Load Files Go Here__', 'AnimalInventory.csv'))
PATHWAYS_CSV = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '__Load Files Go Here__', 'Pathways for Care.csv'))

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
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
    return driver

def login_to_petpoint(driver, shelter_id, username, password):
    try:
        driver.get("https://sms.petpoint.com/sms3/forms/signinout.aspx")
        time.sleep(5)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
        shelter_id_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "LoginShelterId"))
        )
        shelter_id_input.clear()
        shelter_id_input.send_keys(shelter_id)
        time.sleep(2)
        try:
            continue_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            continue_button.click()
        except Exception:
            shelter_id_input.send_keys(Keys.RETURN)
        time.sleep(5)
        if iframes:
            driver.switch_to.default_content()
            driver.switch_to.frame(iframes[0])
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "LoginUsername"))
        )
        username_input.clear()
        username_input.send_keys(username)
        time.sleep(2)
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "LoginPassword"))
        )
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(2)
        try:
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]") )
            )
            login_button.click()
        except Exception:
            password_input.send_keys(Keys.RETURN)
        time.sleep(5)
        if iframes:
            driver.switch_to.default_content()
        current_url = driver.current_url.lower()
        if "signinout.aspx" in current_url:
            print("Login failed - still on login page")
            return False
        return True
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return False

def get_animal_images(driver, animal_id):
    if len(animal_id) > 8:
        animal_id = animal_id[-8:]
    url = f"https://sms.petpoint.com/sms3/enhanced/animal/{animal_id}"
    try:
        driver.get(url)
        time.sleep(5)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        try:
            overlay = driver.find_element(By.CLASS_NAME, "k-overlay")
            if overlay:
                ActionChains(driver).move_by_offset(0, 0).click().perform()
                time.sleep(2)
        except:
            pass
        try:
            photo_tab = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@id='AnimalImageGalleryTabLink']"))
            )
            try:
                photo_tab.click()
            except:
                driver.execute_script("arguments[0].click();", photo_tab)
            time.sleep(3)
            image_urls = []
            try:
                gallery_images = driver.find_elements(By.CSS_SELECTOR, "#ImageGallery img")
                for img in gallery_images:
                    src = img.get_attribute('src')
                    if src:
                        image_urls.append(src)
            except Exception:
                pass
            if not image_urls:
                try:
                    tab_images = driver.find_elements(By.CSS_SELECTOR, "#ImageGallery .tab-content img")
                    for img in tab_images:
                        src = img.get_attribute('src')
                        if src:
                            image_urls.append(src)
                except Exception:
                    pass
            if not image_urls:
                try:
                    class_images = driver.find_elements(By.CSS_SELECTOR, ".animal-image, .pet-image, .gallery-image")
                    for img in class_images:
                        src = img.get_attribute('src')
                        if src:
                            image_urls.append(src)
                except Exception:
                    pass
            return image_urls
        except Exception:
            return []
    except Exception:
        return []

def main():
    print("=" * 60)
    print("Pathways for Care - Image Cache Builder (Headless)")
    print("=" * 60)
    if not os.path.exists(PATHWAYS_CSV):
        print(f"Error: {PATHWAYS_CSV} not found.")
        return
    df = pd.read_csv(PATHWAYS_CSV)
    if 'AID' not in df.columns:
        print("Error: 'AID' column not found in Pathways for Care.csv.")
        return
    animal_ids = df['AID'].astype(str).unique()
    print(f"Found {len(animal_ids)} unique animal IDs (AID from Pathways for Care.csv).")
    cache = {}
    driver = setup_driver()
    try:
        if not login_to_petpoint(driver, PETPOINT_SHELTER_ID, PETPOINT_USERNAME, PETPOINT_PASSWORD):
            print("Failed to log in to PetPoint. Exiting.")
            return
        for idx, animal_id in enumerate(animal_ids, 1):
            print(f"[{idx}/{len(animal_ids)}] Processing animal {animal_id}...")
            image_urls = get_animal_images(driver, animal_id)
            if image_urls:
                print(f"  Found {len(image_urls)} images.")
                cache[animal_id] = image_urls
            else:
                print("  No images found.")
            # Optional: Save progress every 20 animals
            if idx % 20 == 0:
                with open(CACHE_FILE, 'w') as f:
                    json.dump(cache, f, indent=2)
                print(f"  Progress saved after {idx} animals.")
        # Final save
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
        print(f"Image cache saved to {CACHE_FILE}.")
    finally:
        driver.quit()
        print("Driver closed.")

if __name__ == "__main__":
    main() 