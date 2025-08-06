#!/usr/bin/env python3
"""
Test script to verify the photo indicator functionality
"""

import pandas as pd
from pathlib import Path

# Test the photo indicator logic
def test_photo_indicator():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent.absolute()
    parent_dir = script_dir.parent
    files_dir = parent_dir / '__Load Files Go Here__'
    
    # Load the headshots data
    headshots_path = files_dir / 'HeadShotsNeeded.csv'
    
    if headshots_path.exists():
        try:
            headshots_df = pd.read_csv(headshots_path, skiprows=3)
            if 'AnimalNumber' in headshots_df.columns:
                headshots_needed = set(headshots_df['AnimalNumber'].dropna().astype(str))
                print(f"✅ Loaded {len(headshots_needed)} animals needing photos")
                print(f"Sample animals needing photos: {list(headshots_needed)[:5]}")
                return True
        except Exception as e:
            print(f"❌ Error loading HeadShotsNeeded.csv: {e}")
            return False
    else:
        print(f"❌ HeadShotsNeeded.csv not found at {headshots_path}")
        return False

if __name__ == "__main__":
    test_photo_indicator() 