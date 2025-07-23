#!/usr/bin/env python3
"""
Setup script for Rodent Intake Case Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def verify_installation():
    """Verify that all packages are installed correctly"""
    print("🔍 Verifying installation...")
    required_packages = ['streamlit', 'pandas', 'plotly', 'numpy']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            return False
    
    return True

def check_data_files():
    """Check if data files are accessible"""
    print("📁 Checking data files...")
    files_to_check = [
        ('RodentIntake.csv', 'Primary rodent intake data'),
        ('../__Load Files Go Here__/FosterCurrent.csv', 'Foster current data'),
        ('../__Load Files Go Here__/AnimalInventory.csv', 'Animal inventory data'),
        ('../__Load Files Go Here__/AnimalOutcome.csv', 'Animal outcome data')
    ]
    
    all_files_ok = True
    for file_path, description in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {description} - Found")
        else:
            print(f"⚠️  {description} - Not found")
            all_files_ok = False
    
    return all_files_ok

def main():
    """Main setup function"""
    print("🐹 Rodent Intake Case Dashboard Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during package installation")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Setup failed during verification")
        sys.exit(1)
    
    # Check data files
    data_files_ok = check_data_files()
    
    print("\n" + "=" * 50)
    if data_files_ok:
        print("🎉 Setup completed successfully!")
        print("\n🚀 To start the dashboard, run:")
        print("   python3 run_dashboard.py")
        print("   or")
        print("   streamlit run rodent_dashboard.py")
    else:
        print("⚠️  Setup completed with warnings")
        print("   Some data files are missing, but the dashboard will still run")
        print("   It will show warnings for missing files")
        print("\n🚀 To start the dashboard, run:")
        print("   python3 run_dashboard.py")
    
    print("\n📱 The dashboard will be available at: http://localhost:8501")

if __name__ == "__main__":
    main() 