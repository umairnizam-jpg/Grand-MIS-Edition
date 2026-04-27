import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. DATA ENGINE ---
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
        month_map = {'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
                     'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6}
        df['Month_Num'] = df['Months'].map(month_map)
        df['Fiscal_Year_Label'] = df.apply(lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1)
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 2. MAIN APP ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    # Session States
    if "messages" not in st.session_state: st.session_state.messages = []
    if "current_filter" not in st.session_state: st.session_state.current_filter = None

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
            st.session_state.current_filter = None
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")

        st.title("🎢 Joyland Great Grand Master BI")

        # Chat Display
        chat_box = st.container()
        with chat_box:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        # --- INTEGRATED INPUT BAR (Icons on Right) ---
        st.markdown("---")
        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])
        with input_col: prompt = st.chat_input("Ask about Revenue or Footfall...")
        with mic_col: voice_data = st.audio_input("🎤", key="mic", label_visibility="collapsed")
        with clip_col: attached_file = st.file_uploader("📎", type=['xlsx','csv'], key="clip", label_visibility="collapsed")

        # Combine Input Logic
        user_query = prompt if prompt else ("Voice command" if voice_data else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            query_lower = user_query.lower()

            # 1. INTRO
            if any(greet in query_lower for greet in ["hi", "hello", "intro", "who are you", "salam"]):
                intro = "✨ **Greetings! I am the Joyland BI Assistant, developed by Umair Nizam.** How can I assist you?"
                st.session_state.messages.append({"content": intro, "is_user": False})
                st.rerun()

            # 2. FILTERING
            if not df_live.empty:
                months_list = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
                found_months = [m.capitalize() for m in months_list if m in query_lower or m[:3] in query_lower]
                found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
                
                f_df = df_live.copy()
                if found_months: f_df = f_df[f_df['Months'].isin(found_months)]
                if found_years: f_df = f_df[f_df['Year'].isin(found_years)]
                
                if not f_df.empty:
                    st.session_state.current_filter = f_df # Store for visual persistence
                    res = f_df[["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]].sum()
                    rev_ach = (res[0]/res[1]*100) if res[1]>0 else 0
                    ff_ach = (res[2]/res[3]*100) if res[3]>0 else 0
                    
                    msg = f"### 📊 Result\n* **Revenue Ach:** {rev_ach:.1f}%\n* **Footfall Ach:** {ff_ach:.1f}%"
                    st.session_state.messages.append({"content": msg, "is_user": False})
                    st.rerun()

        # --- PERSISTENT VISUALS (Ye Section Charts ko hamesha dikhaye ga) ---
        if st.session_state.current_filter is not None:
            f_df = st.session_state.current_filter
            res = f_df[["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]].sum()
            rev_ach = (res[0]/res[1]*100) if res[1]>0 else 0
            ff_ach = (res[2]/res[3]*100) if res[3]>0 else 0

            st.divider()
            t1, t2 = st.tabs(["📈 Trend Analysis", "🎯 Performance Gauges"])
            with t1:
                fig = px.line(f_df, x='Months', y=['Actual Revenue', 'Target revenue'], markers=True, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            with t2:
                c1, c2 = st.columns(2)
                c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text':"Revenue %"}, gauge={'bar':{'color':"white"}})).update_layout(height=300, template="plotly_dark"))
                c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text':"Footfall %"}, gauge={'bar':{'color':"white"}})).update_layout(height=300, template="plotly_dark"))
    else:
        st.info("Umair Nizam's BI Portal: Please Login.")

if __name__ == "__main__":
    main()
