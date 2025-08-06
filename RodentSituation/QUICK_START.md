# 🚀 Quick Start Guide

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
python3 setup.py
```

### 2. Run the Dashboard
```bash
python3 run_dashboard.py
```

### 3. Open Your Browser
Navigate to: **http://localhost:8501**

---

## What You'll See

### 📊 Key Statistics
- **Total Rodents**: Complete count from the hoarding case
- **In Foster**: Number and percentage currently in foster care
- **Needing Placement**: Animals still requiring foster placement
- **Active Fosters**: Unique foster caregivers

### 🔍 Interactive Filters
Use the sidebar to filter by:
- **Species**: GUINEA PIG, HAMSTER
- **Sex**: M, F, U (Unknown)
- **Status**: Current stage or operation type
- **Location**: Combined location and sub-location

### 📋 Main Data Table
Each row shows:
- **Animal ID**: Clickable link to PetPoint profile
- **Name**: Animal name
- **Species**: Type of rodent
- **Sex**: Gender
- **Age**: Age information
- **Status**: Current stage
- **Location**: Where the animal is located
- **Foster Info**: Foster person ID and name

### 📈 Visualizations
- **Status Distribution**: Pie chart of current statuses
- **Species Distribution**: Bar chart of species counts
- **Foster Progress**: Gauge showing placement progress

---

## Data Sources

The dashboard automatically combines data from:
- `RodentIntake.csv` (Primary file)
- `FosterCurrent.csv` (Foster information)
- `AnimalInventory.csv` (Current status and location)
- `AnimalOutcome.csv` (Outcome information)

---

## Troubleshooting

### ❌ "Module not found" errors
Run: `pip install -r requirements.txt`

### ⚠️ Missing data files
The dashboard will show warnings but still run. Check file paths in the README.

### 🔄 Dashboard not updating
Refresh your browser or restart the application.

---

## Need Help?

- Check the full `README.md` for detailed documentation
- Verify all CSV files are in the correct locations
- Ensure Python 3.7+ is installed

---

**🎯 Ready to manage your rodent intake case!** 