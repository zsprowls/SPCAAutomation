#!/usr/bin/env python3
"""
Test script to verify Google Sheets update functionality
"""

import sys
import os

def test_update_functionality():
    """Test the update functionality"""
    print("=" * 60)
    print("Testing Google Sheets Update Functionality")
    print("=" * 60)
    
    try:
        from google_drive_manager import get_gdrive_manager
        
        # Get the manager
        manager = get_gdrive_manager(use_service_account=True)
        
        # Test reading data first
        print("\n📖 Testing data reading...")
        df = manager.read_from_sheets_with_api_key()
        if df is None:
            print("❌ Failed to read data from Google Sheets")
            return False
        
        print(f"✅ Successfully read {len(df)} records from Google Sheets")
        
        # Show first few records
        if len(df) > 0:
            print("\n📋 First few records:")
            # Show available columns
            print("Available columns:", list(df.columns))
            # Show first few records with available columns
            display_cols = ['AID']
            if 'AnimalName' in df.columns:
                display_cols.append('AnimalName')
            elif 'Name' in df.columns:
                display_cols.append('Name')
            if 'Stage' in df.columns:
                display_cols.append('Stage')
            
            print(df.head(3)[display_cols].to_string())
        
        # Test updating a record (use the first animal if available)
        if len(df) > 0:
            first_aid = df.iloc[0]['AID']
            print(f"\n🔄 Testing update for animal {first_aid}...")
            
            # Try to update the record
            success = manager.update_animal_record_with_api_key(
                aid=str(first_aid),
                foster_value="Yes",
                transfer_value="No", 
                communications_value="No",
                new_note="Test update from script"
            )
            
            if success:
                print("✅ Update test successful!")
                
                # Read data again to verify the change
                print("\n📖 Verifying update...")
                df_updated = manager.read_from_sheets_with_api_key()
                if df_updated is not None:
                    updated_row = df_updated[df_updated['AID'] == first_aid]
                    if len(updated_row) > 0:
                        print("✅ Update verified in Google Sheets!")
                        return True
                    else:
                        print("❌ Could not find updated record")
                        return False
                else:
                    print("❌ Failed to read updated data")
                    return False
            else:
                print("❌ Update test failed")
                return False
        else:
            print("❌ No data found to test with")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_update_functionality()
    if success:
        print("\n🎉 All tests passed! The update functionality should work in the Streamlit app.")
    else:
        print("\n❌ Tests failed. Please check the error messages above.") 