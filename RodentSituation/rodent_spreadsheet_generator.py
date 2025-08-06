import pandas as pd
import os
from datetime import datetime
from pathlib import Path

def load_data_files():
    """Load all required data files"""
    
    # Define possible file paths for different environments
    base_paths = [
        '__Load Files Go Here__',  # Primary location for data files (from repo root)
        'RodentSituation',  # Current subdirectory (for RodentIntake.csv)
        '.',  # Current directory
        '..',  # Parent directory
        '../__Load Files Go Here__',  # Local development fallback
        '/app/__Load Files Go Here__',  # Streamlit Cloud with data files
        '/app',  # Streamlit Cloud default
        '/tmp',  # Alternative Streamlit Cloud path
    ]
    
    print("🔍 Loading data files...")
    print(f"Current working directory: {os.getcwd()}")
    
    # Find the data directory
    data_dir_found = None
    for base_path in base_paths:
        try:
            if os.path.exists(base_path):
                print(f"✅ Found directory: {base_path}")
                if os.path.exists(f"{base_path}/AnimalInventory.csv"):
                    data_dir_found = base_path
                    print(f"✅ Found data directory: {base_path}")
                    break
        except Exception as e:
            continue
    
    if data_dir_found is None:
        print("❌ Could not find data directory with AnimalInventory.csv")
        print("Available directories checked:")
        for base_path in base_paths:
            print(f"  - {base_path}")
        return None, None, None
    
    # Load RodentIntake.csv
    rodent_intake = None
    rodent_paths = [
        "RodentIntake.csv",  # Current directory
        "RodentSituation/RodentIntake.csv",  # From repo root
        f"{data_dir_found}/RodentIntake.csv"  # From data directory
    ]
    
    for file_path in rodent_paths:
        try:
            if os.path.exists(file_path):
                rodent_intake = pd.read_csv(file_path)
                print(f"✅ Loaded {len(rodent_intake)} rodents from {file_path}")
                break
        except Exception as e:
            continue
    
    if rodent_intake is None:
        print("❌ Could not load RodentIntake.csv from any location")
        print("Tried paths:")
        for path in rodent_paths:
            print(f"  - {path}")
        return None, None, None
    
    # Load AnimalInventory.csv
    inventory_data = None
    try:
        file_path = f"{data_dir_found}/AnimalInventory.csv"
        if os.path.exists(file_path):
            inventory = pd.read_csv(file_path, skiprows=3)
            # Extract relevant columns
            inventory_data = inventory[['AnimalNumber', 'Sex', 'Stage', 'Location', 'SubLocation', 'SpayedNeutered']].copy()
            inventory_data = inventory_data.dropna(subset=['AnimalNumber'])
            print(f"✅ Loaded {len(inventory_data)} inventory records from {file_path}")
    except Exception as e:
        print(f"⚠️ Could not load AnimalInventory.csv: {e}")
    
    if inventory_data is None:
        print("⚠️ Could not load AnimalInventory.csv, using empty dataset")
        inventory_data = pd.DataFrame(columns=['AnimalNumber', 'Sex', 'Stage', 'Location', 'SubLocation', 'SpayedNeutered'])
    
    # Load FosterCurrent.csv
    foster_data = None
    try:
        file_path = f"{data_dir_found}/FosterCurrent.csv"
        if os.path.exists(file_path):
            foster_current = pd.read_csv(file_path, skiprows=6)
            # Extract relevant columns
            foster_data = foster_current[['textbox9', 'textbox10', 'textbox11']].copy()
            foster_data.columns = ['AnimalNumber', 'FosterPID', 'FosterName']
            foster_data = foster_data.dropna(subset=['AnimalNumber'])
            print(f"✅ Loaded {len(foster_data)} foster records from {file_path}")
    except Exception as e:
        print(f"⚠️ Could not load FosterCurrent.csv: {e}")
    
    if foster_data is None:
        print("⚠️ Could not load FosterCurrent.csv, using empty dataset")
        foster_data = pd.DataFrame(columns=['AnimalNumber', 'FosterPID', 'FosterName'])
    
    return rodent_intake, inventory_data, foster_data

def merge_data(rodent_intake, inventory_data, foster_data):
    """Merge all data sources into a comprehensive dataset"""
    
    print("🔄 Merging data...")
    
    # Start with rodent intake data
    merged = rodent_intake.copy()
    
    # Add inventory information
    merged = merged.merge(inventory_data, on='AnimalNumber', how='left')
    
    # Add foster information
    merged = merged.merge(foster_data, on='AnimalNumber', how='left')
    
    # Fill missing values for animals not in inventory
    merged['Stage'] = merged['Stage'].fillna('Released')
    merged['Location'] = merged['Location'].fillna('Released')
    merged['SubLocation'] = merged['SubLocation'].fillna('Released')
    merged['Sex'] = merged['Sex'].fillna(merged['Gender'])
    merged['SpayedNeutered'] = merged['SpayedNeutered'].fillna('Unknown')
    
    # Clean up foster information
    merged['FosterPID'] = merged['FosterPID'].fillna('Not in Foster')
    merged['FosterName'] = merged['FosterName'].fillna('Not in Foster')
    
    print(f"✅ Merged data complete: {len(merged)} total records")
    
    return merged

def generate_spreadsheet(merged_data):
    """Generate the final spreadsheet"""
    
    print("📊 Generating spreadsheet...")
    
    # Select and reorder columns for the final output
    final_columns = [
        'AnimalNumber',
        'AnimalName', 
        'Species',
        'Gender',
        'Color',
        'Sex',
        'Stage',
        'Location',
        'SubLocation',
        'SpayedNeutered',
        'FosterPID',
        'FosterName'
    ]
    
    # Create the final dataset
    final_data = merged_data[final_columns].copy()
    
    # Rename columns for clarity
    column_mapping = {
        'AnimalNumber': 'Animal ID',
        'AnimalName': 'Animal Name',
        'Species': 'Species',
        'Gender': 'Gender',
        'Color': 'Color',
        'Sex': 'Sex',
        'Stage': 'Status',
        'Location': 'Location',
        'SubLocation': 'Sub Location',
        'SpayedNeutered': 'Spayed/Neutered',
        'FosterPID': 'Foster PID',
        'FosterName': 'Foster Name'
    }
    
    final_data = final_data.rename(columns=column_mapping)
    
    # Sort by Location and Sub Location for better organization
    final_data = final_data.sort_values(['Location', 'Sub Location', 'Animal ID'])
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Rodent_Status_Report_{timestamp}.xlsx"
    
    # Save to Excel with formatting
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        final_data.to_excel(writer, sheet_name='Rodent Status', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Rodent Status']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Spreadsheet generated: {filename}")
    print(f"📋 Total records: {len(final_data)}")
    
    # Print summary statistics
    print("\n📊 Summary Statistics:")
    print(f"  - Total rodents: {len(final_data)}")
    
    # Status breakdown
    status_counts = final_data['Status'].value_counts()
    print("  - Status breakdown:")
    for status, count in status_counts.items():
        print(f"    * {status}: {count}")
    
    # Foster breakdown
    foster_counts = final_data['Foster Name'].value_counts()
    foster_count = len(foster_counts[foster_counts.index != 'Not in Foster'])
    print(f"  - In foster care: {foster_count}")
    
    return filename

def main():
    """Main function to generate the rodent status spreadsheet"""
    
    print("🐹 Rodent Status Spreadsheet Generator")
    print("=" * 50)
    
    # Load data files
    rodent_intake, inventory_data, foster_data = load_data_files()
    
    if rodent_intake is None:
        print("❌ Failed to load required data files. Exiting.")
        return
    
    # Merge data
    merged_data = merge_data(rodent_intake, inventory_data, foster_data)
    
    # Generate spreadsheet
    filename = generate_spreadsheet(merged_data)
    
    print("\n🎉 Process complete!")
    print(f"📁 File saved as: {filename}")
    print("=" * 50)

if __name__ == "__main__":
    main() 