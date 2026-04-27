import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. DATA ENGINE (Scope: 2017 - 2026) ---
def load_excel_data():
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
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # --- CHARTS PERSISTENCE ---
    if "active_viz" not in st.session_state:
        st.session_state.active_viz = None

    df_live = load_excel_data()

    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.active_viz = None
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")

        st.title("🎢 Joyland Great Grand Master BI")

        # Chat display
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        # --- PROFESSIONALLY ARRANGED CHAT BAR ---
        st.markdown("---")
        # Layout adjustment for perfect alignment
        bar_col, mic_col, up_col = st.columns([4, 0.5, 0.5])

        with bar_col:
            prompt = st.chat_input("Ask about Revenue, Footfall, Comparisons...")
        with mic_col:
            voice_data = st.audio_input("🎤", key="v_mic", label_visibility="collapsed")
        with up_col:
            attached_file = st.file_uploader("📎", type=['xlsx', 'csv'], key="f_clip", label_visibility="collapsed")

        user_query = prompt if prompt else ("Voice data received" if voice_data else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            query_lower = user_query.lower()

            # Intro Logic
            if any(greet in query_lower for greet in ["hi", "hello", "intro", "salam"]):
                intro = "✨ **Greetings! I am the Joyland Ultimate BI Assistant, developed by Umair Nizam.** How can I help you today?"
                st.session_state.messages.append({"content": intro, "is_user": False})
                st.rerun()

            if not df_live.empty:
                # Analytics Logic
                all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
                found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
                found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
                
                filtered_df = df_live.copy()
                if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
                if found_years: filtered_df = filtered_df[filtered_df['Year'].isin(found_years)]

                if not filtered_df.empty:
                    metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                    results = filtered_df[metrics].sum()
                    rev_ach = (results[0]/results[1]*100) if results[1]>0 else 0
                    ff_ach = (results[2]/results[3]*100) if results[3]>0 else 0

                    report = f"### 📊 BI Analysis Result\n* **Revenue Achievement:** {rev_ach:.1f}%\n* **Footfall Achievement:** {ff_ach:.1f}%"
                    st.session_state.messages.append({"content": report, "is_user": False})
                    
                    # SAVE TO STATE FOR CHARTS
                    st.session_state.active_viz = {"rev": rev_ach, "ff": ff_ach, "df": filtered_df[metrics].sum().to_frame().T}
                    st.rerun()

        # --- PERSISTENT CHART DISPLAY (FIXED) ---
        if st.session_state.active_viz:
            st.divider()
            tab1, tab2 = st.tabs(["🌎 Data Table", "🎯 Achievement Gauges"])
            with tab1:
                st.table(st.session_state.active_viz["df"].style.format('{:,.0f}'))
            with tab2:
                c1, c2 = st.columns(2)
                # Revenue Chart
                fig_rev = go.Figure(go.Indicator(mode="gauge+number", value=st.session_state.active_viz["rev"],
                    title={'text': "Revenue Ach %"}, gauge={'bar':{'color':"white"}}))
                fig_rev.update_layout(height=280, template="plotly_dark")
                c1.plotly_chart(fig_rev, use_container_width=True)
                
                # Footfall Chart
                fig_ff = go.Figure(go.Indicator(mode="gauge+number", value=st.session_state.active_viz["ff"],
                    title={'text': "Footfall Ach %"}, gauge={'bar':{'color':"white"}}))
                fig_ff.update_layout(height=280, template="plotly_dark")
                c2.plotly_chart(fig_ff, use_container_width=True)
    else:
        st.info("System Developed by **Umair Nizam**. Please log in.")

if __name__ == "__main__":
    main()
