# Google Drive Setup Guide

This guide will help you set up the Pathways for Care Viewer to use Google Drive instead of Google Cloud SQL. This is a much more cost-effective solution!

## Why Google Drive?

- **Cost-effective**: No monthly database costs
- **Simple**: Uses CSV files that anyone can edit
- **Reliable**: Google Drive is very stable
- **Collaborative**: Multiple people can edit the same file

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements_gdrive.txt
```

### 2. Set Up Google Drive API

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### 3. Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Download the credentials file
5. Rename it to `credentials.json` and place it in the `PathwaysUpdate/` directory

### 4. Test the Connection

```bash
python3 test_gdrive_connection.py
```

The first time you run this, it will open a browser window for authentication. Follow the prompts to authorize the application.

### 5. Run the App

```bash
streamlit run streamlit_gdrive_app.py
```

## How It Works

1. **Data Storage**: All data is stored in a CSV file in your Google Drive
2. **File Creation**: The app will automatically create a `pathways_data.csv` file if it doesn't exist
3. **Permissions**: The file is set to "Anyone with the link can edit"
4. **Real-time Updates**: Changes are saved directly to the Google Drive file

## File Structure

The CSV file will have these columns:
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

## Benefits Over Google Cloud SQL

- **No monthly costs**: Google Drive is free
- **No database management**: Just a simple CSV file
- **Easy backup**: File is automatically backed up by Google
- **Simple sharing**: Anyone with the link can view/edit
- **No connection issues**: No database connection problems

## Troubleshooting

### Authentication Issues
- Delete `token.pickle` and try again
- Make sure `credentials.json` is in the correct location
- Check that Google Drive API is enabled

### File Not Found
- The app will create the file automatically on first run
- Check that you have write permissions to Google Drive

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements_gdrive.txt`
- Check that you're using Python 3.7+

## Migration from Google Cloud SQL

If you have existing data in Google Cloud SQL:

1. Export your data to CSV
2. Upload the CSV to Google Drive
3. Rename it to `pathways_data.csv`
4. Run the Google Drive app

The app will automatically use the existing data file. 