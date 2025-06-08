import pandas as pd
import re
from datetime import datetime, timedelta
import os

def get_user_dates():
    while True:
        try:
            date_input = input("Enter the dates to include (mm/dd/yyyy, separated by commas): ")
            dates = [date.strip() for date in date_input.split(',') if date.strip()]
            # Validate each date
            validated_dates = []
            for date in dates:
                datetime.strptime(date, '%m/%d/%Y')
                validated_dates.append(date)
            return validated_dates
        except ValueError:
            print("Invalid date format. Please use mm/dd/yyyy format and separate dates with commas.")

# Use relative path to the __Load Files Go Here__ directory
LOAD_FILES_DIR = '__Load Files Go Here__'

# Define the stage mappings
STAGE_MAPPINGS = {
    'In Foster': 'In Foster',
    'Hold – SAFE Foster': 'Hold SAFE Foster',
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

# Add this list in the order of your mapping
INTAKE_GROUP_ORDER = [
    'Transfer In', 'DOA', 'Euthanasia Request', 'Euthanasia Req – Field', 'Field – Stray', 'Field – OS',
    'Seized – Abandoned', 'Seized – Cruelty', 'Seized – General', 'Seized – Hospital', 'Seized – Signed over',
    'Seized – Eviction', 'Seized – Police', 'Seized – Owner Died', 'Seized – Order Violation', 'Seized - Hoarding',
    'Return', 'Stray', 'OTC – OS', 'OTC - OS - SAFE', 'Clinic - Medical Treatment', 'Clinic - Stray',
    'Clinic - Retention', 'Clinic - Case Assistance', 'Clinic - Case Assistance - Outreach', 'Clinic - Outreach', 'Boarder'
]

def get_report_date_from_csv():
    # Read the second line of FosterCurrent.csv to get the report date
    with open(os.path.join(LOAD_FILES_DIR, 'FosterCurrent.csv'), 'r') as f:
        lines = f.readlines()
        if len(lines) >= 2:
            # Join the first three columns to reconstruct the date string
            parts = [p.strip().replace('"', '') for p in lines[1].split(',')[:3]]
            date_str = ', '.join(parts)
            # Example format: 'Monday, May 12, 2025'
            return datetime.strptime(date_str, '%A, %B %d, %Y')
        else:
            raise ValueError('Could not find report date in FosterCurrent.csv')



def get_fur_fits_count(check_dates):
    # Read FosterCurrent.csv, skipping first 6 rows
    df_foster = pd.read_csv(os.path.join(LOAD_FILES_DIR, 'FosterCurrent.csv'), skiprows=6)
    
    # Convert StartStatusDate to datetime and normalize to remove time component
    df_foster['StartStatusDate'] = pd.to_datetime(df_foster['StartStatusDate'], format='mixed').dt.normalize()
    check_datetimes = [pd.to_datetime(date, format='%m/%d/%Y').normalize() for date in check_dates]
    
    # Count entries where Location is "If The Fur Fits" and StartStatusDate matches any check date
    fur_fits_count = len(df_foster[
        (df_foster['Location'] == 'If The Fur Fits') & 
        (df_foster['StartStatusDate'].isin(check_datetimes))
    ])
    
    return fur_fits_count

def get_foster_count():
    # Read FosterCurrent.csv, skipping first 6 rows
    foster_path = os.path.join(LOAD_FILES_DIR, 'FosterCurrent.csv')
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
    inventory_path = os.path.join(LOAD_FILES_DIR, 'AnimalInventory.csv')
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
    df = pd.read_csv(os.path.join(LOAD_FILES_DIR, 'AnimalInventory.csv'), skiprows=3)
    
    # Convert DateOfBirth to datetime
    df['DateOfBirth'] = pd.to_datetime(df['DateOfBirth'], format='mixed')
    
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

def get_adoptions_count(check_dates):
    # Read AnimalOutcome.csv, skipping the first 3 rows to get to the header
    try:
        df_outcomes = pd.read_csv(os.path.join(LOAD_FILES_DIR, 'AnimalOutcome.csv'), skiprows=3)
    except FileNotFoundError:
        print("AnimalOutcome.csv not found. Returning 0 adoptions.")
        return 0

    # Convert the date column to datetime and extract only the date component
    df_outcomes['Textbox50'] = pd.to_datetime(df_outcomes['Textbox50'], format='mixed').dt.date
    check_dates_dt = [pd.to_datetime(date, format='%m/%d/%Y').date() for date in check_dates]
    
    # Count adoptions for the specified dates
    adoptions_count = len(df_outcomes[
        (df_outcomes['textbox16'] == 'Adoption') & 
        (df_outcomes['Textbox50'].isin(check_dates_dt))
    ])
    
    return adoptions_count

def map_intake_group(row):
    op_type = str(row['OperationType']).strip().upper()
    op_subtype = str(row['OperationSubType']).strip().upper()
    # Logic from mapping
    if op_type == 'TRANSFER IN':
        return 'Transfer In'
    if op_type == 'OWNER/GUARDIAN SURRENDER' and op_subtype == 'DOA':
        return 'DOA'
    if op_type == 'OWNER/GUARDIAN SURRENDER' and op_subtype in ['EUTHANASIA REQUEST', 'EUTHANASIA REQUEST - OTC!']:
        return 'Euthanasia Request'
    if (op_type == 'SEIZED / CUSTODY' and op_subtype == 'SIGNED OVER/EUTHANASIA REQUEST') or \
       (op_type == 'OWNER/GUARDIAN SURRENDER' and op_subtype == 'EUTHANASIA REQUEST - FIELD!'):
        return 'Euthanasia Req – Field'
    if op_type == 'STRAY' and ('FIELD' in op_subtype):
        return 'Field – Stray'
    if op_type == 'OWNER/GUARDIAN SURRENDER' and ('FIELD' in op_subtype) and op_subtype != 'EUTHANASIA REQUEST - FIELD!':
        return 'Field – OS'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'ABANDONED':
        return 'Seized – Abandoned'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'CRUELTY':
        return 'Seized – Cruelty'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'GENERAL':
        return 'Seized – General'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'HOSPITAL':
        return 'Seized – Hospital'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'SIGNED OVER':
        return 'Seized – Signed over'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'EVICTION':
        return 'Seized – Eviction'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'POLICE':
        return 'Seized – Police'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'OWNER DIED':
        return 'Seized – Owner Died'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'COURT ORDER VIOLATION':
        return 'Seized – Order Violation'
    if op_type == 'SEIZED / CUSTODY' and op_subtype == 'HOARDING':
        return 'Seized - Hoarding'
    if op_type == 'RETURN':
        return 'Return'
    if op_type == 'STRAY' and not ('FIELD' in op_subtype):
        return 'Stray'
    if op_type == 'OWNER/GUARDIAN SURRENDER' and ('OTC' in op_subtype):
        return 'OTC – OS'
    if op_type == 'OWNER/GUARDIAN SURRENDER' and op_subtype == 'SAFE FOSTER':
        return 'OTC - OS - SAFE'
    if op_type == 'CLINIC' and op_subtype == 'MEDICAL TREATMENT':
        return 'Clinic - Medical Treatment'
    if op_type == 'CLINIC' and op_subtype == 'STRAY':
        return 'Clinic - Stray'
    if op_type == 'CLINIC' and op_subtype == 'RETENTION':
        return 'Clinic - Retention'
    if op_type == 'CLINIC' and op_subtype == 'CASE ASSISTANCE':
        return 'Clinic - Case Assistance'
    if op_type == 'CLINIC' and op_subtype == 'CASE - OUTREACH':
        return 'Clinic - Case Assistance - Outreach'
    if op_type == 'CLINIC' and op_subtype == 'OUTREACH':
        return 'Clinic - Outreach'
    if op_type == 'BOARDER':
        return 'Boarder'
    return 'not counted'

def get_intake_count_detail(check_dates):
    intake_path = os.path.join(LOAD_FILES_DIR, 'AnimalIntake.csv')
    df_intake = pd.read_csv(intake_path, skiprows=3)
    # Filter by intake date (textbox44)
    df_intake['textbox44'] = pd.to_datetime(df_intake['textbox44']).dt.date
    check_dates_dt = [pd.to_datetime(date).date() for date in check_dates]
    filtered = df_intake[df_intake['textbox44'].isin(check_dates_dt)].copy()
    # Assign group
    filtered['IntakeGroup'] = filtered.apply(map_intake_group, axis=1)
    # For detail, include all rows (even not counted)
    all_rows = df_intake.copy()
    all_rows['IntakeGroup'] = all_rows.apply(map_intake_group, axis=1)
    # Only keep relevant columns
    detail = all_rows[['AnimalNumber', 'Species', 'textbox44', 'OperationType', 'OperationSubType', 'IntakeGroup']]
    return detail

def get_intake_summary(detail_df):
    # Only use rows that are in the mapping order (including not counted)
    summary = []
    for group in INTAKE_GROUP_ORDER:
        group_df = detail_df[detail_df['IntakeGroup'] == group]
        cat_count = (group_df['Species'].str.lower() == 'cat').sum() if not group_df.empty else ''
        dog_count = (group_df['Species'].str.lower() == 'dog').sum() if not group_df.empty else ''
        other_count = (~group_df['Species'].str.lower().isin(['cat', 'dog'])).sum() if not group_df.empty else ''
        # Leave blank if 0
        cat_count = cat_count if cat_count != 0 else ''
        dog_count = dog_count if dog_count != 0 else ''
        other_count = other_count if other_count != 0 else ''
        summary.append({'Group': group, 'Cat': cat_count, 'Dog': dog_count, 'Other': other_count})
    return pd.DataFrame(summary)

def export_to_excel(check_dates):
    # Get all our data
    adoptions = get_adoptions_count(check_dates)
    fur_fits = get_fur_fits_count(check_dates)
    foster_holds = get_stage_counts()
    occupancy = get_occupancy_counts()
    
    # Create Excel writer object - save in the MorningEmail directory
    output_path = os.path.join('MorningEmail', 'morning_report.xlsx')
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
            f'Adoptions ({", ".join(check_dates)})',
            f'If The Fur Fits ({", ".join(check_dates)})'
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
    stageReview_df = pd.read_csv(os.path.join(LOAD_FILES_DIR, 'StageReview.csv'), skiprows=3)
    hold_stray_df = stageReview_df[stageReview_df['Stage'] == 'Hold - Stray']

    if not hold_stray_df.empty:
        hold_stray_data = hold_stray_df.apply(
            lambda row: [
                row['textbox89'],  # Animal ID
                f"{row['Location']}, {row['SubLocation']}", # Location info
                pd.to_datetime(row['ReviewDate']).strftime('%Y-%m-%d') if pd.notna(row['ReviewDate']) else 'No Review Date'  # Date in YYYY-MM-DD format
            ], 
            axis=1
        ).tolist()
        
        for row_data in hold_stray_data:
            worksheet.write_row(current_row, 0, row_data)
            current_row += 1
    
    # Set column widths
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:C', 15)

    # Add a blank row for separation
    current_row += 1

    # Intake Count Detail
    intake_detail = get_intake_count_detail(check_dates)
    intake_detail.to_excel(writer, sheet_name='Intake Count Detail', index=False)

    # Add a blank row for separation
    current_row += 1

    # Intake Count Summary
    intake_summary = get_intake_summary(intake_detail)
    worksheet.write(current_row, 0, 'Intake Count Summary', header_format)
    worksheet.write(current_row, 1, 'Cat', header_format)
    worksheet.write(current_row, 2, 'Dog', header_format)
    worksheet.write(current_row, 3, 'Other', header_format)
    current_row += 1
    for _, row in intake_summary.iterrows():
        worksheet.write(current_row, 0, row['Group'])
        worksheet.write(current_row, 1, row['Cat'])
        worksheet.write(current_row, 2, row['Dog'])
        worksheet.write(current_row, 3, row['Other'])
        current_row += 1

    # Save the file
    writer.close()


if __name__ == "__main__":
    check_dates = get_user_dates()
    get_adoptions_count(check_dates)
    export_to_excel(check_dates)
    # All other function calls are commented out for debugging
    # test_weekend_handling()
    # occupancy = get_occupancy_counts() 