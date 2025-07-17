# Service Account Setup for Web Deployment

This guide will help you set up a Google Service Account for deploying your Pathways for Care app to the web.

## Why Service Account?

- **No user login required**: The app works immediately without OAuth flows
- **Perfect for web deployment**: No browser redirects needed
- **Secure**: Uses a dedicated service account with limited permissions
- **Simple**: Just upload the key file and you're done

## Important: Service Account Storage Limitation

**Service accounts don't have their own Google Drive storage quota.** We need to use your personal Google Drive and share files with the service account.

## Step-by-Step Setup

###1te Service Account
1. Go to [Google Cloud Console](https://console.developers.google.com/)2. Navigate to **APIs & Services > Credentials**
3. Click **+ CREATE CREDENTIALS** > **Service Account**
4. **Service account name:** `pathways-drive-service`
5. **Service account ID:** (auto-generated)
6. **Description:** `Service account for Pathways for Care Google Drive access`7Click **Create and Continue**8. **Role:** Skip (we'll handle permissions manually)
9. Click **Done**

### 2. Create and Download Key
1. Click on your new service account2Go to **Keys** tab
3 Click **Add Key** > **Create new key**
4. Choose **JSON**5. Click **Create** - this downloads the key file6ame it to `service_account_key.json`
7. Place it in your `PathwaysUpdate/` directory

### 3. Get Service Account Email1he service account details, copy the **Email** 
   - Looks like: `pathways-drive-service@your-project.iam.gserviceaccount.com`

### 4. Set Up Google Drive File (IMPORTANT)

**You must create the file in YOUR personal Google Drive and share it with the service account:**

1. **Create the CSV file in your personal Google Drive:**
   - Go to [Google Drive](https://drive.google.com)
   - Create a new Google Sheets file or upload a CSV
   - Name it `pathways_data.csv`
   - Right-click the file > **Share**

2. **Share with the service account:**
   - Add the service account email: `pathways-drive-service@your-project.iam.gserviceaccount.com`
   - Give it **Editor** permissions
   - Click **Send** (uncheck Notify people")
3*Alternative: Make file public (for easier collaboration):**
   - Right-click the file > **Share**
   - Click **Change to anyone with the link**
   - Set to **Editor**
   - Click **Done**

###5 Update the App to Use Your File

The app needs to know which file to use. You have two options:

**Option A: Let the app find the file by name**
- Make sure your file is named exactly `pathways_data.csv`
- The app will search for it in your shared files

**Option B: Specify the file ID directly**
- Get the file ID from the Google Drive URL
- Update the app code to use that specific file ID

###6. Test the Setup

```bash
python3 test_gdrive_connection.py
```

You should see:
```
✅ service_account_key.json found
✅ Google Drive manager imported successfully
✅ Service account authentication successful
✅ Found existing file: pathways_data.csv (ID:1..)
✅ Google Drive connection successful!
```

### 7. Deploy to Web

1. **Upload to your hosting platform:**
   - `streamlit_gdrive_app.py`
   - `google_drive_manager.py`
   - `image_cache_manager.py`
   - `service_account_key.json` (keep this secure!)
   - `requirements_gdrive.txt`
   - `animal_images_cache.json`

2. **Set environment variables** (if needed):
   - Some platforms require you to set the service account key as an environment variable
   - Check your hosting platforms documentation

## Security Notes

- **Keep `service_account_key.json` secure**: Don't commit it to public repositories
- **Limited permissions**: The service account only has access to files you explicitly share with it
- **File ownership**: Files remain in your personal Google Drive, service account just has access

## Troubleshooting

###Service Accounts do not have storage quota"
- **Solution**: Create the file in your personal Google Drive and share it with the service account
- Make sure the file is shared with the service account email

### "service_account_key.json not found"
- Make sure the file is in the same directory as your app
- Check the filename spelling

### "Service account authentication failed"
- Verify the JSON key file is valid
- Check that Google Drive API is enabled in your project

### "File not found" or Permission denied"
- Make sure the service account has access to the Google Drive file
- Check file sharing permissions
- Verify the file name is exactly `pathways_data.csv`

### Deployment Issues
- Some platforms require the service account key to be set as an environment variable
- Check your hosting platform's documentation for Google API setup

## File Structure After Setup

```
PathwaysUpdate/
├── streamlit_gdrive_app.py      # Main app (uses service account)
├── google_drive_manager.py      # Updated for service accounts
├── service_account_key.json     # Your service account key
├── image_cache_manager.py       # Image cache management
├── build_cache.py               # Build image cache
├── animal_images_cache.json     # Cached images
├── requirements_gdrive.txt      # Dependencies
├── test_gdrive_connection.py    # Test script
└── README.md                    # Updated documentation
```

## Benefits of This Approach

- ✅ **No user authentication required**
- ✅ **Works immediately on web deployment**
- ✅ **No browser redirects or OAuth flows**
- ✅ **Secure and isolated permissions**
- ✅ **Perfect for public web apps**
- ✅ **No monthly costs**
- ✅ **Uses your existing Google Drive storage**

Your app is now ready for web deployment! 