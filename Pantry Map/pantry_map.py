import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime, timedelta
import plotly.io as pio

# Page config
st.set_page_config(
    page_title="Pet Pantry Client Map",
    page_icon="🐾",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stSlider {
        width: 100% !important;
    }
    .year-display {
        position: absolute;
        bottom: 220px; /* Move up into the map area */
        left: 100px;
        font-size: 48px;
        font-weight: bold;
        color: #000000;
        text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
        z-index: 1000;
        pointer-events: none;
    }
    /* Hide all slider labels, ticks, and marks */
    .stSlider [data-testid="stTickBar"],
    .stSlider [data-testid="stMarkdownContainer"],
    .stSlider .rc-slider-mark,
    .stSlider .rc-slider-step,
    .stSlider .rc-slider-dot,
    .stSlider .rc-slider-mark-text {
        display: none !important;
    }
    /* Hide the value label above the slider thumb (all placements) */
    .stSlider .rc-slider-tooltip,
    .stSlider .rc-slider-tooltip-content,
    .stSlider .rc-slider-tooltip-placement-top {
        display: none !important;
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
st.title("Pet Pantry Client Map")

# Load data
data = load_data()
if not data:
    st.error("No data found. Please ensure processed_pantry_data.json exists.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert date strings to datetime
df['date'] = pd.to_datetime(df['date'])

# Add PetPoint link column
base_url = "https://sms.petpoint.com/sms3/enhanced/person/"
def format_petpoint_link(pid):
    # Remove non-digits, then strip leading zeros
    digits = ''.join(filter(str.isdigit, str(pid)))
    digits = digits.lstrip('0')
    return base_url + digits

df['petpoint_link'] = df['person_id'].apply(format_petpoint_link)

# Download button (move above map and slider)
if st.button("Download Map as PNG"):
    # Create a temporary file
    img_bytes = pio.to_image(fig, format="png")
    st.download_button(
        label="Click to Download",
        data=img_bytes,
        file_name=f"pantry_map_{selected_date.strftime('%Y%m%d')}.png",
        mime="image/png"
    )

# Create controls in a single row
col1, col2 = st.columns([3, 1])

with col1:
    # Create date slider
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    # Use date objects directly in the slider
    if 'selected_date' not in st.session_state:
        st.session_state['selected_date'] = max_date
    selected_date = st.slider(
        "Select Date",
        min_value=min_date,
        max_value=max_date,
        value=st.session_state['selected_date'],
        step=timedelta(days=1),
        format="YYYY-MM-DD",
        label_visibility="collapsed"
    )
    st.session_state['selected_date'] = selected_date

with col2:
    # Add visualization toggle
    show_heatmap = st.toggle("Show Heatmap", value=True)

# Filter data for selected date
filtered_df = df[df['date'].dt.date <= selected_date]

# Create map with both scatter and heatmap
fig = px.scatter_mapbox(
    filtered_df,
    lat='lat',
    lon='lng',
    hover_name='name',
    hover_data=None,  # We'll use customdata for custom hovertemplate
    zoom=7,
    center={"lat": 42.8864, "lon": -78.8784},
    mapbox_style="carto-positron",
    title=f"Pet Pantry Clients as of {selected_date.strftime('%B %d, %Y')}",
    size=[10] * len(filtered_df),
    size_max=15,
    custom_data=['date', 'address_type', 'person_id', 'petpoint_link']
)

# Add heatmap layer if toggle is on
if show_heatmap:
    heatmap = px.density_mapbox(
        filtered_df,
        lat='lat',
        lon='lng',
        zoom=7,
        mapbox_style="carto-positron",
        radius=20,
        opacity=0.6,
    )
    # Remove color scale from the heatmap trace
    for trace in heatmap.data:
        trace.showscale = False
        if hasattr(trace, 'colorbar'):
            trace.colorbar = None
    fig.add_trace(heatmap.data[0])

# Remove colorbar from layout if present
if 'coloraxis' in fig.layout:
    fig.layout.coloraxis.showscale = False
    fig.layout.coloraxis.colorbar = None

# Update layout
fig.update_layout(
    mapbox_bounds={
        "west": -80.0,
        "east": -77.8,
        "south": 42.0,
        "north": 43.6
    },
    margin={"r":0,"t":30,"l":0,"b":0},
    height=800,
    showlegend=False,
    hovermode='closest',
    mapbox=dict(
        zoom=7,
        center=dict(lat=42.8864, lon=-78.8784),
        style="carto-positron",
        layers=[{
            "sourcetype": "geojson",
            "source": "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            "below": "traces",
            "type": "fill",
            "color": "rgba(200,200,200,0.2)",
            "opacity": 0.5,
            "line": {
                "width": 1
            }
        }]
    )
)

# Update hover template to include clickable PetPoint link
fig.update_traces(
    hovertemplate="""
    <b>%{hovertext}</b><br>
    Date: %{customdata[0]|%Y-%m-%d}<br>
    Address Type: %{customdata[1]}<br>
    Client ID: %{customdata[2]}<br>
    <a href='%{customdata[3]}' target='_blank'>PetPoint Account</a><extra></extra>
    """,
    hoverlabel=dict(namelength=0)
)

# Display map
st.plotly_chart(fig, use_container_width=True)

# Add year display (moved up into the map area)
st.markdown(f'<div class="year-display">{selected_date.year}</div>', unsafe_allow_html=True)

# Statistics
st.sidebar.header("Statistics")
st.sidebar.metric("Total Clients", len(filtered_df))
st.sidebar.metric("Unique Locations", filtered_df['name'].nunique())

# Data table
if st.sidebar.checkbox("Show Data Table"):
    st.dataframe(filtered_df[['name', 'date', 'address_type', 'person_id']].sort_values('date', ascending=False)) 
    
