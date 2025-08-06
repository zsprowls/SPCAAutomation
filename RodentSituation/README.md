# Rodent Intake Case Dashboard

A comprehensive Streamlit web application for managing and visualizing data from a mass rodent intake hoarding case.

## Features

- **Real-time Data Integration**: Combines data from multiple CSV files
- **Interactive Filtering**: Filter by species, sex, status, and location
- **Key Statistics**: Total rodents, foster placement rates, and placement needs
- **Visual Analytics**: Pie charts, bar charts, and progress gauges
- **PetPoint Integration**: Direct links to animal profiles
- **Professional UI**: Clean, modern interface with SPCA branding colors

## Data Sources

The dashboard integrates data from the following files:

1. **RodentIntake.csv** (Primary file)
   - Location: `RodentSituation/`
   - Header row: 4
   - Columns: AnimalNumber, Name, Species, Gender, Color

2. **FosterCurrent.csv** (Supplemental)
   - Location: `../__Load Files Go Here__/`
   - Header row: 7
   - Matches: textbox9 → AnimalNumber
   - Pulls: textbox10 (Foster Person ID), textbox11 (Foster Name)

3. **AnimalInventory.csv** (Supplemental)
   - Location: `../__Load Files Go Here__/`
   - Header row: 4
   - Matches: AnimalNumber
   - Pulls: Stage, Age, Sex, Location + SubLocation

4. **AnimalOutcome.csv** (Supplemental)
   - Location: `../__Load Files Go Here__/`
   - Header row: 4
   - Used when AnimalNumber not in Inventory
   - Pulls: OperationType (used as Status)

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify file structure**:
   ```
   RodentSituation/
   ├── rodent_dashboard.py
   ├── requirements.txt
   ├── README.md
   └── RodentIntake.csv
   
   ../__Load Files Go Here__/
   ├── FosterCurrent.csv
   ├── AnimalInventory.csv
   └── AnimalOutcome.csv
   ```

## Usage

1. **Start the dashboard**:
   ```bash
   streamlit run rodent_dashboard.py
   ```

2. **Access the application**:
   - Open your web browser
   - Navigate to `http://localhost:8501`

## Dashboard Components

### 1. Header Section
- Clear dashboard title with rodent icon
- Professional gradient styling using SPCA brand colors

### 2. Filter Panel (Sidebar)
- **Species**: Filter by GUINEA PIG, HAMSTER, etc.
- **Sex**: Filter by M, F, U (Unknown)
- **Status**: Filter by current stage or operation type
- **Location**: Filter by combined location/sub-location

### 3. Key Statistics Cards
- **Total Rodents**: Complete count from intake
- **In Foster**: Number and percentage in foster care
- **Needing Placement**: Animals requiring foster placement
- **Active Fosters**: Unique foster caregivers

### 4. Visualizations
- **Status Distribution**: Pie chart showing current status breakdown
- **Species Distribution**: Bar chart of species counts
- **Foster Progress Gauge**: Visual progress indicator

### 5. Main Data Table
- **AnimalNumber**: Unique identifier (clickable PetPoint link)
- **Name**: Animal name
- **Species**: Type of rodent
- **Sex**: Gender (M/F/U)
- **Age**: Age information (defaults to "N/A" if missing)
- **Status**: Current stage or operation type
- **Location**: Combined location and sub-location
- **Foster Info**: Foster person ID and name

### 6. Summary Statistics
- Breakdown by species with foster placement percentages

## Data Processing

The application automatically:
- Handles missing values gracefully
- Combines location and sub-location fields
- Falls back to Gender when Sex is missing
- Uses OperationType as Status when Stage is unavailable
- Creates clickable PetPoint profile links

## PetPoint Integration

Each AnimalNumber in the table is automatically converted to a clickable link:
```
https://service.sheltermanager.com/animal/{AnimalNumber}
```

## Branding

The dashboard uses SPCA brand colors:
- Primary: #062b49 (Dark Blue)
- Secondary: #bc6f32 (Orange)
- Accent: #512a44 (Purple)
- Neutral: #4f5b35 (Green)

## Troubleshooting

### Common Issues

1. **File Not Found Errors**:
   - Verify all CSV files are in the correct locations
   - Check file permissions
   - Ensure header row specifications are correct

2. **Data Loading Issues**:
   - Check CSV file encoding (should be UTF-8)
   - Verify column names match expected format
   - Review file structure for any formatting issues

3. **Performance Issues**:
   - Large datasets may load slowly initially
   - Use filters to reduce data volume
   - Consider data caching for better performance

### Data Validation

The application includes error handling for:
- Missing files
- Incorrect file formats
- Data type mismatches
- Empty or corrupted data

## Support

For technical support or feature requests, please contact the SPCA Automation team.

## Version History

- **v1.0**: Initial release with core dashboard functionality
- Integrated data from multiple sources
- Interactive filtering and visualization
- PetPoint profile integration 