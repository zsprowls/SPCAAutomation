# 🚀 Quick Start Guide - Adoptions Dashboard

## Get Started in 3 Steps

### 1. Open Terminal/Command Prompt
Navigate to the dashboard folder:
```bash
cd spcaautomation/adoptions_dashboard
```

### 2. Run the Dashboard
**Option A - Easy Launch (Recommended):**
```bash
./run_dashboard.sh
```

**Option B - Manual Launch:**
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

### 3. Open Your Browser
The dashboard will automatically open at: `http://localhost:8501`

---

## What You'll See

### 📊 Top Metrics Bar
- **Daily Adoptions**: Adoptions for the selected date
- **Animals in Shelter**: Current shelter occupancy  
- **In Foster/Off-Site**: Animals in foster care
- **Total Intake**: Animals received on selected date

### 📈 Charts & Analysis
- **Occupancy Chart**: Visual breakdown by animal type and location
- **Animal Stages**: Pie chart of current stages (foster, holds, etc.)
- **Intake Analysis**: Daily intake by group and species

### ⚠️ Capacity Alerts
- **Green**: All good - normal capacity levels
- **Yellow**: Approaching capacity - plan ahead
- **Red**: At/over capacity - take action now

### 💡 Smart Recommendations
The dashboard automatically suggests actions based on current data:
- Increase adoptions when at capacity
- Boost marketing when adoptions are low
- Balance intake vs. outflow

---

## Daily Workflow Tips

### Morning Check (8-9 AM)
1. Review overnight intake numbers
2. Check current shelter occupancy
3. Note any capacity alerts

### Midday Update (12-1 PM)
1. Monitor adoption progress
2. Adjust capacity thresholds if needed
3. Plan afternoon activities based on recommendations

### End of Day (5-6 PM)
1. Final capacity check
2. Review daily performance
3. Plan for tomorrow based on trends

---

## Need Help?

### Common Issues
- **Can't find data files**: Make sure CSV files are in `__Load Files Go Here__` folder
- **Import errors**: Ensure you're in the right directory and `morning_email.py` exists
- **Dashboard won't start**: Try `pip install -r requirements.txt` first

### Customization
Edit `config.py` to adjust:
- Shelter and foster capacity limits
- Alert thresholds
- Daily adoption goals

### Support
See the full `README.md` for detailed documentation and troubleshooting.

---

*🐾 Happy monitoring! The dashboard updates in real-time as you refresh your data.*