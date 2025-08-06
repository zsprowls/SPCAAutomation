#!/usr/bin/env python3

import sys
import os
import pandas as pd
sys.path.append('.')

try:
    from streamlit_gdrive_app_new import load_data_from_multiple_sources
    
    print("Testing display logic for animal 58831524...")
    
    # Load app data
    df = load_data_from_multiple_sources()
    
    if df is not None:
        # Find animal 58831524
        animal = df[df['AID'] == '58831524']
        
        if len(animal) > 0:
            animal_data = animal.iloc[0]
            aid = animal_data['AID']
            
            print(f"Found animal {aid}")
            print(f"Image_URLs column exists: {'Image_URLs' in animal_data}")
            
            # Test the exact logic from the app
            if 'Image_URLs' in animal_data and pd.notna(animal_data['Image_URLs']) and str(animal_data['Image_URLs']).strip():
                print("✅ Image_URLs condition passed")
                image_urls = str(animal_data['Image_URLs']).split(',')
                image_urls = [url.strip() for url in image_urls if url.strip()]
                print(f"Processed image_urls: {image_urls}")
                print(f"Number of images: {len(image_urls)}")
                
                if image_urls:
                    print("✅ Would display images")
                    for i, url in enumerate(image_urls):
                        print(f"  Image {i+1}: {url}")
                else:
                    print("❌ No images after processing")
            else:
                print("❌ Image_URLs condition failed")
                print(f"  Image_URLs value: {repr(animal_data.get('Image_URLs', 'NOT_FOUND'))}")
                print(f"  pd.notna: {pd.notna(animal_data.get('Image_URLs', 'NOT_FOUND'))}")
                print(f"  str().strip(): {repr(str(animal_data.get('Image_URLs', 'NOT_FOUND')).strip())}")
        else:
            print("❌ Animal 58831524 not found in data")
    else:
        print("❌ Failed to load data")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 