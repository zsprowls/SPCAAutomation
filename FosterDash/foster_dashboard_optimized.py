import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="SPCA Foster Dashboard (Optimized)",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import os
from datetime import datetime
import numpy as np
from supabase_manager import supabase_manager

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
    .foster-notes-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .foster-plea-dates {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Supabase Configuration
def initialize_supabase():
    """Initialize Supabase connection"""
    # Check if Supabase credentials are set
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    supabase_key = st.secrets.get("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        st.warning("⚠️ Supabase credentials not configured. Database features will be disabled.")
        st.info("To enable database features, set SUPABASE_URL and SUPABASE_KEY in your Streamlit secrets.")
        return False
    
    # Initialize Supabase
    if supabase_manager.initialize(supabase_url, supabase_key):
        return True
    else:
        st.error("❌ Failed to initialize Supabase connection")
        return False

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load and process the CSV files with optimized loading"""
    try:
        # Load AnimalInventory.csv - try multiple possible paths
        possible_paths = [
            "FosterDash/data/AnimalInventory.csv",  # Streamlit Cloud
            "data/AnimalInventory.csv",  # Streamlit Cloud (alternative)
            "../__Load Files Go Here__/AnimalInventory.csv",  # Local development
            "AnimalInventory.csv"  # Current directory
        ]
        
        animal_inventory_path = None
        for path in possible_paths:
            if os.path.exists(path):
                animal_inventory_path = path
                break
        
        if animal_inventory_path:
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
            st.error(f"Tried paths: {possible_paths}")
            st.error(f"Current working directory: {os.getcwd()}")
            return None, None, None
        
        # Load FosterCurrent.csv - try multiple possible paths
        foster_possible_paths = [
            "FosterDash/data/FosterCurrent.csv",  # Streamlit Cloud
            "data/FosterCurrent.csv",  # Streamlit Cloud (alternative)
            "../__Load Files Go Here__/FosterCurrent.csv",  # Local development
            "FosterCurrent.csv"  # Current directory
        ]
        
        foster_current_path = None
        for path in foster_possible_paths:
            if os.path.exists(path):
                foster_current_path = path
                break
        
        if foster_current_path:
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
            st.warning(f"Tried paths: {foster_possible_paths}")
            foster_current = pd.DataFrame()
        
        # Load Hold - Foster Stage Date.csv - try multiple possible paths
        hold_possible_paths = [
            "FosterDash/data/Hold - Foster Stage Date.csv",  # Streamlit Cloud
            "data/Hold - Foster Stage Date.csv",  # Streamlit Cloud (alternative)
            "../__Load Files Go Here__/Hold - Foster Stage Date.csv",  # Local development
            "Hold - Foster Stage Date.csv"  # Current directory
        ]
        
        hold_foster_path = None
        for path in hold_possible_paths:
            if os.path.exists(path):
                hold_foster_path = path
                break
        
        if hold_foster_path:
            # Skip first 2 rows and start from row 3 where headers are
            try:
                hold_foster_data = pd.read_csv(hold_foster_path, encoding='utf-8', skiprows=2)
            except:
                try:
                    hold_foster_data = pd.read_csv(hold_foster_path, encoding='latin-1', skiprows=2)
                except:
                    # Try with different delimiter and quoting options
                    hold_foster_data = pd.read_csv(hold_foster_path, encoding='utf-8', 
                                                 skiprows=2, quoting=3, on_bad_lines='skip')
            
            st.success(f"✅ Successfully loaded Hold - Foster Stage Date.csv ({len(hold_foster_data)} records)")
        else:
            st.warning(f"⚠️ Hold - Foster Stage Date.csv not found!")
            st.warning(f"Tried paths: {hold_possible_paths}")
            hold_foster_data = pd.DataFrame()
        
        return animal_inventory, foster_current, hold_foster_data
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.error(f"Current working directory: {os.getcwd()}")
        return None, None, None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def classify_animals_optimized(animal_inventory, foster_current, hold_foster_data):
    """Optimized version of classify_animals using vectorized operations"""
    if animal_inventory is None:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying original data
    df = animal_inventory.copy()
    
    # Initialize category column and foster info columns
    df['Foster_Category'] = 'Other'
    df['Foster_PID'] = ''
    df['Foster_Name'] = ''
    df['Hold_Foster_Date'] = ''
    df['Foster_Start_Date'] = ''
    
    # Create mappings for faster lookup
    foster_info = {}
    hold_foster_dates = {}
    
    # Process foster_current data
    if not foster_current.empty:
        # Find the animal ID column
        animal_id_col = None
        for col in ['textbox9', 'ARN', 'AnimalNumber']:
            if col in foster_current.columns:
                animal_id_col = col
                break
        
        if animal_id_col:
            # Create foster info mapping using vectorized operations
            foster_current_clean = foster_current.dropna(subset=[animal_id_col])
            foster_current_clean['AnimalID'] = foster_current_clean[animal_id_col].astype(str)
            
            # Create foster info dictionary
            for _, row in foster_current_clean.iterrows():
                animal_id = str(row[animal_id_col])
                stage = str(row.get('Stage', '')).strip()
                
                # Only add to foster_animal_ids if it's NOT an If The Fur Fits stage
                if not any(fur_fits_stage in stage for fur_fits_stage in [
                    'In If the Fur Fits - Trial', 'In If the Fur Fits - Behavior', 'In If the Fur Fits - Medical'
                ]):
                    foster_info[animal_id] = {
                        'pid': str(row.get('textbox10', '')),
                        'name': str(row.get('textbox11', '')),
                        'start_date': str(row.get('StartStatusDate', '')),
                        'is_foster': True
                    }
                else:
                    foster_info[animal_id] = {
                        'pid': str(row.get('textbox10', '')),
                        'name': str(row.get('textbox11', '')),
                        'start_date': str(row.get('StartStatusDate', '')),
                        'is_foster': False
                    }
    
    # Process hold_foster_data
    if not hold_foster_data.empty:
        if len(hold_foster_data.columns) >= 3:
            animal_id_col = hold_foster_data.columns[0]
            stage_col = hold_foster_data.columns[1]
            date_col = hold_foster_data.columns[2]
            
            # Filter for Hold - Foster stages and create mapping
            hold_foster_filtered = hold_foster_data[
                hold_foster_data[stage_col].str.contains('Hold - Foster|Hold - Cruelty Foster|Hold - SAFE Foster', 
                                                       case=False, na=False)
            ]
            
            for _, row in hold_foster_filtered.iterrows():
                animal_id = str(row[animal_id_col])
                stage_start_date = str(row.get(date_col, ''))
                
                if stage_start_date and stage_start_date != 'nan':
                    hold_foster_dates[animal_id] = stage_start_date
    
    # Vectorized classification using numpy operations
    df['AnimalID'] = df['AnimalNumber'].astype(str)
    df['Stage'] = df['Stage'].astype(str)
    
    # Create boolean masks for different categories
    fur_fits_mask = df['Stage'].str.contains('In If the Fur Fits', case=False, na=False)
    foster_mask = df['AnimalID'].isin([aid for aid, info in foster_info.items() if info.get('is_foster', False)])
    hold_foster_mask = df['AnimalID'].isin(hold_foster_dates.keys())
    
    # Apply classifications
    df.loc[fur_fits_mask, 'Foster_Category'] = 'In If The Fur Fits'
    df.loc[foster_mask, 'Foster_Category'] = 'In Foster'
    df.loc[hold_foster_mask, 'Foster_Category'] = 'Needs Foster Now'
    
    # Add foster info using vectorized operations
    for animal_id, info in foster_info.items():
        mask = df['AnimalID'] == animal_id
        if mask.any():
            df.loc[mask, 'Foster_PID'] = info['pid']
            df.loc[mask, 'Foster_Name'] = info['name']
            df.loc[mask, 'Foster_Start_Date'] = info['start_date']
    
    # Add hold foster dates
    for animal_id, date in hold_foster_dates.items():
        mask = df['AnimalID'] == animal_id
        if mask.any():
            df.loc[mask, 'Hold_Foster_Date'] = date
    
    # Clean up
    df = df.drop('AnimalID', axis=1)
    
    return df

def create_clickable_link(animal_id):
    """Create clickable link for animal ID"""
    if pd.isna(animal_id) or animal_id == '':
        return ''
    return f'<a href="https://petpoint.spca.org/animal/{animal_id}" target="_blank" class="animal-link">{animal_id}</a>'

def create_clickable_pid_link(pid):
    """Create clickable link for PID"""
    if pd.isna(pid) or pid == '':
        return ''
    return f'<a href="https://petpoint.spca.org/person/{pid}" target="_blank" class="animal-link">{pid}</a>'

def main():
    # Header
    st.markdown('<h1 class="main-header">🐾 SPCA Foster Dashboard (Optimized)</h1>', unsafe_allow_html=True)
    
    # Initialize Supabase
    supabase_enabled = initialize_supabase()
    
    # Load data with progress indicator
    with st.spinner("Loading data..."):
        animal_inventory, foster_current, hold_foster_data = load_data()
        
        # Sync AnimalNumbers with Supabase if enabled
        if supabase_enabled and animal_inventory is not None:
            with st.spinner("Syncing with database..."):
                supabase_manager.sync_animal_numbers(animal_inventory)
    
    if animal_inventory is None:
        st.error("Unable to load data. Please check that the CSV files are in the '__Load Files Go Here__' folder.")
        return
    
    # Classify animals with progress indicator
    with st.spinner("Processing data..."):
        classified_data = classify_animals_optimized(animal_inventory, foster_current, hold_foster_data)
    
    if classified_data.empty:
        st.warning("No data available to display.")
        return
    
    # Database Status
    if supabase_enabled:
        st.sidebar.success("✅ Database Connected")
    else:
        st.sidebar.warning("⚠️ Database Disabled")
    
    # Create view selector
    view_option = st.sidebar.radio(
        "Select View:",
        ["Foster Animals", "Foster Database"],
        index=0
    )
    
    if view_option == "Foster Animals":
        # Filter data based on foster categories
        foster_categories = ['Needs Foster Now', 'Pending Foster Pickup', 'In Foster', 'In If The Fur Fits', 'Might Need Foster Soon']
        selected_category = st.sidebar.radio(
            "Select Foster Category:",
            foster_categories,
            index=0
        )
    
        # Filter data
        filtered_data = classified_data[classified_data['Foster_Category'] == selected_category].copy()
        
        if filtered_data.empty:
            st.info(f"No animals found in the '{selected_category}' category.")
            return
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Animals", len(filtered_data))
        with col2:
            species_count = filtered_data['Species'].nunique()
            st.metric("Species", species_count)
        with col3:
            stage_count = filtered_data['Stage'].nunique()
            st.metric("Stages", stage_count)
        
        # Display the data
        st.subheader(f"Animals in '{selected_category}' Category")
        
        # Create clickable links
        filtered_data['AnimalNumber'] = filtered_data['AnimalNumber'].apply(create_clickable_link)
        filtered_data['Foster_PID'] = filtered_data['Foster_PID'].apply(create_clickable_pid_link)
        
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
            'Foster_Name': 'Foster Name',
            'Hold_Foster_Date': 'Hold - Foster Date',
            'Foster_Start_Date': 'Foster Start Date'
        }
        
        display_data = filtered_data.rename(columns=column_mapping)
        
        # Display the data
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )
    
    else:
        st.subheader("Foster Database")
        st.info("This view will show database functionality when Supabase is configured.")

if __name__ == "__main__":
    main() 