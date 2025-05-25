import pandas as pd
import os

# Define the filenames for input and output
OUTCOME_FILE = 'AnimalOutcome.csv'
FOSTER_FILE = 'FosterAnimalExtended.xls'
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

# Function to classify species
def classify_species(species):
    if species == 'Cat':
        return 'Cat'
    elif species == 'Dog':
        return 'Dog'
    else:
        return 'Other'

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
    foster_df['SpeciesCategory'] = foster_df['Animal Type'].apply(classify_species)
    
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

# Process both datasets
outcomes_df, uncounted_outcomes = process_outcomes()
fosters_df, uncounted_fosters = process_fosters()

# Create Excel writer
with pd.ExcelWriter(OUTPUT_FILE) as writer:
    outcomes_df.to_excel(writer, sheet_name='Outcomes', index=False)
    fosters_df.to_excel(writer, sheet_name='Fosters', index=False)
    
    # Add uncounted animals to separate sheets
    uncounted_outcomes.to_excel(writer, sheet_name='Uncounted Outcomes', index=False)
    uncounted_fosters.to_excel(writer, sheet_name='Uncounted Fosters', index=False)

print(f"Summary saved to {OUTPUT_FILE}")
print(f"Found {len(uncounted_outcomes)} uncounted outcomes")
print(f"Found {len(uncounted_fosters)} uncounted fosters")
