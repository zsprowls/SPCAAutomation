#!/usr/bin/env python3
# Pathways for Care Viewer - Google Drive Version
# Uses Google Drive Sheet instead of database
# Pulls data from multiple sources and merges them

import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import json
from pathlib import Path
import traceback

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from google_drive_manager import get_gdrive_manager, connect_to_gdrive
from image_cache_manager import get_animal_images_cached, initialize_cache, get_cache_manager

# Page configuration
st.set_page_config(
    page_title="Pathways for Care Viewer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Texta:wght@400;700&display=swap');
    * { font-family: 'Texta', sans-serif; font-weight: 400; }
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .filter-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #dee2e6;
    }
    .data-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    .stSelectbox > div > div > div {
        border-radius: 8px;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 700;
        font-family: 'Texta', sans-serif;
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
    .section-header {
        font-family: 'Texta', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 10px;
        border-radius: 8px;
        margin: 20px 0;
        color: white;
    }
    .section-content {
        font-family: 'Texta', sans-serif;
        font-weight: 400;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_from_multiple_sources():
    """Load data from multiple sources and merge them"""
    try:
        # Get Google Drive manager (using service account for authentication)
        manager = get_gdrive_manager(use_service_account=True)
        # Load pathways data from Google Sheet using API key
        df_pathways = manager.read_from_sheets_with_api_key()
        if df_pathways is None:
            st.error("❌ Failed to load pathways data from Google Sheet")
            return None
        # Load additional animal data from AnimalInventory.csv
        try:
            inventory_file = os.path.join(os.path.dirname(__file__), "..", "__Load Files Go Here__", "AnimalInventory.csv")
            if os.path.exists(inventory_file):
                df_inventory = pd.read_csv(inventory_file, skiprows=2)
                # Extract AID from AnimalNumber (last 8 characters)
                df_inventory['AID'] = df_inventory['AnimalNumber'].str[-8:].astype(str)
                # Merge pathways data with inventory data on AID
                if 'AID' in df_pathways.columns and 'AID' in df_inventory.columns:
                    # Convert AID to string for merging
                    df_pathways['AID'] = df_pathways['AID'].astype(str)
                    # Merge the dataframes
                    df_merged = pd.merge(df_pathways, df_inventory, on='AID', how='left', suffixes=('', '_inv'))
                else:
                    st.warning("⚠️ AID column not found in one or both datasets, using pathways data only")
                    df_merged = df_pathways
            else:
                st.warning("⚠️ AnimalInventory.csv not found, using pathways data only")
                df_merged = df_pathways
        except Exception as e:
            st.warning(f"⚠️ Error loading inventory data: {e}, using pathways data only")
            st.error(f"Full traceback: {traceback.format_exc()}")
            df_merged = df_pathways
        # Load images from cache and add to dataframe
        try:
            cache_manager = get_cache_manager()
            image_data = []
            for aid in df_merged['AID']:
                images = cache_manager.get_animal_images(str(aid))
                image_data.append(','.join(images) if images else "")
            df_merged['Image_URLs'] = image_data
        except Exception as e:
            st.warning(f"⚠️ Error loading image data: {e}")
            st.error(f"Full traceback: {traceback.format_exc()}")
            df_merged['Image_URLs'] = ''
        # Calculate Length of Stay if IntakeDateTime is available
        try:
            if 'IntakeDateTime' in df_merged.columns:
                df_merged['IntakeDateTime'] = pd.to_datetime(df_merged['IntakeDateTime'], errors='coerce')
                df_merged['Length of Stay'] = (datetime.now() - df_merged['IntakeDateTime']).dt.days
        except Exception as e:
            st.warning(f"⚠️ Error calculating Length of Stay: {e}")
        # Clean and process the data
        if len(df_merged) > 0:
            def clean_welfare_notes(notes):
                if pd.isna(notes) or notes == "":
                    return ""
                cleaned = str(notes).strip()
                cleaned = re.sub(r'\n+', '\n', cleaned)
                return cleaned
            welfare_col = None
            for col in ['Welfare Notes', 'Welfare_Notes', 'welfare_notes']:
                if col in df_merged.columns:
                    welfare_col = col
                    break
            if welfare_col:
                df_merged[welfare_col] = df_merged[welfare_col].apply(clean_welfare_notes)
        return df_merged
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.error(f"Full traceback: {traceback.format_exc()}")
        return None

def save_record_to_drive(aid, foster_value, transfer_value, communications_value, new_note):
    """Save a record to Google Drive Sheet using API key"""
    try:
        manager = get_gdrive_manager(use_service_account=True)
        success = manager.update_animal_record_with_api_key(aid, foster_value, transfer_value, communications_value, new_note)
        if success:
            st.success(f"✅ Successfully updated animal {aid}")
            st.cache_data.clear()
            return True
        else:
            st.error(f"❌ Failed to update animal {aid}")
            return False
    except Exception as e:
        st.error(f"❌ Google Drive error: {e}")
        st.error(f"Full traceback: {traceback.format_exc()}")
        return False

def display_media(animal_id, image_urls):
    """Display images and videos for an animal"""
    if not image_urls:
        st.markdown('<div style="text-align: center; padding: 20px; color: #6c757d; font-style: italic;">No images available</div>', unsafe_allow_html=True)
        return
    
    # Initialize current page for this animal
    page_key = f"current_page_{animal_id}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    current_page = st.session_state[page_key]
    images_per_page = 5
    total_pages = (len(image_urls) + images_per_page - 1) // images_per_page
    
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("←", key=f"prev_page_{animal_id}"):
            st.session_state[page_key] = max(0, current_page - 1)
            st.rerun()
    with col2:
        start_idx = current_page * images_per_page + 1
        end_idx = min((current_page + 1) * images_per_page, len(image_urls))
        st.markdown(f'<div style="text-align: center; font-weight: bold; color: #6757d; padding: 8px;">Images {start_idx}-{end_idx} of {len(image_urls)}</div>', unsafe_allow_html=True)
    with col3:
        if st.button("→", key=f"next_page_{animal_id}"):
            st.session_state[page_key] = min(total_pages - 1, current_page + 1)
            st.rerun()
    
    # Display current page of images
    start_idx = current_page * images_per_page
    end_idx = min(start_idx + images_per_page, len(image_urls))
    current_images = image_urls[start_idx:end_idx]
    
    # Build HTML for images in a row
    html_content = '<div style="display: flex; flex-wrap: nowrap; gap:8px; align-items: center; justify-content: center; padding: 8px;">'
    
    for i, url in enumerate(current_images):
        url = url.strip()
        # Check for YouTube thumbnail image
        yt_thumb_match = None
        import re
        yt_thumb_pattern = r"img\.youtube\.com/vi/([\w-]+)/default\.jpg"
        yt_thumb_match = re.search(yt_thumb_pattern, url)
        if yt_thumb_match:
            video_id = yt_thumb_match.group(1)
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail_url = url
            html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px; position: relative;">'
            html_content += f'<a href="{watch_url}" target="_blank" style="text-decoration: none;">'
            html_content += f'<div style="position: relative; display: inline-block;">'
            html_content += f'<img src="{thumbnail_url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1)" alt="Video {start_idx + i + 1}">'
            html_content += f'<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.7); border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center;">'
            html_content += f'<div style="color: white; font-size: 20px;">▶</div>'
            html_content += f'</div>'
            html_content += f'</div>'
            html_content += f'<div style="font-size: 12px; margin-top: 5px; color: #bc6f32; font-weight: bold;">Watch Video</div>'
            html_content += f'</a>'
            html_content += f'</div>'
        else:
            # Handle regular images
            html_content += f'<div style="flex-shrink: 0; text-align: center; min-width: 200px;"><img src="{url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Image {start_idx + i + 1}"></div>'
    
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)

def main():
    # Password protection
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown('<h1 class="main-header">Pathways for Care Viewer</h1>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="text-align: center; padding:20px; background: #f8f9fa; border-radius:10px; border:1px solid #dee2e6;">', unsafe_allow_html=True)
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
    # Initialize image cache
    if 'cache_initialized' not in st.session_state:
        st.session_state.cache_initialized = False
    if not st.session_state.cache_initialized:
        with st.spinner("Initializing image cache..."):
            try:
                cache_success = initialize_cache()
                if not cache_success:
                    st.sidebar.warning("⚠️ No image cache found")
                else:
                    st.sidebar.success("✅ Image cache loaded successfully")
            except Exception as e:
                st.sidebar.warning(f"⚠️ Cache loading failed: {str(e)}")
        st.session_state.cache_initialized = True
    # Main header
    st.markdown('<h1 class="main-header">Pathways for Care</h1>', unsafe_allow_html=True)
    # Sidebar controls
    st.sidebar.title("Controls")
    # Export to CSV
    if st.sidebar.button("📤 Export to CSV"):
        df = load_data_from_multiple_sources()
        if df is not None:
            csv_data = df.to_csv(index=False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Pathways_Data_Export_{timestamp}.csv"
            st.download_button(
                label="Download CSV Export",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
    # Load data
    df = load_data_from_multiple_sources()
    if df is None:
        st.error("Failed to load data")
        return
    if len(df) == 0:
        st.warning("No data found")
        return
    # Filters section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #062b49; margin-bottom:1rem;">🔍 Filters</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Animal Type filter
        animal_types = sorted(df['AnimalType'].dropna().unique()) if 'AnimalType' in df.columns else []
        selected_animal_types = st.multiselect("Animal Type", animal_types)
    with col2:
        # Breed filter
        breeds = sorted(df['PrimaryBreed'].dropna().unique()) if 'PrimaryBreed' in df.columns else []
        selected_breeds = st.multiselect("Primary Breed", breeds)
    with col3:
        # Location filter
        locations = sorted(df['Location'].dropna().unique()) if 'Location' in df.columns else []
        selected_locations = st.multiselect("Location", locations)
    with col4:
        # Stage filter
        stages = sorted(df['Stage'].dropna().unique()) if 'Stage' in df.columns else []
        selected_stages = st.multiselect("Stage", stages)
    st.markdown('</div>', unsafe_allow_html=True)
    # Apply filters
    filtered_df = df.copy()
    if selected_animal_types:
        filtered_df = filtered_df[filtered_df['AnimalType'].isin(selected_animal_types)]
    if selected_breeds:
        filtered_df = filtered_df[filtered_df['PrimaryBreed'].isin(selected_breeds)]
    if selected_locations:
        filtered_df = filtered_df[filtered_df['Location'].isin(selected_locations)]
    if selected_stages:
        filtered_df = filtered_df[filtered_df['Stage'].isin(selected_stages)]
    # Display filtered data
    st.markdown(f'<div style="text-align: center; font-weight: bold; color: #657; padding: 1rem;">Showing {len(filtered_df)} of {len(df)} animals</div>', unsafe_allow_html=True)

    # Search functionality with placeholder styling
    st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
    st.markdown('<h4 style="color: #062b49; margin-bottom: 10px;">Search Animals</h4>', unsafe_allow_html=True)
    
    # Create search options
    search_options = []
    for idx, row in filtered_df.iterrows():
        aid = row.get('AID', '')
        name = row.get('AnimalName', '')
        breed = row.get('PrimaryBreed', '')
        search_text = f"{aid} - {name} ({breed})" if name else f"{aid} - {breed}" if breed else str(aid)
        search_options.append((search_text, idx))
    
    # Search dropdown with placeholder styling
    if search_options:
        # Initialize search key counter
        if 'search_key_counter' not in st.session_state:
            st.session_state['search_key_counter'] = 0
        
        # Add a placeholder option at the top
        placeholder_text = "Type to search for animals..."
        all_options = [placeholder_text] + [opt[0] for opt in search_options]
        all_indices = [None] + [opt[1] for opt in search_options]
        
        selected_search = st.selectbox(
            "Search by AID, Name, or Breed:",
            options=all_options,
            index=0,
            key=f"search_dropdown_{st.session_state['search_key_counter']}"
        )
        
        # Only update if a real animal was selected (not placeholder)
        if selected_search != placeholder_text:
            selected_idx = all_indices[all_options.index(selected_search)]
            if selected_idx is not None:
                st.session_state['animal_index'] = selected_idx
                # Increment the key counter to force a reset
                st.session_state['search_key_counter'] += 1
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Animal navigation state
    if 'animal_index' not in st.session_state:
        st.session_state['animal_index'] = 0
    if len(filtered_df) > 0:
        # Navigation controls
        col_nav1, col_nav2, col_nav3 = st.columns([1,2,1])
        with col_nav1:
            if st.button('Previous', key='prev_animal'):
                st.session_state['animal_index'] = max(0, st.session_state['animal_index'] - 1)
        with col_nav3:
            if st.button('Next', key='next_animal'):
                st.session_state['animal_index'] = min(len(filtered_df)-1, st.session_state['animal_index'] + 1)
        # Clamp index
        st.session_state['animal_index'] = min(max(st.session_state['animal_index'], 0), len(filtered_df)-1)
        # Show which animal
        with col_nav2:
            st.markdown(f'<div style="text-align:center;font-size:1.1rem;font-family:Texta,sans-serif;font-weight:700;">Animal {st.session_state["animal_index"]+1} of {len(filtered_df)}</div>', unsafe_allow_html=True)
        # Get the current animal
        animal_data = filtered_df.iloc[st.session_state['animal_index']]
        aid = animal_data['AID'] if 'AID' in animal_data else None

        # Images first
        if 'Image_URLs' in animal_data and pd.notna(animal_data['Image_URLs']) and str(animal_data['Image_URLs']).strip():
            image_urls = str(animal_data['Image_URLs']).split(',')
            image_urls = [url.strip() for url in image_urls if url.strip()]
            if image_urls:
                st.markdown('<div style="background: #062b49; color: white; padding:10px; border-radius: 8px; margin: 20px 0; font-family: \'Texta\', sans-serif; font-weight: 700; font-size: 1.2rem;">Images/Videos</div>', unsafe_allow_html=True)
                display_media(aid, image_urls)

        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

        # Animal Information in columns
        st.markdown('<div style="background: #bc6f32; color: white; padding:10px; border-radius: 8px; margin: 20px 0; font-family: \'Texta\', sans-serif; font-weight: 700; font-size: 1.2rem;">Animal Information</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # AID as clickable link to PetPoint
            if 'AID' in animal_data and pd.notna(animal_data['AID']):
                aid_value = animal_data['AID']
                petpoint_url = f"https://sms.petpoint.com/sms3/enhanced/animal/{aid_value}"
                st.markdown(f"**AID:** [{aid_value}]({petpoint_url})")
            if 'AnimalName' in animal_data and pd.notna(animal_data['AnimalName']):
                st.write(f"**Name:** {animal_data['AnimalName']}")
            if 'AnimalType' in animal_data and pd.notna(animal_data['AnimalType']):
                st.write(f"**Type:** {animal_data['AnimalType']}")

        with col2:
            if 'PrimaryBreed' in animal_data and pd.notna(animal_data['PrimaryBreed']):
                st.write(f"**Breed:** {animal_data['PrimaryBreed']}")
            if 'Age' in animal_data and pd.notna(animal_data['Age']):
                st.write(f"**Age:** {animal_data['Age']}")
            if 'Stage' in animal_data and pd.notna(animal_data['Stage']):
                st.write(f"**Stage:** {animal_data['Stage']}")

        with col3:
            if 'Location' in animal_data and pd.notna(animal_data['Location']):
                st.write(f"**Location:** {animal_data['Location']}")
            if 'SubLocation' in animal_data and pd.notna(animal_data['SubLocation']):
                st.write(f"**Sub-Location:** {animal_data['SubLocation']}")
            if 'Length of Stay' in animal_data and pd.notna(animal_data['Length of Stay']):
                st.write(f"**Length of Stay:** {animal_data['Length of Stay']} days")

        with col4:
            # Add Foster Attempted - check multiple possible column names
            foster_value = animal_data.get('Foster_Attempted', animal_data.get('Foster Attempted', 'No'))
            st.write(f"**Foster Attempted:** {foster_value}")
            # Add Transfer Attempted - check multiple possible column names
            transfer_value = animal_data.get('Transfer_Attempted', animal_data.get('Transfer Attempted', 'No'))
            st.write(f"**Transfer Attempted:** {transfer_value}")
            # Add Communications Team Attempted - check multiple possible column names
            comms_value = animal_data.get('Communications_Team_Attempted', animal_data.get('Communications Team Attempted', 'No'))
            st.write(f"**Communications Team Attempted:** {comms_value}")

        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

        # Welfare notes
        welfare_col = None
        for col in ['Welfare Notes', 'Welfare_Notes', 'welfare_notes']:
            if col in animal_data.index and pd.notna(animal_data[col]) and str(animal_data[col]).strip():
                welfare_col = col
                break
        if welfare_col:
            st.markdown('<div style="background: #512a44; color: white; padding:10px; border-radius: 8px; margin: 20px 0; font-family: \'Texta\', sans-serif; font-weight: 700; font-size: 1.02rem;">Welfare Notes</div>', unsafe_allow_html=True)
            st.text_area("", value=animal_data[welfare_col], height=150)
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

        # Edit section
        st.markdown('<div style="background: #4f5b35; color: white; padding:10px; border-radius: 8px; margin: 20px 0; font-family: \'Texta\', sans-serif; font-weight: 700; font-size: 1.2rem;">Edit Animal Record</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            foster_value = st.selectbox(
                "Foster Attempted:",
                ["No", "Yes"],
                index=["No", "Yes"].index(animal_data.get('Foster_Attempted', "No")),
                key=f"foster_{aid}"
            )
        with col2:
            transfer_value = st.selectbox(
                "Transfer Attempted:",
                ["No", "Yes"],
                index=["No", "Yes"].index(animal_data.get('Transfer_Attempted', "No")),
                key=f"transfer_{aid}"
            )
        with col3:
            communications_value = st.selectbox(
                "Communications Team Attempted:",
                ["No", "Yes"],
                index=["No", "Yes"].index(animal_data.get('Communications_Team_Attempted', "No")),
                key=f"comms_{aid}"
            )
        new_note = st.text_area(
            "Add New Note:",
            placeholder="Enter new welfare note...",
            key=f"note_{aid}"
        )
        if st.button("Save Changes", type="primary"):
            if save_record_to_drive(aid, foster_value, transfer_value, communications_value, new_note):
                st.success("Changes saved successfully!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to save changes")

if __name__ == "__main__":
    main() 