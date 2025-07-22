# 🐾 SPCA Adoptions Team Dashboard

## Overview
This dashboard provides real-time insights into shelter capacity, adoption metrics, and daily operations by analyzing the same data used in the morning email reports. It helps the adoptions team make data-driven decisions about capacity management and resource allocation.

## Features

### 📊 Key Metrics
- **Daily Adoptions**: Track adoption counts for selected dates
- **Current Occupancy**: Real-time shelter and foster occupancy numbers
- **Intake Analysis**: Breakdown of daily intake by species and group
- **Capacity Monitoring**: Utilization percentages with automated alerts

### 📈 Visualizations
- **Occupancy Charts**: Bar charts showing shelter vs foster/off-site animals by species/age
- **Stage Distribution**: Pie chart of current animal stages (In Foster, Hold stages, etc.)
- **Intake Breakdown**: Bar chart of intake by group and species

### ⚠️ Capacity Alerts
- Configurable capacity thresholds for shelter and foster programs
- Automated recommendations based on current capacity levels
- Color-coded alerts (green = good, yellow = approaching capacity, red = at capacity)

## Installation

1. **Install Dependencies**:
   ```bash
   cd spcaautomation/adoptions_dashboard
   pip install -r requirements.txt
   ```

2. **Ensure Data Files are Present**:
   Make sure these CSV files are in the `__Load Files Go Here__` directory:
   - `AnimalInventory.csv`
   - `AnimalOutcome.csv`
   - `AnimalIntake.csv`
   - `FosterCurrent.csv`

## Usage

### Running the Dashboard
```bash
cd spcaautomation/adoptions_dashboard
streamlit run dashboard.py
```

The dashboard will open in your web browser at `http://localhost:8501`

### Dashboard Controls

#### Sidebar Controls
- **Analysis Date**: Select the date for adoption and intake analysis
- **Capacity Thresholds**: Adjust warning levels for shelter and foster capacity
- **Refresh Data**: Button to reload data from CSV files

#### Main Dashboard Sections

1. **Metrics Row**: Quick overview of key daily numbers
2. **Occupancy Analysis**: Current shelter and foster breakdown
3. **Animal Stages**: Distribution of animals by their current stage
4. **Intake Analysis**: Daily intake breakdown by species and group
5. **Capacity Analysis**: Utilization percentages and recommendations

### Interpreting the Data

#### Capacity Recommendations
The dashboard provides automated recommendations based on current data:

- **Green Status**: Normal operating levels
- **Yellow Warning**: Approaching capacity - proactive measures recommended
- **Red Alert**: At or over capacity - urgent action needed

#### Typical Daily Workflow
1. **Morning**: Check overnight intake and current occupancy
2. **Midday**: Monitor adoption progress and capacity levels
3. **Afternoon**: Review recommendations for next-day planning
4. **Evening**: Final capacity check and planning for tomorrow

## Data Sources

The dashboard uses the same data sources as the morning email:
- **AnimalInventory.csv**: Current animals and their stages
- **AnimalOutcome.csv**: Adoption and outcome data
- **AnimalIntake.csv**: New animal intake data
- **FosterCurrent.csv**: Animals currently in foster care

## Customization

### Capacity Thresholds
You can adjust capacity estimates in the dashboard code:
```python
estimated_shelter_capacity = 200  # Adjust to your shelter's capacity
estimated_foster_capacity = 300   # Adjust to your foster program capacity
```

### Alert Thresholds
Modify the adoption count threshold for marketing alerts:
```python
if adoptions_count < 5:  # Adjust based on your daily adoption goals
```

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure `morning_email.py` is in the `MorningEmail` directory
2. **Missing Data Files**: Check that all required CSV files are in `__Load Files Go Here__`
3. **Date Format Issues**: Dashboard expects dates in MM/DD/YYYY format
4. **Path Issues**: Run the dashboard from the `adoptions_dashboard` directory

### Error Messages
- **"Could not import morning email functions"**: Check file paths and ensure morning_email.py exists
- **"Missing required data files"**: Verify CSV files are in the correct directory and properly named
- **"No data available"**: Check that the selected date has data in the CSV files

## Future Enhancements

- **Historical Trends**: Track capacity over time to identify patterns
- **Predictive Analytics**: Forecast busy periods based on historical data
- **Email Alerts**: Automated notifications when capacity thresholds are reached
- **Mobile Optimization**: Responsive design for mobile devices
- **Export Features**: Download reports and charts for presentations

## Support

For technical issues or feature requests, contact the development team or refer to the morning email processing documentation.

---

*Last updated: Created for SPCA Automation Project*