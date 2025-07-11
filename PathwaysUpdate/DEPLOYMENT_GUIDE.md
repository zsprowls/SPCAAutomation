# Pathways for Care Viewer - Streamlit App Deployment Guide

## 🚀 Quick Start

### Local Development
1. **Install dependencies:**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run streamlit_pathways_viewer.py
   ```

3. **Open in browser:**
   - The app will automatically open at `http://localhost:8501`
   - Or manually navigate to the URL shown in the terminal

## ☁️ Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended)
1. **Push to GitHub:**
   - Create a GitHub repository
   - Push your code including:
     - `streamlit_pathways_viewer.py`
     - `image_cache_manager.py`
     - `requirements_streamlit.txt`
     - `animal_images_cache.json`
     - `__Load Files Go Here__/` folder with CSV files

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to: `streamlit_pathways_viewer.py`
   - Deploy!

### Option 2: Railway
1. **Create `railway.json`:**
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "streamlit run streamlit_pathways_viewer.py --server.port $PORT --server.address 0.0.0.0",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

2. **Deploy:**
   - Connect your GitHub repo to Railway
   - Railway will automatically detect and deploy your Streamlit app

### Option 3: Render
1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: pathways-viewer
       env: python
       buildCommand: pip install -r requirements_streamlit.txt
       startCommand: streamlit run streamlit_pathways_viewer.py --server.port $PORT --server.address 0.0.0.0
   ```

2. **Deploy:**
   - Connect your GitHub repo to Render
   - Render will automatically deploy your app

## 📁 File Structure
```
PathwaysUpdate/
├── streamlit_pathways_viewer.py      # Main Streamlit app
├── image_cache_manager.py            # Image caching functionality
├── requirements_streamlit.txt        # Python dependencies
├── animal_images_cache.json          # Cached image data
├── __Load Files Go Here__/           # CSV data files
│   ├── Pathways for Care.csv
│   └── AnimalInventory.csv
└── DEPLOYMENT_GUIDE.md              # This file
```

## 🔧 Configuration

### Environment Variables (Optional)
- `STREAMLIT_SERVER_PORT`: Custom port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: localhost)

### Customization
- **App Title:** Edit `page_title` in `st.set_page_config()`
- **Styling:** Modify the CSS in the `st.markdown()` section
- **Data Sources:** Update file paths in `load_data()` function

## 🐛 Troubleshooting

### Common Issues:
1. **Port already in use:**
   ```bash
   streamlit run streamlit_pathways_viewer.py --server.port 8502
   ```

2. **CSV file not found:**
   - Ensure `__Load Files Go Here__/` folder exists
   - Check file paths are correct for your system

3. **Image cache issues:**
   - Delete `animal_images_cache.json` to rebuild cache
   - Check internet connection for image loading

4. **Dependencies missing:**
   ```bash
   pip install --upgrade -r requirements_streamlit.txt
   ```

## 📊 Features
- ✅ **Record Browser:** View individual animal records
- ✅ **Spreadsheet View:** Filter and view all data
- ✅ **CSV Editing:** Save changes back to CSV files
- ✅ **Image/Video Support:** Display animal media
- ✅ **Search & Navigation:** Find animals by AID or name
- ✅ **Data Refresh:** Reload from CSV files
- ✅ **Responsive Design:** Works on desktop and mobile

## 🔒 Security Notes
- The app saves changes directly to CSV files
- Ensure proper file permissions on your CSV files
- Consider backing up your data before making changes
- For production, consider adding authentication

## 📈 Performance Tips
- Image cache reduces loading times
- Use filters in Spreadsheet View for large datasets
- Refresh data only when needed
- Close unused browser tabs to free memory

## 🆘 Support
If you encounter issues:
1. Check the terminal output for error messages
2. Verify all required files are present
3. Ensure Python dependencies are installed
4. Try clearing the browser cache
5. Restart the Streamlit app 