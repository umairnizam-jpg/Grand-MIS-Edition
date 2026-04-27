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

        # --- CHAT DISPLAY ---
        chat_box = st.container()
        with chat_box:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])
            
            # --- PROFESSIONAL 8 CHARTS RENDERER ---
            if st.session_state.chart_data is not None:
                st.divider()
                f_df = st.session_state.chart_data['df']
                rev_ach = st.session_state.chart_data['rev_ach']
                ff_ach = st.session_state.chart_data['ff_ach']

                t1, t2 = st.tabs(["🎯 KPIs & Share", "📈 Trends & Correlation"])
                with t1:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Revenue %"}, gauge={'bar':{'color':"gold"}})).update_layout(height=220, template="plotly_dark"))
                    c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "Footfall %"}, gauge={'bar':{'color':"cyan"}})).update_layout(height=220, template="plotly_dark"))
                    c3.plotly_chart(px.pie(f_df, values='Actual Revenue', names='Months', title="Revenue Share").update_layout(height=220, showlegend=False))
                    c4.plotly_chart(px.bar(f_df, x='Months', y='Actual Revenue', title="Monthly Revenue").update_layout(height=220))

                with t2:
                    tc1, tc2, tc3, tc4 = st.columns(4)
                    tc1.plotly_chart(px.line(f_df, x='Months', y=['Actual Revenue', 'Target revenue'], title="Rev vs Target").update_layout(height=220))
                    tc2.plotly_chart(px.area(f_df, x='Months', y='Actual Footfall', title="Footfall Trend").update_layout(height=220))
                    tc3.plotly_chart(px.scatter(f_df, x='Actual Footfall', y='Actual Revenue', title="FF vs Rev").update_layout(height=220))
                    tc4.plotly_chart(px.bar(f_df, x='Months', y='Actual Footfall', title="Monthly FF").update_layout(height=220))

        # --- INPUT BAR (FIXED AT BOTTOM) ---
        st.markdown("---")
        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])
        with input_col: prompt = st.chat_input("Ask about Revenue, Footfall...")
        with mic_col: voice_data = st.audio_input("🎤", key="mic", label_visibility="collapsed")
        with clip_col: attached_file = st.file_uploader("📎", type=['xlsx','csv'], key="clip", label_visibility="collapsed")

        # LOGIC
        user_query = prompt if prompt else ("Voice command" if voice_data else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            q_low = user_query.lower()

            # 1. INTRO (Old Restored)
            if any(x in q_low for x in ["hi", "hello", "intro", "salam", "who are you"]):
                intro = "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\nDeveloped by **Umair Nizam**, I analyze Joyland Fortress data (2017-2026)."
                st.session_state.messages.append({"content": intro, "is_user": False})
                st.rerun()

            # 2. FILTERING & ANALYSIS
            if not df_live.empty:
                months = [m.capitalize() for m in ['july','august','september','october','november','december','january','february','march','april','may','june'] if m in q_low or m[:3] in q_low]
                years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q_low)]
                
                filtered_df = df_live.copy() # Fixed UnboundLocalError by initializing here
                if months: filtered_df = filtered_df[filtered_df['Months'].isin(months)]
                if years: filtered_df = filtered_df[filtered_df['Year'].isin(years)]

                if not filtered_df.empty:
                    # Fix KeyError by using explicit column names
                    act_rev = filtered_df["Actual Revenue"].sum()
                    tar_rev = filtered_df["Target revenue"].sum()
                    act_ff = filtered_df["Actual Footfall"].sum()
                    tar_ff = filtered_df["Target Footfall"].sum()

                    rev_p = (act_rev / tar_rev * 100) if tar_rev > 0 else 0
                    ff_p = (act_ff / tar_ff * 100) if tar_ff > 0 else 0
                    
                    st.session_state.chart_data = {'df': filtered_df, 'rev_ach': rev_p, 'ff_ach': ff_p}
                    st.session_state.messages.append({"content": f"📊 Results: Revenue Achieved **{rev_p:.1f}%**, Footfall Achieved **{ff_p:.1f}%**.", "is_user": False})
                    st.rerun()
            else:
                st.error("Data file missing!")

    else: st.info("Joyland BI Grand Master: Developed by Umair Nizam. Please Login.")

if __name__ == "__main__": main()
