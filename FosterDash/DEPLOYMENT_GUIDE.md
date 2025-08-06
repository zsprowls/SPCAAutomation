# 🚀 Streamlit Cloud Deployment Guide

## Step 1: Prepare Your Repository

1. **Create a new GitHub repository** (if you haven't already)
2. **Push your code** to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

## Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure your app:**
   - **Repository**: `YOUR_USERNAME/YOUR_REPO_NAME`
   - **Branch**: `main`
   - **Main file path**: `foster_dashboard.py`
   - **App URL**: Choose a custom URL (optional)

## Step 3: Add Streamlit Secrets

1. **In your Streamlit Cloud dashboard**, go to your app
2. **Click "Settings"** → **"Secrets"**
3. **Add your Supabase credentials:**
   ```toml
   SUPABASE_URL = "https://xfhmrxpiupwkahmtlubd.supabase.co"
   SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmaG1yeHBpdXB3a2FobXRsdWJkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0Mzg5MzMsImV4cCI6MjA3MDAxNDkzM30.Lx9N35iu-rkg4jZamfNpGOOyoMS0vE2umT_Zw-7qy7c"
   ```

## Step 4: Add Data Files

Since the data files are in `../__Load Files Go Here__/`, you'll need to either:

**Option A: Copy files to the repo**
```bash
cp -r ../__Load\ Files\ Go\ Here__/ ./data/
```

**Option B: Use Streamlit's file uploader** (modify the app to accept file uploads)

## Step 5: Test Your Deployment

1. **Wait for deployment** (usually 1-2 minutes)
2. **Check the logs** for any errors
3. **Test the database connection**
4. **Test the interactive features**

## Troubleshooting

### Common Issues:
- **"Module not found"**: Check `requirements.txt` has all dependencies
- **"Secrets not found"**: Verify secrets are added in Streamlit Cloud
- **"Data files not found"**: Make sure data files are in the repository

### Debug Commands:
```bash
# Check if all files are committed
git status

# Verify requirements.txt
cat requirements.txt

# Test local deployment
streamlit run foster_dashboard.py
```

## Next Steps

Once deployed:
1. **Test database connection**
2. **Test interactive editing**
3. **Share the URL** with your team
4. **Set up automatic deployments** from your main branch

🎉 **Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`**
