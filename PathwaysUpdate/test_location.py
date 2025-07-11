#!/usr/bin/env python3
"""
Test script to verify location data loading from AnimalInventory.csv
"""

import pandas as pd
import os

def test_location_loading():
    # Load Pathways for Care data
    pathways_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    df = pd.read_csv(pathways_path)
    
    # Load Animal Inventory data for current location
    inventory_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'AnimalInventory.csv')
    
    try:
        # The AnimalInventory.csv has a complex structure with multiple header rows
        # We need to skip the first 2 rows to get to the actual data
        inventory_df = pd.read_csv(inventory_path, skiprows=2)
        print(f"Loaded Animal Inventory with {len(inventory_df)} records")
        
        # Find the AID column in inventory
        aid_columns = ['AnimalNumber', 'AID', 'Animal ID', 'AnimalID', 'ID', 'id']
        inventory_aid_col = None
        for col in aid_columns:
            if col in inventory_df.columns:
                inventory_aid_col = col
                break
        
        if inventory_aid_col:
            print(f"Found AID column in inventory: {inventory_aid_col}")
            
            # Find the location and sublocation columns in inventory
            location_columns = ['Location', 'Current Location', 'Location ', 'CurrentLocation']
            sublocation_columns = ['SubLocation', 'Sub Location', 'SubLocation ', 'Sub-Location']
            
            inventory_location_col = None
            inventory_sublocation_col = None
            
            for col in location_columns:
                if col in inventory_df.columns:
                    inventory_location_col = col
                    break
            
            for col in sublocation_columns:
                if col in inventory_df.columns:
                    inventory_sublocation_col = col
                    break
            
            print(f"Found location column: {inventory_location_col}")
            print(f"Found sublocation column: {inventory_sublocation_col}")
            
            if inventory_location_col:
                # Create a mapping from AID to current location (with sublocation if available)
                location_mapping = {}
                for idx, row in inventory_df.iterrows():
                    full_aid = str(row[inventory_aid_col]).strip()
                    
                    # Extract numeric part from full AID (e.g., "A0058757250" -> "58757250")
                    if full_aid.startswith('A00'):
                        aid = full_aid[3:]  # Remove "A00" prefix
                    else:
                        aid = full_aid  # Keep as is if not in expected format
                    
                    location = str(row[inventory_location_col]).strip() if pd.notna(row[inventory_location_col]) else ''
                    
                    # Add sublocation if available
                    if inventory_sublocation_col and pd.notna(row[inventory_sublocation_col]):
                        sublocation = str(row[inventory_sublocation_col]).strip()
                        if sublocation and location:
                            location = f"{location} {sublocation}"
                        elif sublocation:
                            location = sublocation
                    
                    location_mapping[aid] = location
                
                print(f"Created location mapping for {len(location_mapping)} animals")
                
                # Test with a few sample animals from Pathways data
                sample_aids = df['AID'].head(5).tolist()
                print("\nTesting location mapping with sample animals:")
                for aid in sample_aids:
                    aid_str = str(aid).strip()
                    if aid_str in location_mapping:
                        print(f"  AID {aid_str}: {location_mapping[aid_str]}")
                    else:
                        print(f"  AID {aid_str}: Not found in inventory")
                
                # Update the Pathways data with current locations
                df['Location '] = df['AID'].astype(str).str.strip().map(location_mapping).fillna(df['Location '])
                print(f"\nUpdated locations for {len(location_mapping)} animals from Animal Inventory")
                
                # Show some examples
                print("\nSample updated locations:")
                for i, row in df.head(5).iterrows():
                    print(f"  {row['Name']} (AID: {row['AID']}): {row['Location ']}")
                
            else:
                print("Warning: No location column found in Animal Inventory")
        else:
            print("Warning: No AID column found in Animal Inventory")
            
    except Exception as e:
        print(f"Warning: Could not load Animal Inventory data: {e}")
        print("Using location data from Pathways for Care only")

if __name__ == "__main__":
    test_location_loading() 