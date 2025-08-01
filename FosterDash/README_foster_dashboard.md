# SPCA Foster Dashboard

A Streamlit dashboard for tracking foster needs at the SPCA animal shelter.

## Features

- **Three Foster Categories:**
  - **Needs Foster Now**: Animals with stages like "Hold - Foster", "Hold - Cruelty Foster", "Hold – SAFE Foster"
  - **Might Need Foster Soon**: Animals with stages like "Hold - Doc", "Hold - Behavior", "Hold - Surgery", etc.
  - **In Foster**: Animals currently in foster care or with foster-related stages

- **Key Information Displayed:**
  - Animal ID, Name, Intake Group, Species, Breed, Sex, Age, Stage
  - Direct links to PetPoint profile and Animal View Report
  - Sortable by Intake Date or Name

- **Dashboard Features:**
  - Real-time metrics showing counts for each category
  - Radio button filtering between categories
  - Mobile-responsive design
  - CSV download functionality
  - Data quality information

## Setup

1. **Navigate to the FosterDash folder:**
   ```bash
   cd FosterDash
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements_foster_dashboard.txt
   ```

3. **Data Files:**
   Ensure the following CSV files are in the `__Load Files Go Here__` folder (in the parent directory):
   - `AnimalInventory.csv`
   - `FosterCurrent.csv`

4. **Run the Dashboard:**
   ```bash
   streamlit run foster_dashboard.py
   ```

## Data Requirements

The dashboard expects the following columns in `AnimalInventory.csv`:
- `AnimalNumber`: Unique identifier for each animal
- `AnimalName`: Animal's name
- `IntakeDateTime`: Date/time of intake (formatted as "7/22/2025 11:25:00 AM")
- `Species`: Animal species
- `PrimaryBreed`: Animal breed
- `Sex`: Animal's sex
- `Age`: Animal's age
- `Stage`: Current stage/status

The `FosterCurrent.csv` should contain:
- `textbox9`: Animal ID (to match with AnimalNumber in inventory)
- `textbox10`: Person ID (PID)
- `textbox11`: Person's name

## PetPoint Integration

The dashboard automatically generates links to:
- **PetPoint Profile**: `https://sms.petpoint.com/sms3/enhanced/animal/[Animal Id]`
- **Animal View Report**: `https://sms.petpoint.com/sms3/embeddedreports/animalviewreport.aspx?AnimalID=[Animal Id]`

## Usage

1. Select a foster category using the radio buttons in the sidebar
2. View the filtered list of animals in that category
3. Click on PetPoint links to view detailed information
4. Download filtered data as CSV if needed
5. Check the "Data Quality Information" expander for data insights

## Brand Colors

The dashboard uses SPCA brand colors:
- Primary: #062b49 (Dark Blue)
- Secondary: #bc6f32 (Orange)
- Accent: #512a44 (Purple)
- Accent: #4f5b35 (Green)

## File Structure

```
SPCAAutomation/
├── FosterDash/
│   ├── foster_dashboard.py
│   ├── requirements_foster_dashboard.txt
│   ├── README_foster_dashboard.md
│   ├── run_foster_dashboard.bat
│   └── run_foster_dashboard.sh
└── __Load Files Go Here__/
    ├── AnimalInventory.csv
    └── FosterCurrent.csv
``` 