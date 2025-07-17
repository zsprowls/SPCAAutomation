# Streamlit Cloud Deployment Guide

This guide explains how to deploy the Pathways for Care app to Streamlit Cloud while keeping your service account credentials secure.

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at https://share.streamlit.io/
3. **Google Service Account**: Already set up (see README.md)

## Deployment Steps

### 1. Push Your Code to GitHub

Make sure your code is pushed to GitHub. The `service_account_key.json` file should NOT be in the repository (it's excluded by `.gitignore`).

### 2. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click **"New app"**
4. **Repository**: Select your repository
5. **Branch**: `main` (or your default branch)
6. **Main file path**: `PathwaysUpdate/streamlit_gdrive_app.py`
7. Click **"Deploy!"**

### 3. Configure Streamlit Secrets

After deployment, you need to add your service account credentials as secrets:

1. In your Streamlit Cloud dashboard, click on your app
2. Go to **"Settings"** → **"Secrets"**
3. Add this configuration:

```toml
[service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### 4. Get Your Service Account JSON

To get the values for the secrets:

1. Open your `service_account_key.json` file
2. Copy the entire JSON content
3. Convert it to TOML format (or use the format above)

**Quick Method**: Copy your JSON and replace the values in the template above.

### 5. Test the Deployment

1. Go back to your app URL
2. The app should now work with the service account credentials from secrets
3. Test adding welfare notes or changing dropdown values

## Security Benefits

- ✅ **No credentials in code**: Service account key is not in your repository
- ✅ **Environment-specific**: Different secrets for different deployments
- ✅ **Access control**: Only you can see/edit the secrets
- ✅ **Automatic rotation**: Easy to update credentials without code changes

## Troubleshooting

### "Service account not found" error
- Check that the secrets are properly formatted
- Verify the service account email is correct
- Make sure the Google Sheet is shared with the service account

### "Permission denied" error
- Ensure the service account has Editor access to the Google Sheet
- Check that the Google Drive and Sheets APIs are enabled

### "Invalid JWT Signature" error
- Verify the private key is copied correctly (including newlines)
- Make sure there are no extra spaces or characters

## Alternative: Environment Variables

If you prefer environment variables, you can also set:

```bash
GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```

And update the code to read from `os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')`.

## Local Development vs Production

- **Local**: Uses `service_account_key.json` file
- **Production**: Uses Streamlit secrets
- **Code**: Automatically detects which method to use

This setup allows you to develop locally with the file and deploy securely with secrets! 