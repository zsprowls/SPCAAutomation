#!/usr/bin/env python3

import pandas as pd
import os

def test_data_loading():
    """Test which data files are being loaded and their contents"""
    
    # Test AnimalInventory.csv loading
    possible_paths = [
        "../__Load Files Go Here__/AnimalInventory.csv",  # Local development (prioritized)
        "FosterDash/data/AnimalInventory.csv",  # Streamlit Cloud
        "data/AnimalInventory.csv",  # Streamlit Cloud (alternative)
        "AnimalInventory.csv"  # Current directory
    ]
    
    print("Testing AnimalInventory.csv loading:")
    animal_inventory_path = None
    for path in possible_paths:
        if os.path.exists(path):
            animal_inventory_path = path
            print(f"✅ Found: {path}")
            break
        else:
            print(f"❌ Not found: {path}")
    
    if animal_inventory_path:
        try:
            animal_inventory = pd.read_csv(animal_inventory_path, encoding='utf-8', skiprows=3)
            print(f"✅ Successfully loaded AnimalInventory.csv ({len(animal_inventory)} records)")
            
            # Count Hold - Foster animals
            hold_foster = animal_inventory[animal_inventory['Stage'].str.contains('Hold - Foster', na=False)]
            hold_safe = animal_inventory[animal_inventory['Stage'].str.contains('Hold - SAFE Foster|Hold – SAFE Foster', na=False)]
            hold_safe_em = animal_inventory[animal_inventory['Stage'].str.contains('Hold – SAFE Foster', na=False)]
            hold_cruelty = animal_inventory[animal_inventory['Stage'].str.contains('Hold - Cruelty Foster', na=False)]
            
            print(f"Hold - Foster: {len(hold_foster)}")
            print(f"Hold - SAFE Foster: {len(hold_safe)}")
            print(f"Hold – SAFE Foster (em dash): {len(hold_safe_em)}")
            print(f"Hold - Cruelty Foster: {len(hold_cruelty)}")
            print(f"Total Hold Foster variants: {len(hold_foster) + len(hold_safe) + len(hold_safe_em) + len(hold_cruelty)}")
            
            # Show first few Hold - Foster animals
            if len(hold_foster) > 0:
                print("\nFirst 5 Hold - Foster animals:")
                print(hold_foster[['AnimalNumber', 'AnimalName', 'Stage']].head())
                
        except Exception as e:
            print(f"❌ Error loading AnimalInventory.csv: {e}")
    else:
        print("❌ No AnimalInventory.csv found!")
    
    print("\n" + "="*50 + "\n")
    
    # Test FosterCurrent.csv loading
    foster_possible_paths = [
        "../__Load Files Go Here__/FosterCurrent.csv",  # Local development (prioritized)
        "FosterDash/data/FosterCurrent.csv",  # Streamlit Cloud
        "data/FosterCurrent.csv",  # Streamlit Cloud (alternative)
        "FosterCurrent.csv"  # Current directory
    ]
    
    print("Testing FosterCurrent.csv loading:")
    foster_current_path = None
    for path in foster_possible_paths:
        if os.path.exists(path):
            foster_current_path = path
            print(f"✅ Found: {path}")
            break
        else:
            print(f"❌ Not found: {path}")
    
    if foster_current_path:
        try:
            foster_current = pd.read_csv(foster_current_path, encoding='utf-8', skiprows=6)
            print(f"✅ Successfully loaded FosterCurrent.csv ({len(foster_current)} records)")
        except Exception as e:
            print(f"❌ Error loading FosterCurrent.csv: {e}")
    else:
        print("❌ No FosterCurrent.csv found!")
    
    print("\n" + "="*50 + "\n")
    
    # Test Hold - Foster Stage Date.csv loading
    hold_possible_paths = [
        "../__Load Files Go Here__/Hold - Foster Stage Date.csv",  # Local development (prioritized)
        "FosterDash/data/Hold - Foster Stage Date.csv",  # Streamlit Cloud
        "data/Hold - Foster Stage Date.csv",  # Streamlit Cloud (alternative)
        "Hold - Foster Stage Date.csv"  # Current directory
    ]
    
    print("Testing Hold - Foster Stage Date.csv loading:")
    hold_foster_path = None
    for path in hold_possible_paths:
        if os.path.exists(path):
            hold_foster_path = path
            print(f"✅ Found: {path}")
            break
        else:
            print(f"❌ Not found: {path}")
    
    if hold_foster_path:
        try:
            hold_foster_data = pd.read_csv(hold_foster_path, encoding='utf-8', skiprows=2)
            print(f"✅ Successfully loaded Hold - Foster Stage Date.csv ({len(hold_foster_data)} records)")
        except Exception as e:
            print(f"❌ Error loading Hold - Foster Stage Date.csv: {e}")
    else:
        print("❌ No Hold - Foster Stage Date.csv found!")

if __name__ == "__main__":
    test_data_loading() 