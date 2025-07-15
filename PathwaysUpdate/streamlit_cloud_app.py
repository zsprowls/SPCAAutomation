#!/usr/bin/env python3
"""
Pathways for Care Viewer - Cloud-Ready Streamlit App
Supports both local SQLite and Google Cloud SQL MySQL databases
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
from image_cache_manager import get_animal_images_cached, initialize_cache, cleanup_cache, get_cache_stats
from cloud_database_manager import get_database_manager, connect_to_database, disconnect_database

# Page configuration
st.set_page_config(
    page_title="Pathways for Care Viewer (Cloud)",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match original design
st.markdown("""
<style>
    /* Light mode styling - remove all dark elements */
    .main .block-container {
        background-color: #ffffff;
    }
    
    /* Force light theme */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    /* Card styling to match original */
    .animal-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
    
    .card-header {
        background-color: #007bff;
        color: white;
        padding: 0.75rem 1.25rem;
        border-bottom: 1px solid #dee2e6;
        border-radius: 0.375rem 0.375rem 0 0;
        font-weight: bold;
    }
    
    .card-header-warning {
        background-color: #ffc107;
        color: #212529;
    }
    
    .card-header-success {
        background-color: #28a745;
        color: white;
    }
    
    .card-body {
        padding: 1.25rem;
        background-color: #ffffff;
        border-radius: 0 0 0.375rem 0.375rem;
    }
    
    /* Welfare notes styling */
    .welfare-notes {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 0.5rem 0;
        white-space: pre-wrap;
        max-height: 300px;
        overflow-y: auto;
        font-size: 14px;
        line-height: 1.6;
    }
    
    /* Edit section styling */
    .edit-section {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    /* Navigation styling */
    .nav-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1rem 0;
        padding: 0.5rem 0;
    }
    
    .page-indicator {
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        color: #495057;
    }
    
    /* Search dropdown styling */
    .search-section {
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.375rem;
    }
    
    /* Image container styling - compact single line with horizontal scroll */
    .image-container {
        text-align: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 0.375rem;
        overflow-x: auto;
        scrollbar-width: thin;
        scrollbar-color: #007bff #f8f9fa;
    }
    
    .image-container::-webkit-scrollbar {
        height: 8px;
    }
    
    .image-container::-webkit-scrollbar-track {
        background: #f8f9fa;
        border-radius: 4px;
    }
    
    .image-container::-webkit-scrollbar-thumb {
        background: #007bff;
        border-radius: 4px;
    }
    
    .image-container::-webkit-scrollbar-thumb:hover {
        background: #0056b3;
    }
    
    /* Make images smaller and closer together */
    .image-container img {
        max-width: 120px !important;
        max-height: 90px !important;
        object-fit: cover;
        border-radius: 0.375rem;
        border: 1px solid #dee2e6;
        margin: 0 0.25rem;
    }
    
    /* Reduce spacing between columns */
    .image-container .stColumn {
        padding: 0 0.25rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 0.375rem;
        font-weight: 500;
        background-color: #ffffff;
        color: #495057;
        border: 1px solid #dee2e6;
    }
    
    /* Form label styling */
    .form-label {
        font-weight: bold;
        color: #495057;
        margin-bottom: 0.5rem;
    }
    
    /* Force light mode on all elements */
    .stSelectbox, .stTextInput, .stTextarea {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    /* Force light mode on all Streamlit components */
    .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    .stSelectbox > div > div > div > div {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    /* Database status indicator */
    .db-status {
        padding: 0.5rem;
        border-radius: 0.375rem;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    
    .db-status.local {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .db-status.cloud {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    .db-status.error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_from_database(use_cloud: bool = False):
    """Load data from database (local or cloud)"""
    try:
        # Connect to database
        if not connect_to_database(use_cloud):
            st.error("Failed to connect to database!")
            return None
        
        # Get database manager
        manager = get_database_manager()
        
        # Load main pathways data
        df = manager.get_pathways_data()
        if df is None:
            st.error("Failed to load pathways data!")
            return None
        
        # Load inventory data for location updates
        try:
            inventory_df = manager.get_inventory_data()
            
            if inventory_df is not None and len(inventory_df) > 0:
                # Find the AID column in inventory
                aid_columns = ['AnimalNumber', 'AID', 'Animal ID', 'AnimalID', 'ID', 'id']
                inventory_aid_col = None
                for col in aid_columns:
                    if col in inventory_df.columns:
                        inventory_aid_col = col
                        break
                
                if inventory_aid_col:
                    # Find location columns
                    location_columns = ['Location', 'Current Location', 'Location ', 'CurrentLocation']
                    sublocation_columns = ['SubLocation', 'Sub Location', 'SubLocation ', 'Sub-Location']
                    
                    inventory_location_col = None
                    inventory_sublocation_col = None
                    
                    for col in location_columns:
                        if col in inventory_df.columns:
                            inventory_location_col = col
                            break
                    
                    for col in sublocation_columns:
                        if col in inventory_df.columns:
                            inventory_sublocation_col = col
                            break
                    
                    if inventory_location_col:
                        # Create location mapping
                        location_mapping = {}
                        for idx, row in inventory_df.iterrows():
                            full_aid = str(row[inventory_aid_col]).strip()
                            
                            # Extract numeric part from full AID
                            if full_aid.startswith('A00'):
                                aid = full_aid[3:]
                            else:
                                aid = full_aid
                            
                            location = str(row[inventory_location_col]).strip() if pd.notna(row[inventory_location_col]) else ''
                            
                            # Add sublocation if available
                            if inventory_sublocation_col and pd.notna(row[inventory_sublocation_col]):
                                sublocation = str(row[inventory_sublocation_col]).strip()
                                if sublocation and location:
                                    location = f"{location} {sublocation}"
                                elif sublocation:
                                    location = sublocation
                            
                            location_mapping[aid] = location
                        
                        # Update locations
                        df['Location '] = df['AID'].astype(str).str.strip().map(location_mapping).fillna(df['Location '])
        
        except Exception as e:
            st.warning(f"Could not load inventory data: {e}")
        
        # Clean up data
        df = df.fillna('')
        
        # Clean welfare notes
        def clean_welfare_notes(notes):
            if not notes or pd.isna(notes):
                return ""
            
            notes_str = str(notes).strip()
            if not notes_str:
                return ""
            
            # Common separators
            separators = ['\n\n', ' | ', ' - ', ' • ', ' * ', ' ~ ', ' / ', ' || ', ' -- ']
            
            for separator in separators:
                if separator in notes_str:
                    parts = notes_str.split(separator)
                    cleaned_parts = [part.strip() for part in parts if part.strip()]
                    return '\n\n'.join(cleaned_parts)
            
            # Date patterns
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{2,4}',
                r'\d{1,2}-\d{1,2}-\d{2,4}',
                r'\d{1,2}\.\d{1,2}\.\d{2,4}',
            ]
            
            for pattern in date_patterns:
                if re.search(pattern, notes_str):
                    parts = re.split(pattern, notes_str)
                    if len(parts) > 1:
                        result = []
                        for i, part in enumerate(parts):
                            if part.strip():
                                if i > 0:
                                    date_match = re.search(pattern, notes_str)
                                    if date_match:
                                        result.append(f"{date_match.group()}{part.strip()}")
                                else:
                                    result.append(part.strip())
                        return '\n\n'.join(result)
            
            # Normalize line breaks
            notes_str = re.sub(r'\n(?!\n)', '\n\n', notes_str)
            notes_str = re.sub(r'\n{3,}', '\n\n', notes_str)
            
            return notes_str
        
        df['Welfare Notes'] = df['Welfare Notes'].apply(clean_welfare_notes)
        
        # Calculate Days in System
        try:
            df['Intake Date'] = pd.to_datetime(df['Intake Date'], errors='coerce')
            df['Intake Date'] = df['Intake Date'].dt.strftime('%m/%d/%Y')
            intake_dates_for_calc = pd.to_datetime(df['Intake Date'], errors='coerce')
            today = pd.Timestamp.now().normalize()
            df['Days in System'] = (today - intake_dates_for_calc).dt.days
            df['Days in System'] = df['Days in System'].fillna(0).astype(int)
        except Exception as e:
            st.sidebar.warning(f"Could not calculate Days in System: {e}")
            df['Days in System'] = pd.to_numeric(df['Days in System'], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def save_record_to_database(aid, foster_value, transfer_value, communications_value, new_note):
    """Save a record to the database"""
    try:
        manager = get_database_manager()
        success = manager.update_animal_record(aid, foster_value, transfer_value, communications_value, new_note)
        
        if success:
            st.success("Record updated successfully!")
            # Clear cache to reload data
            st.cache_data.clear()
            return True
        else:
            st.error("Failed to update record!")
            return False
            
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def export_database_to_csv():
    """Export database to CSV"""
    try:
        manager = get_database_manager()
        filename = manager.export_to_csv()
        
        if filename:
            # Read the file and return it for download
            with open(filename, 'r') as f:
                csv_data = f.read()
            
            st.download_button(
                label="Download CSV Export",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
            return True
        else:
            st.error("Failed to export data!")
            return False
            
    except Exception as e:
        st.error(f"Export error: {e}")
        return False

def display_media(animal_id, image_urls):
    """Display images and videos for an animal in a compact single line"""
    if not image_urls:
        return
    
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    
    cols = st.columns(min(len(image_urls), 5))  # Max 5 columns
    
    for i, url in enumerate(image_urls):
        if i >= 5:  # Limit to 5 images
            break
            
        with cols[i]:
            if "youtube.com" in url or "youtu.be" in url:
                # Display YouTube video thumbnail
                video_id = url.split('v=')[1] if 'v=' in url else url.split('/')[-1]
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                st.image(thumbnail_url, caption="Video", use_column_width=True)
            else:
                # Display image
                st.image(url, use_column_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Initialize image cache
    if 'cache_initialized' not in st.session_state:
        try:
            initialize_cache()
            st.session_state.cache_initialized = True
        except Exception as e:
            st.warning(f"Image cache initialization failed: {e}")
    
    # Sidebar
    st.sidebar.title("🐾 Pathways for Care")
    
    # Database selection
    st.sidebar.subheader("Database Connection")
    
    # Check if cloud config exists
    cloud_config_exists = os.path.exists('cloud_config.json')
    
    if cloud_config_exists:
        use_cloud = st.sidebar.checkbox("Use Cloud Database (MySQL)", value=False)
    else:
        use_cloud = False
        st.sidebar.info("Cloud config not found. Using local SQLite.")
    
    # Database status
    manager = get_database_manager()
    if manager.connection:
        db_type = manager.db_type or "Unknown"
        if db_type == "mysql":
            st.sidebar.markdown('<div class="db-status cloud">☁️ Connected to Cloud MySQL</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="db-status local">💾 Connected to Local SQLite</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="db-status error">❌ Not Connected</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data_from_database(use_cloud)
    
    if df is None:
        st.error("Failed to load data. Please check your database connection.")
        return
    
    # Main content
    st.markdown('<h1 class="main-header">Pathways for Care Viewer</h1>', unsafe_allow_html=True)
    
    # Search and filters
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.subheader("🔍 Search & Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Search by name
        search_name = st.text_input("Search by Name", "")
    
    with col2:
        # Filter by species
        species_options = ['All'] + sorted(df['Species'].unique().tolist())
        selected_species = st.selectbox("Species", species_options)
    
    with col3:
        # Filter by location
        location_options = ['All'] + sorted(df['Location '].unique().tolist())
        selected_location = st.selectbox("Location", location_options)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_name:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False, na=False)]
    
    if selected_species != 'All':
        filtered_df = filtered_df[filtered_df['Species'] == selected_species]
    
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['Location '] == selected_location]
    
    # Pagination
    items_per_page = 10
    total_items = len(filtered_df)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    # Navigation controls
    st.markdown('<div class="nav-controls">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous") and st.session_state.current_page > 0:
            st.session_state.current_page -= 1
    
    with col2:
        st.markdown(f'<div class="page-indicator">Page {st.session_state.current_page + 1} of {total_pages} ({total_items} total animals)</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ➡️") and st.session_state.current_page < total_pages - 1:
            st.session_state.current_page += 1
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display animals
    start_idx = st.session_state.current_page * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    if total_items == 0:
        st.info("No animals found matching your criteria.")
        return
    
    for idx in range(start_idx, end_idx):
        animal = filtered_df.iloc[idx]
        
        # Determine card header color based on days in system
        days_in_system = animal['Days in System']
        if days_in_system > 30:
            header_class = "card-header-warning"
            header_text = f"⚠️ {animal['Name']} (AID: {animal['AID']}) - {days_in_system} days in system"
        elif days_in_system > 14:
            header_class = "card-header"
            header_text = f"🐾 {animal['Name']} (AID: {animal['AID']}) - {days_in_system} days in system"
        else:
            header_class = "card-header-success"
            header_text = f"✅ {animal['Name']} (AID: {animal['AID']}) - {days_in_system} days in system"
        
        # Create animal card
        st.markdown(f'<div class="animal-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="{header_class}">{header_text}</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-body">', unsafe_allow_html=True)
        
        # Animal details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Species:** {animal['Species']}")
            st.write(f"**Breed:** {animal['Breed']}")
            st.write(f"**Color:** {animal['Color']}")
            st.write(f"**Sex:** {animal['Sex']}")
            st.write(f"**Age:** {animal['Age']}")
            st.write(f"**Weight:** {animal['Weight']}")
            st.write(f"**Location:** {animal['Location ']}")
            st.write(f"**Intake Date:** {animal['Intake Date']}")
        
        with col2:
            # Status indicators
            st.write("**Status:**")
            foster_status = "✅" if animal['Foster Attempted'] == 'Yes' else "❌"
            transfer_status = "✅" if animal['Transfer Attempted'] == 'Yes' else "❌"
            comm_status = "✅" if animal['Communications Team Attempted'] == 'Yes' else "❌"
            
            st.write(f"Foster: {foster_status}")
            st.write(f"Transfer: {transfer_status}")
            st.write(f"Communications: {comm_status}")
        
        # Welfare notes
        if animal['Welfare Notes']:
            st.markdown("**Welfare Notes:**")
            st.markdown(f'<div class="welfare-notes">{animal["Welfare Notes"]}</div>', unsafe_allow_html=True)
        
        # Images
        try:
            image_urls = get_animal_images_cached(animal['AID'])
            if image_urls:
                st.markdown("**Photos/Videos:**")
                display_media(animal['AID'], image_urls)
        except Exception as e:
            st.warning(f"Could not load images: {e}")
        
        # Edit section
        with st.expander("✏️ Edit Record"):
            st.markdown('<div class="edit-section">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                foster_value = st.selectbox(
                    "Foster Attempted",
                    ["", "Yes", "No"],
                    index=["", "Yes", "No"].index(animal['Foster Attempted']) if animal['Foster Attempted'] in ["", "Yes", "No"] else 0,
                    key=f"foster_{animal['AID']}"
                )
            
            with col2:
                transfer_value = st.selectbox(
                    "Transfer Attempted",
                    ["", "Yes", "No"],
                    index=["", "Yes", "No"].index(animal['Transfer Attempted']) if animal['Transfer Attempted'] in ["", "Yes", "No"] else 0,
                    key=f"transfer_{animal['AID']}"
                )
            
            with col3:
                communications_value = st.selectbox(
                    "Communications Team Attempted",
                    ["", "Yes", "No"],
                    index=["", "Yes", "No"].index(animal['Communications Team Attempted']) if animal['Communications Team Attempted'] in ["", "Yes", "No"] else 0,
                    key=f"comm_{animal['AID']}"
                )
            
            new_note = st.text_area(
                "Add New Note",
                placeholder="Enter new welfare note...",
                key=f"note_{animal['AID']}"
            )
            
            if st.button("💾 Save Changes", key=f"save_{animal['AID']}"):
                if save_record_to_database(animal['AID'], foster_value, transfer_value, communications_value, new_note):
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Export functionality
    st.sidebar.subheader("📊 Export")
    if st.sidebar.button("Export to CSV"):
        export_database_to_csv()
    
    # Database stats
    st.sidebar.subheader("📈 Database Stats")
    try:
        stats = manager.get_database_stats()
        if stats:
            st.sidebar.write(f"**Type:** {stats.get('database_type', 'Unknown')}")
            st.sidebar.write(f"**Animals:** {stats.get('pathways_data', 0)}")
            st.sidebar.write(f"**Inventory:** {stats.get('animal_inventory', 0)}")
            if 'last_updated' in stats:
                st.sidebar.write(f"**Last Updated:** {stats['last_updated']}")
    except Exception as e:
        st.sidebar.warning(f"Could not load stats: {e}")
    
    # Image cache stats
    st.sidebar.subheader("🖼️ Image Cache")
    try:
        cache_stats = get_cache_stats()
        if cache_stats:
            st.sidebar.write(f"**Animals:** {cache_stats.get('total_animals', 0)}")
            st.sidebar.write(f"**With Images:** {cache_stats.get('animals_with_images', 0)}")
            st.sidebar.write(f"**Total Images:** {cache_stats.get('total_images', 0)}")
    except Exception as e:
        st.sidebar.warning(f"Could not load cache stats: {e}")

if __name__ == "__main__":
    main() 