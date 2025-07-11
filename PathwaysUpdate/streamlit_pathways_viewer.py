import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import time
from functools import lru_cache
import re

# Import our image cache manager
from image_cache_manager import get_animal_images_cached, initialize_cache, cleanup_cache, get_cache_stats

# Page configuration
st.set_page_config(
    page_title="Pathways for Care Viewer",
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
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .animal-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .media-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
    }
    .media-item {
        text-align: center;
        margin: 5px;
    }
    .video-link {
        color: #007bff;
        text-decoration: underline;
        font-weight: bold;
        font-size: 12px;
    }
    .welfare-notes {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        white-space: pre-wrap;
        max-height: 300px;
        overflow-y: auto;
    }
    .edit-section {
        background-color: #e9ecef;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Load the CSV data
@st.cache_data
def load_data():
    """Load and process the Pathways for Care data"""
    # Load Pathways for Care data
    pathways_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    df = pd.read_csv(pathways_path)
    
    # Load Animal Inventory data for current location
    inventory_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'AnimalInventory.csv')
    
    try:
        # The AnimalInventory.csv has a complex structure with multiple header rows
        # We need to skip the first 2 rows to get to the actual data
        inventory_df = pd.read_csv(inventory_path, skiprows=2)
        st.sidebar.success(f"Loaded Animal Inventory with {len(inventory_df)} records")
        
        # Find the AID column in inventory (try different possible names)
        aid_columns = ['AnimalNumber', 'AID', 'Animal ID', 'AnimalID', 'ID', 'id']
        inventory_aid_col = None
        for col in aid_columns:
            if col in inventory_df.columns:
                inventory_aid_col = col
                break
        
        if inventory_aid_col:
            st.sidebar.info(f"Found AID column in inventory: {inventory_aid_col}")
            
            # Find the location and sublocation columns in inventory
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
                # Create a mapping from AID to current location (with sublocation if available)
                location_mapping = {}
                for idx, row in inventory_df.iterrows():
                    full_aid = str(row[inventory_aid_col]).strip()
                    
                    # Extract numeric part from full AID (e.g., "A0058757250" -> "58757250")
                    if full_aid.startswith('A00'):
                        aid = full_aid[3:]  # Remove "A00" prefix
                    else:
                        aid = full_aid  # Keep as is if not in expected format
                    
                    location = str(row[inventory_location_col]).strip() if pd.notna(row[inventory_location_col]) else ''
                    
                    # Add sublocation if available
                    if inventory_sublocation_col and pd.notna(row[inventory_sublocation_col]):
                        sublocation = str(row[inventory_sublocation_col]).strip()
                        if sublocation and location:
                            location = f"{location} {sublocation}"
                        elif sublocation:
                            location = sublocation
                    
                    location_mapping[aid] = location
                
                # Update the Pathways data with current locations
                df['Location '] = df['AID'].astype(str).str.strip().map(location_mapping).fillna(df['Location '])
                st.sidebar.success(f"Updated locations for {len(location_mapping)} animals from Animal Inventory")
            else:
                st.sidebar.warning("Warning: No location column found in Animal Inventory")
        else:
            st.sidebar.warning("Warning: No AID column found in Animal Inventory")
            
    except Exception as e:
        st.sidebar.warning(f"Warning: Could not load Animal Inventory data: {e}")
        st.sidebar.info("Using location data from Pathways for Care only")
    
    # Clean up the data
    df = df.fillna('')  # Replace NaN with empty string
    
    # Clean up welfare notes - split into individual lines and ensure consistent spacing
    def clean_welfare_notes(notes):
        if not notes or pd.isna(notes):
            return ""
        
        notes_str = str(notes).strip()
        if not notes_str:
            return ""
        
        # Common separators that indicate different entries
        separators = [
            '\n\n',  # Double line breaks
            ' | ',   # Pipe separator
            ' - ',   # Dash separator
            ' • ',   # Bullet separator
            ' * ',   # Asterisk separator
            ' ~ ',   # Tilde separator
            ' / ',   # Forward slash separator
            ' || ',  # Double pipe
            ' -- ',  # Double dash
        ]
        
        # Try to split by common separators
        for separator in separators:
            if separator in notes_str:
                parts = notes_str.split(separator)
                # Clean up each part and join with double line breaks for consistent spacing
                cleaned_parts = [part.strip() for part in parts if part.strip()]
                return '\n\n'.join(cleaned_parts)
        
        # If no separators found, check for date patterns that might indicate new entries
        # Look for date patterns like MM/DD, MM-DD, etc.
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or MM/DD/YY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\d{1,2}\.\d{1,2}\.\d{2,4}', # MM.DD.YYYY
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, notes_str):
                # Split by date patterns
                parts = re.split(pattern, notes_str)
                if len(parts) > 1:
                    # Reconstruct with dates and double line breaks for consistent spacing
                    result = []
                    for i, part in enumerate(parts):
                        if part.strip():
                            if i > 0:  # Add date back to the part
                                # Find the date that was split
                                date_match = re.search(pattern, notes_str)
                                if date_match:
                                    result.append(f"{date_match.group()}{part.strip()}")
                            else:
                                result.append(part.strip())
                    return '\n\n'.join(result)
        
        # If no clear separators found, normalize line breaks to ensure consistent spacing
        # Replace single line breaks with double line breaks for consistency
        notes_str = re.sub(r'\n(?!\n)', '\n\n', notes_str)
        # Remove any triple or more line breaks and replace with double
        notes_str = re.sub(r'\n{3,}', '\n\n', notes_str)
        
        return notes_str
    
    # Apply welfare notes cleaning
    df['Welfare Notes'] = df['Welfare Notes'].apply(clean_welfare_notes)
    
    # Calculate Days in System from Intake Date
    try:
        # Convert Intake Date to datetime
        df['Intake Date'] = pd.to_datetime(df['Intake Date'], errors='coerce')
        
        # Format Intake Date as mm/dd/yyyy (without time component)
        df['Intake Date'] = df['Intake Date'].dt.strftime('%m/%d/%Y')
        
        # Convert back to datetime for calculation (but keep original for display)
        intake_dates_for_calc = pd.to_datetime(df['Intake Date'], errors='coerce')
        
        # Calculate days from intake date to today
        today = pd.Timestamp.now().normalize()
        df['Days in System'] = (today - intake_dates_for_calc).dt.days
        
        # Fill any invalid values with 0
        df['Days in System'] = df['Days in System'].fillna(0).astype(int)
        
        st.sidebar.success(f"Calculated Days in System for {len(df)} animals from intake dates")
    except Exception as e:
        st.sidebar.warning(f"Warning: Could not calculate Days in System: {e}")
        # Fall back to original calculation
        df['Days in System'] = pd.to_numeric(df['Days in System'], errors='coerce').fillna(0)
    
    return df

def save_data(df):
    """Save data back to CSV file"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
        df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def display_media(animal_id, image_urls):
    """Display images and videos for an animal"""
    if not image_urls:
        st.info("No images or videos available")
        return
    
    # Create columns for media display
    cols = st.columns(min(3, len(image_urls)))
    
    for i, url in enumerate(image_urls):
        col_idx = i % len(cols)
        
        with cols[col_idx]:
            # Check if this is a YouTube link
            if 'youtube.com' in url or 'youtu.be' in url:
                # Extract video ID from YouTube URL
                video_id = None
                
                # Handle different YouTube URL formats
                if 'youtube.com/watch?v=' in url:
                    video_id = url.split('youtube.com/watch?v=')[1].split('&')[0]
                elif 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0]
                elif 'youtube.com/embed/' in url:
                    video_id = url.split('youtube.com/embed/')[1].split('?')[0]
                elif 'img.youtube.com/vi/' in url:
                    # This is a thumbnail URL, extract video ID
                    video_id = url.split('img.youtube.com/vi/')[1].split('/')[0]
                
                if video_id:
                    # Show thumbnail and link to video
                    st.image(url, caption=f"Video {i+1}", use_column_width=True)
                    watch_url = f"https://www.youtube.com/watch?v={video_id}"
                    st.markdown(f"[▶ Watch Video]({watch_url})")
                else:
                    # Fallback to image
                    st.image(url, caption=f"Media {i+1}", use_column_width=True)
            else:
                # Regular image
                st.image(url, caption=f"Image {i+1}", use_column_width=True)

def main():
    # Initialize image cache
    if 'cache_initialized' not in st.session_state:
        st.session_state.cache_initialized = False
    
    if not st.session_state.cache_initialized:
        with st.spinner("Initializing image cache..."):
            cache_success = initialize_cache()
            if cache_success:
                stats = get_cache_stats()
                st.sidebar.success(f"Cache: {stats['animals_with_images']} animals with images, {stats['total_images']} total images")
            else:
                st.sidebar.warning("Cache initialization failed, images may not be available")
        st.session_state.cache_initialized = True
    
    # Load data
    df = load_data()
    
    # Main header
    st.markdown('<h1 class="main-header">🐾 Pathways for Care Viewer</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.title("Controls")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", help="Reload data from CSV file"):
        st.cache_data.clear()
        st.rerun()
    
    # View mode selection
    view_mode = st.sidebar.selectbox(
        "View Mode",
        ["Record Browser", "Spreadsheet View"],
        help="Choose how to view the data"
    )
    
    if view_mode == "Record Browser":
        # Record Browser View
        st.header("Record Browser")
        
        # Search and navigation
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Create search options
            search_options = [f"{row['AID']} - {row['Name']}" for idx, row in df.iterrows()]
            search_options.insert(0, "Select an animal...")
            
            selected_animal = st.selectbox(
                "Search by AID or Name:",
                search_options,
                index=0
            )
        
        with col2:
            if st.button("⬅️ Previous"):
                if 'current_index' not in st.session_state:
                    st.session_state.current_index = 0
                else:
                    st.session_state.current_index = max(0, st.session_state.current_index - 1)
        
        with col3:
            if st.button("Next ➡️"):
                if 'current_index' not in st.session_state:
                    st.session_state.current_index = 0
                else:
                    st.session_state.current_index = min(len(df) - 1, st.session_state.current_index + 1)
        
        # Handle search selection
        if selected_animal != "Select an animal...":
            # Extract AID from selection
            aid = selected_animal.split(" - ")[0]
            # Find the index
            for idx, row in df.iterrows():
                if str(row['AID']).strip() == aid:
                    st.session_state.current_index = idx
                    break
        
        # Initialize current index if not set
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0
        
        # Display current record
        if 0 <= st.session_state.current_index < len(df):
            record = df.iloc[st.session_state.current_index]
            
            # Page indicator
            st.markdown(f"**Record {st.session_state.current_index + 1} of {len(df)}**")
            
            # Animal information card
            with st.container():
                st.markdown('<div class="animal-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Name:** {record['Name'] or 'N/A'}")
                    st.markdown(f"**AID:** [{record['AID']}](https://sms.petpoint.com/sms3/enhanced/animal/{record['AID']})")
                    st.markdown(f"**Species:** {record['Species'] or 'N/A'}")
                    st.markdown(f"**Location:** {record['Location '] or 'N/A'}")
                
                with col2:
                    st.markdown(f"**Intake Date:** {record['Intake Date'] or 'N/A'}")
                    st.markdown(f"**Days in System:** {record['Days in System']:.0f if pd.notna(record['Days in System']) else 'N/A'}")
                    st.markdown(f"**Foster Attempted:** {record['Foster Attempted'] or 'N/A'}")
                    st.markdown(f"**Transfer Attempted:** {record['Transfer Attempted'] or 'N/A'}")
                    st.markdown(f"**Communications Team Attempted:** {record['Communications Team Attempted'] or 'N/A'}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Welfare Notes
            st.subheader("Welfare Notes")
            if record['Welfare Notes']:
                st.markdown(f'<div class="welfare-notes">{record["Welfare Notes"]}</div>', unsafe_allow_html=True)
            else:
                st.info("No welfare notes available")
            
            # Media display
            st.subheader("Media")
            animal_id = str(record['AID']).strip()
            image_urls = get_animal_images_cached(animal_id)
            display_media(animal_id, image_urls)
            
            # Edit section
            st.subheader("Edit Information")
            with st.container():
                st.markdown('<div class="edit-section">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    foster_options = ["", "Yes", "No", "In Progress"]
                    foster_value = st.selectbox(
                        "Foster Attempted:",
                        foster_options,
                        index=foster_options.index(record['Foster Attempted']) if record['Foster Attempted'] in foster_options else 0
                    )
                
                with col2:
                    transfer_options = ["", "Yes", "No", "In Progress"]
                    transfer_value = st.selectbox(
                        "Transfer Attempted:",
                        transfer_options,
                        index=transfer_options.index(record['Transfer Attempted']) if record['Transfer Attempted'] in transfer_options else 0
                    )
                
                with col3:
                    communications_options = ["", "Yes", "No", "In Progress"]
                    communications_value = st.selectbox(
                        "Communications Team Attempted:",
                        communications_options,
                        index=communications_options.index(record['Communications Team Attempted']) if record['Communications Team Attempted'] in communications_options else 0
                    )
                
                # New welfare note
                new_note = st.text_area(
                    "Add new welfare note:",
                    height=100,
                    help="Enter a new welfare note to append to the existing notes"
                )
                
                # Save button
                if st.button("💾 Save Changes", type="primary"):
                    # Update the dataframe
                    if foster_value:
                        df.at[st.session_state.current_index, 'Foster Attempted'] = foster_value
                    
                    if transfer_value:
                        df.at[st.session_state.current_index, 'Transfer Attempted'] = transfer_value
                    
                    if communications_value:
                        df.at[st.session_state.current_index, 'Communications Team Attempted'] = communications_value
                    
                    # Add new welfare note if provided
                    if new_note and new_note.strip():
                        # Get current welfare notes
                        current_notes = df.at[st.session_state.current_index, 'Welfare Notes']
                        if pd.isna(current_notes) or not current_notes:
                            current_notes = ""
                        
                        # Add new note with proper formatting
                        if current_notes:
                            new_welfare_notes = f"{current_notes}\n\n{new_note.strip()}"
                        else:
                            new_welfare_notes = new_note.strip()
                        
                        df.at[st.session_state.current_index, 'Welfare Notes'] = new_welfare_notes
                    
                    # Save to CSV file
                    if save_data(df):
                        st.success("✅ Changes saved successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save changes")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Spreadsheet View
        st.header("Spreadsheet View")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            species_filter = st.multiselect(
                "Filter by Species:",
                options=sorted(df['Species'].unique()),
                default=[]
            )
        
        with col2:
            location_filter = st.multiselect(
                "Filter by Location:",
                options=sorted(df['Location '].unique()),
                default=[]
            )
        
        with col3:
            foster_filter = st.multiselect(
                "Filter by Foster Status:",
                options=sorted(df['Foster Attempted'].unique()),
                default=[]
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if species_filter:
            filtered_df = filtered_df[filtered_df['Species'].isin(species_filter)]
        
        if location_filter:
            filtered_df = filtered_df[filtered_df['Location '].isin(location_filter)]
        
        if foster_filter:
            filtered_df = filtered_df[filtered_df['Foster Attempted'].isin(foster_filter)]
        
        # Display filtered data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name=f"pathways_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main() 