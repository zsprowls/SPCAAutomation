#!/bin/bash

echo "Setting up PetPoint Automation Environment"
echo "========================================="

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv petpoint_env

# Activate virtual environment
echo "Activating virtual environment..."
source petpoint_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements_petpoint.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file template..."
    cat > .env << EOF
# PetPoint Automation Environment Variables
# Fill in your actual credentials below

PETPOINT_USER=your_username_here
PETPOINT_PASS=your_password_here
PETPOINT_BASE_URL=https://your-petpoint-instance.com
EOF
    echo "Created .env file. Please edit it with your actual credentials."
else
    echo ".env file already exists."
fi

echo ""
echo "Setup complete! Next steps:"
echo "1. Edit .env file with your PetPoint credentials"
echo "2. Update selectors in pull_petpoint_reports.py based on your PetPoint instance"
echo "3. Run: python pull_petpoint_reports.py"
echo ""
echo "To activate the environment in the future:"
echo "source petpoint_env/bin/activate"
