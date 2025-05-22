import pandas as pd
import re
from datetime import datetime, timedelta

# Define the stage mappings
STAGE_MAPPINGS = {
    'In Foster': 'In Foster',
    'Hold - SAFE Foster': 'Hold SAFE Foster',
    'Hold - Foster': 'Hold Foster',
    'Hold - Cruelty Foster': 'Hold Cruelty Foster',
    'Hold - Behavior Foster': 'Hold Behavior Foster',
    'Hold - Surgery': 'Hold Surgery',
    'Hold - Doc': 'Hold Doc',
    'Hold - Behavior': 'Hold Behavior',
    'Hold - Dental': 'Hold Dental',
    'Hold - Behavior Mod.': 'Hold Behavior Mod.',
    'Hold - Complaint': 'Hold Complaint',
    'Hold - Stray': 'Hold Stray/Legal',
    'Hold - Legal Notice': 'Hold Stray/Legal'
}

# Define the order for the report
STAGE_ORDER = [
    'In Foster',
    'Hold SAFE Foster',
    'Hold Foster',
    'Hold Cruelty Foster',
    'Hold Behavior Foster',
    'Hold Surgery',
    'Hold Dental',
    'Hold Doc',
    'Hold Behavior',
    'Hold Behavior Mod.',
    'Hold Complaint',
    'Hold Stray/Legal'
]

def get_report_date_from_csv():
    # Read the second line of FosterCurrent.csv to get the report date
    with open('FosterCurrent.csv', 'r') as f:
        lines = f.readlines()
        if len(lines) >= 2:
            # Join the first three columns to reconstruct the date string
            parts = [p.strip().replace('"', '') for p in lines[1].split(',')[:3]]
            date_str = ', '.join(parts)
            # Example format: 'Monday, May 12, 2025'
            return datetime.strptime(date_str, '%A, %B %d, %Y')
        else:
            raise ValueError('Could not find report date in FosterCurrent.csv')

def get_previous_business_days_from_report_date(report_date):
    if report_date.weekday() == 0:  # Monday
        # Return Friday and Saturday
        friday = report_date - timedelta(days=3)
        saturday = report_date - timedelta(days=2)
        return [friday.strftime('%-m/%-d/%Y'), saturday.strftime('%-m/%-d/%Y')]
    else:
        # Return previous day
        yesterday = report_date - timedelta(days=1)
        return [yesterday.strftime('%-m/%-d/%Y')]

def get_fur_fits_count():
    # Read FosterCurrent.csv, skipping first 6 rows
    df_foster = pd.read_csv('FosterCurrent.csv', skiprows=6)
    
    # Get the report date from cell A2
    report_date = get_report_date_from_csv()
    check_dates = get_previous_business_days_from_report_date(report_date)
    
    # Convert StartStatusDate to datetime and normalize to remove time component
    df_foster['StartStatusDate'] = pd.to_datetime(df_foster['StartStatusDate']).dt.normalize()
    check_datetimes = [pd.to_datetime(date).normalize() for date in check_dates]
    
    # Count entries where Location is "If The Fur Fits" and StartStatusDate matches any check date
    fur_fits_count = len(df_foster[
        (df_foster['Location'] == 'If The Fur Fits') & 
        (df_foster['StartStatusDate'].isin(check_datetimes))
    ])
    
    return fur_fits_count

def get_foster_count():
    # Read FosterCurrent.csv, skipping first 6 rows
    foster_path = 'FosterCurrent.csv'
    df_foster = pd.read_csv(foster_path, skiprows=6)
    
    # Get the first value from textbox53
    total_text = df_foster['textbox53'].iloc[0]
    
    # Extract the number using regex
    match = re.search(r'Total Animals: (\d+)', total_text)
    if match:
        return int(match.group(1))
    return 0

def get_stage_counts():
    # Read the CSV file, skipping the first 3 rows
    inventory_path = 'AnimalInventory.csv'
    df = pd.read_csv(inventory_path, skiprows=3)
    
    # Map the stages using our defined mappings
    df['Mapped_Stage'] = df['Stage'].map(STAGE_MAPPINGS)
    
    # Count the animals in each mapped stage
    stage_counts = df['Mapped_Stage'].value_counts()
    
    # Create a dictionary with all stages initialized to 0
    final_counts = {stage: 0 for stage in STAGE_ORDER}
    
    # Update counts for stages that have animals
    for stage, count in stage_counts.items():
        if stage in final_counts:
            final_counts[stage] = count
    
    # Update In Foster count from FosterCurrent.csv
    final_counts['In Foster'] = get_foster_count()
            
    # Return counts in the specified order
    return {stage: final_counts[stage] for stage in STAGE_ORDER}

def get_occupancy_counts():
    # Read the CSV file, skipping first 3 rows
    df = pd.read_csv('AnimalInventory.csv', skiprows=3)
    
    # Convert DateOfBirth to datetime
    df['DateOfBirth'] = pd.to_datetime(df['DateOfBirth'])
    
    # Get the most recent date from the data to use as "today"
    today = pd.Timestamp.now().normalize()  # Use today's date without the time component
    
    # Calculate age in months - Fix calculation for very young animals
    df['AgeMonths'] = ((today - df['DateOfBirth']).dt.total_seconds() / (60 * 60 * 24 * 30.44))
    
    # Define offsite locations
    offsite_locations = ['Foster Home', 'If The Fur Fits', 'Offsite Adoptions']
    
    # Create location category
    df['LocationCategory'] = df['Location'].apply(
        lambda x: 'Foster/Offsite' if x in offsite_locations else 'Shelter'
    )
    
    # Categorize animals
    def get_category(row):
        animal_type = row['AnimalType'].strip()  # Remove any whitespace
        if animal_type not in ['Cat', 'Dog']:
            return 'Other'  # Bird, Livestock, Equine, and any other types
        elif animal_type == 'Cat':
            return 'Kitten' if row['AgeMonths'] < 6 else 'Cat'
        else:  # Must be Dog
            return 'Puppy' if row['AgeMonths'] < 6 else 'Dog'
    
    df['Category'] = df.apply(get_category, axis=1)
    
    # Create the counts
    categories = ['Cat', 'Dog', 'Kitten', 'Other', 'Puppy']
    counts = {
        'Species/Age': categories + ['TOTAL'],
        'Animals in Shelter': [],
        'Animals in Foster/Off-Site': []
    }
    
    # Get counts for each category
    for category in categories:
        shelter_count = len(df[(df['Category'] == category) & 
                             (df['LocationCategory'] == 'Shelter')])
        offsite_count = len(df[(df['Category'] == category) & 
                              (df['LocationCategory'] == 'Foster/Offsite')])
        
        counts['Animals in Shelter'].append(shelter_count)
        counts['Animals in Foster/Off-Site'].append(offsite_count)
    
    # Add totals
    counts['Animals in Shelter'].append(sum(counts['Animals in Shelter']))
    counts['Animals in Foster/Off-Site'].append(sum(counts['Animals in Foster/Off-Site']))
    
    return pd.DataFrame(counts)

def get_adoptions_count():
    # Read AnimalOutcomes.csv, skipping the first 3 rows to get to the header
    try:
        df_outcomes = pd.read_csv('AnimalOutcome.csv', skiprows=3)
    except FileNotFoundError:
        print("AnimalOutcomes.csv not found. Returning 0 adoptions.")
        return 0
    # Only keep debugging for textbox16
    print("\nAnimalOutcomes.csv columns:", df_outcomes.columns.tolist())
    if 'textbox16' in df_outcomes.columns:
        print("Unique values in textbox16:", df_outcomes['textbox16'].unique())
        adoptions_count = (df_outcomes['textbox16'] == 'Adoption').sum()
    else:
        print("Column 'textbox16' not found in AnimalOutcomes.csv!")
        adoptions_count = 0
    print(f"Found {adoptions_count} adoptions in AnimalOutcomes.csv")
    return adoptions_count

def export_to_excel():
    # Get all our data
    adoptions = get_adoptions_count()
    fur_fits = get_fur_fits_count()
    foster_holds = get_stage_counts()
    occupancy = get_occupancy_counts()
    
    # Create Excel writer object
    output_path = 'morning_report.xlsx'
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    workbook = writer.book
    
    # Create formats
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#D3D3D3'
    })
    
    normal_format = workbook.add_format({
        'font_size': 11
    })
    
    # Create DataFrame for Adoptions and If The Fur Fits counts
    metrics_df = pd.DataFrame({
        'Outcomes': [
            'Adoptions (previous business day)',
            'If The Fur Fits (previous business day)'
        ],
        'Count': [adoptions, fur_fits]
    })
    
    # Create DataFrame for Foster/Hold counts
    foster_holds_df = pd.DataFrame(list(foster_holds.items()), columns=['Stage', 'Count'])
    
    # Create the sheet with an empty DataFrame first
    pd.DataFrame().to_excel(writer, sheet_name='Morning Report', startrow=0, index=False)
    
    # Get the worksheet
    worksheet = writer.sheets['Morning Report']
    
    # Write Outcomes section
    worksheet.write('A1', 'Outcomes', header_format)
    worksheet.write('B1', 'Count', header_format)
    metrics_df.to_excel(writer, sheet_name='Morning Report', startrow=1, index=False, header=False)
    
    current_row = 4  # Start Stage section at row 4 to leave one blank row after metrics
    
    # Write Stage section
    worksheet.write(current_row, 0, 'Stage', header_format)
    worksheet.write(current_row, 1, 'Count', header_format)
    current_row += 1
    foster_holds_df.to_excel(writer, sheet_name='Morning Report', startrow=current_row, index=False, header=False)
    
    current_row += foster_holds_df.shape[0] + 1  # Add 1 for single blank row
    
    # Write Occupancy section
    worksheet.write(current_row, 0, 'Species/Age', header_format)
    worksheet.write(current_row, 1, 'Animals in Shelter', header_format)
    worksheet.write(current_row, 2, 'Animals in Foster/Off-Site', header_format)
    current_row += 1
    occupancy.to_excel(writer, sheet_name='Morning Report', startrow=current_row, index=False, header=False)
    
    current_row += occupancy.shape[0] + 1  # Add 1 for single blank row
    
    # Add Hold - Stray section
    worksheet.write(current_row, 0, 'Animal ID', header_format)
    worksheet.write(current_row, 1, 'Location', header_format)
    worksheet.write(current_row, 2, 'Review Date', header_format)
    current_row += 1

    # Add Hold - Stray cases from StageReview.csv
    stageReview_df = pd.read_csv('StageReview.csv', skiprows=3)
    hold_stray_df = stageReview_df[stageReview_df['Stage'] == 'Hold - Stray']

    if not hold_stray_df.empty:
        hold_stray_data = hold_stray_df.apply(
            lambda row: [
                row['textbox89'],  # Animal ID
                f"{row['Location']}, {row['SubLocation']}", # Location info
                pd.to_datetime(row['ReviewDate']).strftime('%Y-%m-%d')  # Date in YYYY-MM-DD format
            ], 
            axis=1
        ).tolist()
        
        for row_data in hold_stray_data:
            worksheet.write_row(current_row, 0, row_data)
            current_row += 1
    
    # Set column widths
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:C', 15)

    # Save the file
    writer.close()

def test_weekend_handling():
    # Simulate running on Monday, May 12th
    test_date = datetime(2025, 5, 12)
    
    # Get Friday and Saturday dates
    friday = test_date - timedelta(days=3)  # May 9th
    saturday = test_date - timedelta(days=2)  # May 10th
    
    # Read FosterCurrent.csv, skipping first 6 rows
    df_foster = pd.read_csv('FosterCurrent.csv', skiprows=6)
    
    # Convert StartStatusDate to datetime
    df_foster['StartStatusDate'] = pd.to_datetime(df_foster['StartStatusDate'])
    
    # Get all If The Fur Fits entries for Friday and Saturday
    fur_fits_entries = df_foster[
        (df_foster['Location'] == 'If The Fur Fits') &
        (
            (df_foster['StartStatusDate'].dt.date == friday.date()) |
            (df_foster['StartStatusDate'].dt.date == saturday.date())
        )
    ]
    
    print(f"\nTotal entries found: {len(fur_fits_entries)}")

if __name__ == "__main__":
    get_adoptions_count()
    # All other function calls are commented out for debugging
    # test_weekend_handling()
    # occupancy = get_occupancy_counts()
    export_to_excel() 