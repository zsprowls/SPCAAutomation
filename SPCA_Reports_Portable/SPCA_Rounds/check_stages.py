import pandas as pd
from pathlib import Path

# Get the directory where the script is located
script_dir = Path(__file__).parent.absolute()
# Get the parent directory (SPCAAutomation)
parent_dir = script_dir.parent
# Get the path to the files directory
files_dir = parent_dir / '__Load Files Go Here__'

# Define the STATUS_MAP from RoundsMapp.py
STATUS_MAP = {
    'Evaluate': 'EVAL',
    'Hold - Adopted!': 'ADPT',
    'Hold - Behavior': 'BEHA',
    'Hold - Behavior Foster': 'BFOS',
    'Hold - Behavior Mod.': 'BMOD',
    'Hold - Bite/Scratch': 'B/S',
    'Hold - Canisus Program': 'CANISUS',
    'Hold - Complaint': 'COMP',
    'Hold - Cruelty Foster': 'CF',
    'Hold - Dental': 'DENT',
    'Hold - Doc': 'DOC',
    'Hold - Evidence!': 'EVID',
    'Hold - For RTO': 'RTO',
    'Hold - Foster': 'FOST',
    'Hold - Legal Notice': 'LEGAL',
    'Hold - Media!': 'MEDIA',
    'Hold - Meet and Greet': 'M+G',
    'Hold - Offsite': 'OFFSITE',
    'Hold - Possible Adoption': 'PADPT',
    'Hold - Pups at the Pen!': 'PEN',
    'Hold - Rescue': 'RESC',
    'Hold – SAFE Foster': 'SAFE',
    'Hold - Special Event': 'SPEC',
    'Hold - Stray': 'STRAY',
    'Hold - Surgery': 'SX',
}

# Read the AnimalInventory.csv file
df = pd.read_csv(files_dir / 'AnimalInventory.csv', skiprows=3)

# Get unique stages from the CSV
csv_stages = set(df['Stage'].unique())

# Get stages from STATUS_MAP
map_stages = set(STATUS_MAP.keys())

# Find stages in CSV that aren't in STATUS_MAP
missing_stages = csv_stages - map_stages

print("\nStages in AnimalInventory.csv that aren't in STATUS_MAP:")
print("--------------------------------------------------------")
for stage in sorted(missing_stages):
    print(f"- {stage}")

print("\nTotal missing stages:", len(missing_stages)) 