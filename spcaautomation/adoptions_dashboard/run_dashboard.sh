#!/bin/bash

# SPCA Adoptions Dashboard Launcher
echo "🐾 Starting SPCA Adoptions Dashboard..."

# Check if we're in the right directory
if [ ! -f "dashboard.py" ]; then
    echo "❌ Error: dashboard.py not found. Please run this script from the adoptions_dashboard directory."
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
python3 -c "import streamlit, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing required dependencies..."
    pip install -r requirements.txt
fi

# Check if data files exist
if [ ! -d "../../__Load Files Go Here__" ]; then
    echo "❌ Warning: Data directory '__Load Files Go Here__' not found."
    echo "   Please ensure your data files are in the correct location."
fi

echo "🚀 Launching dashboard..."
echo "📊 Dashboard will open in your browser at http://localhost:8501"
echo "💡 Press Ctrl+C to stop the dashboard"

# Launch Streamlit
streamlit run dashboard.py