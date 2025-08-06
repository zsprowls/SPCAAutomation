# Supabase Setup Guide for Foster Dashboard

## Overview
This guide will help you set up Supabase database integration for the SPCA Foster Dashboard.

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in to your account
3. Click "New Project"
4. Choose your organization
5. Enter project details:
   - **Name**: `spca-foster-dashboard`
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to your location
6. Click "Create new project"

## Step 2: Create Database Table

Once your project is created, go to the SQL Editor and run this SQL:

```sql
-- Create the foster_animals table
CREATE TABLE foster_animals (
    id BIGSERIAL PRIMARY KEY,
    AnimalNumber TEXT UNIQUE NOT NULL,
    FosterNotes TEXT DEFAULT '',
    OnMeds BOOLEAN DEFAULT FALSE,
    FosterPleaDates JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_foster_animals_animal_number ON foster_animals(AnimalNumber);
CREATE INDEX idx_foster_animals_updated_at ON foster_animals(updated_at);

-- Enable Row Level Security (RLS)
ALTER TABLE foster_animals ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (you can restrict this later)
CREATE POLICY "Allow all operations" ON foster_animals FOR ALL USING (true);
```

## Step 3: Get API Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the following values:
   - **Project URL** (looks like: `https://your-project-id.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

## Step 4: Configure Streamlit Secrets

### For Local Development:
Create a `.streamlit/secrets.toml` file in your project root:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

### For Streamlit Cloud Deployment:
1. Go to your Streamlit app dashboard
2. Navigate to **Settings** → **Secrets**
3. Add the following:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

## Step 5: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements_foster_dashboard.txt
```

## Step 6: Test the Integration

1. Run the foster dashboard:
   ```bash
   streamlit run foster_dashboard.py
   ```

2. Check that you see:
   - ✅ Database Connected in the sidebar
   - Successfully connected to Supabase message
   - AnimalNumbers syncing with database

## Database Schema

The `foster_animals` table has the following structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key (auto-increment) |
| `AnimalNumber` | TEXT | Unique animal identifier (from PetPoint) |
| `FosterNotes` | TEXT | Editable foster notes |
| `OnMeds` | BOOLEAN | Checkbox for medication status |
| `FosterPleaDates` | JSONB | Array of foster plea dates |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

## Features Enabled

Once configured, you'll have access to:

1. **Foster Notes**: Text area for each animal
2. **On Medications**: Checkbox for medication status
3. **Foster Plea Dates**: Date picker for tracking foster requests
4. **Real-time Updates**: All changes sync immediately to Supabase
5. **Data Persistence**: All foster data is stored in the cloud

## Troubleshooting

### Connection Issues
- Verify your Supabase URL and key are correct
- Check that your project is active
- Ensure the `foster_animals` table exists

### Permission Issues
- Verify RLS policies are set correctly
- Check that your API key has the right permissions

### Data Sync Issues
- Check that AnimalInventory.csv is loading correctly
- Verify AnimalNumber column exists and has data

## Security Notes

- The current setup uses the `anon` public key for simplicity
- For production, consider using service role keys with proper RLS policies
- Regularly backup your Supabase database
- Monitor usage and costs in your Supabase dashboard 