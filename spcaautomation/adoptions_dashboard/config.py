# SPCA Adoptions Dashboard Configuration

# Shelter Capacity Settings
SHELTER_CAPACITY = 200  # Maximum animals the shelter can house
FOSTER_CAPACITY = 300   # Target foster program capacity

# Alert Thresholds (percentages)
SHELTER_WARNING_THRESHOLD = 75   # Yellow warning at 75%
SHELTER_CRITICAL_THRESHOLD = 85  # Red alert at 85%

FOSTER_WARNING_THRESHOLD = 80    # Yellow warning at 80%
FOSTER_CRITICAL_THRESHOLD = 90   # Red alert at 90%

# Adoption Goals
DAILY_ADOPTION_TARGET = 5  # Minimum daily adoptions before marketing alerts

# Intake vs Adoption Balance
INTAKE_ADOPTION_RATIO_ALERT = 2  # Alert if intake > adoptions * this ratio

# Dashboard Settings
DEFAULT_ANALYSIS_DAYS_BACK = 1  # How many days back to default for analysis
REFRESH_INTERVAL_SECONDS = 300  # Auto-refresh every 5 minutes

# Data File Paths (relative to dashboard location)
DATA_DIRECTORY = "../../__Load Files Go Here__"
REQUIRED_DATA_FILES = [
    "AnimalInventory.csv",
    "AnimalOutcome.csv", 
    "AnimalIntake.csv",
    "FosterCurrent.csv"
]

# Chart Colors
CHART_COLORS = {
    'shelter': '#FF6B6B',
    'foster': '#4ECDC4',
    'cat': '#FF9F43',
    'dog': '#10AC84', 
    'other': '#5F27CD',
    'success': '#2ECC71',
    'warning': '#F39C12',
    'danger': '#E74C3C'
}

# Stage Priority Order (for displays)
STAGE_DISPLAY_ORDER = [
    'In Foster',
    'Hold SAFE Foster',
    'Hold Foster', 
    'Hold Cruelty Foster',
    'Hold Behavior Foster',
    'Hold Surgery',
    'Hold Doc',
    'Hold Behavior',
    'Hold Dental',
    'Hold Behavior Mod.',
    'Hold Complaint',
    'Hold Stray/Legal'
]