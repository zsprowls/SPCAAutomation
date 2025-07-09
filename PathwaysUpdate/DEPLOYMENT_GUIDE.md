# Pathways Viewer - Deployment Guide

## 🚀 **Recommended: Streamlit Cloud (Free)**

### **Step 1: Prepare Your Repositories**

#### **Public Repository (SPCAAutomation)**
Keep your current repository public and ensure these files are accessible:
```
SPCAAutomation/
├── __Load Files Go Here__/
│   ├── AnimalInventory.csv
│   ├── Pathways for Care.csv
│   └── ... (other CSV files)
└── README.md
```

#### **Private Repository (pathways-viewer)**
Create a new private repository with these files:
```
pathways-viewer/
├── streamlit_app_new.py (rename to app.py)
├── image_cache_manager.py
├── animal_images_cache.json
├── config.py
├── requirements_streamlit_deploy.txt (rename to requirements.txt)
└── README.md
```

### **Step 2: Update Configuration**

1. **Edit `streamlit_app_new.py`:**
   - Replace `YOUR_USERNAME` with your actual GitHub username
   - Update the repository name if different

```python
PUBLIC_REPO_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/SPCAAutomation/main"
```

2. **Rename files for deployment:**
   ```bash
   mv streamlit_app_new.py app.py
   mv requirements_streamlit_deploy.txt requirements.txt
   ```

### **Step 3: Deploy to Streamlit Cloud**

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure:**
   - **Repository:** `your-username/pathways-viewer`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** `pathways-viewer` (or your preferred name)
5. **Click "Deploy"**

### **Step 4: Configure Secrets (Optional)**

If you need to add any API keys or sensitive data:
1. Go to your app settings in Streamlit Cloud
2. Add secrets in the "Secrets" section

## 🔧 **Alternative: Render (Free)**

### **Step 1: Create render.yaml**
```yaml
services:
  - type: web
    name: pathways-viewer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
```

### **Step 2: Deploy**
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Configure as above
4. Deploy

## 🔧 **Alternative: Railway (Free with $5 credit)**

### **Step 1: Deploy**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Deploy automatically

## 📊 **Repository Structure**

### **Public Repo (SPCAAutomation)**
```
├── __Load Files Go Here__/
│   ├── AnimalInventory.csv          # ✅ Public
│   ├── Pathways for Care.csv        # ✅ Public
│   └── ... (other CSV files)
├── README.md
└── ... (other public files)
```

### **Private Repo (pathways-viewer)**
```
├── app.py                           # ✅ Private (main app)
├── image_cache_manager.py           # ✅ Private
├── animal_images_cache.json         # ✅ Private (20KB cache)
├── config.py                        # ✅ Private
├── requirements.txt                 # ✅ Private
└── README.md                        # ✅ Private
```

## 🔒 **Security Considerations**

### **What's Public:**
- ✅ CSV data files (animal information)
- ✅ Basic animal details
- ✅ Location and status information

### **What's Private:**
- ✅ Image cache (contains PetPoint URLs)
- ✅ App configuration
- ✅ Source code
- ✅ Deployment credentials

### **Data Flow:**
1. **Public repo** → CSV files accessible via GitHub raw URLs
2. **Private app** → Loads data from public repo
3. **Private app** → Uses private image cache
4. **Users** → Access app via Streamlit Cloud

## 🚀 **Quick Start Commands**

### **Local Testing:**
```bash
# Test the Streamlit app locally
cd PathwaysUpdate
streamlit run streamlit_app_new.py
```

### **Deployment Prep:**
```bash
# Create deployment files
cp streamlit_app_new.py app.py
cp requirements_streamlit_deploy.txt requirements.txt

# Update GitHub username in app.py
# Then push to private repo
```

## 📈 **Performance Optimizations**

### **Caching Strategy:**
- **CSV data:** Cached for 1 hour (GitHub rate limits)
- **Image cache:** Pre-built and included in repo
- **Session state:** Maintains user preferences

### **Data Loading:**
- **Lazy loading:** Only loads data when needed
- **Error handling:** Graceful fallbacks
- **Progress indicators:** Shows loading status

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Data not loading:**
   - Check GitHub repository URL
   - Verify CSV files are in correct location
   - Check GitHub raw URL accessibility

2. **Images not showing:**
   - Verify `animal_images_cache.json` is included
   - Check cache file format
   - Ensure image URLs are still valid

3. **Deployment fails:**
   - Check requirements.txt
   - Verify file names (app.py, requirements.txt)
   - Check Streamlit Cloud logs

### **Debug Mode:**
```python
# Add to app.py for debugging
st.write("Debug info:", st.session_state.df.head() if st.session_state.df is not None else "No data")
```

## 🎯 **Next Steps**

1. **Choose deployment platform** (Streamlit Cloud recommended)
2. **Create private repository** for the app
3. **Update configuration** with your GitHub username
4. **Deploy and test**
5. **Share the URL** with your team

## 📞 **Support**

- **Streamlit Cloud:** [docs.streamlit.io](https://docs.streamlit.io)
- **GitHub:** [github.com](https://github.com)
- **Render:** [render.com/docs](https://render.com/docs)
- **Railway:** [railway.app/docs](https://railway.app/docs) 