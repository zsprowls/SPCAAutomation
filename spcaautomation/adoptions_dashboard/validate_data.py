#!/usr/bin/env python3
"""
Data Validation Script for SPCA Adoptions Dashboard
Checks if all required data files are present and have the expected structure.
"""

import os
import pandas as pd
from datetime import datetime
from config import DATA_DIRECTORY, REQUIRED_DATA_FILES

def validate_data_files():
    """Validate that all required data files exist and are readable."""
    print("🔍 SPCA Dashboard Data Validation")
    print("=" * 50)
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIRECTORY):
        print(f"❌ Data directory not found: {DATA_DIRECTORY}")
        print("   Please ensure the '__Load Files Go Here__' folder exists")
        return False
    
    print(f"✅ Data directory found: {DATA_DIRECTORY}")
    
    # Check each required file
    all_files_valid = True
    
    for filename in REQUIRED_DATA_FILES:
        filepath = os.path.join(DATA_DIRECTORY, filename)
        print(f"\nChecking {filename}...")
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filename}")
            all_files_valid = False
            continue
        
        try:
            # Try to read the file
            if filename == 'AnimalInventory.csv':
                df = pd.read_csv(filepath, skiprows=3)
                expected_columns = ['AnimalID', 'AnimalType', 'Stage', 'Location']
            elif filename == 'AnimalOutcome.csv':
                df = pd.read_csv(filepath, skiprows=3)
                expected_columns = ['textbox16', 'Textbox50']  # Outcome type and date
            elif filename == 'AnimalIntake.csv':
                df = pd.read_csv(filepath, skiprows=3)
                expected_columns = ['AnimalID', 'AnimalType', 'IntakeDate']
            elif filename == 'FosterCurrent.csv':
                df = pd.read_csv(filepath, skiprows=3)
                expected_columns = ['AnimalID', 'AnimalType']
            else:
                df = pd.read_csv(filepath)
                expected_columns = []
            
            print(f"   📊 Rows: {len(df)}")
            print(f"   📋 Columns: {len(df.columns)}")
            
            # Check for expected columns (basic validation)
            missing_cols = [col for col in expected_columns if col not in df.columns]
            if missing_cols:
                print(f"   ⚠️  Missing expected columns: {missing_cols}")
                print(f"   📝 Available columns: {list(df.columns)}")
            else:
                print(f"   ✅ File structure looks good")
                
        except Exception as e:
            print(f"❌ Error reading {filename}: {str(e)}")
            all_files_valid = False
    
    print("\n" + "=" * 50)
    
    if all_files_valid:
        print("🎉 All data files validated successfully!")
        print("✅ Dashboard should work properly")
        
        # Additional data quality checks
        print("\n📈 Data Quality Summary:")
        try:
            inventory_df = pd.read_csv(os.path.join(DATA_DIRECTORY, 'AnimalInventory.csv'), skiprows=3)
            print(f"   • Total animals in system: {len(inventory_df)}")
            
            if 'AnimalType' in inventory_df.columns:
                animal_counts = inventory_df['AnimalType'].value_counts()
                for animal_type, count in animal_counts.items():
                    print(f"   • {animal_type}s: {count}")
            
            if 'Stage' in inventory_df.columns:
                stage_counts = inventory_df['Stage'].value_counts()
                print(f"   • Most common stage: {stage_counts.index[0]} ({stage_counts.iloc[0]} animals)")
                
        except Exception as e:
            print(f"   ⚠️  Could not generate summary: {str(e)}")
        
    else:
        print("❌ Data validation failed!")
        print("   Please check the missing/corrupted files above")
        print("   Ensure all CSV files are in the correct location")
        print("   and have been exported from your animal management system")
    
    return all_files_valid

def check_morning_email_integration():
    """Check if morning_email.py functions are accessible."""
    print("\n🔗 Morning Email Integration Check")
    print("=" * 50)
    
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'MorningEmail'))
        
        from morning_email import (
            get_stage_counts, get_occupancy_counts, get_adoptions_count,
            get_intake_count_detail, get_intake_summary, get_foster_count
        )
        
        print("✅ Successfully imported morning_email functions")
        print("✅ Dashboard integration should work")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import morning_email functions: {str(e)}")
        print("   Please ensure morning_email.py is in the MorningEmail directory")
        print("   and is accessible from the dashboard location")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Run all validation checks."""
    print(f"🕐 Validation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    data_valid = validate_data_files()
    integration_valid = check_morning_email_integration()
    
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY")
    print("=" * 50)
    
    if data_valid and integration_valid:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your dashboard is ready to run")
        print("\n🚀 Next steps:")
        print("   1. Run: ./run_dashboard.sh")
        print("   2. Open: http://localhost:8501")
        print("   3. Start monitoring your capacity!")
    else:
        print("❌ SOME CHECKS FAILED")
        print("   Please fix the issues above before running the dashboard")
        
        if not data_valid:
            print("   • Check data files and ensure they're properly exported")
        if not integration_valid:
            print("   • Verify morning_email.py location and accessibility")

if __name__ == "__main__":
    main()