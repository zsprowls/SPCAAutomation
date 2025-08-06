import streamlit as st
import pandas as pd
import os

# Mock the secrets for testing
class MockSecrets:
    def get(self, key, default=""):
        return default

# Mock st.secrets
st.secrets = MockSecrets()

# Test basic functionality
st.title("Foster Dashboard Test")
st.write("Testing basic app functionality...")

# Test data loading
try:
    # Check if data files exist
    data_files = [
        "data/AnimalInventory.csv",
        "data/FosterCurrent.csv", 
        "data/Hold - Foster Stage Date.csv"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            st.success(f"✅ {file} exists")
        else:
            st.error(f"❌ {file} missing")
            
    # Test loading one file
    if os.path.exists("data/AnimalInventory.csv"):
        df = pd.read_csv("data/AnimalInventory.csv")
        st.write(f"✅ Loaded {len(df)} rows from AnimalInventory.csv")
        st.write(f"Columns: {list(df.columns)}")
        
except Exception as e:
    st.error(f"❌ Error loading data: {e}")

st.write("Test complete!") 