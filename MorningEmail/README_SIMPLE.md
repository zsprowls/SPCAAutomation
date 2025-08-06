# Morning Email Script - Simple Setup (No Homebrew)

This setup completely ignores Homebrew and uses system Python.

## Quick Start

### Option 1: Simple Launcher (Recommended)
```bash
cd MorningEmail
python3 run_morning_email.py
```

### Option 2: Direct Command
```bash
cd MorningEmail
python3 morning_email.py
```

## What This Does

- ✅ Uses **system Python** (ignores Homebrew completely)
- ✅ Installs packages to **user directory** (no conflicts)
- ✅ No virtual environments needed
- ✅ No Homebrew dependencies

## Required Files

Make sure these CSV files are in the `__Load Files Go Here__` folder:
- FosterCurrent.csv
- AnimalInventory.csv
- AnimalOutcome.csv
- StageReview.csv

## What the Script Does

1. **Asks for dates** - Enter dates in mm/dd/yyyy format (separated by commas)
2. **Generates reports** - Creates Word documents with:
   - Foster counts
   - Stage counts
   - Intake summaries
   - Adoption counts
   - "If The Fur Fits" counts

## Troubleshooting

**If you get import errors:**
```bash
python3 -m pip install --user pandas xlsxwriter python-docx
```

**If you get file not found errors:**
Make sure all CSV files are in the `__Load Files Go Here__` folder

## Files

- `morning_email.py` - Main script
- `run_morning_email.py` - Simple launcher
- `requirements.txt` - Package list (for reference)

That's it! No Homebrew, no virtual environments, no complications. 