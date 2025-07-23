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

@st.cache_data
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
            inventory_data = inventory[['AnimalNumber', 'Stage', 'Age', 'Sex', 'Location', 'SubLocation']].copy()
            inventory_data = inventory_data.dropna(subset=['AnimalNumber'])
            st.success(f"✅ Loaded {len(inventory_data)} inventory records from {file_path}")
    except Exception as e:
        st.warning(f"⚠️ Could not load AnimalInventory.csv: {e}")
    
    if inventory_data is None:
        st.warning("⚠️ Could not load AnimalInventory.csv, using empty dataset")
        inventory_data = pd.DataFrame(columns=['AnimalNumber', 'Stage', 'Age', 'Sex', 'Location', 'SubLocation'])
    
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
    
    # Create combined location field
    merged['Location_Combined'] = merged['Location'].fillna('') + ' - ' + merged['SubLocation'].fillna('')
    merged['Location_Combined'] = merged['Location_Combined'].str.replace(' - $', '', regex=False)
    merged['Location_Combined'] = merged['Location_Combined'].str.replace('^ - ', '', regex=True)
    merged['Location_Combined'] = merged['Location_Combined'].fillna('Unknown')
    
    # Determine Status: First try Stage from inventory, then OperationType from outcome
    merged['Status'] = merged['Stage'].fillna(merged['OperationType']).fillna('Unknown')
    
    # Clean up foster information
    merged['FosterPersonID'] = merged['FosterPersonID'].fillna('Not in Foster')
    merged['FosterName'] = merged['FosterName'].fillna('Not in Foster')
    
    return merged

def create_clickable_link(animal_id):
    """Create a clickable HTML link for the animal ID"""
    return f'<a href="https://sms.petpoint.com/sms3/enhanced/animal/{animal_id}" target="_blank" class="animal-link">{animal_id}</a>'

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
    
    # Merge data
    merged_data = merge_data(rodent_intake, foster_data, inventory_data, outcome_data)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Species filter
    species_options = ['All'] + sorted(merged_data['Species'].unique().tolist())
    selected_species = st.sidebar.selectbox("Species", species_options)
    
    # Sex filter
    sex_options = ['All'] + sorted(merged_data['Sex'].dropna().unique().tolist())
    selected_sex = st.sidebar.selectbox("Sex", sex_options)
    
    # Status filter
    status_options = ['All'] + sorted(merged_data['Status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Status", status_options)
    
    # Location filter
    location_options = ['All'] + sorted(merged_data['Location_Combined'].dropna().unique().tolist())
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
            <h3>Total Rodents</h3>
            <h2>{len(filtered_data)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        in_foster = len(filtered_data[filtered_data['FosterPersonID'] != 'Not in Foster'])
        foster_percentage = (in_foster / len(filtered_data)) * 100 if len(filtered_data) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>In Foster</h3>
            <h2>{in_foster} ({foster_percentage:.1f}%)</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Only count living females that need foster placement
        # Excluded: Males, Euthanized, DOA, and animals already in foster
        living_females = filtered_data[
            (filtered_data['Sex'] == 'F') & 
            (filtered_data['Status'].str.contains('Euthanasia|DOA', case=False, na=False) == False) &
            (filtered_data['FosterPersonID'] == 'Not in Foster')
        ]
        needing_placement = len(living_females)
        st.markdown(f"""
        <div class="metric-card">
            <h3>Needing Placement</h3>
            <h2>{needing_placement}</h2>
            <small style="color: #666;">Living females only (excludes males, euthanized, DOA)</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        unique_fosters = filtered_data[filtered_data['FosterPersonID'] != 'Not in Foster']['FosterPersonID'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Active Fosters</h3>
            <h2>{unique_fosters}</h2>
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
    
    # Main Data Table
    st.header("📋 Rodent Inventory")
    
    # Prepare table data with clickable links
    table_data = filtered_data[['AnimalNumber', 'AnimalName', 'Species', 'Sex', 'Age', 'Status', 'Location_Combined', 'FosterPersonID', 'FosterName']].copy()
    
    # Create clickable AnimalNumber links using HTML
    table_data['AnimalNumber'] = table_data['AnimalNumber'].apply(create_clickable_link)
    
    # Display table with HTML rendering
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
    
    st.dataframe(species_summary, use_container_width=True)
    
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