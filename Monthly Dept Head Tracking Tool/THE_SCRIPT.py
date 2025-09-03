import pandas as pd
import os

# Define the filenames for input and output
OUTCOME_FILE = 'AnimalOutcome.csv'
FOSTER_FILE = 'FosterAnimalExtended.xls'
MEDICAL_FILE = 'MedicalExamSurgeryExtended.xlsx'
MED_CONDITION_FILE = 'MedConditionHistory.csv'
INTAKE_FILE = 'AnimalIntake.csv'
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

# Define intake category mapping rules
# Format: (Category, OperationType, OperationSubType, DOA)
# If OperationType or OperationSubType is empty string, it means "all values allowed"
# If DOA is None, it means "all values allowed"
INTAKE_CATEGORY_RULES = [
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Guardian Surrender - OTC!", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Evaluation/Poss Adopt - OTC!", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Evaluation/Poss Adopt - FIELD!", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Eviction - OTC", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Guardian Surrender - FIELD!", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "OTC", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Owned More than 30 Days - OTC!", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Eviction - Field!", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Field", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Born in Foster", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "Born in Care", False),
    ("Surrender or Return Past 30 Days", "Owner/Guardian Surrender", "SAFE Candidate", False),
    ("Surrender or Return Past 30 Days", "Stray", "Born in Care", False),
    ("Surrender or Return Past 30 Days", "Seized / Custody", "Born in Care", False),
    ("Surrender or Return Past 30 Days", "Service In", "Born in Care", False),
    ("Surrender or Return Past 30 Days", "Return", "Owned More than 30 Days - OTC!", False),
    ("Surrender or Return Past 30 Days", "Return", "Owned More than 30 Days", False),
    ("Surrender or Return Past 30 Days", "Return", "Owned More than 30 Days - FIELD!", False),
    ("Surrender or Return Past 30 Days", "Return", "Owned More than 30 Days FIELD!", False),
    ("Surrender or Return Past 30 Days", "Return", "Guardian Surrender - OTC!", False),
    ("Return Within 30 Days", "Return", "Owned 30 Days or Less - OTC!", False),
    ("Return Within 30 Days", "Return", "Owned 30 Days or Less - FIELD!", False),
    ("Surrender or Return Past 30 Days", "Return", "Medical Treatment - OTC!", False),
    ("Surrender or Return Past 30 Days", "Return", "Surrender or Return Past 30 days", False),
    ("Seized", "Seized / Custody", "Cruelty", False),
    ("Seized", "Seized / Custody", "Signed Over", False),
    ("Seized", "Seized / Custody", "Eviction", False),
    ("Seized", "Seized / Custody", "Abandoned", False),
    ("Seized", "Seized / Custody", "Protective Custody", False),
    ("Seized", "Seized / Custody", "Hospital", False),
    ("Seized", "Seized / Custody", "Police", False),
    ("Seized", "Seized / Custody", "Court Order Violation", False),
    ("Seized", "Seized / Custody", "Owner died", False),
    ("Seized", "Seized / Custody", "General", False),
    ("Stray", "Stray", "OTC", False),
    ("Stray", "Stray", "No Hold", False),
    ("Stray", "Stray", "Eviction - OTC", False),
    ("Stray", "Stray", "Abandoned/Dumped Off at SPCA", False),
    ("Stray", "Stray", "Abandoned by owner - OTC!", False),
    ("Stray", "Stray", "Abandoned by owner - FIELD!", False),
    ("Stray", "Stray", "Field", False),
    ("Stray", "Stray", "Special Circumstance", False),
    ("Stray", "Stray", "No Hold/Surgery", False),
    ("Stray", "Stray", "Animal Control", False),
    ("Clinic In", "Clinic", "", None),
    ("Transferred In Locally", "Transfer In", "ACO or DCO in County", False),
    ("Transferred In Locally", "Transfer In", "Furever Friends", False),
    ("Transferred In Locally", "Transfer In", "Vet clinic", False),
    ("Transferred In Locally", "Transfer In", "Buffalo City Animal Shelter", False),
    ("Transferred In Locally", "Transfer In", "Feral Cat Focus", False),
    ("Transferred  In Out of Area", "Transfer In", "SPCA - Other Counties", False),
    ("Transferred  In Out of Area", "Transfer In", "Rescue Group (any other)", False),
    ("Transferred  In Out of Area", "Transfer In", "Other Shelter (Not SPCA)", False),
    ("Euth Request", "Seized / Custody", "Signed Over/Euthanasia Request", False),
    ("Euth Request", "Owner/Guardian Surrender", "Euthanasia Request - OTC!", False),
    ("Euth Request", "Owner/Guardian Surrender", "Euthanasia Request - FIELD!", False),
    ("Euth Request", "Return", "Euthanasia Request - OTC!", False),
    ("Euth Request", "Return", "Euthanasia Request - FIELD!", False),
    ("Euth Request", "Transfer In", "ACO or DCO Euthanasia Request", False),
    ("DOA", "", "", True),
]

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
    ('Other', 'Other Surgeries')
]

# Function to classify species
def classify_species(species):
    if species == 'Cat':
        return 'Cat'
    elif species == 'Dog':
        return 'Dog'
    else:
        return 'Other'

# Function to classify species for foster data (original logic)
def classify_species_foster(species):
    if species == 'Cat':
        return 'Cat'
    elif species == 'Dog':
        return 'Dog'
    else:
        return 'Other'

# Function to classify species for intake data
def classify_species_intake(species):
    """Classify species for intake data into Cat, Dog, or Other categories."""
    if pd.isna(species) or species == "":
        return "Other"
    
    species_str = str(species).strip().title()
    if species_str == "Cat":
        return "Cat"
    elif species_str == "Dog":
        return "Dog"
    else:
        return "Other"

# Function to classify intake records
def classify_intake(row):
    """Classify an intake record based on OperationType, OperationSubType, and DOA fields."""
    for category, op_type, op_sub, doa in INTAKE_CATEGORY_RULES:
        # Check OperationType (if specified)
        if op_type and row["OperationType"] != op_type:
            continue
        # Check OperationSubType (if specified)
        if op_sub and row["OperationSubType"] != op_sub:
            continue
        # Check DOA (if specified)
        if doa is not None and row["DOA"] != doa:
            continue
        return category
    return "Other"

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
        if species == 'Other':
            # For "Other", include all species except Cat and Dog
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
    
    # Filter for only "Yelp For Help Candidate" conditions
    yelp_candidates = df[df['Condition'] == 'Yelp For Help Candidate']
    
    # Count unique Animal IDs from the filtered data
    unique_animal_count = yelp_candidates['textbox27'].nunique()
    
    # Create a result row for Yelp For Help Candidate
    result = [("", ""), ("Yelp For Help Candidate", unique_animal_count)]
    
    return pd.DataFrame(result, columns=['Category', 'Count'])

# Process Intake Data
def process_intakes():
    """Process intake data and return categorized counts by species with subtotals and totals."""
    try:
        # Load the intake data from CSV file
        df = pd.read_csv(INTAKE_FILE, skiprows=3)
        
        # Clean and standardize the data
        df["OperationType"] = df["OperationType"].fillna("").str.strip()
        df["OperationSubType"] = df["OperationSubType"].fillna("").str.strip()
        df["Species"] = df["Species"].fillna("").str.strip()
        df["DOA"] = df["DOA"].fillna(False)
        
        # Apply classification
        df["Category"] = df.apply(classify_intake, axis=1)
        df["SpeciesCategory"] = df["Species"].apply(classify_species_intake)
        

        
        # Initialize results list
        intake_results = []
        
        # Track counted animals
        counted_animals = set()
        
        # Process each species with detailed breakdown
        for species in ['Cat', 'Dog', 'Other']:
            # Add species header
            if species == 'Cat':
                intake_results.append((f"{species}s", ""))
            elif species == 'Dog':
                intake_results.append((f"{species}s", ""))
            else:
                intake_results.append((f"{species}s", ""))
            
            species_df = df[df['SpeciesCategory'] == species]
            species_total = 0
            
            # Process each category for this species
            category_order = [
                "Surrender or Return Past 30 Days",
                "Return Within 30 Days", 
                "Seized",
                "Stray",
                "Clinic In",
                "Transferred In Locally",
                "Transferred  In Out of Area"
            ]
            
            for category in category_order:
                # Count animals in this category/species combination
                category_df = species_df[species_df['Category'] == category]
                count = category_df.shape[0]  # Count total records, not unique animals
                
                # Always show all categories, even if count is 0
                # Format category name for display
                if category == "Surrender or Return Past 30 Days":
                    display_name = f"{species}s, Surrender or Return Past 30 Days"
                elif category == "Return Within 30 Days":
                    display_name = f"{species}s, Return within 30 Days"
                else:
                    display_name = f"{species}s, {category}"
                
                intake_results.append((display_name, count))
                species_total += count
                
                # Track counted animals
                counted_animals.update(category_df['AnimalNumber'].tolist())
            
            # Add species subtotal
            if species == 'Cat':
                intake_results.append((f"{species} Subtotal", species_total))
            elif species == 'Dog':
                intake_results.append((f"{species} Subtotal", species_total))
            else:
                intake_results.append((f"{species} Subtotal", species_total))
            
            # Add blank row after each species
            intake_results.append(("", ""))
        
        # Calculate adoptable intake totals (excluding Euth Request and DOA)
        adoptable_categories = [
            "Surrender or Return Past 30 Days",
            "Return Within 30 Days", 
            "Seized",
            "Stray",
            "Clinic In",
            "Transferred In Locally",
            "Transferred  In Out of Area"
        ]
        
        adoptable_df = df[df['Category'].isin(adoptable_categories)]
        adoptable_total = adoptable_df.shape[0]
        intake_results.append(("Adoptable Intake Totals", adoptable_total))
        intake_results.append(("", ""))
        
        # Add Euthanasia Requests section
        intake_results.append(("Euthanasia Requests", ""))
        euth_request_df = df[df['Category'] == 'Euth Request']
        
        for species in ['Cat', 'Dog', 'Other']:
            species_euth = euth_request_df[euth_request_df['SpeciesCategory'] == species]
            count = species_euth.shape[0]  # Count total records, not unique animals
            # Always show all species, even if count is 0
            intake_results.append((f"{species}, Euth Request", count))
            counted_animals.update(species_euth['AnimalNumber'].tolist())
        
        euth_total = euth_request_df.shape[0]  # Count total records, not unique animals
        intake_results.append(("Euth Request Totals", euth_total))
        intake_results.append(("", ""))
        
        # Add DOA/Cremations section
        intake_results.append(("DOA/Cremations", ""))
        doa_df = df[df['Category'] == 'DOA']
        
        for species in ['Cat', 'Dog', 'Other']:
            species_doa = doa_df[doa_df['SpeciesCategory'] == species]
            count = species_doa.shape[0]  # Count total records, not unique animals
            # Always show all species, even if count is 0
            intake_results.append((f"{species}, DOA Cremation", count))
            counted_animals.update(species_doa['AnimalNumber'].tolist())
        
        doa_total = doa_df.shape[0]  # Count total records, not unique animals
        intake_results.append(("DOA Totals", doa_total))
        intake_results.append(("", ""))
        
        # Add grand total
        grand_total = df.shape[0]  # Count total records, not unique animals
        intake_results.append(("Total of intakes", grand_total))
        
        # Find uncounted animals
        all_animals = set(df['AnimalNumber'].tolist())
        uncounted_animals = all_animals - counted_animals
        
        # Create DataFrame for uncounted animals
        uncounted_df = df[df['AnimalNumber'].isin(uncounted_animals)][
            ['AnimalNumber', 'Species', 'OperationType', 'OperationSubType', 'DOA', 'Category']
        ].sort_values('AnimalNumber')
        
        return pd.DataFrame(intake_results, columns=['Category', 'Count']), uncounted_df
        
    except FileNotFoundError:
        print(f"Warning: {INTAKE_FILE} not found. Skipping intake processing.")
        return pd.DataFrame(columns=['Category', 'Count']), pd.DataFrame()
    except Exception as e:
        print(f"Error processing intake data: {e}")
        return pd.DataFrame(columns=['Category', 'Count']), pd.DataFrame()

# Export intake summary to separate file
def export_intake_summary(intake_df):
    """Export intake summary to a separate Excel file for easy copy/paste."""
    try:
        output_file = "Monthly_Intake_Summary.xlsx"
        intake_df.to_excel(output_file, index=False)
        print(f"Intake summary saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error exporting intake summary: {e}")
        return False

# Process both datasets
outcomes_df, uncounted_outcomes = process_outcomes()
fosters_df, uncounted_fosters = process_fosters()
medical_surgery_df, uncounted_medical_surgery = process_medical_surgery()
med_condition_df = process_med_condition_history()
intake_df, uncounted_intake = process_intakes()

# Export intake summary to separate file
export_intake_summary(intake_df)

# Combine medical surgery data with medical condition data
combined_medical_df = pd.concat([medical_surgery_df, med_condition_df], ignore_index=True)

# Create Excel writer
with pd.ExcelWriter(OUTPUT_FILE) as writer:
    outcomes_df.to_excel(writer, sheet_name='Outcomes', index=False)
    fosters_df.to_excel(writer, sheet_name='Fosters', index=False)
    combined_medical_df.to_excel(writer, sheet_name='Medical_Surgery', index=False)
    intake_df.to_excel(writer, sheet_name='Intakes', index=False)
    
    # Add uncounted animals to separate sheets
    uncounted_outcomes.to_excel(writer, sheet_name='Uncounted Outcomes', index=False)
    uncounted_fosters.to_excel(writer, sheet_name='Uncounted Fosters', index=False)
    uncounted_medical_surgery.to_excel(writer, sheet_name='Uncounted_Medical_Surgery', index=False)
    uncounted_intake.to_excel(writer, sheet_name='Uncounted_Intakes', index=False)

print(f"Summary saved to {OUTPUT_FILE}")
print(f"Found {len(uncounted_outcomes)} uncounted outcomes")
print(f"Found {len(uncounted_fosters)} uncounted fosters")
print(f"Found {len(uncounted_medical_surgery)} uncounted medical/surgery records")
print(f"Found {med_condition_df.iloc[1]['Count']} Yelp For Help Candidate animals")
print(f"Found {len(uncounted_intake)} uncounted intakes")
