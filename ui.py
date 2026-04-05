import streamlit as st
import pandas as pd
import requests
import os
from supabase import create_client, Client

# --- CONFIGURATION ---
st.set_page_config(page_title="The Artha-Agent System", page_icon="🚀", layout="wide")

# Connection details
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

API_BASE_URL = os.getenv("API_URL", "https://artha-agent-337407073347.us-central1.run.app")

# This is the URL of your BACKEND Cloud Run service
API_BASE_URL = os.getenv("API_URL", "http://localhost:8080")

# Initialize Supabase
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Configuration Error: SUPABASE_URL or SUPABASE_KEY is missing.")

# Initialize Session State for View Management
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'  # Options: 'dashboard', 'pulse_results'
if 'pulse_data' not in st.session_state:
    st.session_state['pulse_data'] = []

# --- HEADER ---
st.title("💼 The Artha-Agent System: Executive Assistant")
st.markdown("---")

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("🔍 Manual Analysis")
    ticker_input = st.text_input("Enter Ticker (e.g., RELIANCE.NS)", "").upper()
    if st.button("🎯 Analyze Now", use_container_width=True):
        if ticker_input:
            with st.spinner(f"Analyzing {ticker_input}..."):
                res = requests.post(f"{API_BASE_URL}/v1/analyze", json={"ticker": ticker_input})
                if res.status_code == 200:
                    st.session_state['last_analysis'] = res.json()
                    st.session_state['view'] = 'dashboard' # Ensure we are on dashboard to see result
                else:
                    st.error("Analysis failed.")
        else:
            st.warning("Please enter a ticker.")

    st.markdown("---")
    st.header("⚡ System Actions")
    if st.button("💓 Trigger Proactive Pulse", use_container_width=True):
        with st.spinner("Artha-Agent is scanning the entire watchlist..."):
            response = requests.post(f"{API_BASE_URL}/v1/pulse")
            if response.status_code == 200:
                # /v1/pulse returns a list of results
                st.session_state['pulse_data'] = response.json()
                st.session_state['view'] = 'pulse_results'
                st.rerun() # Refresh to show the new view
            else:
                st.error("Pulse trigger failed.")

    if st.session_state['view'] == 'pulse_results':
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state['view'] = 'dashboard'
            st.rerun()

# --- MAIN CONTENT AREA ---

if st.session_state['view'] == 'pulse_results':
    # --- VIEW 1: PROACTIVE PULSE RESULTS ---
    st.subheader("📡 Proactive Pulse Results")
    
    if st.session_state['pulse_data']:
        # Fetch the raw data
        raw_data = st.session_state['pulse_data']
        
        # 1. Handle results structure: Ensure we are working with a list of results
        data_list = raw_data['results'] if isinstance(raw_data, dict) and 'results' in raw_data else raw_data
        
        # 2. Flatten the data: This turns nested keys like 'summary.price' into their own columns
        pulse_df = pd.json_normalize(data_list)
        
        # 3. Display the full table
        st.dataframe(pulse_df, use_container_width=True, hide_index=True)
        
        # 4. Optional: A debug button if you want to see the raw structure
        with st.expander("🛠️ View Raw JSON Response"):
            st.json(raw_data)
    else:
        st.info("No actions were required during the last pulse. Artha-Agent is monitoring your watchlist.")

else:
    # --- VIEW 2: STANDARD DASHBOARD ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Active Watchlist")
        try:
            response = supabase.table("watchlist").select("*").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                display_df = df[['ticker', 'company_name', 'target_buy_price', 'target_sell_price', 'last_analyzed_at']]
                display_df.columns = ['Ticker', 'Company', 'Buy Target', 'Sell Target', 'Last Check']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Watchlist Load Error: {e}")

        # Show Manual Analysis Result if available
        if 'last_analysis' in st.session_state:
            with st.container(border=True):
                la = st.session_state['last_analysis']
                st.write(f"**Manual Result for {la['ticker']}**")
                st.info(la['recommendation'])

    with col2:
        st.subheader("📩 Recent Action Briefs")
        try:
            notes_res = supabase.table("notes").select("*").order("created_at", desc=True).limit(5).execute()
            if notes_res.data:
                for note in notes_res.data:
                    content = note.get('content', '')
                    try:
                        title = content.split("for ")[1].split(":")[0]
                    except:
                        title = "Update"
                    with st.expander(f"📝 {title} - {note['created_at'][:10]}"):
                        st.write(content)
        except Exception as e:
            st.error(f"Briefs Load Error: {e}")