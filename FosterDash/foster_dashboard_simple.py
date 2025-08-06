import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="SPCA Foster Dashboard (Simple)",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import os

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #062b49;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #bc6f32;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_simple():
    """Load data with minimal processing"""
    try:
        # Try to load AnimalInventory.csv
        possible_paths = [
            "data/AnimalInventory.csv",
            "FosterDash/data/AnimalInventory.csv",
            "../__Load Files Go Here__/AnimalInventory.csv",
            "AnimalInventory.csv"
        ]
        
        animal_inventory_path = None
        for path in possible_paths:
            if os.path.exists(path):
                animal_inventory_path = path
                break
        
        if animal_inventory_path:
            # Load with minimal processing
            df = pd.read_csv(animal_inventory_path, skiprows=3, nrows=100)  # Only load first 100 rows for testing
            st.success(f"✅ Loaded {len(df)} records from AnimalInventory.csv")
            return df
        else:
            st.error("❌ AnimalInventory.csv not found!")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def main():
    # Header
    st.markdown('<h1 class="main-header">🐾 SPCA Foster Dashboard (Simple)</h1>', unsafe_allow_html=True)
    
    st.info("This is a simplified version for testing. It loads much faster!")
    
    # Load data
    with st.spinner("Loading data (simplified)..."):
        df = load_data_simple()
    
    if df.empty:
        st.error("No data available.")
        return
    
    # Show basic info
    st.subheader("Data Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Sample Size", "100 rows")
    
    # Show column names
    st.subheader("Available Columns")
    st.write(list(df.columns))
    
    # Show first few rows
    st.subheader("Sample Data")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.success("✅ App loaded successfully!")

if __name__ == "__main__":
    main() 