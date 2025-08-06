import streamlit as st
import pandas as pd
import os
import sys

st.set_page_config(
    page_title="Foster Dashboard Debug",
    page_icon="🐾",
    layout="wide"
)

st.title("🔧 Foster Dashboard Debug Tool")
st.write("This tool will help diagnose deployment issues.")

# Check 1: Basic imports
st.header("1. Basic Imports")
try:
    import streamlit as st
    st.success("✅ Streamlit imported successfully")
except Exception as e:
    st.error(f"❌ Streamlit import failed: {e}")

try:
    import pandas as pd
    st.success("✅ Pandas imported successfully")
except Exception as e:
    st.error(f"❌ Pandas import failed: {e}")

try:
    from supabase_manager import supabase_manager
    st.success("✅ Supabase manager imported successfully")
except Exception as e:
    st.error(f"❌ Supabase manager import failed: {e}")

# Check 2: File structure
st.header("2. File Structure")
data_files = [
    "data/AnimalInventory.csv",
    "data/FosterCurrent.csv",
    "data/Hold - Foster Stage Date.csv",
    "data/AnimalIntake.csv",
    "data/AnimalOutcome.csv",
    "data/StageReview.csv",
    "data/Pathways for Care.csv",
    "data/Looking for Foster Care 2025.xlsx"
]

for file in data_files:
    if os.path.exists(file):
        st.success(f"✅ {file}")
    else:
        st.error(f"❌ {file}")

# Check 3: Data loading
st.header("3. Data Loading Test")
try:
    if os.path.exists("data/AnimalInventory.csv"):
        df = pd.read_csv("data/AnimalInventory.csv")
        st.success(f"✅ AnimalInventory.csv loaded: {len(df)} rows, {len(df.columns)} columns")
        st.write("Sample columns:", list(df.columns)[:5])
    else:
        st.error("❌ AnimalInventory.csv not found")
except Exception as e:
    st.error(f"❌ Error loading AnimalInventory.csv: {e}")

# Check 4: Secrets
st.header("4. Streamlit Secrets")
try:
    if hasattr(st, 'secrets'):
        st.success("✅ st.secrets is available")
        keys = list(st.secrets.keys())
        st.write(f"Available keys: {keys}")
        
        supabase_url = st.secrets.get("SUPABASE_URL", "")
        supabase_key = st.secrets.get("SUPABASE_KEY", "")
        
        if supabase_url and supabase_key:
            st.success("✅ Supabase secrets configured")
        else:
            st.warning("⚠️ Supabase secrets not configured")
            st.info("Add SUPABASE_URL and SUPABASE_KEY to your Streamlit secrets")
    else:
        st.error("❌ st.secrets not available")
except Exception as e:
    st.error(f"❌ Error checking secrets: {e}")

# Check 5: Python version
st.header("5. Environment")
st.write(f"Python version: {sys.version}")
st.write(f"Working directory: {os.getcwd()}")

# Check 6: Try to import main app
st.header("6. Main App Import")
try:
    import foster_dashboard
    st.success("✅ Main app imports successfully")
except Exception as e:
    st.error(f"❌ Main app import failed: {e}")

st.write("---")
st.write("If all checks pass, the app should work. If you see errors, fix them before deploying.") 