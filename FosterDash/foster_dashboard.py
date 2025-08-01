import streamlit as st
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="SPCA Foster Dashboard",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #062b49;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #bc6f32;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    .foster-now {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .foster-soon {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .in-foster {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .animal-link {
        color: #bc6f32;
        text-decoration: none;
        font-weight: bold;
    }
    .animal-link:hover {
        text-decoration: underline;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the CSV files"""
    try:
        # Load AnimalInventory.csv - path at same level as FosterDash
        animal_inventory_path = "../__Load Files Go Here__/AnimalInventory.csv"
        full_path = os.path.abspath(animal_inventory_path)
        
        if os.path.exists(animal_inventory_path):
            # Skip first 3 rows and start from row 4 where headers are
            try:
                animal_inventory = pd.read_csv(animal_inventory_path, encoding='utf-8', skiprows=3)
            except:
                try:
                    animal_inventory = pd.read_csv(animal_inventory_path, encoding='latin-1', skiprows=3)
                except:
                    # Try with different delimiter and quoting options
                    animal_inventory = pd.read_csv(animal_inventory_path, encoding='utf-8', 
                                                 skiprows=3, quoting=3, on_bad_lines='skip')
            
            st.success(f"✅ Successfully loaded AnimalInventory.csv ({len(animal_inventory)} records)")
        else:
            st.error(f"❌ AnimalInventory.csv not found!")
            st.error(f"Expected path: {full_path}")
            st.error(f"Current working directory: {os.getcwd()}")
            return None, None
        
        # Load FosterCurrent.csv - path at same level as FosterDash
        foster_current_path = "../__Load Files Go Here__/FosterCurrent.csv"
        full_foster_path = os.path.abspath(foster_current_path)
        
        if os.path.exists(foster_current_path):
            # Skip first 6 rows and start from row 7 where headers are
            try:
                foster_current = pd.read_csv(foster_current_path, encoding='utf-8', skiprows=6)
            except:
                try:
                    foster_current = pd.read_csv(foster_current_path, encoding='latin-1', skiprows=6)
                except:
                    # Try with different delimiter and quoting options
                    foster_current = pd.read_csv(foster_current_path, encoding='utf-8', 
                                               skiprows=6, quoting=3, on_bad_lines='skip')
            
            st.success(f"✅ Successfully loaded FosterCurrent.csv ({len(foster_current)} records)")
        else:
            st.warning(f"⚠️ FosterCurrent.csv not found!")
            st.warning(f"Expected path: {full_foster_path}")
            foster_current = pd.DataFrame()
        
        return animal_inventory, foster_current
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.error(f"Current working directory: {os.getcwd()}")
        return None, None

def classify_animals(animal_inventory, foster_current):
    """Classify animals into foster categories"""
    if animal_inventory is None:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying original data
    df = animal_inventory.copy()
    
    # Initialize category column and foster info columns
    df['Foster_Category'] = 'Other'
    df['Foster_PID'] = ''
    df['Foster_Name'] = ''
    
    # Get list of animals currently in foster and their foster info
    foster_animal_ids = set()
    foster_info = {}
    
    if not foster_current.empty:
        # Check for Animal ID column in foster data - it might be 'textbox9' or 'ARN'
        animal_id_col = None
        for col in ['textbox9', 'ARN', 'AnimalNumber']:
            if col in foster_current.columns:
                animal_id_col = col
                break
        
        if animal_id_col:
            # Create a mapping of animal ID to foster info
            for idx, row in foster_current.iterrows():
                animal_id = str(row[animal_id_col])
                foster_animal_ids.add(animal_id)
                
                # Get foster person info
                foster_pid = str(row.get('textbox10', ''))  # PID
                foster_name = str(row.get('textbox11', ''))  # Person's name
                
                foster_info[animal_id] = {
                    'pid': foster_pid,
                    'name': foster_name
                }
    
    # Classify animals
    for idx, row in df.iterrows():
        animal_id = str(row.get('AnimalNumber', ''))
        stage = str(row.get('Stage', '')).strip()
        
        # Check if in foster
        if (animal_id in foster_animal_ids or 
            'In Foster' in stage or 
            'Pending Foster Pickup' in stage or 
            'In SAFE Foster' in stage or 
            'In Cruelty Foster' in stage):
            df.at[idx, 'Foster_Category'] = 'In Foster'
            
            # Add foster person info if available
            if animal_id in foster_info:
                df.at[idx, 'Foster_PID'] = foster_info[animal_id]['pid']
                df.at[idx, 'Foster_Name'] = foster_info[animal_id]['name']
        
        # Check if needs foster now
        elif any(need_stage in stage for need_stage in [
            'Hold - Foster', 'Hold - Cruelty Foster', 'Hold – SAFE Foster'
        ]):
            df.at[idx, 'Foster_Category'] = 'Needs Foster Now'
        
        # Check if might need foster soon
        elif any(soon_stage in stage for soon_stage in [
            'Hold - Doc', 'Hold - Behavior', 'Hold - Behavior Mod.',
            'Hold - Surgery', 'Hold - Stray', 'Hold - Legal Notice', 'Evaluate'
        ]):
            df.at[idx, 'Foster_Category'] = 'Might Need Foster Soon'
    
    return df

def create_clickable_link(animal_id):
    """Create a clickable HTML link for the animal ID"""
    # Extract the numeric part after "A00" prefix for the PetPoint URL
    if animal_id.startswith('A00'):
        petpoint_id = animal_id[3:]  # Remove "A00" prefix
    else:
        petpoint_id = animal_id  # Fallback if format is different
    
    return f'<a href="https://sms.petpoint.com/sms3/enhanced/animal/{petpoint_id}" target="_blank" class="animal-link">{animal_id}</a>'

def create_clickable_pid_link(pid):
    """Create a clickable HTML link for the PID"""
    if pd.isna(pid) or pid == '' or pid == 'nan':
        return ''
    
    # Extract numeric part from PID (e.g., "P0047897436" -> "40047897436")
    if pid.startswith('P'):
        numeric_pid = pid[1:]  # Remove "P" prefix
    else:
        numeric_pid = pid
    
    return f'<a href="https://sms.petpoint.com/sms3/enhanced/person/{numeric_pid}" target="_blank" class="animal-link">{pid}</a>'

def create_petpoint_links(animal_id):
    """Create PetPoint profile and report links"""
    profile_link = f"https://sms.petpoint.com/sms3/enhanced/animal/{animal_id}"
    report_link = f"https://sms.petpoint.com/sms3/embeddedreports/animalviewreport.aspx?AnimalID={animal_id}"
    
    return f"[Profile]({profile_link}) | [Report]({report_link})"

def main():
    # Header
    st.markdown('<h1 class="main-header">🐾 SPCA Foster Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        animal_inventory, foster_current = load_data()
    
    if animal_inventory is None:
        st.error("Unable to load data. Please check that the CSV files are in the '__Load Files Go Here__' folder.")
        return
    
    # Classify animals
    classified_data = classify_animals(animal_inventory, foster_current)
    
    if classified_data.empty:
        st.warning("No data available to display.")
        return
    
    # Filter data based on foster categories
    foster_categories = ['Needs Foster Now', 'Might Need Foster Soon', 'In Foster']
    selected_category = st.sidebar.radio(
        "Select Foster Category:",
        foster_categories,
        index=0
    )
    
    # Filter data
    filtered_data = classified_data[classified_data['Foster_Category'] == selected_category].copy()
    
    # Add multi-select filters in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Additional Filters")
    
    # Species filter
    if not filtered_data.empty and 'Species' in filtered_data.columns:
        species_options = sorted([str(species) for species in filtered_data['Species'].unique() if pd.notna(species)])
        selected_species = st.sidebar.multiselect(
            "Species",
            species_options,
            help="Select species to display"
        )
        if selected_species:
            filtered_data = filtered_data[filtered_data['Species'].astype(str).isin(selected_species)]
    
    # Stage filter
    if not filtered_data.empty and 'Stage' in filtered_data.columns:
        stage_options = sorted([str(stage) for stage in filtered_data['Stage'].unique() if pd.notna(stage)])
        selected_stages = st.sidebar.multiselect(
            "Stage",
            stage_options,
            help="Select stages to display"
        )
        if selected_stages:
            filtered_data = filtered_data[filtered_data['Stage'].astype(str).isin(selected_stages)]
    
    # Foster Name filter (for animals in foster)
    if selected_category == 'In Foster' and not filtered_data.empty and 'Foster_Name' in filtered_data.columns:
        foster_name_options = sorted([name for name in filtered_data['Foster_Name'].unique() if name and name != 'nan'])
        if foster_name_options:
            selected_foster_names = st.sidebar.multiselect(
                "Foster Name",
                foster_name_options,
                help="Select foster parents to display"
            )
            if selected_foster_names:
                filtered_data = filtered_data[filtered_data['Foster_Name'].isin(selected_foster_names)]
    
    # Show filter summary
    if len(filtered_data) != len(classified_data[classified_data['Foster_Category'] == selected_category]):
        st.sidebar.markdown("---")
        st.sidebar.info(f"📊 Showing {len(filtered_data)} of {len(classified_data[classified_data['Foster_Category'] == selected_category])} animals")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        needs_foster = len(classified_data[classified_data['Foster_Category'] == 'Needs Foster Now'])
        st.metric("Needs Foster Now", needs_foster)
    
    with col2:
        might_need = len(classified_data[classified_data['Foster_Category'] == 'Might Need Foster Soon'])
        st.metric("Might Need Foster Soon", might_need)
    
    with col3:
        in_foster = len(classified_data[classified_data['Foster_Category'] == 'In Foster'])
        st.metric("Currently in Foster", in_foster)
    
    with col4:
        total_animals = len(classified_data)
        st.metric("Total Animals", total_animals)
    
    st.markdown("---")
    
    # Display filtered data
    if not filtered_data.empty:
        st.subheader(f"Animals: {selected_category}")
        
        # Select columns to display - map to actual column names
        display_columns = ['AnimalNumber', 'AnimalName', 'IntakeDateTime', 'Species', 'PrimaryBreed', 'Sex', 'Age', 'Stage', 'Foster_PID', 'Foster_Name']
        
        # Filter to only include columns that exist
        available_columns = [col for col in display_columns if col in filtered_data.columns]
        
        # Create display data
        display_data = filtered_data[available_columns].copy()
        
        # Sort data - check what columns are available for sorting
        sort_column = None
        if 'IntakeDateTime' in filtered_data.columns:
            sort_column = 'IntakeDateTime'
        elif 'AnimalName' in filtered_data.columns:
            sort_column = 'AnimalName'
        elif 'AnimalNumber' in filtered_data.columns:
            sort_column = 'AnimalNumber'
        
        if sort_column and sort_column in filtered_data.columns:
            try:
                if sort_column == 'IntakeDateTime':
                    display_data = display_data.sort_values(sort_column, ascending=False)
                else:
                    display_data = display_data.sort_values(sort_column)
            except Exception as e:
                st.warning(f"Could not sort by {sort_column}: {str(e)}")
        
        # Create clickable links using HTML (like rodent app)
        display_data['AnimalNumber'] = display_data['AnimalNumber'].apply(create_clickable_link)
        display_data['Foster_PID'] = display_data['Foster_PID'].apply(create_clickable_pid_link)
        
        # Rename columns for display
        column_mapping = {
            'AnimalNumber': 'Animal ID',
            'AnimalName': 'Animal Name',
            'IntakeDateTime': 'Intake Date/Time',
            'Species': 'Species',
            'PrimaryBreed': 'Breed',
            'Sex': 'Sex',
            'Age': 'Age',
            'Stage': 'Stage',
            'Foster_PID': 'Foster PID',
            'Foster_Name': 'Foster Name'
        }
        
        display_data = display_data.rename(columns=column_mapping)
        
        # Display the data with HTML rendering (like rodent app)
        st.write("**Note:** Click on Animal ID or Foster PID to open in PetPoint")
        
        # Add CSS for better table styling
        st.markdown("""
        <style>
        .foster-table {
            border-collapse: collapse;
            width: 100%;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
        }
        .foster-table th {
            background-color: #f0f2f6;
            padding: 8px;
            text-align: left;
            border-bottom: 2px solid #e0e0e0;
            font-weight: 600;
        }
        .foster-table td {
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        .foster-table tr:hover {
            background-color: #f8f9fa;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(
            display_data.to_html(
                escape=False,
                index=False,
                classes=['foster-table'],
                table_id='foster-table'
            ),
            unsafe_allow_html=True
        )
        
        # Download button
        # Create a clean version for download (without HTML links)
        download_data = filtered_data[available_columns].copy()
        download_data = download_data.rename(columns=column_mapping)
        
        csv = download_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"foster_dashboard_{selected_category.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.info(f"No animals found in the '{selected_category}' category.")
    
    # Data quality information
    with st.expander("Data Quality Information"):
        st.write(f"**Total records loaded:** {len(animal_inventory)}")
        st.write(f"**Foster records loaded:** {len(foster_current) if foster_current is not None else 0}")
        
        if not classified_data.empty:
            category_counts = classified_data['Foster_Category'].value_counts()
            st.write("**Classification breakdown:**")
            for category, count in category_counts.items():
                st.write(f"- {category}: {count}")
        
        # Show sample of raw data
        st.write("**Sample of raw data:**")
        st.dataframe(animal_inventory.head(), use_container_width=True)

if __name__ == "__main__":
    main() 