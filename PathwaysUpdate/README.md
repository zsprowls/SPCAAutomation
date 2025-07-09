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

2. Make sure the CSV file is available at `../__Load Files Go Here__/Pathways for Care.csv`

**Note**: Image scraping functionality has been removed. The app now uses a pre-built image cache.

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

### Image Cache
The application uses a pre-built image cache for fast loading of animal photos. The cache is already included and contains images for 50 animals with 232 total images.

**Note**: Cache building functionality has been disabled. The app uses the existing pre-built cache.

## Image Functionality

The application uses a pre-built image cache for fast loading of animal photos in the Record Browser view. 

### Cache System
- **Pre-built cache**: All images are already downloaded and cached
- **Fast access**: Images load instantly from local cache
- **Persistent storage**: Cache survives application restarts
- **No external dependencies**: No need for Chrome browser or Selenium

### Current Cache Status
- **50 animals** with cached images
- **232 total images** available
- **Cache file**: `animal_images_cache.json` (20KB)

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
- The app uses a pre-built cache, so no internet connection is required
- Check that `animal_images_cache.json` exists in the PathwaysUpdate folder
- Check console logs for error messages

### Data Not Loading
- Verify the CSV file exists in the correct location
- Check file permissions
- Ensure the CSV format matches expected structure

### Performance Issues
- The application caches images to improve performance
- Large datasets may take time to load initially
- Consider reducing the number of displayed records if needed 