#!/usr/bin/env python3
"""
Test script for Supabase integration with Foster Dashboard
"""

import streamlit as st
import pandas as pd
from supabase_manager import supabase_manager
import os

def test_supabase_connection():
    """Test basic Supabase connection"""
    st.title("🧪 Supabase Integration Test")
    
    # Check if secrets are available
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    supabase_key = st.secrets.get("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        st.error("❌ Supabase credentials not found in secrets")
        st.info("Please add SUPABASE_URL and SUPABASE_KEY to your Streamlit secrets")
        return False
    
    st.info(f"✅ Found Supabase URL: {supabase_url[:30]}...")
    st.info(f"✅ Found Supabase Key: {supabase_key[:20]}...")
    
    # Test connection
    if supabase_manager.initialize(supabase_url, supabase_key):
        st.success("✅ Successfully connected to Supabase")
        return True
    else:
        st.error("❌ Failed to connect to Supabase")
        return False

def test_table_operations():
    """Test basic table operations"""
    st.subheader("📊 Testing Table Operations")
    
    # Test reading from table
    try:
        result = supabase_manager.client.table('foster_animals').select('*').limit(5).execute()
        st.success(f"✅ Successfully read {len(result.data)} records from foster_animals table")
        
        if result.data:
            st.write("**Sample data:**")
            st.json(result.data[0])
        
        return True
    except Exception as e:
        st.error(f"❌ Error reading from table: {str(e)}")
        return False

def test_animal_sync():
    """Test animal number synchronization"""
    st.subheader("🔄 Testing Animal Sync")
    
    # Create sample animal inventory data
    sample_data = pd.DataFrame({
        'AnimalNumber': ['A00123456', 'A00123457', 'A00123458'],
        'AnimalName': ['Test Animal 1', 'Test Animal 2', 'Test Animal 3'],
        'Species': ['Dog', 'Cat', 'Dog']
    })
    
    st.write("**Sample AnimalInventory data:**")
    st.dataframe(sample_data)
    
    # Test sync
    if supabase_manager.sync_animal_numbers(sample_data):
        st.success("✅ Animal sync test completed")
        return True
    else:
        st.error("❌ Animal sync test failed")
        return False

def test_crud_operations():
    """Test CRUD operations"""
    st.subheader("✏️ Testing CRUD Operations")
    
    test_animal = "A00123456"
    
    # Test updating foster notes
    if supabase_manager.update_foster_notes(test_animal, "Test notes from integration test"):
        st.success("✅ Foster notes update test passed")
    else:
        st.error("❌ Foster notes update test failed")
        return False
    
    # Test updating OnMeds
    if supabase_manager.update_on_meds(test_animal, True):
        st.success("✅ OnMeds update test passed")
    else:
        st.error("❌ OnMeds update test failed")
        return False
    
    # Test adding foster plea date
    if supabase_manager.add_foster_plea_date(test_animal, "2024-01-15"):
        st.success("✅ Foster plea date add test passed")
    else:
        st.error("❌ Foster plea date add test failed")
        return False
    
    # Test getting animal data
    animal_data = supabase_manager.get_animal_data(test_animal)
    if animal_data:
        st.success("✅ Get animal data test passed")
        st.write("**Retrieved data:**")
        st.json(animal_data)
    else:
        st.error("❌ Get animal data test failed")
        return False
    
    return True

def main():
    st.set_page_config(page_title="Supabase Test", page_icon="🧪")
    
    st.markdown("""
    # 🧪 Supabase Integration Test
    
    This script tests the Supabase integration for the Foster Dashboard.
    """)
    
    # Run tests
    tests = [
        ("Connection Test", test_supabase_connection),
        ("Table Operations", test_table_operations),
        ("Animal Sync", test_animal_sync),
        ("CRUD Operations", test_crud_operations)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        st.markdown(f"---")
        st.markdown(f"### {test_name}")
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            st.error(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    st.markdown("---")
    st.markdown("## 📋 Test Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        st.success(f"🎉 All {total} tests passed!")
    else:
        st.error(f"❌ {total - passed} out of {total} tests failed")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        st.write(f"- {test_name}: {status}")

if __name__ == "__main__":
    main() 