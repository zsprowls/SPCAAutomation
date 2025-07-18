# Fix Google Sheets Update Issue

## The Problem
You're currently using an API key for authentication, but **API keys only allow read access**. To update Google Sheets, you need **Service Account authentication** with proper permissions.

## The Solution
Set up a Google Service Account with Editor permissions on your Google Sheet.

## Step-by-Step Fix

### 1. Create a Google Service Account

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Select your project (or create a new one)

2. **Enable Required APIs:**
   - Go to "APIs & Services" > "Library"
   - Search for and enable:
     - **Google Drive API**
     - **Google Sheets API**

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - **Name:** `pathways-drive-service`
   - **Description:** `Service account for Pathways for Care Google Drive access`
   - Click "Create and Continue"
   - Skip role assignment (we'll handle permissions manually)
   - Click "Done"

4. **Create and Download Key:**
   - Click on your new service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON"
   - Click "Create" - this downloads the key file
   - **Rename it to `service_account_key.json`**
   - **Place it in your `PathwaysUpdate/` directory**

### 2. Get Your Service Account Email

1. In the service account details, copy the **Email**
   - Looks like: `pathways-drive-service@your-project.iam.gserviceaccount.com`
   - **Save this email - you'll need it for sharing**

### 3. Share Your Google Sheet

1. **Open your Google Sheet:**
   - Go to: https://docs.google.com/spreadsheets/d/1IDixZ49uXsCQsAdjZkVAm_6vcSNU0uehiUm7Wc2JRWQ

2. **Share with Service Account:**
   - Click "Share" button (top right)
   - Add the service account email: `pathways-drive-service@your-project.iam.gserviceaccount.com`
   - **Set permission to "Editor"** (this is crucial!)
   - Uncheck "Notify people"
   - Click "Send"

### 4. Test the Setup

Run the test script to verify everything works:

```bash
cd PathwaysUpdate
python3 test_update_functionality.py
```

You should see:
```
✅ service_account_key.json found
✅ Authentication successful
✅ Successfully read X records
✅ Update test successful!
🎉 All tests passed! Update functionality should work.
```

### 5. Update Your Streamlit App

Your app is already configured to use service account authentication. The key changes are in your `streamlit_gdrive_app_new.py`:

```python
# This line already uses service account authentication
manager = get_gdrive_manager(use_service_account=True)

# This method uses service account for updates
success = manager.update_animal_record_with_api_key(aid, foster_value, transfer_value, communications_value, new_note)
```

## Common Issues and Solutions

### ❌ "service_account_key.json not found"
- Make sure you downloaded the JSON key file
- Rename it to exactly `service_account_key.json`
- Place it in the `PathwaysUpdate/` directory

### ❌ "Authentication failed"
- Check that the JSON key file is valid
- Verify Google Drive API and Google Sheets API are enabled
- Make sure you're using the correct project

### ❌ "Permission denied" or "File not found"
- **Most common issue:** The Google Sheet isn't shared with the service account
- Add the service account email to the sheet's sharing settings
- **Give it "Editor" permissions** (not Viewer)

### ❌ "Update test failed"
- Check that the service account has Editor permissions
- Verify the Google Sheet contains the expected columns
- Make sure the AID column exists and contains valid data

## Security Notes

- ✅ **Keep `service_account_key.json` secure** - don't commit it to public repositories
- ✅ **Limited permissions** - the service account only has access to files you explicitly share
- ✅ **File ownership** - files remain in your personal Google Drive

## After Setup

Once everything is working:

1. **Test the app:**
   ```bash
   streamlit run streamlit_gdrive_app_new.py
   ```

2. **Try updating a record** in the app to verify it works

3. **For web deployment:** Add the service account key to your hosting platform's secrets/environment variables

## Why This Fixes the Issue

- **API Keys** = Read-only access
- **Service Accounts** = Full access (read/write) when properly shared
- **Editor permissions** = Required for updating Google Sheets

Your app will now be able to both read from and write to Google Sheets using the service account authentication! 