# 🚀 Streamlit Cloud Deployment Guide

## Step 1: Prepare Your Repository

1. Make sure your code is in a Git repository
2. Ensure these files are in your repository:
   - foster_dashboard.py
   - supabase_manager.py
   - requirements.txt
   - .streamlit/config.toml

## Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Configure your app:
   - **Repository**: Your GitHub repo
   - **Branch**: main (or your default branch)
   - **Main file path**: FosterDash/foster_dashboard.py
   - **App URL**: Choose a unique URL

## Step 3: Configure Secrets

1. In your Streamlit Cloud app dashboard
2. Go to Settings > Secrets
3. Add this configuration:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

Replace with your actual Supabase credentials.

## Step 4: Deploy

1. Click "Deploy!" 
2. Wait for deployment to complete
3. Your app will be available at: https://your-app-name.streamlit.app

## Step 5: Test

1. Open your deployed app
2. Check that database connection works
3. Test the interactive features

## Troubleshooting

### App won't deploy:
- Check that all required files are in the repository
- Verify the main file path is correct
- Check the requirements.txt file

### Database connection fails:
- Verify Supabase credentials in Streamlit Cloud secrets
- Check that your Supabase project is active
- Ensure the foster_animals table exists

### Data not loading:
- Verify CSV files are in the correct location
- Check file permissions and paths

## Local Development vs Deployment

- **Local**: Uses .streamlit/secrets.toml
- **Deployed**: Uses Streamlit Cloud secrets
- Both use the same code, just different secret storage
