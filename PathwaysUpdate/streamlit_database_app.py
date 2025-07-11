import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import re
from image_cache_manager import get_animal_images_cached, initialize_cache, cleanup_cache, get_cache_stats

# Page configuration
st.set_page_config(
    page_title="Pathways for Care Viewer (Database)",
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
    
    /* Force light mode on textarea */
    .stTextarea > div > div > textarea {
        background-color: #ffffff !important;
        color: #495057 !important;
        border: 1px solid #dee2e6 !important;
    }
    
    /* Force light mode on multiselect */
    .stMultiSelect > div > div > div {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    /* Force light mode on dataframe */
    .stDataFrame {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    .stDataFrame > div {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    .stDataFrame table {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    .stDataFrame th {
        background-color: #f8f9fa !important;
        color: #495057 !important;
        border-color: #dee2e6 !important;
    }
    
    .stDataFrame td {
        background-color: #ffffff !important;
        color: #495057 !important;
        border-color: #dee2e6 !important;
    }
    
    .stDataFrame tr:nth-child(even) td {
        background-color: #f8f9fa !important;
    }
    
    /* Remove any dark backgrounds */
    .stMarkdown {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    /* Override Streamlit's dark theme for form elements */
    [data-testid="stSelectbox"] {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    [data-testid="stTextInput"] {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    [data-testid="stTextarea"] {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    [data-testid="stMultiSelect"] {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    /* Force light mode on all input elements */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #495057 !important;
        border: 1px solid #dee2e6 !important;
    }
    
    /* Force light mode on dropdown options */
    .stSelectbox [role="listbox"] {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    .stSelectbox [role="option"] {
        background-color: #ffffff !important;
        color: #495057 !important;
    }
    
    .stSelectbox [role="option"]:hover {
        background-color: #f8f9fa !important;
        color: #495057 !important;
    }
    
    /* Hide Streamlit default styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Override any dark theme elements */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    .stSidebar .stMarkdown {
        background-color: #f8f9fa !important;
        color: #495057 !important;
    }
</style>
""", unsafe_allow_html=True)

# Database functions
def get_db_connection():
    """Get database connection"""
    db_path = 'pathways_database.db'
    if not os.path.exists(db_path):
        st.error("Database not found! Please run the CSV to SQLite converter first.")
        return None
    return sqlite3.connect(db_path)

@st.cache_data
def load_data_from_db():
    """Load data from SQLite database"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    # Load main pathways data
    df = pd.read_sql_query("SELECT * FROM pathways_data", conn)
    
    # Load inventory data for location updates
    try:
        inventory_df = pd.read_sql_query("SELECT * FROM animal_inventory", conn)
        
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
        pass  # Silently ignore inventory loading errors
    
    conn.close()
    
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

def save_record_to_db(aid, foster_value, transfer_value, communications_value, new_note):
    """Save a record to the database"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        # Get current welfare notes
        cursor = conn.cursor()
        cursor.execute("SELECT \"Welfare Notes\" FROM pathways_data WHERE AID = ?", (aid,))
        result = cursor.fetchone()
        current_notes = result[0] if result and result[0] else ""
        
        # Add new note if provided
        if new_note and new_note.strip():
            if current_notes:
                new_welfare_notes = f"{current_notes}\n\n{new_note.strip()}"
            else:
                new_welfare_notes = new_note.strip()
        else:
            new_welfare_notes = current_notes
        
        # Update the record
        cursor.execute("""
            UPDATE pathways_data 
            SET "Foster Attempted" = ?, "Transfer Attempted" = ?, "Communications Team Attempted" = ?, 
                "Welfare Notes" = ?
            WHERE AID = ?
        """, (foster_value, transfer_value, communications_value, new_welfare_notes, aid))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Database error: {e}")
        conn.close()
        return False

def export_db_to_csv():
    """Export database to CSV"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    df = pd.read_sql_query("SELECT * FROM pathways_data", conn)
    conn.close()
    
    csv_path = f"Pathways_Data_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_path, index=False)
    return csv_path

def display_media(animal_id, image_urls):
    """Display images and videos for an animal in a compact single line"""
    if not image_urls:
        st.markdown('<div style="text-align: center; padding: 20px; color: #6c757d; font-style: italic; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">No images or videos available</div>', unsafe_allow_html=True)
        return
    
    # Create HTML for compact image display with horizontal scrolling - centered
    html_content = '<div style="display: flex; flex-wrap: nowrap; gap: 8px; align-items: center; justify-content: center; overflow-x: auto; padding: 8px; scrollbar-width: thin; scrollbar-color: #007bff #f8f9fa;">'
    
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
                html_content += f'<div style="flex-shrink: 0; text-align: center;"><img src="{url}" style="max-width: 200px; max-height: 200px; margin: 5px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Video {i+1}"><div style="font-size: 12px; margin-top: 2px; font-weight: bold;"><a href="{watch_url}" target="_blank" style="color: #007bff; text-decoration: underline;">▶ Watch Video</a></div></div>'
            else:
                html_content += f'<div style="flex-shrink: 0; text-align: center;"><img src="{url}" style="max-width: 200px; max-height: 200px; margin: 5px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Media {i+1}"><div style="font-size: 10px; margin-top: 2px;">Media {i+1}</div></div>'
        else:
            html_content += f'<div style="flex-shrink: 0; text-align: center;"><img src="{url}" style="max-width: 200px; max-height: 200px; margin: 5px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Image {i+1}"><div style="font-size: 10px; margin-top: 2px;">Image {i+1}</div></div>'
    
    html_content += '</div>'
    
    # Display the compact image layout
    st.markdown(html_content, unsafe_allow_html=True)

def main():
    # Initialize image cache
    if 'cache_initialized' not in st.session_state:
        st.session_state.cache_initialized = False
    
    if not st.session_state.cache_initialized:
        with st.spinner("Initializing image cache..."):
            cache_success = initialize_cache()
            if not cache_success:
                st.sidebar.warning("Cache initialization failed, images may not be available")
        st.session_state.cache_initialized = True
    
    # Main header
    st.markdown('<h1 class="main-header">Pathways for Care Viewer</h1>', unsafe_allow_html=True)
    
    # Check database exists
    db_path = 'pathways_database.db'
    if not os.path.exists(db_path):
        st.error("❌ Database not found! Please run the CSV to SQLite converter first.")
        return
    
    # Sidebar controls - simplified
    st.sidebar.title("Controls")
    
    # Export to CSV
    if st.sidebar.button("📤 Export to CSV"):
        csv_path = export_db_to_csv()
        if csv_path:
            st.success(f"✅ Data exported to: {csv_path}")
    
    # View mode selection
    view_mode = st.sidebar.selectbox(
        "View Mode",
        ["Animal Details", "Spreadsheet View"],
        help="Choose how to view the data"
    )
    
    # Load data
    df = load_data_from_db()
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
        
        # Navigation controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Previous"):
                if 'current_index' not in st.session_state:
                    st.session_state.current_index = 0
                else:
                    st.session_state.current_index = max(0, st.session_state.current_index - 1)
        
        with col2:
            if 'current_index' not in st.session_state:
                st.session_state.current_index = 0
            st.markdown(f'<div class="page-indicator">Animal {st.session_state.current_index + 1} of {len(df)}</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button("Next →"):
                if 'current_index' not in st.session_state:
                    st.session_state.current_index = 0
                else:
                    st.session_state.current_index = min(len(df) - 1, st.session_state.current_index + 1)
        
        # Handle search selection
        if selected_animal != "Select an animal...":
            aid = selected_animal.split(" - ")[0]
            for idx, row in df.iterrows():
                if str(row['AID']).strip() == aid:
                    st.session_state.current_index = idx
                    break
        
        # Initialize current index
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0
        
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
            st.markdown('<div class="card-body">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Name:** {record['Name'] or 'N/A'}")
                st.markdown(f"**AID:** [{record['AID']}](https://sms.petpoint.com/sms3/enhanced/animal/{record['AID']})")
                st.markdown(f"**Species:** {record['Species'] or 'N/A'}")
            
            with col2:
                st.markdown(f"**Location:** {record['Location '] or 'N/A'}")
                st.markdown(f"**Intake Date:** {record['Intake Date'] or 'N/A'}")
                days_value = record['Days in System'] if pd.notna(record['Days in System']) else 'N/A'
                if isinstance(days_value, (int, float)) and days_value != 'N/A':
                    st.markdown(f"**Days in System:** {days_value:.0f}")
                else:
                    st.markdown(f"**Days in System:** {days_value}")
            
            with col3:
                st.markdown(f"**Foster Attempted:** {record['Foster Attempted'] or 'N/A'}")
                st.markdown(f"**Transfer Attempted:** {record['Transfer Attempted'] or 'N/A'}")
                st.markdown(f"**Communications Team:** {record['Communications Team Attempted'] or 'N/A'}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Welfare Notes Card
            st.markdown('<div class="card-header card-header-warning">Welfare Notes</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-body">', unsafe_allow_html=True)
            
            if record['Welfare Notes']:
                st.markdown(f'<div class="welfare-notes">{record["Welfare Notes"]}</div>', unsafe_allow_html=True)
            else:
                st.info("No welfare notes available")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Edit Information Card
            st.markdown('<div class="card-header card-header-success">Edit Information</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-body">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<p class="form-label">Foster Attempted:</p>', unsafe_allow_html=True)
                foster_options = ["", "Yes", "No", "N/A"]
                foster_value = st.selectbox(
                    "Foster Attempted:",
                    foster_options,
                    index=foster_options.index(record['Foster Attempted']) if record['Foster Attempted'] in foster_options else 0,
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown('<p class="form-label">Transfer Attempted:</p>', unsafe_allow_html=True)
                transfer_options = ["", "Yes", "No", "N/A"]
                transfer_value = st.selectbox(
                    "Transfer Attempted:",
                    transfer_options,
                    index=transfer_options.index(record['Transfer Attempted']) if record['Transfer Attempted'] in transfer_options else 0,
                    label_visibility="collapsed"
                )
            
            with col3:
                st.markdown('<p class="form-label">Communications Team Attempted:</p>', unsafe_allow_html=True)
                communications_options = ["", "Yes", "No", "N/A"]
                communications_value = st.selectbox(
                    "Communications Team Attempted:",
                    communications_options,
                    index=communications_options.index(record['Communications Team Attempted']) if record['Communications Team Attempted'] in communications_options else 0,
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
                    if save_record_to_db(record['AID'], foster_value, transfer_value, communications_value, new_note):
                        st.success("✅ Changes saved to database!")
                        st.cache_data.clear()  # Clear cache to reload data
                        st.rerun()
                    else:
                        st.error("❌ Failed to save changes")
            
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Spreadsheet View
        st.header("Spreadsheet View")

        # Prepare styled DataFrame
        def make_clickable(val):
            aid = str(val)
            return f'<a href="https://sms.petpoint.com/sms3/enhanced/animal/{aid}" target="_blank" style="color:#007bff;text-decoration:underline;">{aid}</a>'

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
            .set_properties(subset=['Welfare Notes'], **{'text-align': 'left', 'min-width': '300px', 'max-width': '400px'}) \
            .set_properties(subset=['AID'], **{'min-width': '100px', 'max-width': '120px'}) \
            .apply(lambda x: ['background-color: #f8f9fa' if i%2 else '' for i in range(len(x))], axis=0) \
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#343a40'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center'), ('vertical-align', 'middle')]},
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