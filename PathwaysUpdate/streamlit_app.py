import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# Import our image cache manager
from image_cache_manager import get_animal_images_cached, initialize_cache, cleanup_cache, get_cache_stats

# Page config
st.set_page_config(
    page_title="Pathways for Care Viewer",
    page_icon="🐾",
    layout="wide"
)

# Load the CSV data
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    df = pd.read_csv(csv_path)
    df = df.fillna('')
    df['Days in System'] = pd.to_numeric(df['Days in System'], errors='coerce').fillna(0)
    return df

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

# Sidebar for navigation
st.sidebar.title("Navigation")
view_mode = st.sidebar.radio("Select View", ["Spreadsheet", "Record Browser"])

if view_mode == "Spreadsheet":
    st.header("Spreadsheet View")
    
    # Display the dataframe
    st.dataframe(
        st.session_state.df,
        use_container_width=True,
        height=600
    )
    
    # Add clickable AID links
    st.markdown("### Quick Links")
    for idx, row in st.session_state.df.iterrows():
        aid = str(row['AID']).strip()
        if aid and aid != 'nan':
            if st.button(f"Open {row['Name']} (AID: {aid})", key=f"aid_{idx}"):
                st.markdown(f"[Open in PetPoint](https://sms.petpoint.com/sms3/enhanced/animal/{aid})")

else:  # Record Browser
    st.header("Record Browser")
    
    # Navigation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Previous"):
            st.session_state.current_index = max(0, st.session_state.current_index - 1)
    
    with col2:
        st.write(f"Record {st.session_state.current_index + 1} of {len(st.session_state.df)}")
    
    with col3:
        if st.button("Next →"):
            st.session_state.current_index = min(len(st.session_state.df) - 1, st.session_state.current_index + 1)
    
    # Get current record
    record = st.session_state.df.iloc[st.session_state.current_index]
    
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
st.markdown("*Powered by Streamlit*") 