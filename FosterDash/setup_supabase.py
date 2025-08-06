#!/usr/bin/env python3
"""
Supabase Setup Helper for Foster Dashboard
"""

import os
import streamlit as st
import subprocess
import sys

def create_streamlit_config():
    """Create .streamlit directory and config files"""
    streamlit_dir = ".streamlit"
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
        print(f"✅ Created {streamlit_dir} directory")
    
    # Create config.toml
    config_content = """[server]
port = 8501
address = "localhost"

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#062b49"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
    
    config_path = os.path.join(streamlit_dir, "config.toml")
    with open(config_path, "w") as f:
        f.write(config_content)
    print(f"✅ Created {config_path}")

def create_secrets_template():
    """Create secrets.toml template"""
    secrets_content = """# Supabase Configuration
# Replace these with your actual Supabase credentials
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"

# Instructions:
# 1. Go to https://supabase.com and create a new project
# 2. Go to Settings > API in your Supabase dashboard
# 3. Copy the Project URL and anon public key
# 4. Replace the values above with your actual credentials
"""
    
    secrets_path = ".streamlit/secrets.toml"
    with open(secrets_path, "w") as f:
        f.write(secrets_content)
    print(f"✅ Created {secrets_path}")
    print("📝 Please edit this file with your actual Supabase credentials")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = ["streamlit", "pandas", "numpy", "supabase"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def check_data_files():
    """Check if required data files exist"""
    data_dir = "../__Load Files Go Here__"
    required_files = ["AnimalInventory.csv", "FosterCurrent.csv"]
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file} exists")
        else:
            missing_files.append(file)
            print(f"❌ {file} is missing")
    
    if missing_files:
        print(f"\n📁 Please ensure these files are in {data_dir}:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    return True

def print_supabase_setup_instructions():
    """Print Supabase setup instructions"""
    print("\n" + "="*60)
    print("🚀 SUPABASE SETUP INSTRUCTIONS")
    print("="*60)
    
    print("""
1. Go to https://supabase.com and sign up/login

2. Create a new project:
   - Click "New Project"
   - Name: spca-foster-dashboard
   - Choose your region
   - Set a strong database password
   - Click "Create new project"

3. Wait for project to be ready (green checkmark)

4. Go to SQL Editor and run this SQL:

CREATE TABLE foster_animals (
    id BIGSERIAL PRIMARY KEY,
    AnimalNumber TEXT UNIQUE NOT NULL,
    FosterNotes TEXT DEFAULT '',
    OnMeds BOOLEAN DEFAULT FALSE,
    FosterPleaDates JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_foster_animals_animal_number ON foster_animals(AnimalNumber);
CREATE INDEX idx_foster_animals_updated_at ON foster_animals(updated_at);
ALTER TABLE foster_animals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations" ON foster_animals FOR ALL USING (true);

5. Get your API credentials:
   - Go to Settings > API
   - Copy the Project URL
   - Copy the anon public key

6. Update .streamlit/secrets.toml with your credentials

7. Test the integration:
   streamlit run test_supabase_integration.py

8. Run the dashboard:
   streamlit run foster_dashboard.py
""")

def main():
    print("🔧 Foster Dashboard Setup Helper")
    print("="*40)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()
    
    # Check data files
    print("\n📁 Checking data files...")
    data_ok = check_data_files()
    
    # Create Streamlit config
    print("\n⚙️ Setting up Streamlit configuration...")
    create_streamlit_config()
    create_secrets_template()
    
    # Print instructions
    print_supabase_setup_instructions()
    
    # Summary
    print("\n" + "="*40)
    print("📋 SETUP SUMMARY")
    print("="*40)
    
    if deps_ok and data_ok:
        print("✅ All checks passed!")
        print("🎉 You're ready to set up Supabase and run the dashboard")
    else:
        print("⚠️ Some issues found. Please address them before proceeding.")
    
    print("\n🚀 Next steps:")
    print("1. Follow the Supabase setup instructions above")
    print("2. Update .streamlit/secrets.toml with your credentials")
    print("3. Run: streamlit run test_supabase_integration.py")
    print("4. Run: streamlit run foster_dashboard.py")

if __name__ == "__main__":
    main() 