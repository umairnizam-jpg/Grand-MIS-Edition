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

    # Authentication
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

        st.title("🎢 Joyland MIS Assistant")

        # --- CHAT & VISUALS DISPLAY ---
        display_box = st.container()
        with display_box:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])
            
            # 8 PROFESSIONAL CHARTS RENDERER
            if st.session_state.chart_data is not None:
                st.divider()
                f_df = st.session_state.chart_data['df']
                ra, fa = st.session_state.chart_data['ra'], st.session_state.chart_data['fa']

                t1, t2, t3 = st.tabs(["🎯 Achievements", "📈 Growth Trends", "📋 Data Table"])
                with t1: # 4 Professional Charts
                    c1, c2, c3, c4 = st.columns(4)
                    c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ra, title={'text': "Rev %"})).update_layout(height=200, template="plotly_dark"))
                    c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=fa, title={'text': "FF %"})).update_layout(height=200, template="plotly_dark"))
                    c3.plotly_chart(px.pie(f_df, values='Actual Revenue', names='Months', hole=.3, title="Rev Share").update_layout(height=220, showlegend=False))
                    c4.plotly_chart(px.bar(f_df, x='Months', y='Actual Revenue', title="Monthly Rev").update_layout(height=220))

                with t2: # 4 Trend Charts
                    tc1, tc2, tc3, tc4 = st.columns(4)
                    tc1.plotly_chart(px.line(f_df, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], title="Rev Trend").update_layout(height=220))
                    tc2.plotly_chart(px.area(f_df, x='Date_Obj', y='Actual Footfall', title="FF Volume").update_layout(height=220))
                    tc3.plotly_chart(px.scatter(f_df, x='Actual Footfall', y='Actual Revenue', title="Correlation").update_layout(height=220))
                    tc4.plotly_chart(px.bar(f_df, x='Months', y=['Actual Footfall', 'Target Footfall'], barmode='group', title="FF Compare").update_layout(height=220))
                
                with t3:
                    st.dataframe(f_df.style.format(subset=['Actual Revenue', 'Target revenue'], formatter="{:,.0f}"))

        # --- COMPACT PROFESSIONAL INPUT BAR ---
        st.markdown("---")
        # Ratio optimized for small icons
        in_col, v_col, f_col = st.columns([6, 0.3, 0.3])
        with in_col: prompt = st.chat_input("Ask about Revenue, Footfall, Trends...")
        with v_col: voice = st.audio_input("🎤", key="v_chat", label_visibility="collapsed")
        with f_col: attachment = st.file_uploader("📎", type=['xlsx','csv','docx','pdf','txt'], key="f_chat", label_visibility="collapsed")

        # Process Logic
        user_input = prompt if prompt else ("Voice command" if voice else None)

        if user_input:
            st.session_state.messages.append({"content": user_input, "is_user": True})
            q_low = user_input.lower()

            # --- RESTORE ORIGINAL INTRO (EXACT) ---
            if any(g in q_low for g in ["hi", "hello", "intro", "salam", "who are you"]):
                intro = (
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
                st.session_state.messages.append({"content": intro, "is_user": False})
                st.rerun()

            # --- CORE ANALYTICS ENGINE (ERROR FREE) ---
            if not df_live.empty:
                filtered_df = df_live.copy() # FIX: UnboundLocalError solved
                
                months_list = ['july','august','september','october','november','december','january','february','march','april','may','june']
                f_months = [m.capitalize() for m in months_list if m in q_low or m[:3] in q_low]
                f_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q_low)]
                
                if f_months: filtered_df = filtered_df[filtered_df['Months'].isin(f_months)]
                if f_years: filtered_df = filtered_df[filtered_df['Year'].isin(f_years)]

                if not filtered_df.empty:
                    # Sum columns safely
                    ar, tr = filtered_df["Actual Revenue"].sum(), filtered_df["Target revenue"].sum()
                    af, tf = filtered_df["Actual Footfall"].sum(), filtered_df["Target Footfall"].sum()
                    
                    ra = (ar / tr * 100) if tr > 0 else 0
                    fa = (af / tf * 100) if tf > 0 else 0
                    
                    st.session_state.chart_data = {'df': filtered_df, 'ra': ra, 'fa': fa}
                    st.session_state.messages.append({"content": f"✅ Report generated for the period. Visuals updated below.", "is_user": False})
                    st.rerun()
                else:
                    st.session_state.messages.append({"content": "No data found for this specific period.", "is_user": False})
                    st.rerun()

    else: st.info("System Developed by **Umair Nizam**. Please log in.")

if __name__ == "__main__": main()
