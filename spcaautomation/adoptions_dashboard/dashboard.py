import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import sys

# Import configuration
from config import *

# Add the parent directory to the path to import morning_email functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'MorningEmail'))

# Import functions from morning_email.py
try:
    from morning_email import (
        get_stage_counts, get_occupancy_counts, get_adoptions_count,
        get_intake_count_detail, get_intake_summary, get_foster_count
    )
except ImportError:
    st.error("Could not import morning email functions. Please ensure morning_email.py is in the MorningEmail directory.")

st.set_page_config(
    page_title="SPCA Adoptions Dashboard",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🐾 SPCA Adoptions Team Dashboard")
st.markdown("---")

# Sidebar for date selection and filters
with st.sidebar:
    st.header("📅 Dashboard Controls")
    
    # Date range selector
    st.subheader("Analysis Period")
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    analysis_date = st.date_input(
        "Select analysis date:",
        value=yesterday,
        max_value=today
    )
    
    # Convert to the format expected by the morning email functions
    check_dates = [analysis_date.strftime('%m/%d/%Y')]
    
    st.subheader("Capacity Thresholds")
    shelter_capacity = st.slider("Shelter Capacity Alert (%)", 50, 100, 85)
    foster_capacity = st.slider("Foster Capacity Alert (%)", 50, 100, 90)
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Check if data files exist
load_files_dir = DATA_DIRECTORY
required_files = REQUIRED_DATA_FILES

missing_files = []
for file in required_files:
    if not os.path.exists(os.path.join(load_files_dir, file)):
        missing_files.append(file)

if missing_files:
    st.error(f"⚠️ Missing required data files: {', '.join(missing_files)}")
    st.info("Please ensure all required CSV files are in the '__Load Files Go Here__' directory.")
    st.stop()

# Main dashboard content
try:
    # Get data from morning email functions
    stage_counts = get_stage_counts()
    occupancy_data = get_occupancy_counts()
    adoptions_count = get_adoptions_count(check_dates)
    intake_detail = get_intake_count_detail(check_dates)
    intake_summary = get_intake_summary(intake_detail)
    foster_count = get_foster_count()
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 Total Adoptions",
            value=adoptions_count,
            delta=f"Date: {analysis_date.strftime('%m/%d/%Y')}"
        )
    
    with col2:
        total_in_shelter = occupancy_data['Animals in Shelter'].iloc[-1]  # TOTAL row
        st.metric(
            label="🏠 Animals in Shelter",
            value=total_in_shelter,
            delta="Current count"
        )
    
    with col3:
        total_in_foster = occupancy_data['Animals in Foster/Off-Site'].iloc[-1]  # TOTAL row
        st.metric(
            label="👨‍👩‍👧‍👦 In Foster/Off-Site",
            value=total_in_foster,
            delta="Current count"
        )
    
    with col4:
        total_intake = intake_summary['Total'].sum() if not intake_summary.empty else 0
        st.metric(
            label="📥 Total Intake",
            value=total_intake,
            delta=f"Date: {analysis_date.strftime('%m/%d/%Y')}"
        )
    
    st.markdown("---")
    
    # Create two columns for main content
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.subheader("🏠 Current Shelter Occupancy")
        
        # Create occupancy chart
        fig_occupancy = go.Figure()
        
        # Remove the TOTAL row for the chart
        chart_data = occupancy_data[occupancy_data['Species/Age'] != 'TOTAL']
        
                 fig_occupancy.add_trace(go.Bar(
             name='Shelter',
             x=chart_data['Species/Age'],
             y=chart_data['Animals in Shelter'],
             marker_color=CHART_COLORS['shelter']
         ))
         
         fig_occupancy.add_trace(go.Bar(
             name='Foster/Off-Site',
             x=chart_data['Species/Age'],
             y=chart_data['Animals in Foster/Off-Site'],
             marker_color=CHART_COLORS['foster']
         ))
        
        fig_occupancy.update_layout(
            barmode='group',
            title="Animals by Location and Type",
            xaxis_title="Species/Age",
            yaxis_title="Count",
            showlegend=True
        )
        
        st.plotly_chart(fig_occupancy, use_container_width=True)
        
        # Display occupancy table
        st.dataframe(occupancy_data, use_container_width=True)
    
    with right_col:
        st.subheader("📊 Animal Stages Overview")
        
        # Create stage breakdown pie chart
        stage_data = pd.DataFrame(list(stage_counts.items()), columns=['Stage', 'Count'])
        stage_data = stage_data[stage_data['Count'] > 0]  # Only show stages with animals
        
        if not stage_data.empty:
            fig_stages = px.pie(
                stage_data,
                values='Count',
                names='Stage',
                title="Current Animal Stages Distribution"
            )
            fig_stages.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_stages, use_container_width=True)
        else:
            st.info("No animals in tracked stages.")
        
        # Display stage counts table
        st.write("**Stage Counts:**")
        stage_df = pd.DataFrame(list(stage_counts.items()), columns=['Stage', 'Count'])
        st.dataframe(stage_df, use_container_width=True)
    
    st.markdown("---")
    
    # Intake Analysis Section
    st.subheader("📥 Intake Analysis")
    
    if not intake_summary.empty:
        # Create intake breakdown chart
        intake_melted = intake_summary.melt(
            id_vars=['Group'], 
            value_vars=['Cat', 'Dog', 'Other'],
            var_name='Species',
            value_name='Count'
        )
        intake_melted = intake_melted[intake_melted['Count'] > 0]
        
        if not intake_melted.empty:
                         fig_intake = px.bar(
                 intake_melted,
                 x='Group',
                 y='Count',
                 color='Species',
                 title=f"Intake Breakdown for {analysis_date.strftime('%m/%d/%Y')}",
                 color_discrete_map={'Cat': CHART_COLORS['cat'], 'Dog': CHART_COLORS['dog'], 'Other': CHART_COLORS['other']}
             )
            fig_intake.update_layout(xaxis_title="Intake Group", yaxis_title="Count")
            st.plotly_chart(fig_intake, use_container_width=True)
        
        # Display intake summary table
        st.write("**Intake Summary:**")
        st.dataframe(intake_summary, use_container_width=True)
    else:
        st.info("No intake data available for the selected date.")
    
    st.markdown("---")
    
    # Capacity Analysis Section
    st.subheader("⚠️ Capacity Analysis & Alerts")
    
    # Calculate capacity metrics
    total_animals = total_in_shelter + total_in_foster
    
         # Get capacity from configuration
     estimated_shelter_capacity = SHELTER_CAPACITY
     estimated_foster_capacity = FOSTER_CAPACITY
    
    shelter_utilization = (total_in_shelter / estimated_shelter_capacity) * 100
    foster_utilization = (total_in_foster / estimated_foster_capacity) * 100
    
    cap_col1, cap_col2 = st.columns(2)
    
    with cap_col1:
        st.metric(
            label="🏠 Shelter Utilization",
            value=f"{shelter_utilization:.1f}%",
            delta=f"{total_in_shelter}/{estimated_shelter_capacity}"
        )
        
        if shelter_utilization >= shelter_capacity:
            st.error(f"🚨 Shelter is at {shelter_utilization:.1f}% capacity!")
        elif shelter_utilization >= (shelter_capacity - 10):
            st.warning(f"⚠️ Shelter approaching capacity at {shelter_utilization:.1f}%")
        else:
            st.success(f"✅ Shelter capacity is manageable at {shelter_utilization:.1f}%")
    
    with cap_col2:
        st.metric(
            label="👨‍👩‍👧‍👦 Foster Utilization",
            value=f"{foster_utilization:.1f}%",
            delta=f"{total_in_foster}/{estimated_foster_capacity}"
        )
        
        if foster_utilization >= foster_capacity:
            st.error(f"🚨 Foster program is at {foster_utilization:.1f}% capacity!")
        elif foster_utilization >= (foster_capacity - 10):
            st.warning(f"⚠️ Foster program approaching capacity at {foster_utilization:.1f}%")
        else:
            st.success(f"✅ Foster capacity is manageable at {foster_utilization:.1f}%")
    
    # Capacity recommendations
    st.subheader("💡 Capacity Recommendations")
    
    recommendations = []
    
    if shelter_utilization >= shelter_capacity:
        recommendations.append("🔄 **Urgent**: Increase adoption events and foster placements")
        recommendations.append("📞 **Contact**: Reach out to rescue partners for transfers")
    elif shelter_utilization >= (shelter_capacity - 10):
        recommendations.append("📈 **Proactive**: Schedule additional adoption events")
        recommendations.append("🏠 **Foster**: Recruit emergency foster volunteers")
    
    if foster_utilization >= foster_capacity:
                 recommendations.append("👥 **Foster**: Launch foster recruitment campaign")
         recommendations.append("🎯 **Target**: Focus on long-term foster placements")
     
     if adoptions_count < DAILY_ADOPTION_TARGET:
         recommendations.append("📢 **Marketing**: Boost social media promotion")
         recommendations.append("💰 **Incentives**: Consider adoption fee specials")
     
     if total_intake > adoptions_count * INTAKE_ADOPTION_RATIO_ALERT:
         recommendations.append("⚖️ **Balance**: Intake exceeds adoptions - focus on outflow")
    
    if recommendations:
        for rec in recommendations:
            st.write(rec)
    else:
        st.success("✅ Current capacity levels are within normal operating ranges!")
    
    st.markdown("---")
    
    # Historical Trends Section (placeholder for future enhancement)
    st.subheader("📈 Historical Trends")
    st.info("📊 Historical trend analysis will be added in future updates. This will show capacity trends over time to help predict busy periods.")
    
    # Data refresh info
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 Data last refreshed: {datetime.now().strftime('%H:%M:%S')}")
    st.sidebar.info("💡 Tip: Refresh data regularly throughout the day for accurate capacity monitoring.")

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please ensure all required data files are present and the morning_email.py functions are available.")