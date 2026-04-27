import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. ROBUST AI MODULE INITIALIZATION ---
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    AI_AVAILABLE = False

# Function to safely get AI Response (Key Check Fix)
def get_ai_response(query, api_key):
    if not AI_AVAILABLE:
        return "⚠️ 'google-generativeai' library is missing. Add it to requirements.txt."
    try:
        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            return "Global Search currently unavailable. Please check API Key."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Act as a BI expert for Joyland. Answer: {query}")
        return response.text
    except Exception as e:
        return f"🌐 Global Search Result: Currently unavailable. Error: {str(e)}"

# --- 2. DATA ENGINE (Scope: 2017 - 2026) ---
def load_excel_data():
    file_options = ["RAW DATA.xlsx", r"Z:\data\RAW DATA.xlsx"]
    file_path = next((path for path in file_options if os.path.exists(path)), None)
    
    if not file_path: return pd.DataFrame()
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        month_map = {'July':7,'August':8,'September':9,'October':10,'November':11,'December':12,
                     'January':1,'February':2,'March':3,'April':4,'May':5,'June':6}
        df['Month_Num'] = df['Months'].map(month_map)
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        return df[(df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-03-01')].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 3. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    if "last_filtered_df" not in st.session_state: st.session_state.last_filtered_df = None

    df_live = load_excel_data()

    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")
        
        st.title("🎢 Joyland MIS Assistant")
        
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ask about Revenue or Global Search...")

        if prompt:
            st.session_state.messages.append({"content": prompt, "is_user": True})
            query_l = prompt.lower()

            # Fixed Syntax Error Line 107
            if any(greet in query_l for greet in ["hi", "hello", "intro", "introduce"]):
                intro_msg = "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\nPROUDLY **DEVELOPED BY UMAIR NIZAM**.\n\n* **Flexibility:** Attach your own files using the clip."
                st.session_state.messages.append({"content": intro_msg, "is_user": False})
                st.rerun()

            month_pattern = r'(july|august|september|october|november|december|january|february|march|april|may|june)'
            found_months = [m.capitalize() for m in re.findall(month_pattern, query_l)]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_l)]

            temp_df = pd.DataFrame()
            if found_months or found_years:
                temp_df = df_live.copy()
                if found_months: temp_df = temp_df[temp_df['Months'].isin(found_months)]
                if found_years: temp_df = temp_df[temp_df['Year'].isin(found_years)]

            if temp_df.empty:
                with st.spinner("Searching Globally..."):
                    my_api_key = "YOUR_GEMINI_API_KEY" # Replace with your key
                    answer = get_ai_response(prompt, my_api_key)
                    st.session_state.messages.append({"content": answer, "is_user": False})
            else:
                res = temp_df[["Actual Revenue", "Actual Footfall", "Target revenue", "Target Footfall"]].sum()
                report = f"### 📊 BI Analysis Result\n* Total Actual Revenue: **Rs. {res['Actual Revenue']:,.0f}**\n* Total Actual Footfall: **{res['Actual Footfall']:,.0f}**"
                st.session_state.messages.append({"content": report, "is_user": False})
                st.session_state.last_filtered_df = temp_df
            
            st.rerun()

        if st.session_state.last_filtered_df is not None:
            df_plot = st.session_state.last_filtered_df
            res_plot = df_plot[["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]].sum()
            
            # Fixed KeyError Line 187 (Capital 'F')
            rev_ach = (res_plot['Actual Revenue'] / res_plot['Target revenue'] * 100) if res_plot['Target revenue'] > 0 else 0
            ff_ach = (res_plot['Actual Footfall'] / res_plot['Target Footfall'] * 100) if res_plot['Target Footfall'] > 0 else 0

            st.divider()
            # Fixed Syntax Error Line 195
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Revenue Achievement %"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00CC96"}})), use_container_width=True)
            with col2:
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "Footfall Achievement %"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#636EFA"}})), use_container_width=True)

            st.table(df_plot[["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]].sum().to_frame().T.style.format('{:,.0f}'))

    else:
        st.info("System Developed by **Umair Nizam**. Please log in to proceed.")

if __name__ == "__main__":
    main()
