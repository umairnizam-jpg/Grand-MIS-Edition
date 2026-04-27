import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. CORE DATA ENGINE ---
def load_excel_data():
    # GitHub (Cloud) vs Office (Local) Path Detection
    file_options = ["RAW DATA.xlsx", r"Z:\data\RAW DATA.xlsx"]
    file_path = None
    for path in file_options:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        return pd.DataFrame()
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        
        month_map = {
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6
        }
        df['Month_Num'] = df['Months'].map(month_map)
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        
        # Constraint: 2017-2026
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 2. MAIN BI INTERFACE ---
def main():
    st.set_page_config(page_title="Joyland BI Master", layout="wide", page_icon="🎢")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    df_live = load_excel_data()

    # Security
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # Sidebar
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 Developed by\n**Umair Nizam**")

        st.title("🎢 Joyland Great Grand Master BI")

        # Chat Container
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        # --- NEW INTEGRATED CHAT BAR ---
        # User input logic with icons at the bottom
        st.write("---")
        
        # UI Columns for Input + Mic + Clip
        # We place input first, then tools on the right
        input_col, mic_col, clip_col = st.columns([4, 0.4, 0.4])

        with input_col:
            prompt = st.chat_input("Ask about Revenue, Footfall, or your attached file...")
        
        with mic_col:
            # Mic icon triggers audio input
            voice_data = st.audio_input("🎤", key="mic_btn", label_visibility="collapsed")
            
        with clip_col:
            # Clip icon triggers file uploader
            uploaded_file = st.file_uploader("📎", type=['xlsx', 'csv'], key="clip_btn", label_visibility="collapsed")

        # Combine Inputs
        final_query = None
        if prompt:
            final_query = prompt
        elif voice_data:
            final_query = "Voice Command Received (Processing...)"

        if final_query:
            st.session_state.messages.append({"content": final_query, "is_user": True})
            query_lower = final_query.lower()

            # 1. INTRO LOGIC
            if any(greet in query_lower for greet in ["hi", "hello", "intro", "who are you", "salam"]):
                intro = (
                    "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\n"
                    "I am a highly intelligent Business Intelligence tool, meticulously **developed by Umair Nizam**. "
                    "I analyze **Revenue and Footfall** data from July 2017 to June 2026.\n\n"
                    "**How can I help you today?**"
                )
                st.session_state.messages.append({"content": intro, "is_user": False})
                st.rerun()

            # 2. DATA LOGIC
            if df_live.empty:
                st.session_state.messages.append({"content": "❌ **Data Error:** Master file nahi mili. Check GitHub folder.", "is_user": False})
                st.rerun()

            # Filtering & Calculations
            all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
            
            filtered_df = df_live.copy()
            if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
            if found_years: filtered_df = filtered_df[filtered_df['Year'].isin(found_years)]

            if not filtered_df.empty:
                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                totals = filtered_df[metrics].sum()
                rev_ach = (totals['Actual Revenue'] / totals['Target revenue'] * 100) if totals['Target revenue'] > 0 else 0
                ff_ach = (totals['Actual Footfall'] / totals['Target Footfall'] * 100) if totals['Target Footfall'] > 0 else 0

                response = (
                    f"### 📊 BI Report\n"
                    f"* **Revenue:** Rs. {totals['Actual Revenue']:,.0f} ({rev_ach:.1f}% Achieved)\n"
                    f"* **Footfall:** {totals['Actual Footfall']:,.0f} ({ff_ach:.1f}% Achieved)"
                )
                if uploaded_file: response += f"\n\n📎 **File Attached:** `{uploaded_file.name}`"
                
                st.session_state.messages.append({"content": response, "is_user": False})
                st.rerun()
            else:
                st.session_state.messages.append({"content": "No data found for this query.", "is_user": False})
                st.rerun()

        # Visuals
        if not filtered_df.empty:
            st.divider()
            t1, t2 = st.tabs(["🌎 Table", "🎯 Charts"])
            with t1: st.table(filtered_df[metrics].sum().to_frame().T.style.format('{:,.0f}'))
            with t2:
                c1, c2 = st.columns(2)
                c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text':"Rev %"})).update_layout(height=250, template="plotly_dark"))
                c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text':"FF %"})).update_layout(height=250, template="plotly_dark"))

    else:
        st.info("Log in as Admin. System developed by Umair Nizam.")

if __name__ == "__main__":
    main()
