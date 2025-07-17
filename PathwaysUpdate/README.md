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

### 2. Set Up Google Drive API

See the step-by-step guide at the end of this README.

### 3. Test Connection

```bash
python3 test_gdrive_connection.py
```

### 4. Run the App

```bash
streamlit run streamlit_gdrive_app.py
```

## File Structure

```
PathwaysUpdate/
├── streamlit_gdrive_app.py      # Main Streamlit application
├── google_drive_manager.py      # Google Drive API integration
├── image_cache_manager.py       # Image cache management
├── build_cache.py               # Build image cache from PetPoint
├── animal_images_cache.json     # Cached animal images
├── requirements_gdrive.txt      # Python dependencies
├── test_gdrive_connection.py    # Connection test script
├── GOOGLE_DRIVE_SETUP.md        # Detailed setup guide
└── README.md                    # This file
```

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

See `GOOGLE_DRIVE_SETUP.md` for detailed troubleshooting information.

## Support

For issues or questions, check the setup guide or contact the development team.

---

# Google API Setup: Step-by-Step

1. **Go to Google Cloud Console**
   - Visit: https://console.developers.google.com/

2. **Select Your Project**
   - At the top left, select the project you want to use (or create a new one if needed).

3. **Enable Google Drive API**
   - (You said this is already done, so you can skip this step.)

4. **Configure OAuth Consent Screen**
   - In the left sidebar, go to **APIs & Services > OAuth consent screen**.
   - **User Type:** Choose “External” (unless you want to restrict to your Google Workspace).
   - **App Name:** Enter a name (e.g., “Pathways for Care Viewer”).
   - **User Support Email:** Enter your email.
   - **Developer Contact Information:** Enter your email again.
   - **Scopes:** You can leave as default for now (the app will only request Drive access).
   - **Test Users:** Add your Google account email (and any others who will use the app).
   - Click **Save and Continue** until you reach the summary, then **Back to Dashboard**.

5. **Create OAuth 2.0 Credentials**
   - Go to **APIs & Services > Credentials**.
   - Click **+ CREATE CREDENTIALS** > **OAuth client ID**.
   - **Application type:** Select “Desktop app”.
   - **Name:** (e.g., “Pathways Streamlit Local”)
   - Click **Create**.

6. **Download Credentials**
   - Click **Download JSON** for your new OAuth client.
   - Rename the file to `credentials.json`.
   - Place it in your `PathwaysUpdate/` directory.

7. **First-Time Authentication**
   - Run:
     ```bash
     python3 test_gdrive_connection.py
     ```
   - A browser window will open. Log in with your Google account and approve access.
   - A `token.pickle` file will be created for future logins. 