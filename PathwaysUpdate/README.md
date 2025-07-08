# Pathways for Care Viewer

A web application for viewing and browsing animal care data from the SPCA Pathways for Care system.

## Features

### 📄 Spreadsheet View
- Displays all animal data in a scrollable table format
- Fixed row height to show 3-4 lines of text
- Zebra striping for improved readability
- Hover highlighting
- Sortable and filterable columns
- Wide "Welfare Notes" column with text wrapping
- All other columns are center-aligned

### 🖼️ Record Browser View
- Shows one animal record at a time (flashcard style)
- Page indicator showing current position (e.g., "1/34")
- Left/right navigation arrows
- Displays animal images from PetPoint system (if available)
- Emphasized "Welfare Notes" section
- Clean, organized layout for all animal information

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have Chrome browser installed (required for image scraping)

3. Make sure the CSV file is available at `../__Load Files Go Here__/Pathways for Care.csv`

## Usage

### Quick Start
1. Start the application:
```bash
python run_app.py
```

2. Open your web browser and navigate to:
```
http://localhost:8050
```

3. Use the toggle buttons to switch between:
   - **Spreadsheet View**: See all animals in a table format
   - **Record Browser**: Browse animals one at a time

### Building Image Cache (Optional)
For faster image loading, build the cache first:
```bash
python build_cache.py
```

This will download all animal images once and cache them for fast access.

## Image Functionality

The application uses a pre-built image cache for fast loading of animal photos in the Record Browser view. 

### Cache System
- **Pre-built cache**: All images are downloaded once during cache building
- **Fast access**: Images load instantly from local cache
- **Automatic updates**: Cache refreshes daily or when rebuilt
- **Persistent storage**: Cache survives application restarts

### Building the Cache
1. **Automatic**: Cache builds automatically when starting the app (if needed)
2. **Manual**: Run `python build_cache.py` to build cache independently
3. **Resume**: Cache building can be interrupted and resumed

**Note**: Cache building requires:
- Valid PetPoint credentials
- Internet connection
- Chrome browser installed
- Selenium WebDriver

If the cache is not available, the application will display placeholders.

## Data Source

The application loads data from `Pathways for Care.csv` which contains:
- Animal names and IDs
- Species and location information
- Intake dates and days in system
- Foster and transfer attempts
- Communications team interactions
- Detailed welfare notes

## Technical Details

- Built with Dash and Bootstrap for responsive design
- Uses pandas for data manipulation
- Implements caching for image URLs to reduce API calls
- Supports real-time filtering and sorting
- Mobile-friendly responsive layout

## Troubleshooting

### Images Not Loading
- Check your internet connection
- Verify PetPoint credentials in the image service
- Ensure Chrome browser is installed
- Check console logs for error messages

### Data Not Loading
- Verify the CSV file exists in the correct location
- Check file permissions
- Ensure the CSV format matches expected structure

### Performance Issues
- The application caches images to improve performance
- Large datasets may take time to load initially
- Consider reducing the number of displayed records if needed 