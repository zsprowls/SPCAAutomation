# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

1. **Upload Files to GitHub:**
   - Upload `rodent_dashboard.py` to your GitHub repository
   - Upload `requirements.txt` to the same repository
   - Upload your CSV files to the repository root or a subdirectory

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to: `rodent_dashboard.py`
   - Click "Deploy"

## File Structure for Deployment

Your repository should look like this:
```
your-repo/
├── rodent_dashboard.py
├── requirements.txt
├── RodentIntake.csv
├── FosterCurrent.csv
├── AnimalInventory.csv
└── AnimalOutcome.csv
```

## Troubleshooting

- **File not found errors:** Make sure all CSV files are in the repository root
- **Path issues:** The app now tries multiple path locations automatically
- **Dependencies:** All required packages are listed in requirements.txt

## Local Testing

To test locally before deployment:
```bash
streamlit run rodent_dashboard.py
``` 