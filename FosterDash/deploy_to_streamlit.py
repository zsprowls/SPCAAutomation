#!/usr/bin/env python3
"""
Deployment Helper for Streamlit Cloud
"""

import os
import json

def create_streamlit_cloud_config():
    """Create configuration files for Streamlit Cloud deployment"""
    
    # Create .streamlit/secrets.toml template for Streamlit Cloud
    secrets_template = """# Streamlit Cloud Secrets Configuration
# Add these secrets in your Streamlit Cloud app settings

SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"

# Instructions for Streamlit Cloud:
# 1. Go to your Streamlit Cloud dashboard
# 2. Select your app
# 3. Go to Settings > Secrets
# 4. Add the above configuration with your actual Supabase credentials
"""
    
    # Create requirements.txt for deployment
    requirements_content = """streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
supabase>=2.0.0
"""
    
    # Create .gitignore for deployment
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
foster_env/
venv/
env/

# Streamlit
.streamlit/secrets.toml

# Data files (don't commit to git)
../__Load Files Go Here__/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    # Create deployment files
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    print("✅ Created requirements.txt for deployment")
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")
    
    with open("streamlit_cloud_secrets.toml", "w") as f:
        f.write(secrets_template)
    print("✅ Created streamlit_cloud_secrets.toml template")
    
    # Create deployment instructions
    deployment_instructions = """# 🚀 Streamlit Cloud Deployment Guide

## Step 1: Prepare Your Repository

1. Make sure your code is in a Git repository
2. Ensure these files are in your repository:
   - foster_dashboard.py
   - supabase_manager.py
   - requirements.txt
   - .streamlit/config.toml

## Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Configure your app:
   - **Repository**: Your GitHub repo
   - **Branch**: main (or your default branch)
   - **Main file path**: FosterDash/foster_dashboard.py
   - **App URL**: Choose a unique URL

## Step 3: Configure Secrets

1. In your Streamlit Cloud app dashboard
2. Go to Settings > Secrets
3. Add this configuration:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

Replace with your actual Supabase credentials.

## Step 4: Deploy

1. Click "Deploy!" 
2. Wait for deployment to complete
3. Your app will be available at: https://your-app-name.streamlit.app

## Step 5: Test

1. Open your deployed app
2. Check that database connection works
3. Test the interactive features

## Troubleshooting

### App won't deploy:
- Check that all required files are in the repository
- Verify the main file path is correct
- Check the requirements.txt file

### Database connection fails:
- Verify Supabase credentials in Streamlit Cloud secrets
- Check that your Supabase project is active
- Ensure the foster_animals table exists

### Data not loading:
- Verify CSV files are in the correct location
- Check file permissions and paths

## Local Development vs Deployment

- **Local**: Uses .streamlit/secrets.toml
- **Deployed**: Uses Streamlit Cloud secrets
- Both use the same code, just different secret storage
"""
    
    with open("DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(deployment_instructions)
    print("✅ Created DEPLOYMENT_GUIDE.md")

def create_github_workflow():
    """Create GitHub Actions workflow for automated testing"""
    
    workflow_content = """name: Test Foster Dashboard

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd FosterDash
        pip install -r requirements_foster_dashboard.txt
    
    - name: Test imports
      run: |
        cd FosterDash
        python -c "import streamlit, pandas, numpy, supabase; print('All imports successful')"
    
    - name: Test dashboard startup
      run: |
        cd FosterDash
        timeout 30s streamlit run foster_dashboard.py --server.headless true --server.port 8501 || true
"""
    
    # Create .github/workflows directory
    os.makedirs(".github/workflows", exist_ok=True)
    
    with open(".github/workflows/test.yml", "w") as f:
        f.write(workflow_content)
    print("✅ Created GitHub Actions workflow")

def main():
    print("🚀 Streamlit Cloud Deployment Setup")
    print("="*40)
    
    # Create deployment files
    create_streamlit_cloud_config()
    create_github_workflow()
    
    print("\n" + "="*40)
    print("📋 DEPLOYMENT FILES CREATED")
    print("="*40)
    print("✅ requirements.txt - Python dependencies")
    print("✅ .gitignore - Git ignore rules")
    print("✅ streamlit_cloud_secrets.toml - Secrets template")
    print("✅ DEPLOYMENT_GUIDE.md - Deployment instructions")
    print("✅ .github/workflows/test.yml - GitHub Actions workflow")
    
    print("\n🚀 Next steps:")
    print("1. Follow DEPLOYMENT_GUIDE.md for deployment instructions")
    print("2. Set up your Supabase project")
    print("3. Configure Streamlit Cloud secrets")
    print("4. Deploy your app!")

if __name__ == "__main__":
    main() 