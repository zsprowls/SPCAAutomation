import pandas as pd
from pathlib import Path

# Get the directory where the script is located
script_dir = Path(__file__).parent.absolute()
# Get the parent directory (SPCAAutomation)
parent_dir = script_dir.parent
# Get the path to the files directory
files_dir = parent_dir / '__Load Files Go Here__'

# Load the HeadShotsNeeded.csv file
headshots_path = files_dir / 'HeadShotsNeeded.csv'

print("=== Photo Flagging Debug Tool ===\n")

if headshots_path.exists():
    try:
        headshots_df = pd.read_csv(headshots_path, skiprows=3)
        if 'AnimalNumber' in headshots_df.columns:
            headshots_needed = set(headshots_df['AnimalNumber'].dropna().astype(str))
            print(f"✅ Loaded {len(headshots_needed)} animals needing photos")
            print("\nAnimals currently flagged as needing photos:")
            for animal_num in sorted(headshots_needed):
                # Find the animal details in the dataframe
                animal_row = headshots_df[headshots_df['AnimalNumber'] == animal_num]
                if not animal_row.empty:
                    name = animal_row.iloc[0].get('AnimalName', 'Unknown')
                    location = animal_row.iloc[0].get('Location_1', 'Unknown')
                    print(f"  {animal_num} - {name} ({location})")
                else:
                    print(f"  {animal_num} - Details not found")
        else:
            print("❌ AnimalNumber column not found in HeadShotsNeeded.csv")
    except Exception as e:
        print(f"❌ Could not load HeadShotsNeeded.csv: {e}")
else:
    print("❌ HeadShotsNeeded.csv not found")

# Test specific animal numbers
test_animals = ['58994375', 'A0058994375']
print(f"\n=== Testing specific animal numbers ===")
for test_animal in test_animals:
    if test_animal in headshots_needed:
        print(f"❌ {test_animal} is STILL flagged as needing a photo")
    else:
        print(f"✅ {test_animal} is NOT flagged as needing a photo")

print(f"\n=== Summary ===")
print(f"Total animals flagged for photos: {len(headshots_needed)}")
if headshots_needed:
    print("First 5 animals flagged:")
    for i, animal in enumerate(sorted(headshots_needed)[:5]):
        print(f"  {i+1}. {animal}")
else:
    print("No animals currently flagged for photos") 