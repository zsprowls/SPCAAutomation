# Pathways for Care Viewer – Google Drive Version

A Streamlit application for viewing and managing Pathways for Care data using Google Drive as the backend storage. This is a cost-effective alternative to cloud databases.

## Features

- **Google Drive Integration**: Uses Google Drive CSV files for data storage
- **Real-time Updates**: Changes are saved directly to Google Drive
- **Image Support**: Displays animal images and videos
- **Search Functionality**: Search by AID, name, or location
- **Two View Modes**: Animal Details and Spreadsheet View
- **Password Protection**: Secure access to the application
- **Responsive Design**: Modern UI with custom styling

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_gdrive.txt
```

### 2. Set Up Google Service Account

**Option A: Use the setup script (Recommended)**
```bash
python3 setup_service_account.py
```

**Option B: Manual setup**
1. Follow the instructions in `SERVICE_ACCOUNT_SETUP.md`
2. Download your service account key as `service_account_key.json`
3. Place it in the `PathwaysUpdate/` directory

### 3. Test Connection

```bash
python3 test_update_functionality.py
```

### 4. Run the App

```bash
streamlit run streamlit_gdrive_app.py
```

## File Structure

```
PathwaysUpdate/
├── streamlit_gdrive_app.py          # Main Streamlit application
├── google_drive_manager.py          # Google Drive API integration
├── image_cache_manager.py           # Image cache management
├── build_cache.py                   # Build image cache from PetPoint
├── animal_images_cache.json         # Cached animal images
├── requirements_gdrive.txt          # Python dependencies
├── setup_service_account.py         # Service account setup helper
├── test_update_functionality.py     # Update functionality test
├── service_account_key_template.json # Template for service account key
├── .gitignore                       # Git ignore rules (excludes sensitive files)
├── SERVICE_ACCOUNT_SETUP.md         # Service account setup guide
└── README.md                        # This file
```

## Security Notes

⚠️ **Important**: The following files contain sensitive information and are automatically excluded from Git:
- `service_account_key.json` - Your Google service account credentials
- `.env` - Environment variables
- `credentials.json` - OAuth credentials (if using OAuth)
- `token.pickle` - OAuth tokens (if using OAuth)

These files are listed in `.gitignore` to prevent accidental commits of sensitive data.

## Data Structure

The app uses a CSV file in Google Drive with these columns:
- `AID`: Animal ID
- `Animal Name`: Animal's name
- `Location`: Current location
- `SubLocation`: Sub-location
- `Age`: Animal's age
- `Stage`: Current stage
- `Foster_Attempted`: Foster status
- `Transfer_Attempted`: Transfer status
- `Communications_Team_Attempted`: Communications status
- `Welfare_Notes`: Welfare notes
- `Image_URLs`: Comma-separated image URLs

## Benefits

- **Cost-effective**: No monthly database costs
- **Simple**: Uses CSV files that anyone can edit
- **Reliable**: Google Drive is very stable
- **Collaborative**: Multiple people can edit the same file
- **Automatic Backup**: Google Drive handles backups

## Authentication

The app uses password protection. Default password: `SPCAPathways1*`

## Image Cache

To enable animal images:
1. Run `python3 build_cache.py` to build the image cache
2. The app will automatically use the cached images

## Troubleshooting

### Common Issues

1. **"Invalid JWT Signature" error**
   - Your service account key is corrupted or invalid
   - Solution: Download a fresh key from Google Cloud Console

2. **"Permission denied" error**
   - The service account doesn't have access to the Google Sheet
   - Solution: Share the sheet with the service account email (Editor permissions)

3. **"API not enabled" error**
   - Google Drive API or Google Sheets API not enabled
   - Solution: Enable both APIs in Google Cloud Console

### Getting Help

1. Run the setup script: `python3 setup_service_account.py`
2. Check the test script: `python3 test_update_functionality.py`
3. See `SERVICE_ACCOUNT_SETUP.md` for detailed troubleshooting
4. Contact the development team for additional support

## Support

For issues or questions, check the setup guide or contact the development team.

---

# Google API Setup: Step-by-Step

1. **Go to Google Cloud Console**
   - Visit: https://console.developers.google.com/

2. **Select Your Project**
   - At the top left, select the project you want to use (or create a new one if needed).

3. **Enable Required APIs**
   - Go to **APIs & Services > Library**
   - Search for and enable:
     - **Google Drive API**
     - **Google Sheets API**

4. **Create Service Account**
   - Go to **IAM & Admin > Service Accounts**
   - Click **"Create Service Account"**
   - **Name**: `pathways-sheets-service`
   - **Description**: `Service account for Pathways for Care Google Sheets access`
   - Click **"Create and Continue"**
   - **Grant access**: Select **"Editor"** role
   - Click **"Continue"** then **"Done"**

5. **Create Service Account Key**
   - Click on your new service account
   - Go to **"Keys"** tab
   - Click **"Add Key"** → **"Create new key"** → **"JSON"**
   - Download the key file
   - Rename it to `service_account_key.json`
   - Place it in your `PathwaysUpdate/` directory

6. **Share Your Google Sheet**
   - Open your Google Sheet
   - Click **"Share"** (top right)
   - Add your service account email (found in the JSON file)
   - Give it **"Editor"** permissions
   - Uncheck "Notify people"
   - Click **"Share"**

7. **Test the Setup**
   ```bash
   python3 setup_service_account.py
   ``` 