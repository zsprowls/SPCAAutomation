@echo off
echo 🐹 Rodent Intake Case Dashboard
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 🔍 Checking dependencies...
python -c "import streamlit, pandas, plotly, numpy" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✅ Dependencies OK
echo.

REM Check data files
echo 📁 Checking data files...
if not exist "RodentIntake.csv" (
    echo ⚠️  Warning: RodentIntake.csv not found
)
if not exist "..\__Load Files Go Here__\FosterCurrent.csv" (
    echo ⚠️  Warning: FosterCurrent.csv not found
)
if not exist "..\__Load Files Go Here__\AnimalInventory.csv" (
    echo ⚠️  Warning: AnimalInventory.csv not found
)
if not exist "..\__Load Files Go Here__\AnimalOutcome.csv" (
    echo ⚠️  Warning: AnimalOutcome.csv not found
)

echo ✅ Ready to launch
echo.

REM Launch dashboard
echo 🚀 Starting dashboard...
echo 📱 The dashboard will open in your web browser at http://localhost:8501
echo 🛑 Press Ctrl+C to stop the dashboard
echo.

python -m streamlit run rodent_dashboard.py

echo.
echo 👋 Dashboard stopped
pause 