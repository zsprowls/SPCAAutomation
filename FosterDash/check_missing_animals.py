import pandas as pd
import os

def load_data():
    """Load the data files using the same logic as the dashboard"""
    try:
        # Load AnimalInventory.csv
        animal_inventory_path = "../__Load Files Go Here__/AnimalInventory.csv"
        animal_inventory = pd.read_csv(animal_inventory_path, encoding='utf-8', skiprows=3)
        print(f"✅ Loaded AnimalInventory.csv ({len(animal_inventory)} records)")
        
        # Load FosterCurrent.csv
        foster_current_path = "../__Load Files Go Here__/FosterCurrent.csv"
        foster_current = pd.read_csv(foster_current_path, encoding='utf-8', skiprows=6)
        print(f"✅ Loaded FosterCurrent.csv ({len(foster_current)} records)")
        
        # Load Hold - Foster Stage Date.csv
        hold_foster_path = "../__Load Files Go Here__/Hold - Foster Stage Date.csv"
        hold_foster_data = pd.read_csv(hold_foster_path, encoding='utf-8', skiprows=2)
        print(f"✅ Loaded Hold - Foster Stage Date.csv ({len(hold_foster_data)} records)")
        
        return animal_inventory, foster_current, hold_foster_data
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return None, None, None

def classify_animals(animal_inventory, foster_current, hold_foster_data):
    """Classify animals into foster categories - same logic as dashboard"""
    if animal_inventory is None:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying original data
    df = animal_inventory.copy()
    
    # Initialize category column and foster info columns
    df['Foster_Category'] = 'Other'
    df['Foster_PID'] = ''
    df['Foster_Name'] = ''
    df['Hold_Foster_Date'] = ''
    df['Foster_Start_Date'] = ''
    
    # Get list of animals currently in foster and their foster info
    foster_animal_ids = set()
    foster_info = {}
    
    if not foster_current.empty:
        # Check for Animal ID column in foster data
        animal_id_col = None
        for col in ['textbox9', 'ARN', 'AnimalNumber']:
            if col in foster_current.columns:
                animal_id_col = col
                break
        
        if animal_id_col:
            # Create a mapping of animal ID to foster info
            for idx, row in foster_current.iterrows():
                animal_id = str(row[animal_id_col])
                
                # Get the stage to check if it's If The Fur Fits
                stage = str(row.get('Stage', '')).strip()
                
                # Only add to foster_animal_ids if it's NOT an If The Fur Fits stage
                if not any(fur_fits_stage in stage for fur_fits_stage in [
                    'In If the Fur Fits - Trial', 'In If the Fur Fits - Behavior', 'In If the Fur Fits - Medical'
                ]):
                    foster_animal_ids.add(animal_id)
                
                # Always add foster info for all animals
                foster_pid = str(row.get('textbox10', ''))
                foster_name = str(row.get('textbox11', ''))
                foster_start_date = str(row.get('StartStatusDate', ''))
                
                foster_info[animal_id] = {
                    'pid': foster_pid,
                    'name': foster_name,
                    'start_date': foster_start_date
                }
    
    # Create mapping of animal ID to Hold - Foster date
    hold_foster_dates = {}
    if not hold_foster_data.empty:
        if len(hold_foster_data.columns) >= 3:
            animal_id_col = hold_foster_data.columns[0]
            stage_col = hold_foster_data.columns[1]
            date_col = hold_foster_data.columns[2]
            
            for idx, row in hold_foster_data.iterrows():
                animal_id = str(row[animal_id_col])
                stage = str(row.get(stage_col, ''))
                stage_start_date = str(row.get(date_col, ''))
                
                if (stage_start_date and stage_start_date != 'nan' and 
                    any(hold_stage in stage for hold_stage in [
                        'Hold - Foster', 'Hold - Cruelty Foster', 'Hold - SAFE Foster', 'Hold – SAFE Foster'
                    ])):
                    hold_foster_dates[animal_id] = stage_start_date
    
    # Classify animals
    for idx, row in df.iterrows():
        animal_id = str(row.get('AnimalNumber', ''))
        stage = str(row.get('Stage', '')).strip()
        
        # Check if in If The Fur Fits program
        if any(fur_fits_stage in stage for fur_fits_stage in [
            'In If the Fur Fits - Trial', 'In If the Fur Fits - Behavior', 'In If the Fur Fits - Medical'
        ]):
            df.at[idx, 'Foster_Category'] = 'In If The Fur Fits'
            
            if animal_id in foster_info:
                df.at[idx, 'Foster_PID'] = foster_info[animal_id]['pid']
                df.at[idx, 'Foster_Name'] = foster_info[animal_id]['name']
                df.at[idx, 'Foster_Start_Date'] = foster_info[animal_id]['start_date']
        
        # Check if pending foster pickup
        elif 'Pending Foster Pickup' in stage:
            df.at[idx, 'Foster_Category'] = 'Pending Foster Pickup'
            
            if animal_id in foster_info:
                df.at[idx, 'Foster_PID'] = foster_info[animal_id]['pid']
                df.at[idx, 'Foster_Name'] = foster_info[animal_id]['name']
                df.at[idx, 'Foster_Start_Date'] = foster_info[animal_id]['start_date']
        
        # Check if in foster
        elif (animal_id in foster_animal_ids or 
              'In Foster' in stage or 
              'In SAFE Foster' in stage or 
              'In Cruelty Foster' in stage):
            df.at[idx, 'Foster_Category'] = 'In Foster'
            
            if animal_id in foster_info:
                df.at[idx, 'Foster_PID'] = foster_info[animal_id]['pid']
                df.at[idx, 'Foster_Name'] = foster_info[animal_id]['name']
                df.at[idx, 'Foster_Start_Date'] = foster_info[animal_id]['start_date']
        
        # Check if needs foster now
        elif any(need_stage in stage for need_stage in [
            'Hold - Foster', 'Hold - Cruelty Foster', 'Hold - SAFE Foster', 'Hold – SAFE Foster'
        ]):
            df.at[idx, 'Foster_Category'] = 'Needs Foster Now'
            
            if animal_id in hold_foster_dates:
                df.at[idx, 'Hold_Foster_Date'] = hold_foster_dates[animal_id]
        
        # Check if might need foster soon
        elif any(soon_stage in stage for soon_stage in [
            'Hold - Doc', 'Hold - Behavior', 'Hold - Behavior Mod.',
            'Hold - Surgery', 'Hold - Stray', 'Hold - Legal Notice', 'Evaluate'
        ]):
            df.at[idx, 'Foster_Category'] = 'Might Need Foster Soon'
    
    return df

def main():
    print("🔍 INVESTIGATING MISSING ANIMALS")
    print("="*50)
    
    # Load data
    animal_inventory, foster_current, hold_foster_data = load_data()
    
    if animal_inventory is None:
        print("❌ Could not load data")
        return
    
    # Find all animals with Hold - Foster stages in AnimalInventory
    hold_foster_stages = ['Hold - Foster', 'Hold - Cruelty Foster', 'Hold - SAFE Foster', 'Hold – SAFE Foster']
    hold_foster_animals = []
    
    for idx, row in animal_inventory.iterrows():
        stage = str(row.get('Stage', '')).strip()
        animal_id = str(row.get('AnimalNumber', ''))
        
        if any(hold_stage in stage for hold_stage in hold_foster_stages):
            hold_foster_animals.append({
                'animal_id': animal_id,
                'stage': stage,
                'name': str(row.get('AnimalName', ''))
            })
    
    print(f"\n📊 Total animals with Hold - Foster stages in AnimalInventory: {len(hold_foster_animals)}")
    
    # Classify animals using the same logic as the dashboard
    classified_data = classify_animals(animal_inventory, foster_current, hold_foster_data)
    
    # Count animals classified as "Needs Foster Now"
    needs_foster_now = classified_data[classified_data['Foster_Category'] == 'Needs Foster Now']
    print(f"📊 Animals classified as 'Needs Foster Now' in dashboard: {len(needs_foster_now)}")
    
    # Find the missing animals
    animal_ids_in_inventory = [animal['animal_id'] for animal in hold_foster_animals]
    animal_ids_classified = needs_foster_now['AnimalNumber'].astype(str).tolist()
    
    missing_animals = []
    for animal in hold_foster_animals:
        if animal['animal_id'] not in animal_ids_classified:
            missing_animals.append(animal)
    
    print(f"\n❌ Missing animals (should be 'Needs Foster Now' but aren't): {len(missing_animals)}")
    
    if missing_animals:
        print("\nMissing animals:")
        for animal in missing_animals:
            print(f"  - {animal['animal_id']} ({animal['name']}): {animal['stage']}")
            
            # Check what category it was classified as
            animal_row = classified_data[classified_data['AnimalNumber'] == animal['animal_id']]
            if not animal_row.empty:
                category = animal_row.iloc[0]['Foster_Category']
                print(f"    → Classified as: {category}")
    
    # Check for animals that are in FosterCurrent.csv with Hold - Foster stage
    if not foster_current.empty:
        stage_col = None
        for col in foster_current.columns:
            if 'stage' in col.lower():
                stage_col = col
                break
        
        if stage_col:
            foster_current_hold_foster = []
            for idx, row in foster_current.iterrows():
                stage = str(row.get(stage_col, '')).strip()
                
                if any(hold_stage in stage for hold_stage in hold_foster_stages):
                    animal_id_col = None
                    for col in ['textbox9', 'ARN', 'AnimalNumber']:
                        if col in foster_current.columns:
                            animal_id_col = col
                            break
                    
                    if animal_id_col:
                        animal_id = str(row.get(animal_id_col, ''))
                        foster_current_hold_foster.append({
                            'animal_id': animal_id,
                            'stage': stage
                        })
            
            print(f"\n📊 Animals in FosterCurrent.csv with Hold - Foster stages: {len(foster_current_hold_foster)}")
            for animal in foster_current_hold_foster:
                print(f"  - {animal['animal_id']}: {animal['stage']}")

if __name__ == "__main__":
    main() 