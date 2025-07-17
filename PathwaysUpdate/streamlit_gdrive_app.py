#!/usr/bin/env python3
"""
Pathways for Care Viewer - Google Drive Version
Uses Google Drive CSV file instead of Google Cloud SQL
Much more cost-effective solution
"""

import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system environment variables

from google_drive_manager import get_gdrive_manager, connect_to_gdrive
from image_cache_manager import get_animal_images_cached, initialize_cache

# Page configuration
st.set_page_config(
    page_title="Pathways for Care Viewer",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Texta:wght@400;700&display=swap');
    
    * {
        font-family: 'Texta', sans-serif;
    }
    
    .main-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        font-family: 'Texta', sans-serif;
        margin-bottom: 2rem;
        padding: 1rem;
        background: #062b49;
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .card-header {
        background: #062b49;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-weight: 700;
        font-family: 'Texta', sans-serif;
        font-size: 1.2rem;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    .card-header-warning {
        background: #bc6f32;
    }
    
    .card-header-success {
        background: #4f5b35;
    }
    
    .welfare-notes {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #bc6f32;
        font-style: italic;
        white-space: pre-wrap;
        max-height: 300px;
        overflow-y: auto;
        color: #333333;
        font-family: 'Texta', sans-serif;
        font-weight: 400;
    }
    
    .form-label {
        font-weight: 700;
        font-family: 'Texta', sans-serif;
        color: #495057;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .search-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #dee2e6;
    }
    
    .page-indicator {
        text-align: center;
        font-weight: 700;
        font-family: 'Texta', sans-serif;
        color: #6c757d;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    
    .nav-controls {
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    
    .image-container {
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    
    .edit-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-top: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 700;
        font-family: 'Texta', sans-serif;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 8px;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        font-family: 'Texta', sans-serif;
        font-weight: 400;
    }
    
    .stMarkdown {
        font-family: 'Texta', sans-serif;
        font-weight: 400;
    }
    
    .stMarkdown strong {
        font-weight: 700;
        font-family: 'Texta', sans-serif;
    }
    
    /* Custom scrollbar styling for webkit browsers */
    ::-webkit-scrollbar {
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #bc6f32;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a05a28;
    }
    
    /* Force scrollbar to always show for image containers */
    .image-scroll-container::-webkit-scrollbar {
        height: 12px !important;
        display: block !important;
    }
    
    .image-scroll-container::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 6px !important;
    }
    
    .image-scroll-container::-webkit-scrollbar-thumb {
        background: #bc6f32 !important;
        border-radius: 6px !important;
    }
    
    .image-scroll-container::-webkit-scrollbar-thumb:hover {
        background: #a05a28 !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_from_drive():
    """Load data from Google Drive CSV"""
    try:
        # Connect to Google Drive
        if not connect_to_gdrive():
            st.error("Failed to connect to Google Drive")
            return None
        
        # Get Google Drive manager
        manager = get_gdrive_manager()
        
        # Load pathways data
        df = manager.get_pathways_data()
        if df is None:
            return None
        
        # Clean and process the data
        if len(df) > 0:
            # Clean welfare notes
            def clean_welfare_notes(notes):
                if pd.isna(notes) or notes == "":
                    return ""
                # Remove extra whitespace and normalize line breaks
                cleaned = str(notes).strip()
                # Replace multiple newlines with double newlines
                cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
                return cleaned
            
            # Apply cleaning to welfare notes column
            welfare_col = None
            for col in ['Welfare Notes', 'Welfare_Notes', 'welfare_notes']:
                if col in df.columns:
                    welfare_col = col
                    break
            
            if welfare_col:
                df[welfare_col] = df[welfare_col].apply(clean_welfare_notes)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def save_record_to_drive(aid, foster_value, transfer_value, communications_value, new_note):
    """Save a record to Google Drive CSV"""
    try:
        manager = get_gdrive_manager()
        
        # Check if we have a connection
        if not manager.service:
            if not connect_to_gdrive():
                st.error("Failed to connect to Google Drive")
                return False
        
        success = manager.update_animal_record(aid, foster_value, transfer_value, communications_value, new_note)
        
        if success:
            # Clear cache to reload data
            st.cache_data.clear()
            return True
        else:
            st.error("Failed to update record")
            return False
            
    except Exception as e:
        st.error(f"Google Drive error: {e}")
        return False

def export_drive_to_csv():
    """Export Google Drive data to CSV"""
    try:
        # Ensure we have a fresh connection
        if not connect_to_gdrive():
            st.error("Failed to connect to Google Drive")
            return False
        
        manager = get_gdrive_manager()
        
        # Get the data
        df = manager.get_pathways_data()
        
        if df is None or len(df) == 0:
            st.error("No data available to export")
            return False
        
        # Convert DataFrame to CSV string
        csv_data = df.to_csv(index=False)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Pathways_Data_Export_{timestamp}.csv"
        
        st.download_button(
            label="Download CSV Export",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )
        return True
        
    except Exception as e:
        st.error(f"Export error: {e}")
        return False

def display_media(animal_id, image_urls):
    """Display images and videos for an animal with navigation buttons - 5 at a time"""
    if not image_urls:
        st.markdown('<div style="text-align: center; padding: 20px; color: #6c757d; font-style: italic; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">No images or videos available</div>', unsafe_allow_html=True)
        return
    
    # Initialize current page for this animal
    page_key = f"current_page_{animal_id}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    
    current_page = st.session_state[page_key]
    images_per_page = 5
    total_pages = (len(image_urls) + images_per_page - 1) // images_per_page
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("←", key=f"prev_page_{animal_id}"):
            st.session_state[page_key] = max(0, current_page - 1)
            st.rerun()
    
    with col2:
        start_idx = current_page * images_per_page + 1
        end_idx = min((current_page + 1) * images_per_page, len(image_urls))
        st.markdown(f'<div style="text-align: center; font-weight: bold; color: #6c757d; padding: 8px;">Images {start_idx}-{end_idx} of {len(image_urls)}</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("→", key=f"next_page_{animal_id}"):
            st.session_state[page_key] = min(total_pages - 1, current_page + 1)
            st.rerun()
    
    # Display current page of images
    start_idx = current_page * images_per_page
    end_idx = min(start_idx + images_per_page, len(image_urls))
    current_images = image_urls[start_idx:end_idx]
    
    # Build HTML for 5 images in a row
    html_content = '<div style="display: flex; flex-wrap: nowrap; gap: 8px; align-items: center; justify-content: center; padding: 8px;">'
    
    for i, url in enumerate(current_images):
        if 'youtube.com' in url or 'youtu.be' in url:
            # Extract video ID
            video_id = None
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('youtube.com/watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            elif 'youtube.com/embed/' in url:
                video_id = url.split('youtube.com/embed/')[1].split('?')[0]
            elif 'img.youtube.com/vi/' in url:
                video_id = url.split('img.youtube.com/vi/')[1].split('/')[0]
    
            if video_id:
                watch_url = f"https://www.youtube.com/watch?v={video_id}"
                html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px;"><img src="{url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Video {start_idx + i + 1}"><div style="font-size: 12px; margin-top: 2px; font-weight: bold;"><a href="{watch_url}" target="_blank" style="color: #bc6f32; text-decoration: underline;">▶ Watch Video</a></div></div>'
            else:
                html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px;"><img src="{url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Media {start_idx + i + 1}"><div style="font-size: 10px; margin-top: 2px;">Media {start_idx + i + 1}</div></div>'
        else:
            html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px;"><img src="{url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Image {start_idx + i + 1}"><div style="font-size: 10px; margin-top: 2px;">Image {start_idx + i + 1}</div></div>'
    
    html_content += '</div>'
    
    # Display the images
    st.markdown(html_content, unsafe_allow_html=True)

def main():
    # Password protection
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<h1 class="main-header">Pathways for Care Viewer</h1>', unsafe_allow_html=True)
        
        # Center the password input
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #062b49; margin-bottom: 20px;">🔐 Authentication Required</h3>', unsafe_allow_html=True)
            
            password = st.text_input("Enter Password:", type="password", label_visibility="collapsed")
            
            if st.button("Login", type="primary", use_container_width=True):
                if password == "SPCAPathways1*":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        return
    
    # Initialize image cache (with cloud environment handling)
    if 'cache_initialized' not in st.session_state:
        st.session_state.cache_initialized = False
    
    if not st.session_state.cache_initialized:
        with st.spinner("Initializing image cache..."):
            try:
                cache_success = initialize_cache()
                if not cache_success:
                    st.sidebar.warning("⚠️ No image cache found")
                    st.sidebar.info("📋 Images will not be available. To enable images:")
                    st.sidebar.markdown("""
                    **Build cache locally:** Run `python build_cache.py`  
                    **Push to git:** Upload the `animal_images_cache.json` file  
                    **Deploy:** The app will automatically use the updated cache
                    """)
                else:
                    st.sidebar.success("✅ Image cache loaded successfully")
            except Exception as e:
                st.sidebar.warning(f"⚠️ Cache loading failed: {str(e)}")
                st.sidebar.info("📋 Images will not be available. Check that animal_images_cache.json exists.")
        st.session_state.cache_initialized = True
    
    # Main header
    st.markdown('<h1 class="main-header">Pathways for Care Viewer (Google Drive)</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.title("Controls")
    
    # Export to CSV
    if st.sidebar.button("📤 Export to CSV"):
        export_drive_to_csv()
    
    # View mode selection
    view_mode = st.sidebar.selectbox(
        "View Mode",
        ["Animal Details", "Spreadsheet View"],
        help="Choose how to view the data"
    )
    
    # Load data
    df = load_data_from_drive()
    if df is None:
        st.error("Failed to load data from Google Drive")
        return
    
    if len(df) == 0:
        st.warning("No data found in Google Drive CSV file")
        return
    
    # Search functionality
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #062b49; margin-bottom: 1rem;">🔍 Search Animals</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_aid = st.text_input("Search by AID:", placeholder="Enter AID...")
    
    with col2:
        search_name = st.text_input("Search by Name:", placeholder="Enter animal name...")
    
    with col3:
        search_location = st.text_input("Search by Location:", placeholder="Enter location...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter data based on search
    filtered_df = df.copy()
    
    if search_aid:
        filtered_df = filtered_df[filtered_df['AID'].astype(str).str.contains(search_aid, case=False, na=False)]
    
    if search_name:
        name_col = None
        for col in ['Animal Name', 'AnimalName', 'Name', 'name']:
            if col in filtered_df.columns:
                name_col = col
                break
        
        if name_col:
            filtered_df = filtered_df[filtered_df[name_col].astype(str).str.contains(search_name, case=False, na=False)]
    
    if search_location:
        location_col = None
        for col in ['Location', 'Current Location', 'Location ', 'CurrentLocation']:
            if col in filtered_df.columns:
                location_col = col
                break
        
        if location_col:
            filtered_df = filtered_df[filtered_df[location_col].astype(str).str.contains(search_location, case=False, na=False)]
    
    if len(filtered_df) == 0:
        st.warning("No animals found matching your search criteria")
        return
    
    # Display data based on view mode
    if view_mode == "Animal Details":
        # Animal Details View
        st.markdown(f'<div class="page-indicator">Showing {len(filtered_df)} animals</div>', unsafe_allow_html=True)
        
        # Pagination
        items_per_page = 10
        total_pages = (len(filtered_df) + items_per_page - 1) // items_per_page
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        
        # Navigation controls
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("← Previous", disabled=st.session_state.current_page == 0):
                st.session_state.current_page = max(0, st.session_state.current_page - 1)
                st.rerun()
        
        with col2:
            st.markdown(f'<div class="page-indicator">Page {st.session_state.current_page + 1} of {total_pages}</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button("Next →", disabled=st.session_state.current_page >= total_pages - 1):
                st.session_state.current_page = min(total_pages - 1, st.session_state.current_page + 1)
                st.rerun()
        
        # Display current page
        start_idx = st.session_state.current_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_df))
        current_page_data = filtered_df.iloc[start_idx:end_idx]
        
        for idx, record in current_page_data.iterrows():
            st.markdown('<div class="card-header">', unsafe_allow_html=True)
            st.markdown(f"🐾 <strong>AID: {record['AID']}</strong>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Animal information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Animal Information:**")
                
                # Find name column
                name_col = None
                for col in ['Animal Name', 'AnimalName', 'Name', 'name']:
                    if col in record.index:
                        name_col = col
                        break
                
                if name_col and pd.notna(record[name_col]):
                    st.write(f"**Name:** {record[name_col]}")
                
                # Find location columns
                location_col = None
                sublocation_col = None
                for col in ['Location', 'Current Location', 'Location ', 'CurrentLocation']:
                    if col in record.index:
                        location_col = col
                        break
                
                for col in ['SubLocation', 'Sub Location', 'SubLocation ', 'Sub-Location']:
                    if col in record.index:
                        sublocation_col = col
                        break
                
                if location_col and pd.notna(record[location_col]):
                    st.write(f"**Location:** {record[location_col]}")
                
                if sublocation_col and pd.notna(record[sublocation_col]):
                    st.write(f"**Sub-Location:** {record[sublocation_col]}")
                
                # Age and Stage
                age_col = None
                stage_col = None
                for col in ['Age', 'age', 'Animal Age']:
                    if col in record.index:
                        age_col = col
                        break
                
                for col in ['Stage', 'stage', 'Animal Stage']:
                    if col in record.index:
                        stage_col = col
                        break
                
                if age_col and pd.notna(record[age_col]):
                    st.write(f"**Age:** {record[age_col]}")
                
                if stage_col and pd.notna(record[stage_col]):
                    st.write(f"**Stage:** {record[stage_col]}")
            
            with col2:
                st.markdown("**Pathways Status:**")
                
                # Foster status
                foster_col = None
                for col in ['Foster_Attempted', 'Foster Attempted', 'FosterAttempted']:
                    if col in record.index:
                        foster_col = col
                        break
                
                if foster_col:
                    foster_value = record[foster_col] if pd.notna(record[foster_col]) else "Not Attempted"
                    if foster_value == "Yes":
                        st.markdown("🟢 **Foster:** Attempted")
                    elif foster_value == "No":
                        st.markdown("🔴 **Foster:** Not Attempted")
                    else:
                        st.markdown(f"⚪ **Foster:** {foster_value}")
                
                # Transfer status
                transfer_col = None
                for col in ['Transfer_Attempted', 'Transfer Attempted', 'TransferAttempted']:
                    if col in record.index:
                        transfer_col = col
                        break
                
                if transfer_col:
                    transfer_value = record[transfer_col] if pd.notna(record[transfer_col]) else "Not Attempted"
                    if transfer_value == "Yes":
                        st.markdown("🟢 **Transfer:** Attempted")
                    elif transfer_value == "No":
                        st.markdown("🔴 **Transfer:** Not Attempted")
                    else:
                        st.markdown(f"⚪ **Transfer:** {transfer_value}")
                
                # Communications status
                comms_col = None
                for col in ['Communications_Team_Attempted', 'Communications Team Attempted', 'CommunicationsTeamAttempted']:
                    if col in record.index:
                        comms_col = col
                        break
                
                if comms_col:
                    comms_value = record[comms_col] if pd.notna(record[comms_col]) else "Not Attempted"
                    if comms_value == "Yes":
                        st.markdown("🟢 **Communications:** Attempted")
                    elif comms_value == "No":
                        st.markdown("🔴 **Communications:** Not Attempted")
                    else:
                        st.markdown(f"⚪ **Communications:** {comms_value}")
            
            # Welfare notes
            welfare_col = None
            for col in ['Welfare Notes', 'Welfare_Notes', 'welfare_notes']:
                if col in record.index:
                    welfare_col = col
                    break
            
            if welfare_col and pd.notna(record[welfare_col]) and str(record[welfare_col]).strip():
                st.markdown('<div class="welfare-notes">', unsafe_allow_html=True)
                st.markdown(f"**Welfare Notes:**\n{record[welfare_col]}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Images
            image_col = None
            for col in ['Image_URLs', 'Image URLs', 'image_urls', 'Images']:
                if col in record.index:
                    image_col = col
                    break
            
            if image_col and pd.notna(record[image_col]) and str(record[image_col]).strip():
                image_urls = str(record[image_col]).split(',')
                image_urls = [url.strip() for url in image_urls if url.strip()]
                
                if image_urls:
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    st.markdown("**Images/Videos:**")
                    display_media(record['AID'], image_urls)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Edit section
            st.markdown('<div class="edit-section">', unsafe_allow_html=True)
            st.markdown("**Edit Animal Record:**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                foster_value = st.selectbox(
                    "Foster Attempted:",
                    ["Not Attempted", "Yes", "No"],
                    index=["Not Attempted", "Yes", "No"].index(record.get(foster_col, "Not Attempted")),
                    key=f"foster_{record['AID']}"
                )
            
            with col2:
                transfer_value = st.selectbox(
                    "Transfer Attempted:",
                    ["Not Attempted", "Yes", "No"],
                    index=["Not Attempted", "Yes", "No"].index(record.get(transfer_col, "Not Attempted")),
                    key=f"transfer_{record['AID']}"
                )
            
            with col3:
                communications_value = st.selectbox(
                    "Communications Team Attempted:",
                    ["Not Attempted", "Yes", "No"],
                    index=["Not Attempted", "Yes", "No"].index(record.get(comms_col, "Not Attempted")),
                    key=f"comms_{record['AID']}"
                )
            
            new_note = st.text_area(
                "Add New Note:",
                placeholder="Enter new welfare note...",
                key=f"note_{record['AID']}"
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Save Changes", type="primary"):
                    if save_record_to_drive(record['AID'], foster_value, transfer_value, communications_value, new_note):
                        st.cache_data.clear()  # Clear cache to reload data
                        st.rerun()
                    else:
                        st.error("Failed to save changes")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
    
    else:
        # Spreadsheet View
        st.markdown('<div class="card-header">Spreadsheet View</div>', unsafe_allow_html=True)
        
        # Create a copy for display
        display_df = filtered_df.copy()
        
        # Clean up the display
        def make_clickable(val):
            if pd.isna(val) or val == "":
                return ""
            return str(val)
        
        # Apply clickable formatting to all columns
        for col in display_df.columns:
            display_df[col] = display_df[col].apply(make_clickable)
        
        # Display the dataframe
        st.dataframe(display_df, use_container_width=True)

if __name__ == "__main__":
    main() 