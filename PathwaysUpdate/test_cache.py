#!/usr/bin/env python3
"""
Test script to verify the image cache is working properly
"""

import os
import sys
from image_cache_manager import get_cache_manager, get_animal_images_cached, get_cache_stats

def test_cache():
    print("=== Testing Image Cache ===")
    
    # Get cache stats
    stats = get_cache_stats()
    print(f"Cache stats: {stats}")
    
    # Test a few animal IDs from the cache
    test_animal_ids = ["57230680", "57711591", "58089142", "99999999"]  # Last one doesn't exist
    
    for animal_id in test_animal_ids:
        print(f"\nTesting animal ID: {animal_id}")
        images = get_animal_images_cached(animal_id)
        if images:
            print(f"  ✓ Found {len(images)} images")
            print(f"  First image: {images[0]}")
        else:
            print(f"  ✗ No images found")
    
    # Test with some animal IDs from the CSV
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    if os.path.exists(csv_path):
        import pandas as pd
        df = pd.read_csv(csv_path)
        print(f"\n=== Testing with CSV data ===")
        print(f"CSV has {len(df)} animals")
        
        # Test first 5 animals
        for i, row in df.head(5).iterrows():
            animal_id = str(row['AID']).strip()
            print(f"\nAnimal {i+1}: {row['Name']} (ID: {animal_id})")
            images = get_animal_images_cached(animal_id)
            if images:
                print(f"  ✓ Found {len(images)} images")
            else:
                print(f"  ✗ No images found")

if __name__ == "__main__":
    test_cache() 