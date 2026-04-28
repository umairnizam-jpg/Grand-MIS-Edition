import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate
from sklearn.linear_model import LinearRegression 

# --- 1. DATA ENGINE (Scope: 2017 - 2030) ---
@st.cache_data 
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
        
        # Date Object for filtering
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2030-12-01')
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    # ORIGINAL CSS
    st.markdown("""
        <style>
        .main { background: #0e1117; }
        div[data-testid="stMetric"] { 
            background: #1c2128; padding: 20px; border-radius: 12px; border: 1px solid #30363d;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if "messages" not in st.session_state: st.session_state.messages = []
    if "last_filtered_df" not in st.session_state: st.session_state.last_filtered_df = None

    df_live = load_excel_data()
    
    # Auth Logic
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_status := st.session_state.get("authentication_status"):
        st.sidebar.title(f"🚀 Analyst: {st.session_state['name']}")
        auth.logout('Logout', 'sidebar')
        
        st.title("🎢 Joyland MIS Assistant")

        # Chat
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ex: 'Revenue July 2018 to Dec 2022' or 'Actual Revenue 2017 to 2026'...")

        if prompt:
            st.session_state.messages.append({"content": prompt, "is_user": True})
            q = prompt.lower()
            
            # --- ADVANCED DATE RANGE DETECTOR ---
            month_ref = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
                         'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
            
            years = re.findall(r'\b(20\d{2})\b', q)
            # Find months in order
            found_months = []
            words = q.split()
            for w in words:
                clean_w = w.strip('.,')
                if clean_w in month_ref:
                    found_months.append(month_ref[clean_w])

            temp_df = df_live.copy()
            period_label = ""

            # Logic for Range (e.g., 2018 to 2022 or Jan 2023 to Dec 2023)
            if len(years) >= 2:
                start_yr, end_yr = int(years[0]), int(years[1])
                start_mo = found_months[0] if len(found_months) >= 2 else 1
                end_mo = found_months[1] if len(found_months) >= 2 else 12
                
                start_dt = pd.to_datetime(f"{start_yr}-{start_mo}-01")
                end_dt = pd.to_datetime(f"{end_yr}-{end_mo}-01")
                
                temp_df = temp_df[(temp_df['Date_Obj'] >= start_dt) & (temp_df['Date_Obj'] <= end_dt)]
                period_label = f"from {start_dt.strftime('%b %Y')} to {end_dt.strftime('%b %Y')}"
            
            # Fallback to specific months/years if no range
            elif years or found_months:
                if years: temp_df = temp_df[temp_df['Year'].isin([int(y) for y in years])]
                if found_months: 
                    m_names = [m.capitalize() for m, n in month_ref.items() if n in found_months and len(m)>3]
                    temp_df = temp_df[temp_df['Months'].isin(list(set(m_names)))]
                period_label = "for selected period"

            if not temp_df.empty:
                st.session_state.last_filtered_df = temp_df
                rev_total = temp_df['Actual Revenue'].sum()
                ff_total = temp_df['Actual Footfall'].sum()
                
                res_msg = f"### 📊 Result {period_label}\n"
                if "revenue" in q or "rev" in q: res_msg += f"* Total Revenue: **Rs. {rev_total:,.0f}**\n"
                if "footfall" in q or "ff" in q: res_msg += f"* Total Footfall: **{ff_total:,.0f} Pax**"
                if "revenue" not in q and "footfall" not in q:
                    res_msg += f"* Total Revenue: **Rs. {rev_total:,.0f}**\n* Total Footfall: **{ff_total:,.0f} Pax**"
                
                st.session_state.messages.append({"content": res_msg, "is_user": False})
                st.rerun()

        # --- 3. DASHBOARD VISUALS (100% ORIGINAL WITH NEW CHARTS) ---
        if st.session_state.last_filtered_df is not None:
            df_p = st.session_state.last_filtered_df
            tab1, tab2 = st.tabs(["📉 Visual Insights", "🔮 Prediction Trend"])
            with tab1:
                choice = st.selectbox("🎯 Switch Insight View", [
                    "1. Revenue Achievement Gauge", 
                    "2. Revenue Trend Line (New)", 
                    "3. Actual vs Target Bar Chart", 
                    "4. Footfall Trend Line",
                    "5. Monthly Share Pie", 
                    "6. Footfall Achievement Gauge"
                ])
                
                mets = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                
                if choice.startswith("1"):
                    ach = (df_p['Actual Revenue'].sum()/df_p['Target revenue'].sum()*100) if df_p['Target revenue'].sum()>0 else 0
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ach, title={'text':"Rev Achievement %"})).update_layout(template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("2"): # NEW REVENUE TREND
                    fig_rev = px.line(df_p, x='Date_Obj', y='Actual Revenue', title="Revenue Trend Over Time", markers=True)
                    st.plotly_chart(fig_rev.update_layout(template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("3"): # BAR CHART
                    st.plotly_chart(px.bar(df_p, x='Months', y=['Actual Revenue', 'Target revenue'], barmode='group', template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("4"):
                    st.plotly_chart(px.line(df_p, x='Date_Obj', y='Actual Footfall', title="Footfall Trend Over Time", markers=True, template="plotly_dark"), use_container_width=True)
                
                st.table(df_p[mets].sum().to_frame().T.style.format('{:,.0f}'))

    else: st.info("Logged out.")

if __name__ == "__main__": main()
