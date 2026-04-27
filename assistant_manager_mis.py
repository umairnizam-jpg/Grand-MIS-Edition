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
    # GitHub ke liye relative path aur Office ke liye local path dono check karega
    file_options = ["RAW DATA.xlsx", r"Z:\data\RAW DATA.xlsx"]
    file_path = None
    
    for path in file_options:
        if os.path.exists(path):
            file_path = path
            break
            
    if not file_path:
        # Agar dono jagah file na mile toh error handle karega
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

# --- 2. MAIN APP ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    df_live = load_excel_data()

    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')

        st.title("🎢 Joyland Great Grand Master BI")

        # TOOL BAR (Voice & File)
        col_v, col_f = st.columns([1, 4])
        with col_v: audio_cmd = st.audio_input("🎤 Voice")
        with col_f: attached_file = st.file_uploader("📎 Attach File", type=['xlsx', 'csv'], label_visibility="collapsed")

        # CHAT DISPLAY
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        # INPUT HANDLING
        prompt = st.chat_input("Ask anything about Revenue or Footfall...")
        user_query = prompt if prompt else ("Voice command" if audio_cmd else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            
            # Error Prevention: Check if data is loaded
            if df_live.empty:
                err_msg = "❌ **Data Error:** Excel file nahi mil rahi. Please check karein ke `RAW DATA.xlsx` aapke GitHub repo mein maujood hai ya Z drive connect hai."
                st.session_state.messages.append({"content": err_msg, "is_user": False})
                st.rerun()

            query_lower = user_query.lower()
            all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
            found_fy = re.findall(r'fy\s?\d{4}', query_lower)

            # Filtering
            filtered_df = df_live.copy()
            if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
            if found_years: filtered_df = filtered_df[filtered_df['Year'].isin(found_years)]
            if found_fy:
                tag = found_fy[0].upper().replace("FY", "FY ") if " " not in found_fy[0] else found_fy[0].upper()
                filtered_df = filtered_df[filtered_df['Fiscal_Year_Label'] == tag]

            if not filtered_df.empty:
                # Calculations
                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                res = filtered_df[metrics].sum()
                rev_ach = (res['Actual Revenue'] / res['Target revenue'] * 100) if res['Target revenue'] > 0 else 0
                ff_ach = (res['Actual Footfall'] / res['Target Footfall'] * 100) if res['Target Footfall'] > 0 else 0

                analysis_msg = (
                    f"### 📊 Analysis Report\n"
                    f"* **Revenue:** Rs. {res['Actual Revenue']:,.0f} ({rev_ach:.1f}% Achieved)\n"
                    f"* **Footfall:** {res['Actual Footfall']:,.0f} ({ff_ach:.1f}% Achieved)"
                )
                st.session_state.messages.append({"content": analysis_msg, "is_user": False})
                
                # Visuals Persistence
                st.divider()
                t1, t2 = st.tabs(["🌎 Data Matrix", "🎯 Gauges"])
                with t1: st.table(filtered_df[metrics].sum().to_frame().T.style.format('{:,.0f}'))
                with t2:
                    c1, c2 = st.columns(2)
                    c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Rev %"})).update_layout(height=250, template="plotly_dark"))
                    c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "FF %"})).update_layout(height=250, template="plotly_dark"))
                
                st.rerun()
            else:
                st.session_state.messages.append({"content": "Nahi mila! Please check karein ke saal aur mahina 2017-2026 ke darmiyan hai.", "is_user": False})
                st.rerun()

    else:
        st.info("Umair Nizam's BI System: Please Login.")

if __name__ == "__main__":
    main()
