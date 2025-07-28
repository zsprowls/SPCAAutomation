import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Rodent Intake Case Dashboard",
    page_icon="🐹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #062b49 0%, #bc6f32 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #bc6f32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
    .animal-link {
        color: #bc6f32;
        text-decoration: none;
        font-weight: bold;
    }
    .animal-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes, then auto-refresh
def load_data():
    """Load and process all data files"""
    
    # Define possible file paths for different environments
    # Streamlit Cloud runs from repository root, local runs from subdirectory
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
    
    # Debug: Show current working directory and available files
    st.info(f"🔍 Current working directory: {os.getcwd()}")
    try:
        current_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        st.info(f"🔍 Available CSV files in current directory: {current_files}")
    except Exception as e:
        st.warning(f"⚠️ Could not list current directory files: {e}")
    
    # Try to find the data directory
    data_dir_found = None
    for base_path in base_paths:
        try:
            if os.path.exists(base_path):
                st.info(f"✅ Found directory: {base_path}")
                if os.path.exists(f"{base_path}/AnimalInventory.csv"):
                    data_dir_found = base_path
                    st.success(f"✅ Found data directory: {base_path}")
                    break
        except Exception as e:
            continue
    
    if data_dir_found is None:
        st.error("❌ Could not find data directory with AnimalInventory.csv")
        st.info("Available directories checked:")
        for base_path in base_paths:
            st.info(f"  - {base_path}")
        return None, None, None, None
    
    # Load RodentIntake.csv (no header skip needed - it's clean)
    rodent_intake = None
    # Try multiple locations for RodentIntake.csv
    rodent_paths = [
        "RodentIntake.csv",  # Current directory
        "RodentSituation/RodentIntake.csv",  # From repo root
        f"{data_dir_found}/RodentIntake.csv"  # From data directory
    ]
    
    for file_path in rodent_paths:
        try:
            if os.path.exists(file_path):
                rodent_intake = pd.read_csv(file_path)
                st.success(f"✅ Loaded {len(rodent_intake)} rodents from {file_path}")
                break
        except Exception as e:
            continue
    
    if rodent_intake is None:
        st.error("❌ Could not load RodentIntake.csv from any location")
        st.info("Tried paths:")
        for path in rodent_paths:
            st.info(f"  - {path}")
        return None, None, None, None
    
    if rodent_intake is None:
        st.error("❌ Could not load RodentIntake.csv from any location")
        return None, None, None, None
    
    # Load FosterCurrent.csv (header row 7)
    foster_data = None
    try:
        file_path = f"{data_dir_found}/FosterCurrent.csv"
        if os.path.exists(file_path):
            foster_current = pd.read_csv(file_path, skiprows=6)
            # Extract relevant columns
            foster_data = foster_current[['textbox9', 'textbox10', 'textbox11']].copy()
            foster_data.columns = ['AnimalNumber', 'FosterPersonID', 'FosterName']
            foster_data = foster_data.dropna(subset=['AnimalNumber'])
            st.success(f"✅ Loaded {len(foster_data)} foster records from {file_path}")
    except Exception as e:
        st.warning(f"⚠️ Could not load FosterCurrent.csv: {e}")
    
    if foster_data is None:
        st.warning("⚠️ Could not load FosterCurrent.csv, using empty dataset")
        foster_data = pd.DataFrame(columns=['AnimalNumber', 'FosterPersonID', 'FosterName'])
    
    # Load AnimalInventory.csv (header row 4)
    inventory_data = None
    try:
        file_path = f"{data_dir_found}/AnimalInventory.csv"
        if os.path.exists(file_path):
            inventory = pd.read_csv(file_path, skiprows=3)
            # Extract relevant columns - Stage and Location are the key ones
            inventory_data = inventory[['AnimalNumber', 'Stage', 'Age', 'Sex', 'Location', 'SubLocation', 'SpayedNeutered']].copy()
            inventory_data = inventory_data.dropna(subset=['AnimalNumber'])
            st.success(f"✅ Loaded {len(inventory_data)} inventory records from {file_path}")
    except Exception as e:
        st.warning(f"⚠️ Could not load AnimalInventory.csv: {e}")
    
    if inventory_data is None:
        st.warning("⚠️ Could not load AnimalInventory.csv, using empty dataset")
        inventory_data = pd.DataFrame(columns=['AnimalNumber', 'Stage', 'Age', 'Sex', 'Location', 'SubLocation', 'SpayedNeutered'])
    
    # Load AnimalOutcome.csv (header row 4)
    outcome_data = None
    try:
        file_path = f"{data_dir_found}/AnimalOutcome.csv"
        if os.path.exists(file_path):
            outcome = pd.read_csv(file_path, skiprows=3)
            # Extract relevant columns - OperationType is the key one
            outcome_data = outcome[['AnimalNumber', 'OperationType']].copy()
            outcome_data = outcome_data.dropna(subset=['AnimalNumber'])
            st.success(f"✅ Loaded {len(outcome_data)} outcome records from {file_path}")
    except Exception as e:
        st.warning(f"⚠️ Could not load AnimalOutcome.csv: {e}")
    
    if outcome_data is None:
        st.warning("⚠️ Could not load AnimalOutcome.csv, using empty dataset")
        outcome_data = pd.DataFrame(columns=['AnimalNumber', 'OperationType'])
    
    return rodent_intake, foster_data, inventory_data, outcome_data

def merge_data(rodent_intake, foster_data, inventory_data, outcome_data):
    """Merge all data sources into a comprehensive dataset"""
    
    # Start with rodent intake data
    merged = rodent_intake.copy()
    
    # Add foster information
    merged = merged.merge(foster_data, on='AnimalNumber', how='left')
    
    # Add inventory information (Stage and Location)
    merged = merged.merge(inventory_data, on='AnimalNumber', how='left')
    
    # Add outcome information for animals not in inventory
    merged = merged.merge(outcome_data, on='AnimalNumber', how='left')
    
    # Clean up and standardize data
    merged['Sex'] = merged['Sex'].fillna(merged['Gender'])
    merged['Age'] = merged['Age'].fillna('N/A')
    
    # For animals not in inventory, mark as "Released"
    # Check if animal is in inventory by looking for non-null Stage values
    released_mask = merged['Stage'].isna()
    
    # Set "Released" for missing inventory data
    merged.loc[released_mask, 'Status'] = 'Released'
    merged.loc[released_mask, 'Location'] = 'Released'
    merged.loc[released_mask, 'SubLocation'] = 'Released'
    merged.loc[released_mask, 'SpayedNeutered'] = 'Released'
    merged.loc[released_mask, 'FosterPersonID'] = 'Released'
    merged.loc[released_mask, 'FosterName'] = 'Released'
    
    # For animals in inventory, set Status from Stage and fill missing values
    merged.loc[~released_mask, 'Status'] = merged.loc[~released_mask, 'Stage'].fillna('Unknown')
    merged.loc[~released_mask, 'SpayedNeutered'] = merged.loc[~released_mask, 'SpayedNeutered'].fillna('Unknown')
    merged.loc[~released_mask, 'FosterPersonID'] = merged.loc[~released_mask, 'FosterPersonID'].fillna('Not in Foster')
    merged.loc[~released_mask, 'FosterName'] = merged.loc[~released_mask, 'FosterName'].fillna('Not in Foster')
    
    # Create combined location field
    merged['Location_Combined'] = merged['Location'].fillna('') + ' - ' + merged['SubLocation'].fillna('')
    merged['Location_Combined'] = merged['Location_Combined'].str.replace(' - $', '', regex=False)
    merged['Location_Combined'] = merged['Location_Combined'].str.replace('^ - ', '', regex=True)
    merged['Location_Combined'] = merged['Location_Combined'].fillna('Unknown')
    
    return merged

def create_clickable_link(animal_id):
    """Create a clickable HTML link for the animal ID"""
    # Extract the numeric part after "A00" prefix for the PetPoint URL
    if animal_id.startswith('A00'):
        petpoint_id = animal_id[3:]  # Remove "A00" prefix
    else:
        petpoint_id = animal_id  # Fallback if format is different
    
    return f'<a href="https://sms.petpoint.com/sms3/enhanced/animal/{petpoint_id}" target="_blank" class="animal-link">{animal_id}</a>'

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🐹 Rodent Intake Case Dashboard</h1>
        <p>Mass Hoarding Case Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        rodent_intake, foster_data, inventory_data, outcome_data = load_data()
    
    if rodent_intake is None:
        st.error("Failed to load primary data file. Please check file paths.")
        return
    
    # Show data freshness
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"📅 **Data loaded:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.sidebar.markdown("💡 *Click 'Refresh Data' to reload from files*")
    
    # Merge data
    merged_data = merge_data(rodent_intake, foster_data, inventory_data, outcome_data)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Cache management
    if st.sidebar.button("🔄 Refresh Data", help="Clear cache and reload data from files"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Species filter
    species_options = ['All'] + sorted(merged_data['Species'].unique().tolist())
    selected_species = st.sidebar.selectbox("Species", species_options)
    
    # Sex filter
    sex_values = merged_data['Sex'].dropna().unique().tolist()
    sex_options = ['All'] + sorted(sex_values)
    selected_sex = st.sidebar.selectbox("Sex", sex_options)
    
    # Status filter
    status_values = merged_data['Status'].dropna().unique().tolist()
    status_options = ['All'] + sorted(status_values)
    selected_status = st.sidebar.selectbox("Status", status_options)
    
    # Location filter
    location_values = merged_data['Location_Combined'].dropna().unique().tolist()
    location_options = ['All'] + sorted(location_values)
    selected_location = st.sidebar.selectbox("Location", location_options)
    
    # Apply filters
    filtered_data = merged_data.copy()
    
    if selected_species != 'All':
        filtered_data = filtered_data[filtered_data['Species'] == selected_species]
    
    if selected_sex != 'All':
        filtered_data = filtered_data[filtered_data['Sex'] == selected_sex]
    
    if selected_status != 'All':
        filtered_data = filtered_data[filtered_data['Status'] == selected_status]
    
    if selected_location != 'All':
        filtered_data = filtered_data[filtered_data['Location_Combined'] == selected_location]
    
    # Filter note
    if len(filtered_data) != len(merged_data):
        st.info(f"🔍 **Filters Applied**: Showing {len(filtered_data)} of {len(merged_data)} total rodents")
    
    # Key Statistics
    st.header("📊 Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Intake</h3>
            <h2>{len(filtered_data)}</h2>
            <small style="color: #666;">All rodents from intake</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Count animals in shelter (not released, not in foster)
        in_shelter = len(filtered_data[
            (filtered_data['Status'] != 'Released') & 
            (filtered_data['Status'] != 'In Foster')
        ])
        st.markdown(f"""
        <div class="metric-card">
            <h3>In Shelter</h3>
            <h2>{in_shelter}</h2>
            <small style="color: #666;">Not released or in foster</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Count released animals
        released_count = len(filtered_data[filtered_data['Status'] == 'Released'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Released</h3>
            <h2>{released_count}</h2>
            <small style="color: #666;">No longer in system</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Count animals with "In Foster" status
        in_foster = len(filtered_data[filtered_data['Status'] == 'In Foster'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>In Foster</h3>
            <h2>{in_foster}</h2>
            <small style="color: #666;">Status: In Foster</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualizations
    st.header("📈 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = filtered_data['Status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribution by Status",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Species distribution by sex (stacked bar)
        species_sex_counts = filtered_data.groupby(['Species', 'Sex']).size().reset_index(name='Count')
        
        # Create stacked bar chart using go.Figure for better control
        fig_species = go.Figure()
        
        # Get unique species and sexes
        species_list = species_sex_counts['Species'].unique()
        sex_list = ['M', 'F', 'U']
        colors = {'M': '#4f5b35', 'F': '#bc6f32', 'U': '#512a44'}
        
        for sex in sex_list:
            sex_data = species_sex_counts[species_sex_counts['Sex'] == sex]
            fig_species.add_trace(go.Bar(
                name=sex,
                x=sex_data['Species'],
                y=sex_data['Count'],
                marker_color=colors[sex],
                text=sex_data['Count'],
                textposition='inside'
            ))
        
        fig_species.update_layout(
            title="Distribution by Species and Sex",
            xaxis_title="Species",
            yaxis_title="Count",
            barmode='stack',
            showlegend=True
        )
        
        st.plotly_chart(fig_species, use_container_width=True)
    
    # Comprehensive Data Table (like spreadsheet generator)
    st.header("📋 Complete Rodent Inventory")
    
    # Sort data by Location and SubLocation for better organization
    sorted_data = filtered_data.sort_values(['Location', 'SubLocation', 'AnimalNumber'])
    
    # Prepare comprehensive table data with all columns
    table_columns = [
        'AnimalNumber', 'AnimalName', 'Species', 'Gender', 'Color', 
        'Sex', 'Status', 'Location', 'SubLocation', 'SpayedNeutered',
        'FosterPersonID', 'FosterName'
    ]
    
    table_data = sorted_data[table_columns].copy()
    
    # Create clickable AnimalNumber links using HTML
    table_data['AnimalNumber'] = table_data['AnimalNumber'].apply(create_clickable_link)
    
    # Rename columns for display
    column_mapping = {
        'AnimalNumber': 'Animal ID',
        'AnimalName': 'Animal Name',
        'Species': 'Species',
        'Gender': 'Gender',
        'Color': 'Color',
        'Sex': 'Sex',
        'Status': 'Status',
        'Location': 'Location',
        'SubLocation': 'Sub Location',
        'SpayedNeutered': 'Spayed/Neutered',
        'FosterPersonID': 'Foster PID',
        'FosterName': 'Foster Name'
    }
    
    table_data = table_data.rename(columns=column_mapping)
    
    # Display comprehensive table with HTML rendering
    st.write("**Note:** Click on Animal ID to open in PetPoint")
    st.markdown(
        table_data.to_html(
            escape=False,
            index=False,
            classes=['dataframe'],
            table_id='rodent-table'
        ),
        unsafe_allow_html=True
    )
    
    # Summary statistics
    st.subheader("📊 Summary by Species")
    species_summary = filtered_data.groupby('Species').agg({
        'AnimalNumber': 'count',
        'FosterPersonID': lambda x: (x != 'Not in Foster').sum()
    }).rename(columns={'AnimalNumber': 'Total', 'FosterPersonID': 'In Foster'})
    
    species_summary['Not in Foster'] = species_summary['Total'] - species_summary['In Foster']
    species_summary['Foster %'] = (species_summary['In Foster'] / species_summary['Total'] * 100).round(1)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Rodent Intake Case Dashboard | SPCA Automation System</p>
        <p>Data last updated: {}</p>
    </div>
    """.format(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main() 