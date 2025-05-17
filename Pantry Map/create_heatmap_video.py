from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from moviepy.editor import ImageSequenceClip
import subprocess
from flask import Flask, jsonify
import threading
import webbrowser
import json

app = Flask(__name__)

# Global variable to store the data
pantry_data = None

@app.route('/data')
def get_data():
    return jsonify(pantry_data)

def load_data():
    global pantry_data
    with open('processed_pantry_data.json', 'r') as f:
        pantry_data = json.load(f)

def create_heatmap_video():
    # Load the data
    load_data()
    
    # Start Flask server in a separate thread
    server_thread = threading.Thread(target=lambda: app.run(port=5000))
    server_thread.daemon = True
    server_thread.start()
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--window-size=1920,1080')  # Set window size
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Open the map page
        driver.get('http://localhost:5000')
        
        # Wait for the map to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'map'))
        )
        
        # Switch to heatmap view
        heatmap_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Heat Map')]")
        heatmap_button.click()
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        # Get the date slider
        date_slider = driver.find_element(By.ID, 'dateSlider')
        
        # Take screenshots at different dates
        frames = []
        for i in range(0, 101, 2):  # Step by 2 for smoother animation
            # Update slider value
            driver.execute_script(f"arguments[0].value = {i}; arguments[0].dispatchEvent(new Event('input'));", date_slider)
            time.sleep(0.5)  # Wait for map to update
            
            # Take screenshot
            screenshot_path = f'screenshots/frame_{i:03d}.png'
            driver.save_screenshot(screenshot_path)
            frames.append(screenshot_path)
        
        # Create video from screenshots
        clip = ImageSequenceClip(frames, fps=10)
        clip.write_videofile('heatmap_animation.mp4', codec='libx264')
        
        print("Video created successfully: heatmap_animation.mp4")
        
    finally:
        driver.quit()
        
        # Clean up screenshots
        for frame in frames:
            os.remove(frame)
        os.rmdir('screenshots')

if __name__ == '__main__':
    create_heatmap_video() 