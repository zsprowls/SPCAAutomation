@echo off
echo ========================================
echo    SPCA Reports - Setup Script
echo ========================================
echo.
echo This script will:
echo 1. Check if Python is installed
echo 2. Install required packages
echo 3. Verify the installation
echo.
pause

echo.
echo ========================================
echo Step 1: Checking Python installation...
echo ========================================
python --version
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo ✅ Python is installed!

echo.
echo ========================================
echo Step 2: Installing required packages...
echo ========================================
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to install packages!
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo ✅ Packages installed successfully!

echo.
echo ========================================
echo Step 3: Verifying installation...
echo ========================================
python -c "import pandas; print('✅ pandas installed')"
python -c "import docx; print('✅ python-docx installed')"
python -c "import openpyxl; print('✅ openpyxl installed')"
python -c "import xlsxwriter; print('✅ xlsxwriter installed')"

echo.
echo ========================================
echo 🎉 Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Update the files in "__Load Files Go Here__" folder
echo 2. Double-click "Run_SPCA_Reports.bat" to run reports
echo.
pause 