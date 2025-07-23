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
    required_files = [
        'RodentIntake.csv',
        '../__Load Files Go Here__/FosterCurrent.csv',
        '../__Load Files Go Here__/AnimalInventory.csv',
        '../__Load Files Go Here__/AnimalOutcome.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Missing data files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n📁 Please ensure all CSV files are in the correct locations.")
        return False
    
    return True

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