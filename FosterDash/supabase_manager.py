import streamlit as st
import pandas as pd
from datetime import datetime
import json
from typing import List, Dict, Optional, Any
import os

# Supabase imports (will be installed via requirements)
try:
    from supabase import create_client, Client
except ImportError:
    # Don't show error immediately - let the initialize function handle it
    Client = None

class SupabaseManager:
    """Manages all Supabase database operations for the foster dashboard"""
    
    def __init__(self):
        self.client = None
        self.initialized = False
        
    def initialize(self, supabase_url: str, supabase_key: str) -> bool:
        """Initialize the Supabase client"""
        try:
            if Client is None:
                # Supabase library not available - this is expected when not installed
                return False
                
            self.client = create_client(supabase_url, supabase_key)
            
            # Test the connection
            result = self.client.table('foster_animals').select('animalnumber').limit(1).execute()
            self.initialized = True
            st.success("✅ Successfully connected to Supabase")
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to connect to Supabase: {str(e)}")
            return False
    
    def sync_animal_numbers(self, animal_inventory_df: pd.DataFrame) -> bool:
        """Sync AnimalNumbers from AnimalInventory.csv with Supabase table"""
        if not self.initialized or self.client is None:
            st.error("Supabase not initialized")
            return False
            
        try:
            # Get all AnimalNumbers from the CSV
            csv_animal_numbers = set()
            if 'AnimalNumber' in animal_inventory_df.columns:
                csv_animal_numbers = set(animal_inventory_df['AnimalNumber'].dropna().astype(str).tolist())
            
            if not csv_animal_numbers:
                st.warning("No AnimalNumbers found in AnimalInventory.csv")
                return False
            
            # Get existing AnimalNumbers from Supabase (use lowercase column name)
            result = self.client.table('foster_animals').select('animalnumber').execute()
            existing_animal_numbers = set()
            if result.data:
                existing_animal_numbers = set([row['animalnumber'] for row in result.data])
            
            # Find missing AnimalNumbers
            missing_animal_numbers = csv_animal_numbers - existing_animal_numbers
            
            if missing_animal_numbers:
                # Insert missing animals
                new_records = []
                for animal_number in missing_animal_numbers:
                    new_records.append({
                        'animalnumber': animal_number,
                        'fosternotes': '',
                        'onmeds': '',
                        'fosterpleadates': [],
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    })
                
                # Insert in batches to avoid overwhelming the database
                batch_size = 50
                for i in range(0, len(new_records), batch_size):
                    batch = new_records[i:i + batch_size]
                    self.client.table('foster_animals').insert(batch).execute()
                
                st.success(f"✅ Added {len(missing_animal_numbers)} new animals to database")
            else:
                st.info("✅ All AnimalNumbers are already in the database")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error syncing AnimalNumbers: {str(e)}")
            return False
    
    def get_animal_data(self, animal_number: str) -> Optional[Dict[str, Any]]:
        """Get foster data for a specific animal"""
        if not self.initialized or self.client is None:
            return None
            
        try:
            result = self.client.table('foster_animals').select('*').eq('animalnumber', animal_number).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            st.error(f"❌ Error getting animal data: {str(e)}")
            return None
    
    def update_foster_notes(self, animal_number: str, notes: str) -> bool:
        """Update foster notes for an animal"""
        if not self.initialized or self.client is None:
            return False
            
        try:
            self.client.table('foster_animals').update({
                'fosternotes': notes,
                'updated_at': datetime.now().isoformat()
            }).eq('animalnumber', animal_number).execute()
            return True
        except Exception as e:
            st.error(f"❌ Error updating foster notes: {str(e)}")
            return False
    
    def update_on_meds(self, animal_number: str, meds: str) -> bool:
        """Update meds for an animal"""
        if not self.initialized or self.client is None:
            return False
            
        try:
            self.client.table('foster_animals').update({
                'onmeds': meds,
                'updated_at': datetime.now().isoformat()
            }).eq('animalnumber', animal_number).execute()
            return True
        except Exception as e:
            st.error(f"❌ Error updating meds: {str(e)}")
            return False
    
    def add_foster_plea_date(self, animal_number: str, plea_date: str) -> bool:
        """Add a new foster plea date for an animal"""
        if not self.initialized or self.client is None:
            return False
            
        try:
            # Get current plea dates
            result = self.client.table('foster_animals').select('fosterpleadates').eq('animalnumber', animal_number).execute()
            current_dates = []
            if result.data and result.data[0]['fosterpleadates']:
                current_dates = result.data[0]['fosterpleadates']
            
            # Add new date if not already present
            if plea_date not in current_dates:
                current_dates.append(plea_date)
                
                self.client.table('foster_animals').update({
                    'fosterpleadates': current_dates,
                    'updated_at': datetime.now().isoformat()
                }).eq('animalnumber', animal_number).execute()
                
                st.success(f"✅ Added foster plea date: {plea_date}")
                return True
            else:
                st.warning(f"⚠️ Foster plea date {plea_date} already exists")
                return False
                
        except Exception as e:
            st.error(f"❌ Error adding foster plea date: {str(e)}")
            return False
    
    def update_foster_plea_dates(self, animal_number: str, plea_dates: List[str]) -> bool:
        """Update all foster plea dates for an animal"""
        if not self.initialized or self.client is None:
            return False
            
        try:
            self.client.table('foster_animals').update({
                'fosterpleadates': plea_dates,
                'updated_at': datetime.now().isoformat()
            }).eq('animalnumber', animal_number).execute()
            
            return True
        except Exception as e:
            st.error(f"❌ Error updating foster plea dates: {str(e)}")
            return False
    
    def remove_foster_plea_date(self, animal_number: str, plea_date: str) -> bool:
        """Remove a foster plea date for an animal"""
        if not self.initialized or self.client is None:
            return False
            
        try:
            # Get current plea dates
            result = self.client.table('foster_animals').select('fosterpleadates').eq('animalnumber', animal_number).execute()
            current_dates = []
            if result.data and result.data[0]['fosterpleadates']:
                current_dates = result.data[0]['fosterpleadates']
            
            # Remove the date if present
            if plea_date in current_dates:
                current_dates.remove(plea_date)
                
                self.client.table('foster_animals').update({
                    'fosterpleadates': current_dates,
                    'updated_at': datetime.now().isoformat()
                }).eq('animalnumber', animal_number).execute()
                
                st.success(f"✅ Removed foster plea date: {plea_date}")
                return True
            else:
                st.warning(f"⚠️ Foster plea date {plea_date} not found")
                return False
                
        except Exception as e:
            st.error(f"❌ Error removing foster plea date: {str(e)}")
            return False
    
    def get_all_foster_data(self) -> Dict[str, Dict[str, Any]]:
        """Get all foster data from the database"""
        if not self.initialized or self.client is None:
            return {}
            
        try:
            result = self.client.table('foster_animals').select('*').execute()
            foster_data = {}
            if result.data:
                for row in result.data:
                    foster_data[row['animalnumber']] = row
            return foster_data
        except Exception as e:
            st.error(f"❌ Error getting all foster data: {str(e)}")
            return {}

# Global Supabase manager instance
supabase_manager = SupabaseManager() 