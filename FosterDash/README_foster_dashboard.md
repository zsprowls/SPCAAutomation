# SPCA Foster Dashboard

A Streamlit dashboard for tracking foster needs at the SPCA animal shelter with cloud database integration.

## Features

- **Three Foster Categories:**
  - **Needs Foster Now**: Animals with stages like "Hold - Foster", "Hold - Cruelty Foster", "Hold – SAFE Foster"
  - **Might Need Foster Soon**: Animals with stages like "Hold - Doc", "Hold - Behavior", "Hold - Surgery", etc.
  - **In Foster**: Animals currently in foster care or with foster-related stages

- **Key Information Displayed:**
  - Animal ID, Name, Intake Group, Species, Breed, Sex, Age, Stage
  - Direct links to PetPoint profile and Animal View Report
  - Sortable by Intake Date or Name

- **Interactive Database Features (with Supabase):**
  - **Foster Notes**: Editable text areas for each animal
  - **On Medications**: Checkbox to track medication status
  - **Foster Plea Dates**: Date picker for tracking foster requests
  - **Real-time Updates**: All changes sync immediately to cloud database
  - **Data Persistence**: All foster data stored securely in Supabase

- **Dashboard Features:**
  - Real-time metrics showing counts for each category
  - Radio button filtering between categories
  - Mobile-responsive design
  - CSV download functionality
  - Data quality information
  - Database status indicator

## Setup

### Basic Setup (CSV Only)

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

### Database Setup (Recommended)

For full functionality with interactive foster data management:

1. **Set up Supabase:**
   - Follow the detailed guide in `SUPABASE_SETUP.md`
   - Create a Supabase project and database table
   - Configure your API credentials

2. **Configure Streamlit Secrets:**
   - Create `.streamlit/secrets.toml` with your Supabase credentials
   - Or configure secrets in Streamlit Cloud for deployment

3. **Test the Integration:**
   ```bash
   streamlit run test_supabase_integration.py
   ```

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

## Database Schema

When using Supabase, the following table structure is created:

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key (auto-increment) |
| `AnimalNumber` | TEXT | Unique animal identifier (from PetPoint) |
| `FosterNotes` | TEXT | Editable foster notes |
| `OnMeds` | BOOLEAN | Checkbox for medication status |
| `FosterPleaDates` | JSONB | Array of foster plea dates |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

## PetPoint Integration

The dashboard automatically generates links to:
- **PetPoint Profile**: `https://sms.petpoint.com/sms3/enhanced/animal/[Animal Id]`
- **Animal View Report**: `https://sms.petpoint.com/sms3/embeddedreports/animalviewreport.aspx?AnimalID=[Animal Id]`

## Usage

### Basic Usage (CSV Only)
1. Select a foster category using the radio buttons in the sidebar
2. View the filtered list of animals in that category
3. Click on PetPoint links to view detailed information
4. Download filtered data as CSV if needed
5. Check the "Data Quality Information" expander for data insights

### Interactive Usage (with Database)
1. **Foster Notes & Medications**: 
   - Expand any animal in the "Foster Notes & Medications" tab
   - Edit foster notes in the text area
   - Toggle medication status with the checkbox
   - Changes save automatically to the database

2. **Foster Plea Dates**:
   - Switch to "Needs Foster Now" category
   - Use the "Foster Plea Dates" tab to manage dates
   - Add new dates with the date picker
   - Remove existing dates with the remove button

3. **Database Status**:
   - Check the sidebar for database connection status
   - Green checkmark indicates successful connection
   - Warning icon indicates database features are disabled

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
│   ├── foster_dashboard.py          # Main dashboard application
│   ├── supabase_manager.py          # Database integration module
│   ├── test_supabase_integration.py # Database testing script
│   ├── SUPABASE_SETUP.md           # Database setup guide
│   ├── requirements_foster_dashboard.txt
│   ├── README_foster_dashboard.md
│   ├── run_foster_dashboard.bat
│   └── run_foster_dashboard.sh
└── __Load Files Go Here__/
    ├── AnimalInventory.csv
    └── FosterCurrent.csv
```

## Troubleshooting

### Database Connection Issues
- Verify Supabase credentials in Streamlit secrets
- Check that the `foster_animals` table exists in your Supabase project
- Run the test script to diagnose connection problems

### Data Sync Issues
- Ensure AnimalInventory.csv is loading correctly
- Check that AnimalNumber column exists and has data
- Verify database permissions and RLS policies

### Performance Issues
- Database operations are cached for better performance
- Large datasets may take time to sync initially
- Consider using filters to reduce displayed data 