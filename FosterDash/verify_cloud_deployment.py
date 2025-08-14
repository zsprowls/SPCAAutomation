#!/usr/bin/env python3
"""
Verification script to check if cloud database is ready for text-based medications
Run this after completing the migration to verify everything is working
"""

import streamlit as st
from supabase_manager import supabase_manager

def verify_cloud_database():
    """Verify that the cloud database is properly migrated"""
    st.title("✅ Cloud Database Verification")
    st.write("This script verifies that your cloud database is ready for text-based medications.")
    
    # Check if Supabase is configured
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    supabase_key = st.secrets.get("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        st.error("❌ Supabase credentials not configured.")
        st.info("Please set up your Supabase credentials in .streamlit/secrets.toml first.")
        return False
    
    # Initialize Supabase
    if not supabase_manager.initialize(supabase_url, supabase_key):
        st.error("❌ Failed to connect to Supabase")
        return False
    
    st.success("✅ Connected to Supabase")
    
    # Check database schema
    st.subheader("🔍 Database Schema Check")
    
    try:
        # Check if onmeds column accepts text
        test_animal = "VERIFICATION_TEST_123"
        
        # Try to insert a text value
        test_result = supabase_manager.client.table('foster_animals').upsert({
            'animalnumber': test_animal,
            'onmeds': 'Test medication - Amoxicillin 250mg twice daily',
            'fosternotes': 'Verification test record',
            'fosterpleadates': [],
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }).execute()
        
        if test_result.data:
            st.success("✅ Database accepts text-based medication entries")
            
            # Clean up test record
            supabase_manager.client.table('foster_animals').delete().eq('animalnumber', test_animal).execute()
            st.info("🧹 Test record cleaned up")
            
            # Check existing data
            st.subheader("📊 Existing Data Check")
            result = supabase_manager.client.table('foster_animals').select('onmeds').limit(10).execute()
            
            if result.data:
                st.write("**Sample medication entries:**")
                for i, row in enumerate(result.data[:5]):
                    meds_value = row.get('onmeds', 'NULL')
                    if meds_value:
                        st.write(f"- Record {i+1}: `{meds_value}`")
                    else:
                        st.write(f"- Record {i+1}: (empty)")
                
                # Check for any remaining boolean values
                boolean_count = sum(1 for row in result.data if isinstance(row.get('onmeds'), bool))
                if boolean_count > 0:
                    st.warning(f"⚠️ Found {boolean_count} records with boolean values. Migration may be incomplete.")
                else:
                    st.success("✅ All checked records have text-based medication entries")
            else:
                st.info("ℹ️ No medication data found to verify")
            
            return True
        else:
            st.error("❌ Database does not accept text-based medication entries")
            return False
            
    except Exception as e:
        st.error(f"❌ Verification failed: {str(e)}")
        st.info("This usually means the database schema hasn't been updated yet.")
        return False

def show_deployment_status():
    """Show deployment readiness status"""
    st.subheader("🚀 Deployment Status")
    
    # Check if we can connect and verify
    if verify_cloud_database():
        st.success("🎉 **READY FOR DEPLOYMENT!**")
        st.write("Your cloud database is properly configured for text-based medications.")
        
        st.info("**Next steps:**")
        st.write("1. ✅ Database migration completed")
        st.write("2. ✅ Schema updated to TEXT")
        st.write("3. ✅ Text entries working")
        st.write("4. 🚀 Deploy your updated code to Streamlit Cloud")
        
        st.balloons()
        
    else:
        st.error("❌ **NOT READY FOR DEPLOYMENT**")
        st.write("Your cloud database needs to be migrated first.")
        
        st.warning("**Required actions:**")
        st.write("1. Run the migration script: `streamlit run migrate_onmeds_to_text.py`")
        st.write("2. Follow the cloud migration guide")
        st.write("3. Run this verification script again")
        st.write("4. Deploy only after verification passes")

def show_test_instructions():
    """Show how to test the new medication field"""
    st.subheader("🧪 Testing Instructions")
    
    st.write("**After deploying to Streamlit Cloud, test these features:**")
    
    test_items = [
        ("📝 **Foster Notes**", "Verify you can edit and save foster notes"),
        ("💊 **Medication Field**", "Try entering medication details like 'Amoxicillin 250mg twice daily'"),
        ("📅 **Foster Plea Dates**", "Test adding and removing foster plea dates"),
        ("🔄 **Data Persistence**", "Refresh the page and verify your entries are saved"),
        ("📊 **Display**", "Check that medication text displays correctly in the dashboard")
    ]
    
    for test_name, test_desc in test_items:
        st.markdown(f"**{test_name}**")
        st.write(test_desc)
        st.write("")

def main():
    st.set_page_config(
        page_title="Cloud Database Verification",
        page_icon="✅",
        layout="wide"
    )
    
    # Main verification
    show_deployment_status()
    
    # Show testing instructions
    with st.expander("🧪 Testing Instructions", expanded=False):
        show_test_instructions()
    
    # Show troubleshooting
    with st.expander("🔧 Troubleshooting", expanded=False):
        st.write("**Common issues and solutions:**")
        
        issues = [
            ("**Migration failed**", "Check your Supabase permissions and try running the migration SQL manually"),
            ("**Text not saving**", "Verify the database schema was updated to TEXT type"),
            ("**Connection errors**", "Check your Streamlit Cloud environment variables and Supabase credentials"),
            ("**Data not displaying**", "Ensure the foster dashboard code was updated and deployed")
        ]
        
        for issue, solution in issues:
            st.markdown(f"**{issue}**")
            st.write(solution)
            st.write("")

if __name__ == "__main__":
    main()
