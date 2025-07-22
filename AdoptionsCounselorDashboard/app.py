#!/usr/bin/env python3
"""
Adoptions Counselor Dashboard
A comprehensive dashboard for adoptions counselors to view morning email data,
outcomes, adoptions by counselor, and longest length of stay animals.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append('..')

# Page configuration
st.set_page_config(
    page_title="Adoptions Counselor Dashboard",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #062b49;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #bc6f32;
        margin: 0.5rem 0;
    }
    .counselor-highlight {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 3px solid #512a44;
    }
    .long-stay-alert {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 3px solid #856404;
    }
    .petpoint-link {
        color: #bc6f32;
        text-decoration: none;
        font-weight: bold;
    }
    .petpoint-link:hover {
        color: #512a44;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all required data files"""
    try:
        # Get the path to the load files directory
        load_files_dir = Path("__Load Files Go Here__")
        
        # Load AnimalInventory for current capacity and LOS data
        inventory_file = load_files_dir / "AnimalInventory.csv"
        if inventory_file.exists():
            df_inventory = pd.read_csv(inventory_file, skiprows=2)
            # Extract AID from AnimalNumber (last 8 characters)
            df_inventory['AID'] = df_inventory['AnimalNumber'].str[-8:].astype(str)
            # Convert dates
            df_inventory['IntakeDateTime'] = pd.to_datetime(df_inventory['IntakeDateTime'], errors='coerce')
            df_inventory['DateOfBirth'] = pd.to_datetime(df_inventory['DateOfBirth'], errors='coerce')
        else:
            st.error("AnimalInventory.csv not found")
            df_inventory = pd.DataFrame()
        
        # Load AnimalIntake for previous day's intakes
        intake_file = load_files_dir / "AnimalIntake.csv"
        if intake_file.exists():
            df_intake = pd.read_csv(intake_file, skiprows=2)
            df_intake['IntakeDateTime'] = pd.to_datetime(df_intake['IntakeDateTime'], errors='coerce')
        else:
            st.warning("AnimalIntake.csv not found")
            df_intake = pd.DataFrame()
        
        # Load AnimalOutcome for previous day's outcomes
        outcome_file = load_files_dir / "AnimalOutcome.csv"
        if outcome_file.exists():
            df_outcome = pd.read_csv(outcome_file, skiprows=2)
            df_outcome['OutcomeDateTime'] = pd.to_datetime(df_outcome['OutcomeDateTime'], errors='coerce')
        else:
            st.warning("AnimalOutcome.csv not found")
            df_outcome = pd.DataFrame()
        
        return df_inventory, df_intake, df_outcome
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def calculate_current_capacity(df_inventory):
    """Calculate current capacity by species and location"""
    if df_inventory.empty:
        return pd.DataFrame()
    
    # Filter for current animals (not outcomes)
    current_animals = df_inventory.copy()
    
    # Group by species and location
    capacity = current_animals.groupby(['Species', 'Location']).size().reset_index(name='Count')
    
    # Add totals
    species_totals = current_animals.groupby('Species').size().reset_index(name='Count')
    species_totals['Location'] = 'Total'
    
    location_totals = current_animals.groupby('Location').size().reset_index(name='Count')
    location_totals['Species'] = 'Total'
    
    grand_total = pd.DataFrame([{'Species': 'Total', 'Location': 'Total', 'Count': len(current_animals)}])
    
    # Combine all
    capacity = pd.concat([capacity, species_totals, location_totals, grand_total], ignore_index=True)
    
    return capacity

def get_previous_day_data(df_intake, df_outcome, days_back=1):
    """Get data for previous day(s)"""
    yesterday = datetime.now().date() - timedelta(days=days_back)
    
    # Previous day intakes
    if not df_intake.empty:
        prev_intakes = df_intake[
            df_intake['IntakeDateTime'].dt.date == yesterday
        ].copy()
    else:
        prev_intakes = pd.DataFrame()
    
    # Previous day outcomes
    if not df_outcome.empty:
        prev_outcomes = df_outcome[
            df_outcome['OutcomeDateTime'].dt.date == yesterday
        ].copy()
    else:
        prev_outcomes = pd.DataFrame()
    
    return prev_intakes, prev_outcomes

def get_adoptions_by_counselor(df_outcome):
    """Get adoptions broken down by counselor"""
    if df_outcome.empty:
        return pd.DataFrame()
    
    # Filter for adoptions
    adoptions = df_outcome[df_outcome['OutcomeType'] == 'Adoption'].copy()
    
    if adoptions.empty:
        return pd.DataFrame()
    
    # Group by counselor
    counselor_adoptions = adoptions.groupby('OutcomeCounselor').size().reset_index(name='Adoptions')
    
    # Add total
    total_adoptions = pd.DataFrame([{'OutcomeCounselor': 'Total', 'Adoptions': len(adoptions)}])
    counselor_adoptions = pd.concat([counselor_adoptions, total_adoptions], ignore_index=True)
    
    return counselor_adoptions, adoptions

def get_longest_stay_animals(df_inventory, top_n=20):
    """Get animals with longest length of stay for specified stages"""
    if df_inventory.empty:
        return pd.DataFrame()
    
    # Filter for specified stages
    target_stages = [
        'Available', 
        'Available - Behind the Scenes', 
        'Available - Doggie Entourage', 
        'Available - ITFF Behavior', 
        'Available - ITFF Medical'
    ]
    
    available_animals = df_inventory[
        df_inventory['Stage'].isin(target_stages)
    ].copy()
    
    if available_animals.empty:
        return pd.DataFrame()
    
    # Calculate length of stay
    today = datetime.now()
    available_animals['LengthOfStay'] = (today - available_animals['IntakeDateTime']).dt.days
    
    # Get top N by species
    cats = available_animals[available_animals['Species'] == 'Cat'].nlargest(top_n, 'LengthOfStay')
    dogs = available_animals[available_animals['Species'] == 'Dog'].nlargest(top_n, 'LengthOfStay')
    others = available_animals[~available_animals['Species'].isin(['Cat', 'Dog'])].nlargest(top_n, 'LengthOfStay')
    
    return cats, dogs, others

def create_petpoint_link(aid):
    """Create PetPoint profile link"""
    return f"https://sms.petpoint.com/sms3/enhanced/animal/{aid}"

def main():
    # Header
    st.markdown('<h1 class="main-header">🐾 Adoptions Counselor Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df_inventory, df_intake, df_outcome = load_data()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Current Capacity", 
        "📈 Previous Day Summary", 
        "👥 Adoptions by Counselor", 
        "⏰ Longest Length of Stay"
    ])
    
    with tab1:
        st.header("Current Capacity")
        
        if not df_inventory.empty:
            capacity = calculate_current_capacity(df_inventory)
            
            # Display capacity metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_animals = len(df_inventory)
                st.metric("Total Animals", total_animals)
            
            with col2:
                cats = len(df_inventory[df_inventory['Species'] == 'Cat'])
                st.metric("Cats", cats)
            
            with col3:
                dogs = len(df_inventory[df_inventory['Species'] == 'Dog'])
                st.metric("Dogs", dogs)
            
            # Capacity breakdown
            st.subheader("Capacity by Species and Location")
            
            # Create pivot table
            pivot_data = df_inventory.groupby(['Species', 'Location']).size().unstack(fill_value=0)
            st.dataframe(pivot_data, use_container_width=True)
            
            # Drill down capability
            st.subheader("Drill Down")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_species = st.selectbox(
                    "Select Species",
                    ['All'] + sorted(df_inventory['Species'].unique().tolist())
                )
            
            with col2:
                if selected_species != 'All':
                    species_locations = sorted(
                        df_inventory[df_inventory['Species'] == selected_species]['Location'].unique()
                    )
                    selected_location = st.selectbox(
                        "Select Location",
                        ['All'] + species_locations
                    )
                else:
                    selected_location = 'All'
            
            # Filter data based on selection
            filtered_data = df_inventory.copy()
            
            if selected_species != 'All':
                filtered_data = filtered_data[filtered_data['Species'] == selected_species]
            
            if selected_location != 'All':
                filtered_data = filtered_data[filtered_data['Location'] == selected_location]
            
            # Display filtered animals
            if not filtered_data.empty:
                st.subheader(f"Animals: {selected_species} - {selected_location}")
                
                # Create display dataframe with PetPoint links
                display_data = filtered_data[['AnimalName', 'Species', 'Location', 'Stage', 'AID']].copy()
                display_data['PetPoint Profile'] = display_data['AID'].apply(
                    lambda x: f"[View Profile]({create_petpoint_link(x)})"
                )
                
                st.dataframe(
                    display_data.drop('AID', axis=1),
                    use_container_width=True,
                    column_config={
                        "PetPoint Profile": st.column_config.LinkColumn("PetPoint Profile")
                    }
                )
            else:
                st.info("No animals found for the selected criteria.")
        else:
            st.warning("No inventory data available.")
    
    with tab2:
        st.header("Previous Day Summary")
        
        # Get previous day data
        prev_intakes, prev_outcomes = get_previous_day_data(df_intake, df_outcome)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Previous Day Intakes", len(prev_intakes))
        
        with col2:
            st.metric("Previous Day Outcomes", len(prev_outcomes))
        
        with col3:
            if not prev_outcomes.empty:
                adoptions = len(prev_outcomes[prev_outcomes['OutcomeType'] == 'Adoption'])
                st.metric("Previous Day Adoptions", adoptions)
            else:
                st.metric("Previous Day Adoptions", 0)
        
        # Intakes breakdown
        if not prev_intakes.empty:
            st.subheader("Previous Day Intakes")
            
            # Species breakdown
            intake_by_species = prev_intakes.groupby('Species').size()
            st.bar_chart(intake_by_species)
            
            # Detailed intakes
            st.subheader("Intake Details")
            intake_display = prev_intakes[['AnimalName', 'Species', 'IntakeType', 'AID']].copy()
            intake_display['PetPoint Profile'] = intake_display['AID'].apply(
                lambda x: f"[View Profile]({create_petpoint_link(x)})"
            )
            
            st.dataframe(
                intake_display.drop('AID', axis=1),
                use_container_width=True,
                column_config={
                    "PetPoint Profile": st.column_config.LinkColumn("PetPoint Profile")
                }
            )
        else:
            st.info("No intake data available for previous day.")
        
        # Outcomes breakdown
        if not prev_outcomes.empty:
            st.subheader("Previous Day Outcomes")
            
            # Outcome type breakdown
            outcome_by_type = prev_outcomes.groupby('OutcomeType').size()
            st.bar_chart(outcome_by_type)
            
            # Detailed outcomes
            st.subheader("Outcome Details")
            outcome_display = prev_outcomes[['AnimalName', 'Species', 'OutcomeType', 'AID']].copy()
            outcome_display['PetPoint Profile'] = outcome_display['AID'].apply(
                lambda x: f"[View Profile]({create_petpoint_link(x)})"
            )
            
            st.dataframe(
                outcome_display.drop('AID', axis=1),
                use_container_width=True,
                column_config={
                    "PetPoint Profile": st.column_config.LinkColumn("PetPoint Profile")
                }
            )
        else:
            st.info("No outcome data available for previous day.")
    
    with tab3:
        st.header("Adoptions by Counselor")
        
        # Get adoptions data
        counselor_adoptions, adoptions_data = get_adoptions_by_counselor(df_outcome)
        
        if not counselor_adoptions.empty:
            # Counselor summary
            st.subheader("Adoptions by Counselor")
            
            # Display counselor totals
            for _, row in counselor_adoptions.iterrows():
                if row['OutcomeCounselor'] != 'Total':
                    st.markdown(f"""
                    <div class="counselor-highlight">
                        <strong>{row['OutcomeCounselor']}</strong>: {row['Adoptions']} adoptions
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>Total Adoptions</strong>: {row['Adoptions']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Filter by counselor
            if not adoptions_data.empty:
                st.subheader("Filter Adoptions by Counselor")
                
                counselors = sorted(adoptions_data['OutcomeCounselor'].unique())
                selected_counselor = st.selectbox("Select Counselor", ['All'] + counselors)
                
                if selected_counselor != 'All':
                    filtered_adoptions = adoptions_data[
                        adoptions_data['OutcomeCounselor'] == selected_counselor
                    ]
                else:
                    filtered_adoptions = adoptions_data
                
                # Display filtered adoptions
                st.subheader(f"Adoptions: {selected_counselor}")
                
                adoption_display = filtered_adoptions[['AnimalName', 'Species', 'OutcomeCounselor', 'AID']].copy()
                adoption_display['PetPoint Profile'] = adoption_display['AID'].apply(
                    lambda x: f"[View Profile]({create_petpoint_link(x)})"
                )
                
                st.dataframe(
                    adoption_display.drop('AID', axis=1),
                    use_container_width=True,
                    column_config={
                        "PetPoint Profile": st.column_config.LinkColumn("PetPoint Profile")
                    }
                )
        else:
            st.info("No adoption data available.")
    
    with tab4:
        st.header("Longest Length of Stay Animals")
        
        if not df_inventory.empty:
            cats, dogs, others = get_longest_stay_animals(df_inventory)
            
            # Create tabs for each species
            los_tab1, los_tab2, los_tab3 = st.tabs(["🐱 Cats", "🐕 Dogs", "🐾 Others"])
            
            with los_tab1:
                st.subheader("Cats - Longest Length of Stay")
                if not cats.empty:
                    cat_display = cats[['AnimalName', 'Location', 'Stage', 'LengthOfStay', 'AID']].copy()
                    cat_display['PetPoint Profile'] = cat_display['AID'].apply(
                        lambda x: f"[View Profile]({create_petpoint_link(x)})"
                    )
                    
                    st.dataframe(
                        cat_display.drop('AID', axis=1),
                        use_container_width=True,
                        column_config={
                            "PetPoint Profile": st.column_config.LinkColumn("PetPoint Profile")
                        }
                    )
                else:
                    st.info("No cats found with specified stages.")
            
            with los_tab2:
                st.subheader("Dogs - Longest Length of Stay")
                if not dogs.empty:
                    dog_display = dogs[['AnimalName', 'Location', 'Stage', 'LengthOfStay', 'AID']].copy()
                    dog_display['PetPoint Profile'] = dog_display['AID'].apply(
                        lambda x: f"[View Profile]({create_petpoint_link(x)})"
                    )
                    
                    st.dataframe(
                        dog_display.drop('AID', axis=1),
                        use_container_width=True,
                        column_config={
                            "PetPoint Profile": st.column_config.LinkColumn("PetPoint Profile")
                        }
                    )
                else:
                    st.info("No dogs found with specified stages.")
            
            with los_tab3:
                st.subheader("Others - Longest Length of Stay")
                if not others.empty:
                    other_display = others[['AnimalName', 'Species', 'Location', 'Stage', 'LengthOfStay', 'AID']].copy()
                    other_display['PetPoint Profile'] = other_display['AID'].apply(
                        lambda x: f"[View Profile]({create_petpoint_link(x)})"
                    )
                    
                    st.dataframe(
                        other_display.drop('AID', axis=1),
                        use_container_width=True,
                        column_config={
                            "PetPoint Profile": st.column_config.LinkColumn("PetPoint Profile")
                        }
                    )
                else:
                    st.info("No other animals found with specified stages.")
        else:
            st.warning("No inventory data available.")

if __name__ == "__main__":
    main() 