#!/usr/bin/env python3
"""
Simple test to check Streamlit secrets
"""

import streamlit as st

def test_secrets():
    st.title("Streamlit Secrets Test")
    
    st.write("### Checking Streamlit secrets...")
    
    # Check if secrets exist
    if hasattr(st, 'secrets'):
        st.success("✅ st.secrets exists")
        
        # Show available keys
        try:
            keys = list(st.secrets.keys())
            st.write(f"**Available keys:** {keys}")
            
            if 'service_account' in st.secrets:
                st.success("✅ 'service_account' key found")
                
                # Show service account info
                sa_info = st.secrets['service_account']
                sa_keys = list(sa_info.keys())
                st.write(f"**Service account keys:** {sa_keys}")
                
                # Check required fields
                required_fields = ['type', 'project_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if field not in sa_keys]
                
                if missing_fields:
                    st.error(f"❌ Missing required fields: {missing_fields}")
                else:
                    st.success("✅ All required fields present")
                    
            else:
                st.error("❌ 'service_account' key not found")
                
        except Exception as e:
            st.error(f"❌ Error accessing secrets: {e}")
    else:
        st.error("❌ st.secrets not available")

if __name__ == "__main__":
    test_secrets() 