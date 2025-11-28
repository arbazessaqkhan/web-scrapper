import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from scraper import scrape_tenders

# Set page config
st.set_page_config(
    page_title="Indian Tender Intelligence",
    page_icon="🇮🇳",
    layout="wide"
)

# Custom CSS for a modern look
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        height: 3em;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF0000;
        color: white;
        border: none;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🇮🇳 Indian Government Tender Intelligence")
st.markdown("### Real-time analysis of active tenders from eprocure.gov.in")

# Sidebar
with st.sidebar:
    st.header("Control Panel")
    if st.button("🔄 Scrape New Tenders"):
        with st.spinner("Scraping and analyzing tenders... This may take a minute."):
            try:
                scrape_tenders()
                st.success("Scraping completed!")
                time.sleep(1) # Allow user to see success message
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    st.info("This dashboard uses **Llama 3.2** to extract structured insights (Sector, Value, Contract Type) from raw tender data.")

# Load Data
csv_path = 'output/tenders_clean.csv'
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    
    # Data Cleaning for UI
    df['estimated_value_inr'] = pd.to_numeric(df['estimated_value_inr'], errors='coerce')
    df['closing_date'] = pd.to_datetime(df['closing_date'], errors='coerce', dayfirst=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Active Tenders", len(df))
    
    with col2:
        total_value = df['estimated_value_inr'].sum()
        if total_value > 0:
            val_str = f"₹{total_value/10000000:.2f} Cr"
        else:
            val_str = "N/A"
        st.metric("Total Estimated Value", val_str)
        
    with col3:
        top_sector = df['sector'].mode()[0] if not df['sector'].empty else "N/A"
        st.metric("Top Sector", top_sector)
        
    with col4:
        top_state = df['location_state'].mode()[0] if not df['location_state'].empty else "N/A"
        st.metric("Top State", top_state)

    st.markdown("---")

    # Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Tenders by Sector")
        if 'sector' in df.columns and not df['sector'].dropna().empty:
            fig_sector = px.pie(df, names='sector', title='Sector Distribution', hole=0.4)
            st.plotly_chart(fig_sector, use_container_width=True)
        else:
            st.warning("Not enough data for Sector chart.")

    with c2:
        st.subheader("Tenders by State")
        if 'location_state' in df.columns and not df['location_state'].dropna().empty:
            state_counts = df['location_state'].value_counts().reset_index()
            state_counts.columns = ['State', 'Count']
            fig_state = px.bar(state_counts, x='State', y='Count', title='State Distribution', color='Count')
            st.plotly_chart(fig_state, use_container_width=True)
        else:
            st.warning("Not enough data for State chart.")

    # Data Table
    st.subheader("Detailed Tender Data")
    
    # Filters
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_sector = st.multiselect("Filter by Sector", options=df['sector'].unique())
    with filter_col2:
        selected_state = st.multiselect("Filter by State", options=df['location_state'].unique())
        
    filtered_df = df.copy()
    if selected_sector:
        filtered_df = filtered_df[filtered_df['sector'].isin(selected_sector)]
    if selected_state:
        filtered_df = filtered_df[filtered_df['location_state'].isin(selected_state)]
        
    st.dataframe(
        filtered_df,
        column_config={
            "title": "Tender Title",
            "reference_number": "Ref No.",
            "ministry": "Ministry",
            "closing_date": st.column_config.DateColumn("Closing Date"),
            "estimated_value_inr": st.column_config.NumberColumn("Value (INR)", format="₹%d"),
            "sector": "Sector",
            "location_state": "State",
            "contract_type": "Type"
        },
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("No data found. Please click 'Scrape New Tenders' in the sidebar.")
