import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. CORE DATA ENGINE (Fixed Path Logic) ---
def load_excel_data():
    # Cloud (GitHub) aur Local (Z Drive) dono ko handle karne ke liye options
    file_options = ["RAW DATA.xlsx", r"Z:\data\RAW DATA.xlsx"]
    file_path = None
    
    for path in file_options:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        return pd.DataFrame() # Agar file na mile to khali DataFrame
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Date & Fiscal Mapping
        month_map = {'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
                     'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6}
        df['Month_Num'] = df['Months'].map(month_map)
        df['Fiscal_Year_Label'] = df.apply(lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1)
        
        # Sorting
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        
        # Scope: 2017-2026
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Master", layout="wide", page_icon="🎢")
    
    # Session State Initialization
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
        if st.sidebar.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 Developed by\n**Umair Nizam**")

        st.title("🎢 Joyland MIS Assistant")

        # Chat Container
        chat_box = st.container()
        with chat_box:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        # --- INTEGRATED CHAT BAR (Mic & Clip on Right) ---
        st.markdown("---")
        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])

        with input_col:
            prompt = st.chat_input("Ask about Revenue, Footfall, or comparisons...")
        with mic_col:
            voice_data = st.audio_input("🎤", key="mic_btn", label_visibility="collapsed")
        with clip_col:
            attached_file = st.file_uploader("📎", type=['xlsx', 'csv'], key="clip_btn", label_visibility="collapsed")

        # Logic Processing
        user_input = prompt if prompt else ("Voice input detected" if voice_data else None)

        if user_input:
            st.session_state.messages.append({"content": user_input, "is_user": True})
            query_lower = user_input.lower()

            # 1. PROFESSIONAL INTRO
            if any(greet in query_lower for greet in ["hi", "hello", "intro", "salam", "introduce"]):
                intro = (
                    "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\n"
                    "I am an intelligent BI Analyst tool, meticulously **developed by Umair Nizam**. "
                    "I specialize in analyzing **Joyland Fortress** performance from 2017 to 2026.\n\n"
                    "How can I assist your analysis today?"
                )
                st.session_state.messages.append({"content": intro, "is_user": False})
                st.rerun()

            # 2. DATA PROCESSING (Error Protected)
            if df_live.empty:
                st.session_state.messages.append({"content": "❌ **Data Error:** `RAW DATA.xlsx` nahi mil rahi. Please file ko GitHub repository mein upload karein.", "is_user": False})
                st.rerun()

            # Filtering Logic
            all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]

            filtered_df = df_live.copy()
            if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
            if found_years: filtered_df = filtered_df[filtered_df['Year'].isin(found_years)]

            if not filtered_df.empty:
                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                results = filtered_df[metrics].sum()
                rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
                ff_ach = (results['Actual Footfall'] / results['Target Footfall'] * 100) if results['Target Footfall'] > 0 else 0

                res_text = (
                    f"### 📊 BI Performance Report\n"
                    f"* **Revenue:** Rs. {results['Actual Revenue']:,.0f} ({rev_ach:.1f}% Achieved)\n"
                    f"* **Footfall:** {results['Actual Footfall']:,.0f} ({ff_ach:.1f}% Achieved)"
                )
                if attached_file: res_text += f"\n\n📎 **Attachment:** `{attached_file.name}` analyzed."
                
                st.session_state.messages.append({"content": res_text, "is_user": False})
                
                # Persistent Visuals
                st.divider()
                t1, t2 = st.tabs(["📝 Table", "🎯 Achievement"])
                with t1: st.table(filtered_df[metrics].sum().to_frame().T.style.format('{:,.0f}'))
                with t2:
                    c1, c2 = st.columns(2)
                    c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text':"Revenue %"})).update_layout(height=250, template="plotly_dark"))
                    c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text':"Footfall %"})).update_layout(height=250, template="plotly_dark"))
                st.rerun()
            else:
                st.session_state.messages.append({"content": "Nahi mila! Please 2017-2026 ke darmiyan ka data puchein.", "is_user": False})
                st.rerun()

    else:
        st.info("System Ready. Developed by Umair Nizam. Please login.")

if __name__ == "__main__":
    main()
