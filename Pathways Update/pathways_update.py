import pandas as pd
from datetime import datetime, timedelta

# Column mapping between PathwaysExportFile and AnimalInventory
column_mapping = {
    'Name': 'AnimalName',  # Name in Pathways maps to AnimalName in Inventory
    'Species': 'Species',
    'Location': 'Location',
    'Intake Date': 'IntakeDateTime',
    'Breed': 'PrimaryBreed',
    'Age': 'Age',
    'Stage': 'Stage',
    'LOSInDays': 'LOSInDays'
}

# Read the files
pathways_df = pd.read_csv('Pathways for Care.csv')
inventory_df = pd.read_csv('AnimalInventory.csv', skiprows=3)  # Skip first 3 rows, use 4th as header

# Print column names to debug
print("PathwaysExportFile columns:", pathways_df.columns.tolist())
print("AnimalInventory columns:", inventory_df.columns.tolist())

# Convert AID to string and ensure it's 8 digits
pathways_df['AID'] = pathways_df['AID'].astype(str).str.zfill(8)

# Convert AnimalNumber to string and get last 8 digits
inventory_df['AnimalNumber'] = inventory_df['AnimalNumber'].astype(str)
inventory_df['AID'] = inventory_df['AnimalNumber'].str[-8:]

# Find animals to remove (in Pathways but not in Inventory)
animals_to_remove = pathways_df[~pathways_df['AID'].isin(inventory_df['AID'])]

# Save animals to remove (using original column names since this is from PathwaysExportFile)
animals_to_remove[['Name', 'AID', 'Species', 'Location ', 'Intake Date']].to_excel('PathwaysRemove.xlsx', index=False)

# Filter inventory for animals that should be added
# Convert IntakeDateTime to datetime
inventory_df['IntakeDateTime'] = pd.to_datetime(inventory_df['IntakeDateTime'])
today = datetime.now()

# Calculate days in shelter
inventory_df['DaysInShelter'] = (today - inventory_df['IntakeDateTime']).dt.days

# Filter based on species and days in shelter
cats_to_add = inventory_df[
    (inventory_df['Species'] == 'Cat') & 
    (inventory_df['DaysInShelter'] >= 60)
]

dogs_to_add = inventory_df[
    (inventory_df['Species'] == 'Dog') & 
    (inventory_df['DaysInShelter'] >= 30)
]

others_to_add = inventory_df[
    (~inventory_df['Species'].isin(['Cat', 'Dog'])) & 
    (inventory_df['DaysInShelter'] >= 14)
]

# Combine all animals to add
animals_to_add = pd.concat([cats_to_add, dogs_to_add, others_to_add])

# Remove animals that are already in Pathways
animals_to_add = animals_to_add[~animals_to_add['AID'].isin(pathways_df['AID'])]

# Remove animals with specific stages
excluded_stages = [
    'Permanent Resident',
    'Unavailable',
    'In If the Fur Fits - Behavior',
    'In If the Fur Fits - Medical',
    'In If the Fur Fits - Trial'
]
animals_to_add = animals_to_add[~animals_to_add['Stage'].isin(excluded_stages)]

# Prepare the output dataframe with required columns (using mapped names since this is from AnimalInventory)
animals_to_add_output = pd.DataFrame({
    'Name': animals_to_add[column_mapping['Name']],
    'AID': animals_to_add['AID'],
    'Species': animals_to_add[column_mapping['Species']],
    'Location': animals_to_add[column_mapping['Location']],
    'Intake Date': animals_to_add['IntakeDateTime'].dt.strftime('%m/%d/%Y'),
    'Breed': animals_to_add[column_mapping['Breed']],
    'Age': animals_to_add[column_mapping['Age']],
    'Stage': animals_to_add[column_mapping['Stage']],
    'LOSInDays': animals_to_add[column_mapping['LOSInDays']]
})

# Custom header as in the screenshot
custom_header = [
    'Name', 'AID', 'Species', 'Location', 'Intake Date', 'Breed', 'Age', 'Stage', 'LOSInDays'
]

# Write the custom header and then the data starting from row 2
with pd.ExcelWriter('PathwaysAdd.xlsx', engine='openpyxl') as writer:
    # Write header only
    pd.DataFrame(columns=custom_header).to_excel(writer, index=False, header=True)
    # Write data starting from row 2
    animals_to_add_output.to_excel(writer, index=False, header=False, startrow=1)

print(f"Found {len(animals_to_remove)} animals to remove")
print(f"Found {len(animals_to_add_output)} animals to add") 