import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. DATA ENGINE (2017 - 2026) ---
def load_excel_data():
    file_options = ["RAW DATA.xlsx", r"Z:\data\RAW DATA.xlsx"]
    file_path = None
    for path in file_options:
        if os.path.exists(path):
            file_path = path
            break
    if not file_path: return pd.DataFrame()
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
    except: return pd.DataFrame()

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    if "chart_data" not in st.session_state: st.session_state.chart_data = None

    df_live = load_excel_data()

    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # SIDEBAR
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.chart_data = None
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")

        st.title("🎢 Joyland Great Grand Master BI")

        # --- CHAT & VISUALS DISPLAY ---
        display_container = st.container()
        with display_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])
            
            if st.session_state.chart_data is not None:
                st.divider()
                f_df = st.session_state.chart_data['df']
                rev_ach = st.session_state.chart_data['rev_ach']
                ff_ach = st.session_state.chart_data['ff_ach']

                t1, t2, t3 = st.tabs(["🎯 Achievements", "📈 Growth Trends", "📋 Raw Analysis"])
                with t1:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Rev %"})).update_layout(height=200, template="plotly_dark"))
                    c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "FF %"})).update_layout(height=200, template="plotly_dark"))
                    c3.plotly_chart(px.pie(f_df, values='Actual Revenue', names='Months', hole=.3, title="Rev Share").update_layout(height=250, showlegend=False))
                    c4.plotly_chart(px.bar(f_df, x='Months', y='Actual Revenue', title="Monthly Rev").update_layout(height=250))
                with t2:
                    tc1, tc2 = st.columns(2)
                    tc1.plotly_chart(px.line(f_df, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], title="Revenue vs Target").update_layout(height=300))
                    tc2.plotly_chart(px.area(f_df, x='Date_Obj', y='Actual Footfall', title="Footfall Volumne").update_layout(height=300))
                with t3:
                    st.dataframe(f_df.style.format(subset=['Actual Revenue', 'Target revenue'], formatter="{:,.0f}"))

        # --- INPUT BAR ---
        st.markdown("---")
        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])
        with input_col: prompt = st.chat_input("Ask about Revenue, Footfall...")
        with mic_col: voice_data = st.audio_input("🎤", key="v_mic", label_visibility="collapsed")
        with clip_col: attached_file = st.file_uploader("📎", type=['xlsx','csv'], key="f_clip", label_visibility="collapsed")

        user_query = prompt if prompt else ("Voice command" if voice_data else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            query_lower = user_query.lower()

            # RESTORE ORIGINAL INTRO (EXACTLY AS REQUESTED)
            if any(greet in query_lower for greet in ["hi", "hello", "intro", "salam", "introduce"]):
                intro_msg = (
                    "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\n"
                    "I am a highly intelligent Business Intelligence & Data Analyst assistant, "
                    "proudly **developed by Umair Nizam**. My architecture is optimized to track, "
                    "analyze, and visualize performance data for **Joyland Fortress**.\n\n"
                    "**My Expert Scope:**\n"
                    "* 📅 **Timeframe:** Data from July 2017 to June 2026.\n"
                    "* 💹 **Analytics:** Revenue & Footfall achievements and YoY comparisons.\n"
                    "* 📎 **Flexibility:** Attach your own files using the clip icon.\n\n"
                    "How can I assist your data-driven decisions today?"
                )
                st.session_state.messages.append({"content": intro_msg, "is_user": False})
                st.rerun()

            # CORE LOGIC - FIXED KEYERROR & UNBOUND ERROR
            if not df_live.empty:
                months_list = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
                found_months = [m.capitalize() for m in months_list if m in query_lower or m[:3] in query_lower]
                found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
                
                f_df = df_live.copy()
                if found_months: f_df = f_df[f_df['Months'].isin(found_months)]
                if found_years: f_df = f_df[f_df['Year'].isin(found_years)]

                if not f_df.empty:
                    # Fix: Using Column Names instead of Index to prevent KeyError
                    act_rev = f_df["Actual Revenue"].sum()
                    tar_rev = f_df["Target revenue"].sum()
                    act_ff = f_df["Actual Footfall"].sum()
                    tar_ff = f_df["Target Footfall"].sum()

                    rev_ach = (act_rev / tar_rev * 100) if tar_rev > 0 else 0
                    ff_ach = (act_ff / tar_ff * 100) if tar_ff > 0 else 0
                    
                    st.session_state.chart_data = {'df': f_df, 'rev_ach': rev_ach, 'ff_ach': ff_ach}
                    st.session_state.messages.append({"content": f"✅ Report generated. Actual Revenue: Rs. {act_rev:,.0f} ({rev_ach:.1f}%)", "is_user": False})
                    st.rerun()

    else: st.info("System Developed by **Umair Nizam**. Please log in.")

if __name__ == "__main__": main()
