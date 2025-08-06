import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="SPCA Foster Dashboard",
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

@st.cache_data
def load_foster_parents_data():
    """Load foster parents data from the Excel file"""
    try:
        # Try multiple possible paths for Excel file
        excel_possible_paths = [
            "FosterDash/data/Looking for Foster Care 2025.xlsx",  # Streamlit Cloud
            "data/Looking for Foster Care 2025.xlsx",  # Streamlit Cloud (alternative)
            "../__Load Files Go Here__/Looking for Foster Care 2025.xlsx",  # Local development
            "Looking for Foster Care 2025.xlsx"  # Current directory
        ]
        
        excel_path = None
        for path in excel_possible_paths:
            if os.path.exists(path):
                excel_path = path
                break
        
        if excel_path:
            # Read the "Available Foster Parents" tab
            df = pd.read_excel(excel_path, sheet_name="Available Foster Parents")
            
            # Clean up the data
            df = df.dropna(subset=['PID'])  # Remove rows without PID
            
            # Convert PID to full format (match FosterCurrent format)
            def format_pid(pid):
                if pd.isna(pid):
                    return ''
                
                # Convert to string first
                pid_str = str(pid).strip()
                
                # If it already starts with 'P', return as-is (it's already in correct format)
                if pid_str.startswith('P'):
                    return pid_str
                
                # Try to convert to int to remove any decimal places
                try:
                    pid_int = int(float(pid_str))  # Handle decimal numbers
                    numeric_part = str(pid_int)
                except (ValueError, TypeError):
                    # If conversion fails, use the original string
                    numeric_part = pid_str
                
                # If it's 8 digits, add P00 prefix to match FosterCurrent format
                if len(numeric_part) == 8:
                    return f"P00{numeric_part}"
                else:
                    # For other lengths, pad to 9 digits after P
                    numeric_part = numeric_part.zfill(9)
                    return f"P{numeric_part}"
            
            df['Full_PID'] = df['PID'].apply(format_pid)
            
            # Clean up column names and data
            df['Last Name'] = df['Last Name'].fillna('')
            df['First Name'] = df['First Name'].fillna('')
            df['Phone Number'] = df['Phone Number'].fillna('')
            df['Foster Request/Animal Preference'] = df['Foster Request/Animal Preference'].fillna('')
            df['Availability/Notes'] = df['Availability/Notes'].fillna('')
            
            # Create full name
            df['Full_Name'] = df['First Name'] + ' ' + df['Last Name']
            df['Full_Name'] = df['Full_Name'].str.strip()
            
            st.success(f"✅ Successfully loaded foster parents data ({len(df)} records)")
            return df
        else:
            st.error(f"❌ Excel file not found!")
            st.error(f"Tried paths: {excel_possible_paths}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Error loading foster parents data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_bottle_fed_kittens_data():
    """Load Emergency Bottle Baby Fosters data from the Excel file"""
    try:
        # Try multiple possible paths for Excel file
        excel_possible_paths = [
            "FosterDash/data/Looking for Foster Care 2025.xlsx",  # Streamlit Cloud
            "data/Looking for Foster Care 2025.xlsx",  # Streamlit Cloud (alternative)
            "../__Load Files Go Here__/Looking for Foster Care 2025.xlsx",  # Local development
            "Looking for Foster Care 2025.xlsx"  # Current directory
        ]
        
        excel_path = None
        for path in excel_possible_paths:
            if os.path.exists(path):
                excel_path = path
                break
        
        if excel_path:
            # Read the "Emergency Bottle Fed Kittens" tab
            df = pd.read_excel(excel_path, sheet_name="Emergency Bottle Fed Kittens")
            
            # The actual structure has unnamed columns, so we need to handle this properly
            # Skip the first row (header) and use the second row as column names
            df = df.iloc[1:].reset_index(drop=True)
            
            # Rename columns based on the actual structure
            df.columns = ['First Name', 'Last Name', 'PID', 'Phone Number', 'Notes']
            
            # Clean up the data - remove rows without PID or with empty names
            df = df.dropna(subset=['PID', 'First Name', 'Last Name'], how='all')
            
            # Convert PID to full format (match FosterCurrent format)
            def format_pid(pid):
                if pd.isna(pid):
                    return ''
                
                # Convert to string first
                pid_str = str(pid).strip()
                
                # If it already starts with 'P', return as-is (it's already in correct format)
                if pid_str.startswith('P'):
                    return pid_str
                
                # Try to convert to int to remove any decimal places
                try:
                    pid_int = int(float(pid_str))  # Handle decimal numbers
                    numeric_part = str(pid_int)
                except (ValueError, TypeError):
                    # If conversion fails, use the original string
                    numeric_part = pid_str
                
                # If it's 8 digits, add P00 prefix to match FosterCurrent format
                if len(numeric_part) == 8:
                    return f"P00{numeric_part}"
                else:
                    # For other lengths, pad to 9 digits after P
                    numeric_part = numeric_part.zfill(9)
                    return f"P{numeric_part}"
            
            df['Full_PID'] = df['PID'].apply(format_pid)
            
            # Clean up column names and data
            df['Last Name'] = df['Last Name'].fillna('')
            df['First Name'] = df['First Name'].fillna('')
            df['Phone Number'] = df['Phone Number'].fillna('')
            df['Notes'] = df['Notes'].fillna('')
            
            # Add missing columns to match the expected structure
            df['Foster Request/Animal Preference'] = 'Bottle Fed Kittens'
            df['Availability/Notes'] = df['Notes']
            
            # Create full name
            df['Full_Name'] = df['First Name'] + ' ' + df['Last Name']
            df['Full_Name'] = df['Full_Name'].str.strip()
            
            st.success(f"✅ Successfully loaded bottle fed kittens data ({len(df)} records)")
            return df
        else:
            st.error(f"❌ Excel file not found!")
            st.error(f"Tried paths: {excel_possible_paths}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Error loading bottle fed kittens data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_panleuk_positive_pids():
    """Load Panleuk Positive PIDs from the Excel file"""
    try:
        # Try multiple possible paths for Excel file
        excel_possible_paths = [
            "FosterDash/data/Looking for Foster Care 2025.xlsx",  # Streamlit Cloud
            "data/Looking for Foster Care 2025.xlsx",  # Streamlit Cloud (alternative)
            "../__Load Files Go Here__/Looking for Foster Care 2025.xlsx",  # Local development
            "Looking for Foster Care 2025.xlsx"  # Current directory
        ]
        
        excel_path = None
        for path in excel_possible_paths:
            if os.path.exists(path):
                excel_path = path
                break
        
        if excel_path:
            # Read the "Panleuk. POSITIVES" tab
            df = pd.read_excel(excel_path, sheet_name="Panleuk. POSITIVES")
            
            # Clean up the data
            df = df.dropna(subset=['PID'])  # Remove rows without PID
            
            # Convert PID to full format (match FosterCurrent format)
            def format_pid(pid):
                if pd.isna(pid):
                    return ''
                
                # Convert to string first
                pid_str = str(pid).strip()
                
                # If it already starts with 'P', return as-is (it's already in correct format)
                if pid_str.startswith('P'):
                    return pid_str
                
                # Try to convert to int to remove any decimal places
                try:
                    pid_int = int(float(pid_str))  # Handle decimal numbers
                    numeric_part = str(pid_int)
                except (ValueError, TypeError):
                    # If conversion fails, use the original string
                    numeric_part = pid_str
                
                # If it's 8 digits, add P00 prefix to match FosterCurrent format
                if len(numeric_part) == 8:
                    return f"P00{numeric_part}"
                else:
                    # For other lengths, pad to 9 digits after P
                    numeric_part = numeric_part.zfill(9)
                    return f"P{numeric_part}"
            
            df['Full_PID'] = df['PID'].apply(format_pid)
            
            # Get list of Panleuk Positive PIDs
            panleuk_pids = set(df['Full_PID'].tolist())
            
            st.success(f"✅ Successfully loaded Panleuk Positive PIDs ({len(panleuk_pids)} records)")
            return panleuk_pids
        else:
            st.error(f"❌ Excel file not found!")
            st.error(f"Tried paths: {excel_possible_paths}")
            return set()
            
    except Exception as e:
        st.error(f"❌ Error loading Panleuk Positive PIDs: {str(e)}")
        return set()

@st.cache_data
def load_data():
    """Load and process the CSV files"""
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

def get_foster_parent_animals(foster_parents_df, foster_current_df):
    """Get current animals for each foster parent"""
    foster_parent_animals = {}
    missing_pids = set()
    
    if foster_current_df.empty:
        return foster_parent_animals, missing_pids
    
    # Find the animal ID column in foster current data
    animal_id_col = None
    for col in ['textbox9', 'ARN', 'AnimalNumber']:
        if col in foster_current_df.columns:
            animal_id_col = col
            break
    
    if not animal_id_col:
        return foster_parent_animals, missing_pids
    
    # Get all PIDs from foster parents database
    database_pids = set(foster_parents_df['Full_PID'].tolist())
    
    # Group animals by foster parent PID
    for idx, row in foster_current_df.iterrows():
        animal_id = str(row[animal_id_col])
        foster_pid = str(row.get('textbox10', ''))  # PID column
        
        if foster_pid and foster_pid != 'nan':
            # The PID in FosterCurrent is already in full format (e.g., P0047897436)
            # Just use it as-is for matching
            full_pid = foster_pid
            
            if full_pid not in foster_parent_animals:
                foster_parent_animals[full_pid] = []
            
            foster_parent_animals[full_pid].append(animal_id)
            
            # Check if this PID is missing from our database
            if full_pid not in database_pids:
                missing_pids.add(full_pid)
    
    return foster_parent_animals, missing_pids

def classify_animals(animal_inventory, foster_current, hold_foster_data):
    """Classify animals into foster categories"""
    if animal_inventory is None:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying original data
    df = animal_inventory.copy()
    
    # Initialize category column and foster info columns
    df['Foster_Category'] = 'Other'
    df['Foster_PID'] = ''
    df['Foster_Name'] = ''
    df['Hold_Foster_Date'] = ''  # New column for Hold - Foster date
    df['Foster_Start_Date'] = ''  # New column for Foster Start Date
    
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
                
                # Get the stage to check if it's If The Fur Fits
                stage = str(row.get('Stage', '')).strip()
                
                # Only add to foster_animal_ids if it's NOT an If The Fur Fits stage
                if not any(fur_fits_stage in stage for fur_fits_stage in [
                    'In If the Fur Fits - Trial', 'In If the Fur Fits - Behavior', 'In If the Fur Fits - Medical'
                ]):
                    foster_animal_ids.add(animal_id)
                
                # Always add foster info for all animals (including If The Fur Fits)
                foster_pid = str(row.get('textbox10', ''))  # PID
                foster_name = str(row.get('textbox11', ''))  # Person's name
                foster_start_date = str(row.get('StartStatusDate', ''))  # Foster start date
                
                foster_info[animal_id] = {
                    'pid': foster_pid,
                    'name': foster_name,
                    'start_date': foster_start_date
                }
    
    # Create mapping of animal ID to Hold - Foster date
    hold_foster_dates = {}
    if not hold_foster_data.empty:
        # Check for Animal ID column in hold foster data
        animal_id_col = None
        stage_col = None
        date_col = None
        
        # Handle generic column names from the CSV file
        if len(hold_foster_data.columns) >= 3:
            # The file has columns: Count, Count.1, Count.2
            # These correspond to: Animal #, Stage, Stage Start Date
            animal_id_col = hold_foster_data.columns[0]  # First column
            stage_col = hold_foster_data.columns[1]      # Second column
            date_col = hold_foster_data.columns[2]       # Third column
        else:
            # Try to find columns by name
            for col in ['Animal #', 'AnimalNumber', 'AnimalID']:
                if col in hold_foster_data.columns:
                    animal_id_col = col
                    break
        
        if animal_id_col and stage_col and date_col:
            # Create a mapping of animal ID to Hold - Foster date
            for idx, row in hold_foster_data.iterrows():
                animal_id = str(row[animal_id_col])
                stage = str(row.get(stage_col, ''))
                stage_start_date = str(row.get(date_col, ''))
                
                # Include if it's any Hold - Foster stage and has a valid date
                if (stage_start_date and stage_start_date != 'nan' and 
                    any(hold_stage in stage for hold_stage in [
                        'Hold - Foster', 'Hold - Cruelty Foster', 'Hold - SAFE Foster'
                    ])):
                    hold_foster_dates[animal_id] = stage_start_date
    
    # Classify animals
    for idx, row in df.iterrows():
        animal_id = str(row.get('AnimalNumber', ''))
        stage = str(row.get('Stage', '')).strip()
        
        # Check if in If The Fur Fits program (check this FIRST)
        if any(fur_fits_stage in stage for fur_fits_stage in [
            'In If the Fur Fits - Trial', 'In If the Fur Fits - Behavior', 'In If the Fur Fits - Medical'
        ]):
            df.at[idx, 'Foster_Category'] = 'In If The Fur Fits'
            
            # Add foster person info if available
            if animal_id in foster_info:
                df.at[idx, 'Foster_PID'] = foster_info[animal_id]['pid']
                df.at[idx, 'Foster_Name'] = foster_info[animal_id]['name']
                df.at[idx, 'Foster_Start_Date'] = foster_info[animal_id]['start_date']
        
        # Check if pending foster pickup
        elif 'Pending Foster Pickup' in stage:
            df.at[idx, 'Foster_Category'] = 'Pending Foster Pickup'
            
            # Add foster person info if available
            if animal_id in foster_info:
                df.at[idx, 'Foster_PID'] = foster_info[animal_id]['pid']
                df.at[idx, 'Foster_Name'] = foster_info[animal_id]['name']
                df.at[idx, 'Foster_Start_Date'] = foster_info[animal_id]['start_date']
        
        # Check if in foster (excluding Pending Foster Pickup and If The Fur Fits)
        elif (animal_id in foster_animal_ids or 
              'In Foster' in stage or 
              'In SAFE Foster' in stage or 
              'In Cruelty Foster' in stage):
            df.at[idx, 'Foster_Category'] = 'In Foster'
            
            # Add foster person info if available
            if animal_id in foster_info:
                df.at[idx, 'Foster_PID'] = foster_info[animal_id]['pid']
                df.at[idx, 'Foster_Name'] = foster_info[animal_id]['name']
                df.at[idx, 'Foster_Start_Date'] = foster_info[animal_id]['start_date']
        
        # Check if needs foster now
        elif any(need_stage in stage for need_stage in [
            'Hold - Foster', 'Hold - Cruelty Foster', 'Hold - SAFE Foster'
        ]):
            df.at[idx, 'Foster_Category'] = 'Needs Foster Now'
            
            # Add Hold - Foster date if available (for any Hold - Foster stage)
            if animal_id in hold_foster_dates:
                df.at[idx, 'Hold_Foster_Date'] = hold_foster_dates[animal_id]
        
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

def handle_data_edit():
    """Handle data editor changes"""
    # This function will be called when the data editor changes
    pass

# These functions are no longer needed since we're using inline editing
# Keeping them for potential future use or reference

def main():
    # Header
    st.markdown('<h1 class="main-header">🐾 SPCA Foster Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize Supabase
    supabase_enabled = initialize_supabase()
    
    # Load data
    with st.spinner("Loading data..."):
        animal_inventory, foster_current, hold_foster_data = load_data()
        foster_parents_data = load_foster_parents_data()
        bottle_fed_kittens_data = load_bottle_fed_kittens_data()
        panleuk_positive_pids = load_panleuk_positive_pids()
        
        # Sync AnimalNumbers with Supabase if enabled
        if supabase_enabled and animal_inventory is not None:
            with st.spinner("Syncing with database..."):
                supabase_manager.sync_animal_numbers(animal_inventory)
    
    if animal_inventory is None:
        st.error("Unable to load data. Please check that the CSV files are in the '__Load Files Go Here__' folder.")
        return
    
    # Classify animals
    classified_data = classify_animals(animal_inventory, foster_current, hold_foster_data)
    
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
        if selected_category in ['In Foster', 'Pending Foster Pickup', 'In If The Fur Fits'] and not filtered_data.empty and 'Foster_Name' in filtered_data.columns:
            foster_name_options = sorted([name for name in filtered_data['Foster_Name'].unique() if name and name != 'nan'])
            if foster_name_options:
                selected_foster_names = st.sidebar.multiselect(
                    "Foster Name",
                    foster_name_options,
                    help="Select foster parents to display"
                )
                if selected_foster_names:
                    filtered_data = filtered_data[filtered_data['Foster_Name'].isin(selected_foster_names)]
        
        # Hold - Foster Date filter (for "Needs Foster Now" category)
        if selected_category == 'Needs Foster Now' and not filtered_data.empty and 'Hold_Foster_Date' in filtered_data.columns:
            # Get unique Hold - Foster Dates, excluding NaN values
            hold_dates = filtered_data['Hold_Foster_Date'].dropna().unique()
            if len(hold_dates) > 0:
                # Convert to string and sort
                hold_date_options = sorted([str(date) for date in hold_dates if pd.notna(date)])
                selected_hold_dates = st.sidebar.multiselect(
                    "Hold - Foster Date",
                    hold_date_options,
                    help="Select Hold - Foster dates to display"
                )
                if selected_hold_dates:
                    filtered_data = filtered_data[filtered_data['Hold_Foster_Date'].astype(str).isin(selected_hold_dates)]
        
        # Foster Start Date filter (for "In Foster" and "In If The Fur Fits" categories)
        if selected_category in ['In Foster', 'In If The Fur Fits'] and not filtered_data.empty and 'Foster_Start_Date' in filtered_data.columns:
            # Get unique Foster Start Dates, excluding NaN values
            foster_start_dates = filtered_data['Foster_Start_Date'].dropna().unique()
            if len(foster_start_dates) > 0:
                # Convert to string and sort
                foster_start_date_options = sorted([str(date) for date in foster_start_dates if pd.notna(date)])
                selected_foster_start_dates = st.sidebar.multiselect(
                    "Foster Start Date",
                    foster_start_date_options,
                    help="Select Foster Start dates to display"
                )
                if selected_foster_start_dates:
                    filtered_data = filtered_data[filtered_data['Foster_Start_Date'].astype(str).isin(selected_foster_start_dates)]
        
        # Show filter summary
        if len(filtered_data) != len(classified_data[classified_data['Foster_Category'] == selected_category]):
            st.sidebar.markdown("---")
            st.sidebar.info(f"📊 Showing {len(filtered_data)} of {len(classified_data[classified_data['Foster_Category'] == selected_category])} animals")
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            needs_foster = len(classified_data[classified_data['Foster_Category'] == 'Needs Foster Now'])
            st.metric("Needs Foster Now", needs_foster)
        
        with col2:
            pending_pickup = len(classified_data[classified_data['Foster_Category'] == 'Pending Foster Pickup'])
            st.metric("Pending Pickup", pending_pickup)
        
        with col3:
            in_foster = len(classified_data[classified_data['Foster_Category'] == 'In Foster'])
            st.metric("In Foster", in_foster)
        
        with col4:
            in_fur_fits = len(classified_data[classified_data['Foster_Category'] == 'In If The Fur Fits'])
            st.metric("In If The Fur Fits", in_fur_fits)
        
        with col5:
            might_need = len(classified_data[classified_data['Foster_Category'] == 'Might Need Foster Soon'])
            st.metric("Might Need Soon", might_need)
        
        st.markdown("---")
        
        # Display filtered data
        if not filtered_data.empty:
            st.subheader(f"Animals: {selected_category}")
            
            # Get foster data from Supabase if enabled
            foster_data_dict = {}
            if supabase_enabled:
                foster_data_dict = supabase_manager.get_all_foster_data()
            
            # Select columns to display - map to actual column names
            display_columns = ['AnimalNumber', 'AnimalName', 'IntakeDateTime', 'Species', 'PrimaryBreed', 'Sex', 'Age', 'Stage', 'Foster_PID', 'Foster_Name']
            
            # Add Hold - Foster Date column for "Needs Foster Now" category
            if selected_category == 'Needs Foster Now':
                display_columns.append('Hold_Foster_Date')
            
            # Add Foster Start Date column for "In Foster" and "In If The Fur Fits" categories
            if selected_category in ['In Foster', 'In If The Fur Fits']:
                display_columns.append('Foster_Start_Date')
            
            # Filter to only include columns that exist
            available_columns = [col for col in display_columns if col in filtered_data.columns]
            
            # Create display data
            display_data = filtered_data[available_columns].copy()
            
            # Sort data - check what columns are available for sorting
            sort_column = None
            if selected_category == 'Needs Foster Now' and 'Hold_Foster_Date' in filtered_data.columns:
                # For "Needs Foster Now" category, sort by Hold - Foster Date
                sort_column = 'Hold_Foster_Date'
            elif selected_category in ['In Foster', 'In If The Fur Fits'] and 'Foster_Start_Date' in filtered_data.columns:
                # For "In Foster" and "In If The Fur Fits" categories, sort by Foster Start Date
                sort_column = 'Foster_Start_Date'
            elif 'IntakeDateTime' in filtered_data.columns:
                sort_column = 'IntakeDateTime'
            elif 'AnimalName' in filtered_data.columns:
                sort_column = 'AnimalName'
            elif 'AnimalNumber' in filtered_data.columns:
                sort_column = 'AnimalNumber'
            
            if sort_column and sort_column in filtered_data.columns:
                try:
                    if sort_column == 'IntakeDateTime':
                        display_data = display_data.sort_values(sort_column, ascending=False)
                    elif sort_column == 'Hold_Foster_Date':
                        # Sort Hold - Foster Date in ascending order (earliest dates first)
                        display_data = display_data.sort_values(sort_column, ascending=True)
                    elif sort_column == 'Foster_Start_Date':
                        # Sort Foster Start Date in ascending order (earliest dates first)
                        display_data = display_data.sort_values(sort_column, ascending=True)
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
                'Foster_Name': 'Foster Name',
                'Hold_Foster_Date': 'Hold - Foster Date',
                'Foster_Start_Date': 'Foster Start Date'
            }
            
            display_data = display_data.rename(columns=column_mapping)
            
            # Keep the original HTML links for Animal ID - they work properly in HTML tables
            # The Animal ID column should already be HTML links from the original data processing
            
            # Add interactive columns to the display data
            # Always add the columns, regardless of database status
            display_data['Foster_Notes'] = 'Database Required'
            display_data['On_Meds'] = False
            if selected_category == 'Needs Foster Now':
                display_data['Foster_Plea_Dates'] = 'Database Required'
            

            
            # If database is enabled, populate with real data
            if supabase_enabled:
                # Use the original filtered_data to get AnimalNumber (before HTML conversion)
                for idx, row in filtered_data.iterrows():
                    animal_number = str(row['AnimalNumber'])
                    foster_data = foster_data_dict.get(animal_number, {})
                    
                    # Find the corresponding row in display_data by matching Animal ID
                    # Make sure we don't go out of bounds
                    if idx < len(display_data):
                        animal_id_in_display = display_data.iloc[idx]['Animal ID']
                        # Extract animal number from clean format
                        display_animal_number = str(animal_id_in_display)
                        
                        # Only update if the animal numbers match
                        if display_animal_number == animal_number:
                            # Update the interactive columns with real data
                            display_data.iloc[idx, display_data.columns.get_loc('Foster_Notes')] = foster_data.get('fosternotes', '')
                            display_data.iloc[idx, display_data.columns.get_loc('On_Meds')] = foster_data.get('onmeds', False)
                            
                            if selected_category == 'Needs Foster Now':
                                dates = foster_data.get('fosterpleadates', [])
                                display_data.iloc[idx, display_data.columns.get_loc('Foster_Plea_Dates')] = ', '.join(dates) if dates else ''
            
            # Update column mapping to include new columns
            column_mapping.update({
                'Foster_Notes': '📝 Foster Notes',
                'On_Meds': '💊 On Meds',
                'Foster_Plea_Dates': '📅 Foster Plea Dates'
            })
            
            # Reorder columns to put interactive columns at the end
            if 'Foster_Plea_Dates' in display_data.columns:
                # For "Needs Foster Now" category, include plea dates
                final_columns = [col for col in display_data.columns if col not in ['Foster_Notes', 'On_Meds', 'Foster_Plea_Dates']] + ['Foster_Notes', 'On_Meds', 'Foster_Plea_Dates']
            else:
                # For other categories, just include notes and meds
                final_columns = [col for col in display_data.columns if col not in ['Foster_Notes', 'On_Meds']] + ['Foster_Notes', 'On_Meds']
            
            display_data = display_data[final_columns]
            
            # Show database status
            if not supabase_enabled:
                st.warning("⚠️ Database features are disabled. Set up Supabase to enable interactive editing.")
                st.info("📝 To enable interactive features:")
                st.write("1. Follow the setup guide in SUPABASE_SETUP.md")
                st.write("2. Update .streamlit/secrets.toml with your Supabase credentials")
                st.write("3. Restart the dashboard")
            
            # Custom inline editing solution with working links
            st.write("**💡 Click any cell to edit. Press Enter to save. Click Animal ID or Foster PID to open PetPoint.**")
            
            # Add CSS for the custom grid
            st.markdown("""
            <style>
            .custom-grid {
                display: grid;
                grid-template-columns: 120px 150px 120px 200px 100px 120px 200px 100px 150px;
                gap: 8px;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 8px;
                margin-bottom: 16px;
            }
            .grid-header {
                background-color: #e9ecef;
                padding: 8px;
                font-weight: 600;
                text-align: center;
                border-radius: 4px;
                font-size: 12px;
            }
            .grid-cell {
                background-color: white;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #dee2e6;
                font-size: 12px;
                min-height: 20px;
                display: flex;
                align-items: center;
            }
            .grid-cell a {
                color: #1f77b4;
                text-decoration: none;
                font-weight: 500;
            }
            .grid-cell a:hover {
                text-decoration: underline;
            }
            .editable-cell {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create header row
            st.markdown("""
            <div class="custom-grid">
                <div class="grid-header">Animal ID</div>
                <div class="grid-header">Animal Name</div>
                <div class="grid-header">Intake Date</div>
                <div class="grid-header">Animal Details</div>
                <div class="grid-header">Stage</div>
                <div class="grid-header">Foster PID</div>
                <div class="grid-header">📝 Foster Notes</div>
                <div class="grid-header">💊 On Meds</div>
                <div class="grid-header">📅 Foster Plea Dates</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create data rows with inline editing
            for idx, row in display_data.iterrows():
                # Extract animal number for database operations
                animal_id = str(row['Animal ID'])
                if '<a href=' in animal_id:
                    animal_number = animal_id.split('>')[1].split('<')[0]
                else:
                    animal_number = animal_id
                
                # Get current database values
                foster_data = foster_data_dict.get(animal_number, {})
                current_notes = foster_data.get('fosternotes', '')
                current_meds = foster_data.get('onmeds', False)
                current_dates = foster_data.get('fosterpleadates', [])
                
                # Create row with columns
                col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
                
                with col1:
                    st.markdown(row['Animal ID'], unsafe_allow_html=True)
                with col2:
                    st.write(row['Animal Name'])
                with col3:
                    st.write(row['Intake Date/Time'])
                with col4:
                    # Combined Animal Details: Age, Sex, Species, Breed
                    animal_details = f"{row['Age']}, {row['Sex']}, {row['Species']}, {row['Breed']}"
                    st.write(animal_details)
                with col5:
                    st.write(row['Stage'])
                with col6:
                    st.markdown(row['Foster PID'], unsafe_allow_html=True)
                with col7:
                    # Foster Notes - editable
                    new_notes = st.text_input(
                        "Notes",
                        value=current_notes,
                        key=f"notes_{animal_number}_{idx}",
                        label_visibility="collapsed"
                    )
                    if new_notes != current_notes:
                        supabase_manager.update_foster_notes(animal_number, new_notes)
                        st.success(f"✅ Updated notes for {animal_number}")
                with col8:
                    # On Meds - editable checkbox
                    new_meds = st.checkbox(
                        "On Meds",
                        value=current_meds,
                        key=f"meds_{animal_number}_{idx}",
                        label_visibility="collapsed"
                    )
                    if new_meds != current_meds:
                        supabase_manager.update_on_meds(animal_number, new_meds)
                        st.success(f"✅ Updated meds for {animal_number}")
                with col9:
                    if selected_category == 'Needs Foster Now':
                        # Foster Plea Dates - editable
                        dates_str = ', '.join(current_dates) if current_dates else ''
                        new_dates = st.text_input(
                            "Dates",
                            value=dates_str,
                            key=f"dates_{animal_number}_{idx}",
                            label_visibility="collapsed"
                        )
                        if new_dates != dates_str:
                            if new_dates:
                                dates = [d.strip() for d in new_dates.split(',') if d.strip()]
                                supabase_manager.update_foster_plea_dates(animal_number, dates)
                                st.success(f"✅ Updated dates for {animal_number}")
                            else:
                                supabase_manager.update_foster_plea_dates(animal_number, [])
                                st.success(f"✅ Cleared dates for {animal_number}")
            

            
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
    
    elif view_option == "Foster Database":
        # Foster Database View
        st.subheader("🏠 Foster Database")
        
        # Create tabs within Foster Database
        tab1, tab2 = st.tabs(["Active Foster Parents", "Emergency Bottle Baby Fosters"])
        
        with tab1:
            # Available Foster Parents Tab
            if not foster_parents_data.empty:
                # Get current animals for each foster parent
                foster_parent_animals, missing_pids = get_foster_parent_animals(foster_parents_data, foster_current)
                
                # Add current animals column to foster parents data
                foster_parents_data['Current_Animals'] = foster_parents_data['Full_PID'].apply(
                    lambda pid: foster_parent_animals.get(pid, [])
                )
                
                # Add Panleuk Positive flag
                foster_parents_data['Is_Panleuk_Positive'] = foster_parents_data['Full_PID'].isin(panleuk_positive_pids)
                
                # Create clickable PID links
                foster_parents_data['Clickable_PID'] = foster_parents_data['Full_PID'].apply(create_clickable_pid_link)
                
                # Create clickable animal links
                def create_animal_links(animal_list):
                    if not animal_list:
                        return ''
                    links = []
                    for animal_id in animal_list:
                        links.append(create_clickable_link(animal_id))
                    return '<br>'.join(links)
                
                foster_parents_data['Clickable_Animals'] = foster_parents_data['Current_Animals'].apply(create_animal_links)
                
                # Add Panleuk Positive flag to Availability notes
                def add_panleuk_flag(row):
                    availability = str(row['Availability/Notes']) if pd.notna(row['Availability/Notes']) else ''
                    if row['Is_Panleuk_Positive']:
                        if availability:
                            return f"{availability}<br><span style='color: red; font-weight: bold;'>Panleuk. Positive</span>"
                        else:
                            return "<span style='color: red; font-weight: bold;'>Panleuk. Positive</span>"
                    return availability
                
                foster_parents_data['Availability_With_Flags'] = foster_parents_data.apply(add_panleuk_flag, axis=1)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_foster_parents = len(foster_parents_data)
                    st.metric("Total Foster Parents", total_foster_parents)
                
                with col2:
                    active_foster_parents = len(foster_parents_data[foster_parents_data['Current_Animals'].apply(len) > 0])
                    st.metric("Active Foster Parents", active_foster_parents)
                
                with col3:
                    panleuk_positive_count = len(foster_parents_data[foster_parents_data['Is_Panleuk_Positive']])
                    st.metric("Panleuk Positive", panleuk_positive_count)
                
                st.markdown("---")
                
                # Display missing PIDs if any
                if missing_pids:
                    st.warning(f"⚠️ **Missing PIDs:** {len(missing_pids)} foster parents in FosterCurrent.csv are not in our database")
                    with st.expander("View Missing PIDs"):
                        missing_pids_list = sorted(list(missing_pids))
                        for pid in missing_pids_list:
                            st.write(f"- {pid}")
                
                # Display foster parents data
                st.write("**Note:** Click on PID to open foster parent profile in PetPoint. Click on Animal IDs to open animal profiles.")
                
                # Select columns to display
                display_columns = [
                    'Clickable_PID', 'Full_Name', 'Phone Number', 
                    'Foster Request/Animal Preference', 'Availability_With_Flags', 'Clickable_Animals'
                ]
                
                # Create display data
                display_data = foster_parents_data[display_columns].copy()
                
                # Rename columns for display
                column_mapping = {
                    'Clickable_PID': 'PID',
                    'Full_Name': 'Name',
                    'Phone Number': 'Phone',
                    'Foster Request/Animal Preference': 'Preferences',
                    'Availability_With_Flags': 'Availability',
                    'Clickable_Animals': 'Current Animals'
                }
                
                display_data = display_data.rename(columns=column_mapping)
                
                # Sort by name
                display_data = display_data.sort_values('Name')
                
                # Display the data with HTML rendering
                st.markdown(
                    display_data.to_html(
                        escape=False,
                        index=False,
                        classes=['foster-table'],
                        table_id='foster-parents-table'
                    ),
                    unsafe_allow_html=True
                )
                
                # Download button
                download_data = foster_parents_data[['Full_PID', 'Full_Name', 'Phone Number', 
                                                   'Foster Request/Animal Preference', 'Availability/Notes']].copy()
                download_data['Current_Animals'] = foster_parents_data['Current_Animals'].apply(
                    lambda x: ', '.join(x) if x else ''
                )
                download_data['Is_Panleuk_Positive'] = foster_parents_data['Is_Panleuk_Positive']
                download_data = download_data.rename(columns={
                    'Full_PID': 'PID',
                    'Full_Name': 'Name',
                    'Phone Number': 'Phone',
                    'Foster Request/Animal Preference': 'Preferences',
                    'Availability/Notes': 'Availability',
                    'Current_Animals': 'Current Animals',
                    'Is_Panleuk_Positive': 'Panleuk Positive'
                })
                
                csv = download_data.to_csv(index=False)
                st.download_button(
                    label="Download Foster Database CSV",
                    data=csv,
                    file_name=f"foster_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.warning("No foster parents data available.")
        
        with tab2:
            # Emergency Bottle Baby Fosters Tab
            if not bottle_fed_kittens_data.empty:
                # Get current animals for each bottle fed kitten foster parent
                bottle_fed_animals, _ = get_foster_parent_animals(bottle_fed_kittens_data, foster_current)
                
                # Add current animals column to bottle fed kittens data
                bottle_fed_kittens_data['Current_Animals'] = bottle_fed_kittens_data['Full_PID'].apply(
                    lambda pid: bottle_fed_animals.get(pid, [])
                )
                
                # Add Panleuk Positive flag
                bottle_fed_kittens_data['Is_Panleuk_Positive'] = bottle_fed_kittens_data['Full_PID'].isin(panleuk_positive_pids)
                
                # Create clickable PID links
                bottle_fed_kittens_data['Clickable_PID'] = bottle_fed_kittens_data['Full_PID'].apply(create_clickable_pid_link)
                
                # Create clickable animal links
                bottle_fed_kittens_data['Clickable_Animals'] = bottle_fed_kittens_data['Current_Animals'].apply(create_animal_links)
                
                # Add Panleuk Positive flag to Availability notes
                bottle_fed_kittens_data['Availability_With_Flags'] = bottle_fed_kittens_data.apply(add_panleuk_flag, axis=1)
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_bottle_fed = len(bottle_fed_kittens_data)
                    st.metric("Total Bottle Fed Foster Parents", total_bottle_fed)
                
                with col2:
                    active_bottle_fed = len(bottle_fed_kittens_data[bottle_fed_kittens_data['Current_Animals'].apply(len) > 0])
                    st.metric("Active Bottle Fed Foster Parents", active_bottle_fed)
                
                with col3:
                    available_bottle_fed = len(bottle_fed_kittens_data[bottle_fed_kittens_data['Current_Animals'].apply(len) == 0])
                    st.metric("Available Bottle Fed Foster Parents", available_bottle_fed)
                
                with col4:
                    panleuk_positive_bottle_fed = len(bottle_fed_kittens_data[bottle_fed_kittens_data['Is_Panleuk_Positive']])
                    st.metric("Panleuk Positive", panleuk_positive_bottle_fed)
                
                st.markdown("---")
                
                # Display bottle fed kittens data
                st.write("**Note:** Click on PID to open foster parent profile in PetPoint. Click on Animal IDs to open animal profiles.")
                
                # Select columns to display
                display_columns = [
                    'Clickable_PID', 'Full_Name', 'Phone Number', 
                    'Foster Request/Animal Preference', 'Availability_With_Flags', 'Clickable_Animals'
                ]
                
                # Create display data
                display_data = bottle_fed_kittens_data[display_columns].copy()
                
                # Rename columns for display
                column_mapping = {
                    'Clickable_PID': 'PID',
                    'Full_Name': 'Name',
                    'Phone Number': 'Phone',
                    'Foster Request/Animal Preference': 'Preferences',
                    'Availability_With_Flags': 'Availability',
                    'Clickable_Animals': 'Current Animals'
                }
                
                display_data = display_data.rename(columns=column_mapping)
                
                # Sort by name
                display_data = display_data.sort_values('Name')
                
                # Display the data with HTML rendering
                st.markdown(
                    display_data.to_html(
                        escape=False,
                        index=False,
                        classes=['foster-table'],
                        table_id='bottle-fed-table'
                    ),
                    unsafe_allow_html=True
                )
                
                # Download button
                download_data = bottle_fed_kittens_data[['Full_PID', 'Full_Name', 'Phone Number', 
                                                       'Foster Request/Animal Preference', 'Availability/Notes']].copy()
                download_data['Current_Animals'] = bottle_fed_kittens_data['Current_Animals'].apply(
                    lambda x: ', '.join(x) if x else ''
                )
                download_data['Is_Panleuk_Positive'] = bottle_fed_kittens_data['Is_Panleuk_Positive']
                download_data = download_data.rename(columns={
                    'Full_PID': 'PID',
                    'Full_Name': 'Name',
                    'Phone Number': 'Phone',
                    'Foster Request/Animal Preference': 'Preferences',
                    'Availability/Notes': 'Availability',
                    'Current_Animals': 'Current Animals',
                    'Is_Panleuk_Positive': 'Panleuk Positive'
                })
                
                csv = download_data.to_csv(index=False)
                st.download_button(
                    label="Download Bottle Fed Kittens CSV",
                    data=csv,
                    file_name=f"bottle_fed_kittens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.warning("No bottle fed kittens data available.")

if __name__ == "__main__":
    main() 