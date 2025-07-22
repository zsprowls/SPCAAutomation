# Adoptions Counselor Dashboard

A comprehensive dashboard for adoptions counselors to view morning email data, outcomes, adoptions by counselor, and longest length of stay animals.

## Features

### 📊 Current Capacity Tab
- **Total animals, cats, and dogs metrics**
- **Capacity breakdown by species and location**
- **Drill-down capability**: Filter by species and location to see individual animals
- **PetPoint profile links** for each animal

### 📈 Previous Day Summary Tab
- **Previous day intakes and outcomes metrics**
- **Species breakdown charts** for intakes and outcomes
- **Detailed lists** with PetPoint profile links
- **Adoption count** from previous day

### 👥 Adoptions by Counselor Tab
- **Counselor performance summary** showing adoptions per counselor
- **Filter adoptions by counselor** to see individual animals
- **PetPoint profile links** for all adoption animals

### ⏰ Longest Length of Stay Tab
- **Top 20 longest stay animals** for cats, dogs, and others
- **Filtered by specific stages**:
  - Available
  - Available - Behind the Scenes
  - Available - Doggie Entourage
  - Available - ITFF Behavior
  - Available - ITFF Medical
- **PetPoint profile links** for all animals

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure data files are available**:
   - `__Load Files Go Here__/AnimalInventory.csv`
   - `__Load Files Go Here__/AnimalIntake.csv`
   - `__Load Files Go Here__/AnimalOutcome.csv`

3. **Run the dashboard**:
   ```bash
   streamlit run app.py
   ```

## Data Requirements

The dashboard expects the following CSV files in the `__Load Files Go Here__` directory:

- **AnimalInventory.csv**: Current animal inventory with columns:
  - AnimalName, Species, Location, Stage, AnimalNumber, IntakeDateTime, DateOfBirth

- **AnimalIntake.csv**: Previous day's intakes with columns:
  - AnimalName, Species, IntakeType, IntakeDateTime

- **AnimalOutcome.csv**: Previous day's outcomes with columns:
  - AnimalName, Species, OutcomeType, OutcomeCounselor, OutcomeDateTime

## Usage

1. **Navigate between tabs** to view different data sections
2. **Use drill-down filters** to see specific animals
3. **Click PetPoint profile links** to view detailed animal information
4. **View charts and metrics** for quick insights

## Styling

The dashboard uses SPCA brand colors:
- Primary: #062b49 (dark blue)
- Secondary: #bc6f32 (orange)
- Accent: #512a44 (purple)
- Accent: #4f5b35 (green)

## Notes

- The dashboard automatically calculates length of stay from intake dates
- PetPoint links are generated using the AID (last 8 digits of AnimalNumber)
- Data is cached for performance
- Previous day data is calculated based on the current date 