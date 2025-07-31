# Rodent Dashboard - Simple Setup (No Homebrew)

This setup completely ignores Homebrew and uses system Python.

## Quick Start

### Option 1: Simple Launcher (Recommended)
```bash
cd RodentSituation
python3 run_simple.py
```

### Option 2: Direct Command
```bash
cd RodentSituation
python3 -m streamlit run rodent_dashboard.py
```

### Option 3: Windows
```cmd
cd RodentSituation
run_simple.bat
```

## What This Does

- ✅ Uses **system Python** (ignores Homebrew completely)
- ✅ Installs packages to **user directory** (no conflicts)
- ✅ No virtual environments needed
- ✅ No Homebrew dependencies

## Troubleshooting

**If you get import errors:**
```bash
python3 -m pip install --user streamlit pandas plotly
```

**If you get path errors:**
Make sure all CSV files are in the RodentSituation folder:
- RodentIntake.csv
- FosterCurrent.csv  
- AnimalInventory.csv
- AnimalOutcome.csv

## Files

- `rodent_dashboard.py` - Main dashboard
- `run_simple.py` - Simple launcher (Mac/Linux)
- `run_simple.bat` - Simple launcher (Windows)
- `requirements.txt` - Package list (for reference)

That's it! No Homebrew, no virtual environments, no complications. 