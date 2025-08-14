#!/usr/bin/env python3
"""
Migration script to update the onmeds column from BOOLEAN to TEXT
Run this script if you have an existing database with the old schema
Handles both local and cloud database migrations
"""

import streamlit as st
from supabase_manager import supabase_manager
import os

def check_database_status():
    """Check the status of both local and cloud databases"""
    st.subheader("🔍 Database Status Check")
    
    # Check if Supabase is configured
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    supabase_key = st.secrets.get("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        st.error("❌ Supabase credentials not configured.")
        st.info("Please set up your Supabase credentials in .streamlit/secrets.toml first.")
        return False, None, None
    
    # Initialize Supabase
    if not supabase_manager.initialize(supabase_url, supabase_key):
        st.error("❌ Failed to connect to Supabase")
        return False, None, None
    
    st.success("✅ Connected to Supabase")
    
    # Check current column type by examining data
    try:
        result = supabase_manager.client.table('foster_animals').select('onmeds').limit(10).execute()
        
        if result.data:
            # Check if any values are boolean
            has_boolean_values = any(isinstance(row.get('onmeds'), bool) for row in result.data)
            
            if has_boolean_values:
                st.warning("⚠️ Found boolean values in onmeds column. Migration needed.")
                return True, True, result.data
            else:
                st.success("✅ onmeds column is already TEXT type. No migration needed.")
                return True, False, result.data
        else:
            st.info("ℹ️ No data found in foster_animals table. Column type will be set when first record is created.")
            return True, False, []
            
    except Exception as e:
        st.error(f"❌ Error checking schema: {str(e)}")
        return False, None, None

def show_migration_options(needs_migration, sample_data):
    """Show migration options based on database status"""
    st.subheader("🔄 Migration Options")
    
    if needs_migration:
        st.warning("⚠️ Your database needs migration to support text-based medications.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Run Data Migration"):
                if run_data_migration(sample_data):
                    st.success("✅ Data migration completed successfully!")
                    st.balloons()
                else:
                    st.error("❌ Data migration failed")
        
        with col2:
            if st.button("📋 Show Migration SQL"):
                show_migration_sql()
        
        with col3:
            if st.button("🌐 Cloud Migration Guide"):
                show_cloud_migration_guide()
        
        # Show current data sample
        if sample_data:
            st.subheader("📊 Current Data Sample")
            st.write("**Sample onmeds values before migration:**")
            for i, row in enumerate(sample_data[:5]):
                meds_value = row.get('onmeds', 'NULL')
                st.write(f"- Record {i+1}: `{meds_value}` (Type: {type(meds_value).__name__})")
    
    else:
        st.success("✅ Your database is already up to date!")
        st.info("You can now use text-based medication entries in the foster dashboard.")

def run_data_migration(sample_data):
    """Run the data migration (converts boolean values to text)"""
    try:
        st.info("🔄 Starting data migration...")
        
        # Step 1: Convert boolean values to text
        st.write("Step 1: Converting boolean values to text...")
        
        # Get all records with boolean onmeds values
        result = supabase_manager.client.table('foster_animals').select('id,onmeds').execute()
        
        if result.data:
            updates_made = 0
            for row in result.data:
                if isinstance(row.get('onmeds'), bool):
                    # Convert boolean to text
                    new_value = "Yes" if row['onmeds'] else "No"
                    
                    # Update the record
                    supabase_manager.client.table('foster_animals').update({
                        'onmeds': new_value
                    }).eq('id', row['id']).execute()
                    
                    updates_made += 1
            
            st.success(f"✅ Converted {updates_made} boolean values to text")
        
        # Step 2: Show next steps
        st.write("Step 2: Schema update required")
        st.warning("⚠️ Data migration completed, but column type still needs to be updated.")
        st.info("📝 Please run the SQL commands shown in the 'Show Migration SQL' section.")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Migration failed: {str(e)}")
        return False

def show_migration_sql():
    """Show the migration SQL for manual execution"""
    st.subheader("📋 Migration SQL")
    st.write("**Run this SQL in your Supabase SQL Editor to complete the migration:**")
    
    migration_sql = """
-- Migration SQL for onmeds column
-- This will convert the onmeds column from BOOLEAN to TEXT

-- Step 1: Convert existing boolean values to text (already done by data migration)
-- UPDATE foster_animals 
-- SET "onmeds" = CASE 
--     WHEN "onmeds" = true THEN 'Yes'
--     WHEN "onmeds" = false THEN 'No'
--     ELSE ''
-- END;

-- Step 2: Alter column type (REQUIRED for cloud deployment)
ALTER TABLE foster_animals 
ALTER COLUMN "onmeds" TYPE TEXT;

-- Step 3: Set default value
ALTER TABLE foster_animals 
ALTER COLUMN "onmeds" SET DEFAULT '';

-- Step 4: Verify the change
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'foster_animals' 
AND column_name = 'onmeds';
    """
    
    st.code(migration_sql, language="sql")
    
    st.info("💡 After running this SQL:")
    st.write("1. Your onmeds column will accept any text")
    st.write("2. Existing 'Yes'/'No' values will remain")
    st.write("3. You can now enter specific medication details")
    st.write("4. Your Streamlit Cloud app will work with the new field")

def show_cloud_migration_guide():
    """Show comprehensive cloud migration guide"""
    st.subheader("🌐 Cloud Migration Guide")
    
    st.write("""
    This guide will help you migrate your **cloud Supabase database** (the one your Streamlit Cloud app connects to).
    """)
    
    # Step-by-step guide
    st.markdown("### 📋 Step-by-Step Instructions")
    
    steps = [
        ("1. **Access Your Supabase Project**", "Go to https://supabase.com and log into your project"),
        ("2. **Open SQL Editor**", "Click 'SQL Editor' in the left sidebar"),
        ("3. **Run Migration SQL**", "Copy and paste the SQL from the 'Show Migration SQL' section"),
        ("4. **Verify Changes**", "Check that the onmeds column is now TEXT type"),
        ("5. **Test Your App**", "Deploy your updated code to Streamlit Cloud")
    ]
    
    for step_title, step_desc in steps:
        st.markdown(f"**{step_title}**")
        st.write(step_desc)
        st.write("")
    
    # Common issues and solutions
    st.markdown("### ⚠️ Common Issues & Solutions")
    
    issues = [
        ("**Permission Denied**", "Make sure you're logged in as the project owner or have admin privileges"),
        ("**Column Already Exists**", "This means the migration was already run - you're good to go!"),
        ("**Table Not Found**", "Make sure you're in the correct project and the foster_animals table exists"),
        ("**Connection Errors**", "Check your internet connection and try refreshing the page")
    ]
    
    for issue, solution in issues:
        st.markdown(f"**{issue}**")
        st.write(solution)
        st.write("")
    
    # Verification
    st.markdown("### ✅ Verification Steps")
    
    verification_sql = """
-- Run this to verify your migration was successful
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'foster_animals' 
AND column_name = 'onmeds';

-- Expected result:
-- column_name | data_type | column_default | is_nullable
-- onmeds      | text      | ''             | YES
    """
    
    st.write("**Run this verification SQL after migration:**")
    st.code(verification_sql, language="sql")

def show_deployment_checklist():
    """Show deployment checklist for Streamlit Cloud"""
    st.subheader("🚀 Streamlit Cloud Deployment Checklist")
    
    st.write("**Before deploying to Streamlit Cloud, ensure:**")
    
    checklist_items = [
        "✅ Local database migration completed",
        "✅ Cloud Supabase schema updated (SQL migration run)",
        "✅ Code changes committed and pushed to git",
        "✅ Streamlit Cloud connected to correct Supabase project",
        "✅ Environment variables configured in Streamlit Cloud"
    ]
    
    for item in checklist_items:
        st.write(item)
    
    st.write("")
    st.info("**After deployment:**")
    st.write("1. Check that the medication field accepts text input")
    st.write("2. Verify that existing medication data displays correctly")
    st.write("3. Test adding new medication entries")
    st.write("4. Confirm all foster dashboard features work as expected")

def main():
    st.set_page_config(
        page_title="OnMeds Migration",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 OnMeds Column Migration")
    st.write("This script will migrate your database to support text-based medication entries.")
    
    # Check database status
    connection_ok, needs_migration, sample_data = check_database_status()
    
    if connection_ok:
        # Show migration options
        show_migration_options(needs_migration, sample_data)
        
        # Show deployment checklist
        with st.expander("🚀 Streamlit Cloud Deployment Checklist", expanded=False):
            show_deployment_checklist()
        
        # Show current status
        st.subheader("📊 Current Status")
        if needs_migration:
            st.error("❌ **Migration Required** - Your database needs updates to support text medications")
        else:
            st.success("✅ **Ready for Deployment** - Your database supports text medications")
        
        # Show next steps
        st.subheader("📋 Next Steps")
        if needs_migration:
            st.write("1. **Complete local data migration** (use the buttons above)")
            st.write("2. **Update cloud database schema** (run SQL in Supabase)")
            st.write("3. **Deploy updated code** (push to git and deploy to Streamlit Cloud)")
        else:
            st.write("1. **Deploy your code** (push to git and deploy to Streamlit Cloud)")
            st.write("2. **Test the new medication field** in your Streamlit Cloud app")
    
    else:
        st.error("❌ Cannot proceed without database connection")
        st.info("Please check your Supabase credentials and try again.")

if __name__ == "__main__":
    main()
