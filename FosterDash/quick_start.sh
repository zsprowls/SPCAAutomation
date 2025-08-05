#!/bin/bash

# Quick Start Script for Foster Dashboard
# This script sets up everything you need to run locally and deploy

echo "🚀 Foster Dashboard Quick Start"
echo "================================"

# Check if we're in the right directory
if [ ! -f "foster_dashboard.py" ]; then
    echo "❌ Error: Please run this script from the FosterDash directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "foster_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv foster_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source foster_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements_foster_dashboard.txt

# Run setup scripts
echo "⚙️ Running setup scripts..."
python setup_supabase.py
python deploy_to_streamlit.py

# Check if data files exist
echo "📁 Checking data files..."
if [ -f "../__Load Files Go Here__/AnimalInventory.csv" ] && [ -f "../__Load Files Go Here__/FosterCurrent.csv" ]; then
    echo "✅ Data files found"
else
    echo "⚠️ Warning: Data files not found in ../__Load Files Go Here__/"
    echo "   Please ensure AnimalInventory.csv and FosterCurrent.csv are present"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 What's been set up:"
echo "✅ Virtual environment with all dependencies"
echo "✅ Streamlit configuration files"
echo "✅ Supabase setup templates"
echo "✅ Deployment configuration"
echo "✅ GitHub Actions workflow"
echo ""
echo "🚀 Next Steps:"
echo "1. Set up Supabase:"
echo "   - Go to https://supabase.com"
echo "   - Create a new project"
echo "   - Run the SQL from SUPABASE_SETUP.md"
echo "   - Get your API credentials"
echo ""
echo "2. Configure secrets:"
echo "   - Edit .streamlit/secrets.toml with your Supabase credentials"
echo ""
echo "3. Test locally:"
echo "   source foster_env/bin/activate"
echo "   streamlit run test_supabase_integration.py"
echo "   streamlit run foster_dashboard.py"
echo ""
echo "4. Deploy to Streamlit Cloud:"
echo "   - Follow DEPLOYMENT_GUIDE.md"
echo "   - Push your code to GitHub"
echo "   - Deploy via Streamlit Cloud"
echo ""
echo "📚 Documentation:"
echo "- SUPABASE_SETUP.md - Database setup guide"
echo "- DEPLOYMENT_GUIDE.md - Deployment instructions"
echo "- README_foster_dashboard.md - Full documentation"
echo ""
echo "🔧 Useful commands:"
echo "- Activate env: source foster_env/bin/activate"
echo "- Run dashboard: streamlit run foster_dashboard.py"
echo "- Test database: streamlit run test_supabase_integration.py"
echo "- Deactivate env: deactivate" 