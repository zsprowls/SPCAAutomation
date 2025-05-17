import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
import os
import plotly.io as pio

# Page config
st.set_page_config(
    page_title="Vaccine Distribution Map",
    page_icon="💉",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stSlider {
        width: 200px !important;
    }
    .year-display {
        position: fixed;
        bottom: 20px;
        left: 20px;
        font-size: 48px;
        font-weight: bold;
        color: #1E88E5;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password.
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # Do not continue if check_password is False.

# Load data
@st.cache_data
def load_data():
    if os.path.exists('processed_pantry_data.json'):
        with open('processed_pantry_data.json', 'r') as f:
            return json.load(f)
    return []

# Main app
st.title("Vaccine Distribution Map")

# Load data
data = load_data()
if not data:
    st.error("No data found. Please ensure processed_pantry_data.json exists.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert date strings to datetime
df['date'] = pd.to_datetime(df['date'])

# Create three columns for the top controls
col1, col2, col3 = st.columns([1, 2, 1])

# Date range slider in the first column
with col1:
    st.markdown("### Date")
    min_date = df['date'].min()
    max_date = df['date'].max()
    selected_date = st.date_input(
        "Select Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

# Filter data for selected date
filtered_df = df[df['date'].dt.date <= selected_date]

# Create map
fig = px.scatter_mapbox(
    filtered_df,
    lat='lat',
    lon='lng',
    hover_name='name',
    hover_data={
        'date': True,
        'address_type': True,
        'lat': False,
        'lng': False
    },
    zoom=10,
    center={"lat": 42.8864, "lon": -78.8784},  # Centered on Buffalo
    mapbox_style="carto-positron",
    title=f"Vaccine Distribution as of {selected_date.strftime('%B %d, %Y')}"
)

# Update layout
fig.update_layout(
    mapbox_bounds={
        "west": -79.2,
        "east": -78.4,
        "south": 42.4,
        "north": 43.2
    },
    margin={"r":0,"t":30,"l":0,"b":0},
    height=800
)

# Display map
st.plotly_chart(fig, use_container_width=True)

# Add year display
st.markdown(f'<div class="year-display">{selected_date.year}</div>', unsafe_allow_html=True)

# Download button
if st.button("Download Map as PNG"):
    # Create a temporary file
    img_bytes = pio.to_image(fig, format="png")
    st.download_button(
        label="Click to Download",
        data=img_bytes,
        file_name=f"vaccine_map_{selected_date.strftime('%Y%m%d')}.png",
        mime="image/png"
    )

# Statistics
st.sidebar.header("Statistics")
st.sidebar.metric("Total Vaccinations", len(filtered_df))
st.sidebar.metric("Unique Locations", filtered_df['name'].nunique())

# Data table
if st.sidebar.checkbox("Show Data Table"):
    st.dataframe(filtered_df[['name', 'date', 'address_type']].sort_values('date', ascending=False)) 