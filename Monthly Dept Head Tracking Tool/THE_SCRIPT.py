import pandas as pd
import os

# Define the filenames for input and output
OUTCOME_FILE = 'AnimalOutcome.csv'
FOSTER_FILE = 'FosterAnimalExtended.xls'
MEDICAL_FILE = 'MedicalExamSurgeryExtended.xlsx'
MED_CONDITION_FILE = 'MedConditionHistory.csv'
OUTPUT_FILE = 'Department Head Monthly Report Generation.xlsx'

# Define the operation types in the required order
OPERATION_TYPES = [
    'Adoption',
    'Return to Owner/Guardian',
    'Transfer Out',
    'Clinic Out',
    'Missing',
    'Wildlife Release',
    'Died',
    'Euthanasia'
]

# Define foster reason groupings
FOSTER_REASON_GROUPS = {
    'Too Young/Pregnant/Nursing': [
        'Bottle Baby under 4 wks',
        'Nursing',
        'Pregnant',
        'Too Young'
    ],
    'Behavior Reasons': [
        'Behavior',
        'Litterbox Watch',
        'Socialization'
    ],
    'Medical Reasons': [
        'Distemper Watch',
        'Heartworm',
        'Hospice Care',
        'Kennel Couch/Pneumonia',
        'Medical Reasons',
        'Parvo Positive',
        'Possible Ringworm',
        'Underweight',
        'Upper Respiratory',
        'Waiting for Dental'
    ],
    'Possible Adoption': [
        'Possible Adoption',
        'Possible Adoption/Behavior',
        'Possible Adoption/Medical'
    ],
    'Space': [
        'Space',
        'Transport'
    ],
    'Cruelty Case': ['Cruelty Case'],
    'Stray Foster': [
        'Stray Hold',
        'Stray Hold/Possible Adoption'
    ],
    'SAFE Foster': [
        'SAFE Program',
        'SAFE Foster'
    ],
    'Trocaire College Program': [
        'Trocaire College Program',
        'Trocaire College Program (x2)'
    ]
}

# Define surgery categories and their order
SURGERY_CATEGORIES = [
    ('Cat', 'Spay'),
    ('Dog', 'Spay'),
    ('Rabbit', 'Spay'),
    ('', ''),  # Blank space
    ('Cat', 'Neuter'),
    ('Dog', 'Neuter'),
    ('Rabbit', 'Neuter'),
    ('Rat', 'Neuter'),
    ('', ''),  # Blank space
    ('Cat', 'Dental'),
    ('Dog', 'Dental'),
    ('', ''),  # Blank space
    ('Cat', 'Other Surgeries'),
    ('Dog', 'Other Surgeries'),
    ('Others', 'Other Surgeries')
]

# Function to classify species
def classify_species(species):
    if species == 'Cat':
        return 'Cat'
    elif species == 'Dog':
        return 'Dog'
    elif species == 'Rabbit':
        return 'Rabbit'
    elif species == 'Rodent':
        return 'Rat'
    else:
        return 'Others'

# Function to classify species for foster data (original logic)
def classify_species_foster(species):
    if species == 'Cat':
        return 'Cat'
    elif species == 'Dog':
        return 'Dog'
    else:
        return 'Other'

# Function to classify surgery subtype
def classify_surgery_subtype(record_subtype):
    if record_subtype == 'Spay':
        return 'Spay'
    elif record_subtype == 'Neuter':
        return 'Neuter'
    elif record_subtype == 'Dental':
        return 'Dental'
    else:
        return 'Other Surgeries'

# Process Outcomes Data
def process_outcomes():
    # Load the data from the CSV file
    df = pd.read_csv(OUTCOME_FILE, skiprows=3)
    
    # Filter out 'DOA' OperationType
    df = df[df['OperationType'] != 'DOA']
    
    # Apply classification to a new column
    df['SpeciesCategory'] = df['Species'].apply(classify_species)
    
    # Initialize a list to collect result rows
    results = []
    
    # Track counted animals
    counted_animals = set()
    
    # Iterate over each specified OperationType
    for op_type in OPERATION_TYPES:
        # Filter dataframe by OperationType
        subset = df[df['OperationType'] == op_type]
        
        # Special handling for 'Euthanasia': exclude 'Requested Sleep'
        if op_type == 'Euthanasia':
            subset = subset[subset['OperationSubType'] != 'Requested Sleep']
        
        # Count the number of AnimalNumbers by SpeciesCategory
        count_series = subset.groupby('SpeciesCategory')['AnimalNumber'].count()
        
        # Track counted animals
        counted_animals.update(subset['AnimalNumber'].tolist())
        
        # Ensure all categories are represented
        for species in ['Cat', 'Dog', 'Other']:
            count = count_series.get(species, 0)
            label = f"{species}, {op_type}"
            results.append((label, count))
        
        # Add a blank row after each operation type
        results.append(("", ""))
    
    # Find uncounted animals
    all_animals = set(df['AnimalNumber'].tolist())
    uncounted_animals = all_animals - counted_animals
    
    # Create DataFrame for uncounted animals
    uncounted_df = df[df['AnimalNumber'].isin(uncounted_animals)][
        ['AnimalNumber', 'Species', 'OperationType', 'OperationSubType']
    ].sort_values('AnimalNumber')
    
    return pd.DataFrame(results, columns=['Category', 'Count']), uncounted_df

# Process Foster Data
def process_fosters():
    # Load foster data
    foster_df = pd.read_excel(FOSTER_FILE)
    
    # Classify species
    foster_df['SpeciesCategory'] = foster_df['Animal Type'].apply(classify_species_foster)
    
    # Initialize results list
    foster_results = []
    
    # Track counted animals
    counted_animals = set()
    
    # Process each species
    for species in ['Cat', 'Dog', 'Other']:
        species_df = foster_df[foster_df['SpeciesCategory'] == species]
        
        # Process each foster reason group
        for group_name, reasons in FOSTER_REASON_GROUPS.items():
            # Count animals in this group
            group_df = species_df[species_df['Foster Start Reason'].isin(reasons)]
            count = group_df.shape[0]
            label = f"{species} - {group_name}"
            foster_results.append((label, count))
            
            # Track counted animals
            counted_animals.update(group_df['Animal #'].tolist())
        
        # Add blank row after each species
        foster_results.append(("", ""))
    
    # Find uncounted animals
    all_animals = set(foster_df['Animal #'].tolist())
    uncounted_animals = all_animals - counted_animals
    
    # Create DataFrame for uncounted animals
    uncounted_df = foster_df[foster_df['Animal #'].isin(uncounted_animals)][
        ['Animal #', 'Animal Type', 'Foster Start Date', 'Foster Start Reason']
    ].sort_values('Animal #')
    
    return pd.DataFrame(foster_results, columns=['Category', 'Count']), uncounted_df

# Process Medical/Surgery Data
def process_medical_surgery():
    # Load the medical/surgery data
    df = pd.read_excel(MEDICAL_FILE)
    
    # Filter for only Surgery Record Type
    surgery_df = df[df['Record Type'] == 'Surgery'].copy()
    
    # Apply classification to new columns
    surgery_df['SpeciesCategory'] = surgery_df['Species'].apply(classify_species)
    surgery_df['SurgeryCategory'] = surgery_df['Record Subtype'].apply(classify_surgery_subtype)
    
    # Initialize results list
    surgery_results = []
    
    # Track counted records
    counted_records = set()
    
    # Process each surgery category in the specified order
    for species, surgery_type in SURGERY_CATEGORIES:
        if species == '' and surgery_type == '':  # Blank space
            surgery_results.append(("", ""))
            continue
            
        # Filter for this species and surgery type
        if species == 'Others':
            # For "Others", include all species except Cat and Dog
            subset = surgery_df[
                (~surgery_df['SpeciesCategory'].isin(['Cat', 'Dog'])) &
                (surgery_df['SurgeryCategory'] == surgery_type)
            ]
        else:
            subset = surgery_df[
                (surgery_df['SpeciesCategory'] == species) & 
                (surgery_df['SurgeryCategory'] == surgery_type)
            ]
        
        # Count unique Record # entries
        unique_count = subset['Record #'].nunique()
        label = f"{species} {surgery_type}"
        surgery_results.append((label, unique_count))
        
        # Track counted records
        counted_records.update(subset['Record #'].tolist())
    
    # Find uncounted surgery records
    all_surgery_records = set(surgery_df['Record #'].tolist())
    uncounted_records = all_surgery_records - counted_records
    
    # Create DataFrame for uncounted records
    uncounted_df = surgery_df[surgery_df['Record #'].isin(uncounted_records)][
        ['Record #', 'Species', 'Record Subtype', 'Animal #', 'Name']
    ].sort_values('Record #')
    
    return pd.DataFrame(surgery_results, columns=['Category', 'Count']), uncounted_df

# Process Medical Condition History Data
def process_med_condition_history():
    # Load the medical condition history data, skip first 3 rows and use row 4 as header
    df = pd.read_csv(MED_CONDITION_FILE, skiprows=3)
    
    # Count unique Animal IDs from the textbox27 column (Animal ID)
    unique_animal_count = df['textbox27'].nunique()
    
    # Create a result row for Yelp For Help Candidate
    result = [("", ""), ("Yelp For Help Candidate", unique_animal_count)]
    
    return pd.DataFrame(result, columns=['Category', 'Count'])

# Process both datasets
outcomes_df, uncounted_outcomes = process_outcomes()
fosters_df, uncounted_fosters = process_fosters()
medical_surgery_df, uncounted_medical_surgery = process_medical_surgery()
med_condition_df = process_med_condition_history()

# Combine medical surgery data with medical condition data
combined_medical_df = pd.concat([medical_surgery_df, med_condition_df], ignore_index=True)

# Create Excel writer
with pd.ExcelWriter(OUTPUT_FILE) as writer:
    outcomes_df.to_excel(writer, sheet_name='Outcomes', index=False)
    fosters_df.to_excel(writer, sheet_name='Fosters', index=False)
    combined_medical_df.to_excel(writer, sheet_name='Medical_Surgery', index=False)
    
    # Add uncounted animals to separate sheets
    uncounted_outcomes.to_excel(writer, sheet_name='Uncounted Outcomes', index=False)
    uncounted_fosters.to_excel(writer, sheet_name='Uncounted Fosters', index=False)
    uncounted_medical_surgery.to_excel(writer, sheet_name='Uncounted_Medical_Surgery', index=False)

print(f"Summary saved to {OUTPUT_FILE}")
print(f"Found {len(uncounted_outcomes)} uncounted outcomes")
print(f"Found {len(uncounted_fosters)} uncounted fosters")
print(f"Found {len(uncounted_medical_surgery)} uncounted medical/surgery records")
print(f"Found {med_condition_df.iloc[1]['Count']} Yelp For Help Candidate animals")
