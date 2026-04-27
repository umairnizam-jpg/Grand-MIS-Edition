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
    # Cloud aur Local paths ka smart check
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
        
        # Fiscal Year (July-June)
        df['Fiscal_Year_Label'] = df.apply(lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1)
        
        # Sorting order
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        # Scope: 2017-2026
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 2. MAIN APP ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    df_live = load_excel_data()

    # Security
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # SIDEBAR
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")

        st.title("🎢 Joyland Great Grand Master BI")

        # Chat History Display
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        # --- INTEGRATED INPUT BAR (RIGHT SIDE ICONS) ---
        st.markdown("---")
        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])

        with input_col:
            prompt = st.chat_input("Ask about Revenue, Footfall, or FY Comparisons...")
        with mic_col:
            voice_data = st.audio_input("🎤", key="mic_btn", label_visibility="collapsed")
        with clip_col:
            attached_file = st.file_uploader("📎", type=['xlsx', 'csv'], key="clip_btn", label_visibility="collapsed")

        # Combine Input
        user_query = prompt if prompt else ("Voice command" if voice_data else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            query_lower = user_query.lower()

            # 1. ATTRACTIVE INTRO
            if any(greet in query_lower for greet in ["hi", "hello", "intro", "salam", "who are you"]):
                intro = (
                    "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\n"
                    "I am a highly advanced Business Intelligence tool, **developed by Umair Nizam**. "
                    "I provide deep insights into **Joyland Fortress** performance (2017-2026).\n\n"
                    "**What I can do:**\n"
                    "* 📊 Revenue & Footfall Analysis\n"
                    "* 📉 YoY Comparisons & Achievement Tracking\n"
                    "* 📎 Custom File Analysis via Attachment"
                )
                st.session_state.messages.append({"content": intro, "is_user": False})
                st.rerun()

            # 2. DATA ANALYTICS
            if df_live.empty:
                st.error("❌ Master file `RAW DATA.xlsx` not found!")
                return

            # Extract Dates
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

                report = (
                    f"### 📊 BI Report Summary\n"
                    f"* **Revenue:** Rs. {totals['Actual Revenue']:,.0f} ({rev_ach:.1f}% Achieved)\n"
                    f"* **Footfall:** {totals['Actual Footfall']:,.0f} ({ff_ach:.1f}% Achieved)"
                )
                st.session_state.messages.append({"content": report, "is_user": False})
                
                # --- VISUALS SECTION (AUTO-RENDER) ---
                st.divider()
                t1, t2, t3 = st.tabs(["🌎 Table", "📈 Trend", "🎯 Achievement"])
                with t1:
                    st.dataframe(filtered_df[metrics].sum().to_frame().T.style.format('{:,.0f}'))
                with t2:
                    fig = px.line(filtered_df, x='Months', y=['Actual Revenue', 'Target revenue'], markers=True, template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                with t3:
                    c1, c2 = st.columns(2)
                    c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text':"Revenue %"}, gauge={'bar':{'color':"gold"}})).update_layout(height=250, template="plotly_dark"))
                    c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text':"Footfall %"}, gauge={'bar':{'color':"cyan"}})).update_layout(height=250, template="plotly_dark"))
                
                # IMPORTANT: No rerun here to allow charts to stay visible
            else:
                st.session_state.messages.append({"content": "No data found for this period (2017-2026).", "is_user": False})
                st.rerun()
    else:
        st.info("Umair Nizam's BI System: Please Login.")

if __name__ == "__main__":
    main()
