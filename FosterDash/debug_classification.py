import pandas as pd
import os

def debug_classification():
    """Debug the classification logic"""
    print("Debugging classification logic...")
    
    # Load AnimalInventory.csv
    animal_inventory_path = "../__Load Files Go Here__/AnimalInventory.csv"
    
    if os.path.exists(animal_inventory_path):
        animal_inventory = pd.read_csv(animal_inventory_path, encoding='utf-8', skiprows=3)
        print(f"✅ Loaded AnimalInventory.csv ({len(animal_inventory)} records)")
        
        # Check for If The Fur Fits animals in AnimalInventory
        fur_fits_animals = animal_inventory[
            animal_inventory['Stage'].str.contains('In If the Fur Fits', na=False)
        ]
        
        print(f"\nFound {len(fur_fits_animals)} If The Fur Fits animals in AnimalInventory:")
        for idx, row in fur_fits_animals.iterrows():
            animal_id = str(row.get('AnimalNumber', ''))
            stage = str(row.get('Stage', ''))
            print(f"  {animal_id}: {stage}")
        
        # Test the classification logic
        print("\nTesting classification logic:")
        for idx, row in fur_fits_animals.head().iterrows():
            animal_id = str(row.get('AnimalNumber', ''))
            stage = str(row.get('Stage', '')).strip()
            
            print(f"\nAnimal {animal_id}:")
            print(f"  Stage: {stage}")
            
            # Test If The Fur Fits check
            fur_fits_stages = ['In If the Fur Fits - Trial', 'In If the Fur Fits - Behavior', 'In If the Fur Fits - Medical']
            is_fur_fits = any(fur_fits_stage in stage for fur_fits_stage in fur_fits_stages)
            print(f"  Is If The Fur Fits: {is_fur_fits}")
            
            # Test foster check
            is_foster = 'In Foster' in stage or 'In SAFE Foster' in stage or 'In Cruelty Foster' in stage
            print(f"  Is Foster: {is_foster}")
            
    else:
        print(f"❌ AnimalInventory.csv not found at: {animal_inventory_path}")

if __name__ == "__main__":
    debug_classification() 