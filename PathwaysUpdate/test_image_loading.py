#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

try:
    from streamlit_gdrive_app_new import load_data_from_multiple_sources
    from image_cache_manager import get_cache_manager
    
    print("Testing image loading for animal 58831524...")
    
    # Test cache directly
    cache_manager = get_cache_manager()
    cache_images = cache_manager.get_animal_images('58831524')
    print(f"Cache images for 58831524: {cache_images}")
    
    # Test app data loading
    print("\nLoading app data...")
    df = load_data_from_multiple_sources()
    
    if df is not None:
        print(f"App data loaded: {len(df)} records")
        
        # Check if animal 58831524 is in the data
        animal = df[df['AID'] == '58831524']
        if len(animal) > 0:
            print(f"Animal 58831524 found in app data")
            print(f"Image_URLs: {animal['Image_URLs'].iloc[0]}")
            
            # Check if Image_URLs column exists and has data
            print(f"Image_URLs column exists: {'Image_URLs' in df.columns}")
            print(f"Sample Image_URLs: {df['Image_URLs'].head()}")
            
            # Check how many animals have images
            animals_with_images = df[df['Image_URLs'].notna() & (df['Image_URLs'] != '')]
            print(f"Animals with images: {len(animals_with_images)}")
            
        else:
            print("Animal 58831524 NOT found in app data")
            print(f"AID values in data: {df['AID'].unique()[:10]}")
    else:
        print("Failed to load app data")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 