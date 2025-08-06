import pandas as pd
import os

def load_data():
    """Load the data files"""
    base_paths = [
        "../__Load Files Go Here__",
        ".",
        "..",
        "/app",
        "/tmp"
    ]
    
    animal_inventory = None
    foster_current = None
    hold_foster_data = None
    
    # Try to load AnimalInventory.csv
    for base_path in base_paths:
        try:
            animal_inventory = pd.read_csv(os.path.join(base_path, "AnimalInventory.csv"))
            print(f"✅ Loaded AnimalInventory.csv from {base_path}")
            break
        except Exception as e:
            continue
    
    # Try to load FosterCurrent.csv
    for base_path in base_paths:
        try:
            foster_current = pd.read_csv(os.path.join(base_path, "FosterCurrent.csv"))
            print(f"✅ Loaded FosterCurrent.csv from {base_path}")
            break
        except Exception as e:
            continue
    
    # Try to load Hold - Foster data
    for base_path in base_paths:
        try:
            hold_foster_data = pd.read_csv(os.path.join(base_path, "Hold - Foster Stage Date.csv"))
            print(f"✅ Loaded Hold - Foster Stage Date.csv from {base_path}")
            break
        except Exception as e:
            continue
    
    return animal_inventory, foster_current, hold_foster_data

def analyze_counts():
    """Analyze the counts to find the discrepancy"""
    animal_inventory, foster_current, hold_foster_data = load_data()
    
    print("\n" + "="*50)
    print("ANALYSIS OF FOSTER COUNTS")
    print("="*50)
    
    # Count animals in AnimalInventory.csv with Hold - Foster stages
    if animal_inventory is not None:
        hold_foster_stages = [
            'Hold - Foster', 'Hold - Cruelty Foster', 'Hold - SAFE Foster'
        ]
        
        hold_foster_count = 0
        hold_foster_animals = []
        
        for idx, row in animal_inventory.iterrows():
            stage = str(row.get('Stage', '')).strip()
            animal_id = str(row.get('AnimalNumber', ''))
            
            if any(hold_stage in stage for hold_stage in hold_foster_stages):
                hold_foster_count += 1
                hold_foster_animals.append(animal_id)
        
        print(f"\n📊 Animals in AnimalInventory.csv with Hold - Foster stages: {hold_foster_count}")
        print("Animal IDs:", hold_foster_animals)
    
    # Count animals in FosterCurrent.csv with Hold - Foster stages
    if foster_current is not None:
        # Find the stage column
        stage_col = None
        for col in foster_current.columns:
            if 'stage' in col.lower():
                stage_col = col
                break
        
        if stage_col:
            hold_foster_in_foster_current = 0
            hold_foster_animals_fc = []
            
            for idx, row in foster_current.iterrows():
                stage = str(row.get(stage_col, '')).strip()
                
                if any(hold_stage in stage for hold_stage in hold_foster_stages):
                    hold_foster_in_foster_current += 1
                    # Try to get animal ID
                    animal_id_col = None
                    for col in ['textbox9', 'ARN', 'AnimalNumber']:
                        if col in foster_current.columns:
                            animal_id_col = col
                            break
                    
                    if animal_id_col:
                        animal_id = str(row.get(animal_id_col, ''))
                        hold_foster_animals_fc.append(animal_id)
            
            print(f"\n📊 Animals in FosterCurrent.csv with Hold - Foster stages: {hold_foster_in_foster_current}")
            print("Animal IDs:", hold_foster_animals_fc)
    
    # Check for overlap
    if animal_inventory is not None and foster_current is not None:
        print(f"\n🔍 Total unique animals that should be 'Needs Foster Now': {hold_foster_count + hold_foster_in_foster_current}")
        print(f"Expected count: 48")
        print(f"Streamlit app shows: 44")
        print(f"Missing: {48 - 44} animals")

if __name__ == "__main__":
    analyze_counts() 