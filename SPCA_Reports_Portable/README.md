# SPCA Reports Automation - Portable Package

This package contains everything needed to run SPCA reports on any Windows computer with Python installed.

## 📁 Package Contents

- `__Load Files Go Here__/` - Folder for your CSV data files
- `MorningEmail/` - Morning email report generator
- `SPCA_Rounds/` - Clear file processing script
- `Run_SPCA_Reports.bat` - One-click launcher for both reports
- `requirements.txt` - Python dependencies
- `SPCA_Reports_Instructions.txt` - User guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation by opening Command Prompt and typing: `python --version`

### Step 2: Install Dependencies
1. Open Command Prompt in this folder
2. Run: `pip install -r requirements.txt`

### Step 3: Update Data Files
1. Copy your latest CSV files into the `__Load Files Go Here__` folder:
   - `AnimalInventory.csv`
   - `StageReview.csv`
   - `FosterCurrent.csv`
   - `AnimalOutcome.csv`

### Step 4: Run Reports
1. Double-click `Run_SPCA_Reports.bat`
2. Follow the prompts on screen

## 📋 Detailed Instructions

### Before Running Reports:
1. **Update Data Files**: Replace the files in `__Load Files Go Here__` with your latest data
2. **Check Python**: Make sure Python is installed and in your PATH
3. **Install Dependencies**: Run `pip install -r requirements.txt` once

### Running the Reports:
1. **Double-click** `Run_SPCA_Reports.bat`
2. **Read the instructions** that appear on screen
3. **Press any key** when prompted to continue
4. **Enter dates** when asked (for morning email report)
   - Format: `mm/dd/yyyy, mm/dd/yyyy`
   - Example: `12/15/2024, 12/16/2024`

### Output Files:
After successful completion, you'll find:
- `SPCA_Rounds/clear.csv` - Clear file processing results
- `MorningEmail/morning_report.xlsx` - Morning email report

## 🔧 What Each Script Does

### Clear File Processing (`SPCA_Rounds/clear_file.py`)
- Reads `AnimalInventory.csv` and `StageReview.csv`
- Filters for animals on "Hold" status
- Creates `clear.csv` with animals needing attention

### Morning Email Report (`MorningEmail/morning_email.py`)
- Reads multiple CSV files from `__Load Files Go Here__`
- Generates comprehensive morning report
- Creates `morning_report.xlsx`

## 🛠️ Troubleshooting

### "Python is not recognized"
- **Solution**: Install Python and check "Add Python to PATH"
- **Alternative**: Use full path to Python in batch file

### "Module not found" errors
- **Solution**: Run `pip install -r requirements.txt`
- **Alternative**: Install packages individually:
  ```
  pip install pandas python-docx openpyxl xlsxwriter
  ```

### "File not found" errors
- **Solution**: Make sure CSV files are in `__Load Files Go Here__` folder
- **Check**: Verify file names match exactly (case-sensitive)

### Script runs but no output
- **Check**: Look for error messages in the command window
- **Verify**: Data files are not empty and have correct format

## 📞 Need Help?

1. **Check the error messages** in the command window
2. **Verify Python installation**: `python --version`
3. **Verify dependencies**: `pip list`
4. **Check file locations**: Make sure all files are in the correct folders

## 🔄 Regular Usage

After initial setup, you only need to:
1. **Update files** in `__Load Files Go Here__` folder
2. **Double-click** `Run_SPCA_Reports.bat`
3. **Enter dates** when prompted
4. **Check output files** when complete

That's it! No need to reinstall Python or dependencies unless you move to a different computer. 