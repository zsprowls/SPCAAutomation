#!/usr/bin/env python3
"""
Quick runner script for the Adoptions Counselor Dashboard
"""

import subprocess
import sys
import os

def main():
    print("🐾 Starting Adoptions Counselor Dashboard...")
    print("=" * 50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Check if data files exist
    data_dir = "../__Load Files Go Here__"
    required_files = ["AnimalInventory.csv", "AnimalIntake.csv", "AnimalOutcome.csv"]
    
    print("\n📁 Checking for data files...")
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file} not found")
    
    print("\n🚀 Starting dashboard...")
    print("The dashboard will open in your browser automatically.")
    print("Press Ctrl+C to stop the dashboard.")
    print("=" * 50)
    
    # Run the dashboard
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main() 