import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import requests
from io import StringIO

# Import our image cache manager
from image_cache_manager import get_animal_images_cached, initialize_cache, cleanup_cache, get_cache_stats

# Page config
st.set_page_config(
    page_title="Pathways for Care Viewer",
    page_icon="🐾",
    layout="wide"
)

# Configuration
PUBLIC_REPO_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/SPCAAutomation/main"
CSV_FILES = {
    'pathways': f"{PUBLIC_REPO_URL}/__Load%20Files%20Go%20Here__/Pathways%20for%20Care.csv",
    'inventory': f"{PUBLIC_REPO_URL}/__Load%20Files%20Go%20Here__/AnimalInventory.csv"
}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_csv_from_github(url):
    """Load CSV file from GitHub raw URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return None

@st.cache_data
def load_data():
    """Load and merge data - try local first, then GitHub"""
    # First try to load from local files
    local_pathways = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    local_inventory = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'AnimalInventory.csv')
    
    pathways_df = None
    inventory_df = None
    
    # Try local Pathways file
    if os.path.exists(local_pathways):
        try:
            pathways_df = pd.read_csv(local_pathways)
            st.success("✅ Loaded Pathways data from local file")
        except Exception as e:
            st.warning(f"⚠️ Error loading local Pathways file: {e}")
    
    # Try local Inventory file
    if os.path.exists(local_inventory):
        try:
            inventory_df = pd.read_csv(local_inventory, skiprows=2)
            st.success("✅ Loaded Inventory data from local file")
        except Exception as e:
            st.warning(f"⚠️ Error loading local Inventory file: {e}")
    
    # If local files failed, try GitHub
    if pathways_df is None:
        st.info("🔄 Trying to load from GitHub...")
        pathways_df = load_csv_from_github(CSV_FILES['pathways'])
        if pathways_df is not None:
            st.success("✅ Loaded Pathways data from GitHub")
    
    if inventory_df is None:
        st.info("🔄 Trying to load Inventory from GitHub...")
        inventory_df = load_csv_from_github(CSV_FILES['inventory'])
        if inventory_df is not None:
            st.success("✅ Loaded Inventory data from GitHub")
    
    # If we have Pathways data, process it
    if pathways_df is not None:
        # Clean up the data
        pathways_df = pathways_df.fillna('')
        pathways_df['Days in System'] = pd.to_numeric(pathways_df['Days in System'], errors='coerce').fillna(0)
        
        # If we also have inventory data, merge it
        if inventory_df is not None:
            try:
                # Extract AID from AnimalNumber
                inventory_df['AID'] = inventory_df['AnimalNumber'].str[-8:].astype(str)
                
                # Merge data
                merged_df = pd.merge(pathways_df, inventory_df, on='AID', how='left')
                st.success("✅ Successfully merged Pathways and Inventory data")
                return merged_df
            except Exception as e:
                st.warning(f"⚠️ Error merging data: {e}")
                return pathways_df
        else:
            return pathways_df
    
    return None

# Initialize
if 'df' not in st.session_state:
    st.session_state.df = load_data()
    st.session_state.current_index = 0

# Initialize image cache
if 'cache_initialized' not in st.session_state:
    print("Initializing image cache...")
    cache_success = initialize_cache()
    if cache_success:
        stats = get_cache_stats()
        print(f"Cache stats: {stats['animals_with_images']} animals with images, {stats['total_images']} total images")
    st.session_state.cache_initialized = True

# Main app
st.title("Pathways for Care Viewer")
st.markdown("*Powered by Streamlit Cloud*")

# Check if data loaded successfully
if st.session_state.df is None:
    st.error("Failed to load data. Please check the file locations or GitHub repository configuration.")
    st.stop()

# Display data source info
st.info(f"📊 Loaded {len(st.session_state.df)} records with {len(st.session_state.df.columns)} columns")

# Sidebar for navigation
st.sidebar.title("Navigation")
view_mode = st.sidebar.radio("Select View", ["Spreadsheet", "Record Browser"])

# Add some filters in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

# Species filter
if 'Species' in st.session_state.df.columns:
    species_options = ['All'] + sorted(st.session_state.df['Species'].dropna().unique().tolist())
    selected_species = st.sidebar.selectbox("Species", species_options)
    
    # Filter data
    if selected_species != 'All':
        filtered_df = st.session_state.df[st.session_state.df['Species'] == selected_species]
    else:
        filtered_df = st.session_state.df
else:
    filtered_df = st.session_state.df

# Location filter
if 'Location ' in filtered_df.columns:
    location_options = ['All'] + sorted(filtered_df['Location '].dropna().unique().tolist())
    selected_location = st.sidebar.selectbox("Location", location_options)
    
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['Location '] == selected_location]

# Update session state with filtered data
st.session_state.filtered_df = filtered_df

if view_mode == "Spreadsheet":
    st.header("Spreadsheet View")
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Animals", len(filtered_df))
    with col2:
        st.metric("Species", len(filtered_df['Species'].unique()) if 'Species' in filtered_df.columns else 0)
    with col3:
        st.metric("Avg Days in System", f"{filtered_df['Days in System'].mean():.1f}" if 'Days in System' in filtered_df.columns else "N/A")
    
    # Display the dataframe
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=600
    )
    
    # Add download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"pathways_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:  # Record Browser
    st.header("Record Browser")
    
    # Navigation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Previous"):
            st.session_state.current_index = max(0, st.session_state.current_index - 1)
    
    with col2:
        st.write(f"Record {st.session_state.current_index + 1} of {len(filtered_df)}")
    
    with col3:
        if st.button("Next →"):
            st.session_state.current_index = min(len(filtered_df) - 1, st.session_state.current_index + 1)
    
    # Get current record
    record = filtered_df.iloc[st.session_state.current_index]
    
    # Display animal information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Basic Info")
        st.write(f"**Name:** {record['Name'] or 'N/A'}")
        st.write(f"**AID:** [{record['AID']}](https://sms.petpoint.com/sms3/enhanced/animal/{record['AID']})")
        st.write(f"**Species:** {record['Species'] or 'N/A'}")
    
    with col2:
        st.subheader("Location & Dates")
        st.write(f"**Location:** {record['Location '] or 'N/A'}")
        st.write(f"**Intake Date:** {record['Intake Date'] or 'N/A'}")
        st.write(f"**Days in System:** {record['Days in System']:.0f}" if pd.notna(record['Days in System']) else "**Days in System:** N/A")
    
    with col3:
        st.subheader("Attempts")
        st.write(f"**Foster Attempted:** {record['Foster Attempted'] or 'N/A'}")
        st.write(f"**Transfer Attempted:** {record['Transfer Attempted'] or 'N/A'}")
        st.write(f"**Communications Team:** {record['Communications Team Attempted'] or 'N/A'}")
    
    # Display images
    st.subheader("Images")
    animal_id = str(record['AID']).strip()
    image_urls = get_animal_images_cached(animal_id)
    
    if image_urls:
        # Display all images in a grid
        cols = st.columns(4)  # 4 images per row
        for i, url in enumerate(image_urls):
            col_idx = i % 4
            with cols[col_idx]:
                st.image(url, caption=f"Image {i+1}", use_column_width=True)
    else:
        st.info("No images available for this animal")
    
    # Display welfare notes
    st.subheader("Welfare Notes")
    st.write(record['Welfare Notes'] or "No notes available")

# Footer
st.markdown("---")
st.markdown("*Data loaded from local files or GitHub repository*") 