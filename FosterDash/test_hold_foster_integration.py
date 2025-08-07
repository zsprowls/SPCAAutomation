import pandas as pd
import os

def test_hold_foster_integration():
    """Test the Hold - Foster date integration"""
    print("Testing Hold - Foster date integration...")
    
    # Test loading the Hold - Foster Stage Date.csv file
    hold_foster_path = "../__Load Files Go Here__/Hold - Foster Stage Date.csv"
    
    if os.path.exists(hold_foster_path):
        print(f"✅ Found Hold - Foster Stage Date.csv at: {hold_foster_path}")
        
        try:
            # Load the file with the same parameters as in the dashboard
            hold_foster_data = pd.read_csv(hold_foster_path, encoding='utf-8', skiprows=2)
            print(f"✅ Successfully loaded Hold - Foster Stage Date.csv ({len(hold_foster_data)} records)")
            
            # Check the columns
            print(f"Columns: {list(hold_foster_data.columns)}")
            
            # Show first few rows
            print("\nFirst 5 rows:")
            print(hold_foster_data.head())
            
            # Check for Animal # column and Stage Start Date column
            animal_id_col = None
            stage_col = None
            date_col = None
            
            # Handle generic column names from the CSV file
            if len(hold_foster_data.columns) >= 3:
                # The file has columns: Count, Count.1, Count.2
                # These correspond to: Animal #, Stage, Stage Start Date
                animal_id_col = hold_foster_data.columns[0]  # First column
                stage_col = hold_foster_data.columns[1]      # Second column
                date_col = hold_foster_data.columns[2]       # Third column
            else:
                # Try to find columns by name
                for col in ['Animal #', 'AnimalNumber', 'AnimalID']:
                    if col in hold_foster_data.columns:
                        animal_id_col = col
                        break
            
            if animal_id_col and stage_col and date_col:
                print(f"✅ Found columns: {animal_id_col}, {stage_col}, {date_col}")
                
                # Create mapping of animal ID to Hold - Foster date
                hold_foster_dates = {}
                for idx, row in hold_foster_data.iterrows():
                    animal_id = str(row[animal_id_col])
                    stage = str(row.get(stage_col, ''))
                    stage_start_date = str(row.get(date_col, ''))
                    
                    # Include if it's any Hold - Foster stage and has a valid date
                    if (stage_start_date and stage_start_date != 'nan' and 
                                            any(hold_stage in stage for hold_stage in [
                        'Hold - Foster', 'Hold - Cruelty Foster', 'Hold - SAFE Foster', 'Hold – SAFE Foster'
                    ])):
                        hold_foster_dates[animal_id] = stage_start_date
                
                print(f"✅ Created mapping with {len(hold_foster_dates)} Hold - Foster dates")
                
                # Show some examples
                print("\nSample Hold - Foster dates:")
                count = 0
                for animal_id, date in hold_foster_dates.items():
                    if count < 5:
                        # Get the stage for this animal
                        animal_row = hold_foster_data[hold_foster_data[animal_id_col] == animal_id]
                        if not animal_row.empty:
                            stage = str(animal_row.iloc[0].get(stage_col, ''))
                            print(f"  {animal_id}: {date} ({stage})")
                        else:
                            print(f"  {animal_id}: {date}")
                        count += 1
                    else:
                        break
                
            else:
                print("❌ Could not find required columns")
                print(f"Available columns: {list(hold_foster_data.columns)}")
                
        except Exception as e:
            print(f"❌ Error loading Hold - Foster Stage Date.csv: {str(e)}")
    else:
        print(f"❌ Hold - Foster Stage Date.csv not found at: {hold_foster_path}")
    
    # Test loading AnimalInventory.csv to see if we can match animals
    animal_inventory_path = "../__Load Files Go Here__/AnimalInventory.csv"
    
    if os.path.exists(animal_inventory_path):
        print(f"\n✅ Found AnimalInventory.csv at: {animal_inventory_path}")
        
        try:
            animal_inventory = pd.read_csv(animal_inventory_path, encoding='utf-8', skiprows=3)
            print(f"✅ Successfully loaded AnimalInventory.csv ({len(animal_inventory)} records)")
            
            # Check for animals with Hold - Foster stage
            hold_foster_animals = animal_inventory[animal_inventory['Stage'].str.contains('Hold - Foster|Hold - Cruelty Foster|Hold - SAFE Foster|Hold – SAFE Foster', na=False)]
            print(f"✅ Found {len(hold_foster_animals)} animals with Hold - Foster stages")
            
            if not hold_foster_animals.empty:
                print("\nSample animals with Hold - Foster stages:")
                for idx, row in hold_foster_animals.head().iterrows():
                    animal_id = str(row.get('AnimalNumber', ''))
                    stage = str(row.get('Stage', ''))
                    print(f"  {animal_id}: {stage}")
            
        except Exception as e:
            print(f"❌ Error loading AnimalInventory.csv: {str(e)}")
    else:
        print(f"❌ AnimalInventory.csv not found at: {animal_inventory_path}")

if __name__ == "__main__":
    test_hold_foster_integration() 