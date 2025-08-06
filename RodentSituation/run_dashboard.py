#!/usr/bin/env python3
"""
Quick launcher for the Rodent Intake Case Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'pandas', 'plotly', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_data_files():
    """Check if required data files exist"""
    # Check primary location first (__Load Files Go Here__ folder)
    primary_files = [
        '../__Load Files Go Here__/RodentIntake.csv',
        '../__Load Files Go Here__/FosterCurrent.csv',
        '../__Load Files Go Here__/AnimalInventory.csv',
        '../__Load Files Go Here__/AnimalOutcome.csv'
    ]
    
    # Also check current directory for deployment
    local_files = [
        'RodentIntake.csv',
        'FosterCurrent.csv',
        'AnimalInventory.csv',
        'AnimalOutcome.csv'
    ]
    
    missing_files = []
    found_in_primary = True
    
    # Check primary location
    for file_path in primary_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            found_in_primary = False
    
    if found_in_primary:
        print("✅ Found all files in __Load Files Go Here__ folder")
        return True
    
    # Check local directory
    missing_local = []
    for file_path in local_files:
        if not Path(file_path).exists():
            missing_local.append(file_path)
    
    if not missing_local:
        print("✅ Found all files in local directory")
        return True
    
    # If we get here, files are missing from both locations
    print("⚠️  Missing data files:")
    for file_path in missing_files:
        print(f"   - {file_path}")
    print("\n📁 Please ensure all CSV files are in the __Load Files Go Here__ folder or local directory.")
    return False

def main():
    """Main launcher function"""
    print("🐹 Rodent Intake Case Dashboard Launcher")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ Dependencies OK")
    
    # Check data files
    print("📁 Checking data files...")
    if not check_data_files():
        print("\n⚠️  Some data files are missing, but the dashboard will still run.")
        print("   It will show warnings for missing files.")
    
    print("✅ Data files OK")
    
    # Launch dashboard
    print("\n🚀 Starting dashboard...")
    print("📱 The dashboard will open in your web browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "rodent_dashboard.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 