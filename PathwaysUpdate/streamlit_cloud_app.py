#!/usr/bin/env python3
"""
Pathways for Care Viewer - Cloud Database Version
Uses Google Cloud SQL MySQL database by default
"""

import streamlit as st
import pandas as pd
import sqlite3
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

from cloud_database_manager import get_database_manager, connect_to_database
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
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_from_database():
    """Load data from cloud database"""
    try:
        # Connect to cloud database
        st.info("Attempting to connect to cloud database...")
        if not connect_to_database(use_cloud=True):
            st.error("Failed to connect to cloud database")
            return None
        st.success("Successfully connected to cloud database")
        
        # Get database manager
        manager = get_database_manager()
        
        # Load main pathways data
        df = manager.get_pathways_data()
        if df is None:
            return None
        
        # Load inventory data for location updates and Age/Stage
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
                    
                    # Find Age and Stage columns
                    age_col = 'Age' if 'Age' in inventory_df.columns else None
                    stage_col = 'Stage' if 'Stage' in inventory_df.columns else None
                    
                    if inventory_location_col or age_col or stage_col:
                        # Create mappings
                        location_mapping = {}
                        age_mapping = {}
                        stage_mapping = {}
                        
                        for idx, row in inventory_df.iterrows():
                            full_aid = str(row[inventory_aid_col]).strip()
                            
                            # Extract numeric part from full AID
                            if full_aid.startswith('A00'):
                                aid = full_aid[3:]
                            else:
                                aid = full_aid
                            
                            # Location mapping
                            if inventory_location_col:
                                location = str(row[inventory_location_col]).strip() if pd.notna(row[inventory_location_col]) else ''
                                
                                # Add sublocation if available
                                if inventory_sublocation_col and pd.notna(row[inventory_sublocation_col]):
                                    sublocation = str(row[inventory_sublocation_col]).strip()
                                    if sublocation and location:
                                        location = f"{location} {sublocation}"
                                    elif sublocation:
                                        location = sublocation
                                
                                location_mapping[aid] = location
                            
                            # Age mapping
                            if age_col and pd.notna(row[age_col]):
                                age_mapping[aid] = str(row[age_col]).strip()
                            
                            # Stage mapping
                            if stage_col and pd.notna(row[stage_col]):
                                stage_mapping[aid] = str(row[stage_col]).strip()
                        
                        # Update locations
                        if location_mapping:
                            df['Location'] = df['AID'].astype(str).str.strip().map(location_mapping).fillna(df['Location'])
                        
                        # Add Age and Stage columns
                        df['Age'] = df['AID'].astype(str).str.strip().map(age_mapping).fillna('N/A')
                        df['Stage'] = df['AID'].astype(str).str.strip().map(stage_mapping).fillna('N/A')
        
        except Exception as e:
            # If inventory data fails to load, add empty Age and Stage columns
            df['Age'] = 'N/A'
            df['Stage'] = 'N/A'
        
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
        
        df['Welfare_Notes'] = df['Welfare_Notes'].apply(clean_welfare_notes)
        
        # Calculate Days in System
        try:
            df['Intake_Date'] = pd.to_datetime(df['Intake_Date'], errors='coerce')
            df['Intake_Date'] = df['Intake_Date'].dt.strftime('%m/%d/%Y')
            intake_dates_for_calc = pd.to_datetime(df['Intake_Date'], errors='coerce')
            today = pd.Timestamp.now().normalize()
            df['Days_in_System'] = (today - intake_dates_for_calc).dt.days
            df['Days_in_System'] = df['Days_in_System'].fillna(0).astype(int)
        except Exception as e:
            df['Days_in_System'] = pd.to_numeric(df['Days_in_System'], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        return None

def save_record_to_database(aid, foster_value, transfer_value, communications_value, new_note):
    """Save a record to the database"""
    try:
        st.info(f"🔧 save_record_to_database called with AID: {aid}")
        
        manager = get_database_manager()
        st.info(f"🔧 Got database manager: {manager}")
        
        # Check if we have a database connection
        if not manager.connection:
            st.error("❌ No database connection available!")
            st.info("🔧 Attempting to connect to cloud database...")
            if not connect_to_database(use_cloud=True):
                st.error("❌ Failed to connect to cloud database")
                return False
            st.success("✅ Connected to cloud database")
        
        st.info(f"🔧 Database type: {manager.db_type}")
        st.info(f"🔧 Connection status: {manager.connection is not None}")
        
        success = manager.update_animal_record(aid, foster_value, transfer_value, communications_value, new_note)
        st.info(f"🔧 update_animal_record returned: {success}")
        
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
        import traceback
        st.error(f"Full traceback: {traceback.format_exc()}")
        return False

def export_database_to_csv():
    """Export database to CSV"""
    try:
        # Ensure we have a fresh connection
        if not connect_to_database(use_cloud=True):
            st.error("Failed to connect to cloud database.")
            return False
        
        manager = get_database_manager()
        
        # Get the data
        df = manager.get_pathways_data()
        
        # Debug info
        if df is None:
            st.error("Database query returned None")
            return False
        
        if len(df) == 0:
            st.error("Database query returned empty DataFrame")
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
        st.success(f"✅ Ready to export {len(df)} records")
        return True
            
    except Exception as e:
        st.error(f"Export error: {e}")
        st.error(f"Error type: {type(e)}")
        return False

def display_media(animal_id, image_urls):
    """Display images and videos for an animal in a compact horizontal scroll"""
    if not image_urls:
        st.markdown('<div style="text-align: center; padding: 20px; color: #6c757d; font-style: italic; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">No images or videos available</div>', unsafe_allow_html=True)
        return
    
    # Build HTML content as a single string for horizontal scroll
    html_content = '<div style="width: 100%; overflow-x: auto; overflow-y: hidden; white-space: nowrap; padding: 8px; scrollbar-width: thin; scrollbar-color: #bc6f32 #f8f9fa; -webkit-overflow-scrolling: touch;"><div style="display: inline-flex; gap: 8px; align-items: center; min-width: min-content;">'
    
    for i, url in enumerate(image_urls):
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
                html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px;"><img src="{url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Video {i+1}"><div style="font-size: 12px; margin-top: 2px; font-weight: bold;"><a href="{watch_url}" target="_blank" style="color: #bc6f32; text-decoration: underline;">▶ Watch Video</a></div></div>'
            else:
                html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px;"><img src="{url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Media {i+1}"><div style="font-size: 10px; margin-top: 2px;">Media {i+1}</div></div>'
        else:
            html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px;"><img src="{url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Image {i+1}"><div style="font-size: 10px; margin-top: 2px;">Image {i+1}</div></div>'
    
    html_content += '</div></div>'
    
    # Display the compact horizontal scroll layout
    st.markdown(html_content, unsafe_allow_html=True)

def main():
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
    st.markdown('<h1 class="main-header">Pathways for Care Viewer</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.title("Controls")
    
    # Export to CSV
    if st.sidebar.button("📤 Export to CSV"):
        export_database_to_csv()
    
    # View mode selection
    view_mode = st.sidebar.selectbox(
        "View Mode",
        ["Animal Details", "Spreadsheet View"],
        help="Choose how to view the data"
    )
    
    # Load data
    df = load_data_from_database()
    if df is None:
        st.error("Failed to load data from database")
        return
    
    if view_mode == "Animal Details":
        # Animal Details View - matching original layout
        
        # Search dropdown
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        st.markdown('<p class="form-label">Search Animal:</p>', unsafe_allow_html=True)
        
        search_options = [f"{row['AID']} - {row['Name']}" for idx, row in df.iterrows()]
        search_options.insert(0, "Select an animal...")
        
        selected_animal = st.selectbox(
            "Search by AID or Name:",
            search_options,
            index=0,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Initialize current index once
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0
        
        # Navigation controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Previous", key="prev_button"):
                st.session_state.current_index = max(0, st.session_state.current_index - 1)
                st.rerun()
        
        with col2:
            st.markdown(f'<div class="page-indicator">Animal {st.session_state.current_index + 1} of {len(df)}</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button("Next →", key="next_button"):
                st.session_state.current_index = min(len(df) - 1, st.session_state.current_index + 1)
                st.rerun()
        
        # Handle search selection
        if selected_animal != "Select an animal...":
            aid = selected_animal.split(" - ")[0]
            for idx, row in df.iterrows():
                if str(row['AID']).strip() == aid:
                    st.session_state.current_index = idx
                    break
        
        # Display current record
        if 0 <= st.session_state.current_index < len(df):
            record = df.iloc[st.session_state.current_index]
            
            # Image section - centered
            st.markdown('<div class="image-container" style="display: flex; justify-content: center; align-items: center;">', unsafe_allow_html=True)
            animal_id = str(record['AID']).strip()
            image_urls = get_animal_images_cached(animal_id)
            display_media(animal_id, image_urls)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Animal Information Card
            st.markdown('<div class="card-header">Animal Information</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Name:** {record['Name'] or 'N/A'}")
                st.markdown(f"**AID:** <a href='https://sms.petpoint.com/sms3/enhanced/animal/{record['AID']}' target='_blank' style='color: #bc6f32; text-decoration: underline;'>{record['AID']}</a>", unsafe_allow_html=True)
                st.markdown(f"**Species:** {record['Species'] or 'N/A'}")
                st.markdown(f"**Age:** {record['Age'] or 'N/A'}")
            
            with col2:
                st.markdown(f"**Location:** {record['Location'] or 'N/A'}")
                st.markdown(f"**Intake Date:** {record['Intake_Date'] or 'N/A'}")
                days_value = record['Days_in_System'] if pd.notna(record['Days_in_System']) else 'N/A'
                if isinstance(days_value, (int, float)) and days_value != 'N/A':
                    st.markdown(f"**Days in System:** {days_value:.0f}")
                else:
                    st.markdown(f"**Days in System:** {days_value}")
                st.markdown(f"**Stage:** {record['Stage'] or 'N/A'}")
            
            with col3:
                st.markdown(f"**Foster Attempted:** {record['Foster_Attempted'] or 'N/A'}")
                st.markdown(f"**Transfer Attempted:** {record['Transfer_Attempted'] or 'N/A'}")
                st.markdown(f"**Communications Team:** {record['Communications_Team_Attempted'] or 'N/A'}")
            
            # Welfare Notes Card
            st.markdown('<div class="card-header card-header-warning">Welfare Notes</div>', unsafe_allow_html=True)
            
            if record['Welfare_Notes']:
                st.markdown(f'<div class="welfare-notes">{record["Welfare_Notes"]}</div>', unsafe_allow_html=True)
            else:
                st.info("No welfare notes available")
            
            # Edit Information Card
            st.markdown('<div class="card-header card-header-success">Edit Information</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<p class="form-label">Foster Attempted:</p>', unsafe_allow_html=True)
                foster_options = ["", "Yes", "No", "N/A"]
                foster_value = st.selectbox(
                    "Foster Attempted:",
                    foster_options,
                    index=foster_options.index(record['Foster_Attempted']) if record['Foster_Attempted'] in foster_options else 0,
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown('<p class="form-label">Transfer Attempted:</p>', unsafe_allow_html=True)
                transfer_options = ["", "Yes", "No", "N/A"]
                transfer_value = st.selectbox(
                    "Transfer Attempted:",
                    transfer_options,
                    index=transfer_options.index(record['Transfer_Attempted']) if record['Transfer_Attempted'] in transfer_options else 0,
                    label_visibility="collapsed"
                )
            
            with col3:
                st.markdown('<p class="form-label">Communications Team Attempted:</p>', unsafe_allow_html=True)
                communications_options = ["", "Yes", "No", "N/A"]
                communications_value = st.selectbox(
                    "Communications Team Attempted:",
                    communications_options,
                    index=communications_options.index(record['Communications_Team_Attempted']) if record['Communications_Team_Attempted'] in communications_options else 0,
                    label_visibility="collapsed"
                )
            
            st.markdown('<p class="form-label">Add New Welfare Note:</p>', unsafe_allow_html=True)
            new_note = st.text_area(
                "Add new welfare note:",
                height=100,
                placeholder="Type your new welfare note here...",
                label_visibility="collapsed"
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Save Changes", type="primary"):
                    st.info(f"🔧 Attempting to save changes for animal {record['AID']}")
                    st.info(f"🔧 Values: foster={foster_value}, transfer={transfer_value}, comms={communications_value}")
                    st.info(f"🔧 New note: {new_note[:50] if new_note else 'None'}...")
                    
                    if save_record_to_database(record['AID'], foster_value, transfer_value, communications_value, new_note):
                        st.success("✅ Changes saved to database!")
                        st.cache_data.clear()  # Clear cache to reload data
                        st.rerun()
                    else:
                        st.error("❌ Failed to save changes")
                        st.error("Check the console logs for detailed error information")

    else:
        # Spreadsheet View
        st.header("Spreadsheet View")

        # Prepare styled DataFrame
        def make_clickable(val):
            aid = str(val)
            return f'<a href="https://sms.petpoint.com/sms3/enhanced/animal/{aid}" target="_blank" style="color:#bc6f32;text-decoration:underline;">{aid}</a>'

        styled_df = df.copy()
        styled_df['AID'] = styled_df['AID'].apply(make_clickable)

        # Use pandas Styler for formatting
        styler = styled_df.style \
            .set_properties(**{
                'text-align': 'center',
                'vertical-align': 'middle',
                'font-size': '12px',
                'padding': '8px',
                'white-space': 'normal',
                'overflow': 'hidden',
                'text-overflow': 'ellipsis',
                'min-height': '80px',
                'max-height': '120px',
            }) \
            .set_properties(subset=['Welfare_Notes'], **{'text-align': 'left', 'min-width': '300px', 'max-width': '400px'}) \
            .set_properties(subset=['AID'], **{'min-width': '100px', 'max-width': '120px'}) \
            .apply(lambda x: ['background-color: #f8f9fa; color: #333333' if i%2 else 'background-color: #ffffff; color: #333333' for i in range(len(x))], axis=0) \
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#062b49'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center'), ('vertical-align', 'middle')]},
                {'selector': 'td', 'props': [('vertical-align', 'middle')]},
            ])

        st.markdown("<style>div[data-testid='stDataFrame'] table {font-size: 12px;}</style>", unsafe_allow_html=True)
        st.write("<small>Tip: Click an AID to open the animal's PetPoint page in a new tab.</small>", unsafe_allow_html=True)
        st.write(styler.to_html(escape=False), unsafe_allow_html=True)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data",
            data=csv,
            file_name=f"pathways_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main() 