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
        
        # Original Date Object for Trends
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2030-12-01')
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# AI Forecasting Logic
def get_prediction(df, m_idx, y_val, col):
    df_clean = df.dropna(subset=[col])
    if df_clean.empty: return 0
    X = np.array(range(len(df_clean))).reshape(-1, 1)
    y = df_clean[col].values
    model = LinearRegression().fit(X, y)
    start_date = df_clean['Date_Obj'].min()
    target_date = pd.to_datetime(f"{y_val}-{m_idx}-01")
    months_diff = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    base_pred = model.predict([[months_diff]])[0]
    eid_calendar = {2026: [3, 4, 6], 2027: [3, 5, 6], 2028: [2, 5], 2029: [2, 4], 2030: [1, 4]}
    multiplier = 1.45 if (y_val in eid_calendar and m_idx in eid_calendar[y_val]) else 1.0
    return max(0, base_pred * multiplier)

# --- 2. MAIN APPLICATION (100% ORIGINAL UI/LAYOUT) ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    # --- 100% ORIGINAL CSS ---
    st.markdown("""
        <style>
        .main { background: #0e1117; }
        div[data-testid="stMetric"] { 
            background: #1c2128; 
            padding: 20px; 
            border-radius: 12px; 
            border: 1px solid #30363d;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        div[data-testid="stMetricLabel"] > div { color: #8b949e !important; font-size: 16px !important; }
        div[data-testid="stMetricValue"] > div { color: #ffffff !important; font-weight: 700 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    if "messages" not in st.session_state: st.session_state.messages = []
    if "last_filtered_df" not in st.session_state: st.session_state.last_filtered_df = None

    df_live = load_excel_data()
    
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    # Fixed syntax check
    is_auth = st.session_state.get("authentication_status")

    if is_auth:
        # --- ORIGINAL SIDEBAR ---
        st.sidebar.title(f"🚀 Analyst: {st.session_state['name']}")
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")

        st.title("🎢 Joyland MIS Assistant")
        
        # --- ORIGINAL METRIC ROW ---
        if not df_live.empty:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Life-Time Revenue", f"Rs. {df_live['Actual Revenue'].sum():,.0f}")
            m2.metric("Total Footfall", f"{df_live['Actual Footfall'].sum():,.0f}")
            m3.metric("Avg Monthly Revenue", f"Rs. {df_live['Actual Revenue'].mean():,.0f}")
            m4.metric("Data Scope", "2017-2030")

        st.divider()

        # Chat Interface
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ex: 'July 2018 to Dec 2022' or 'April 2026 forecast'...")

        if prompt:
            st.session_state.messages.append({"content": prompt, "is_user": True})
            q = prompt.lower()
            
            # --- DATE RANGE DETECTION ---
            month_ref = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
                         'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
            
            years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q)]
            found_months = [month_ref[m] for m in month_ref if m in q]

            # A. AI Forecast
            if any(w in q for w in ['forecast', 'predict']) and years and found_months:
                y_val = years[0]
                m_idx = found_months[0]
                p_rev = get_prediction(df_live, m_idx, y_val, 'Actual Revenue')
                p_ff = get_prediction(df_live, m_idx, y_val, 'Actual Footfall')
                st.session_state.messages.append({"content": f"### 🔮 Forecast: {y_val}\n* Revenue: **Rs. {p_rev:,.0f}**\n* Footfall: **{p_ff:,.0f} Pax**", "is_user": False})
                st.rerun()

            # B. Advanced Filtering (Range Support)
            temp_df = df_live.copy()
            if len(years) >= 2:
                s_dt = pd.to_datetime(f"{years[0]}-{found_months[0] if len(found_months)>=2 else 7}-01")
                e_dt = pd.to_datetime(f"{years[1]}-{found_months[1] if len(found_months)>=2 else 6}-01")
                temp_df = temp_df[(temp_df['Date_Obj'] >= s_dt) & (temp_df['Date_Obj'] <= e_dt)]
            elif years or found_months:
                if years: temp_df = temp_df[temp_df['Year'].isin(years)]
                if found_months: 
                    m_names = [m.capitalize() for m, idx in month_ref.items() if idx in found_months and len(m)>3]
                    temp_df = temp_df[temp_df['Months'].isin(m_names)]

            if not temp_df.empty:
                st.session_state.last_filtered_df = temp_df
                
                # Metric Specific Check
                m_txt = ""
                if "target revenue" in q: m_txt = f"🎯 Target Revenue: **Rs. {temp_df['Target revenue'].sum():,.0f}**"
                elif "revenue" in q or "rev" in q: m_txt = f"💰 Actual Revenue: **Rs. {temp_df['Actual Revenue'].sum():,.0f}**"
                elif "footfall" in q or "ff" in q: m_txt = f"👣 Actual Footfall: **{temp_df['Actual Footfall'].sum():,.0f} Pax**"
                
                ans = f"### 📊 Analysis Result\n{m_txt if m_txt else f'* Actual Revenue: Rs. {temp_df['Actual Revenue'].sum():,.0f}'}"
                st.session_state.messages.append({"content": ans, "is_user": False})
                st.rerun()

        # --- 3. ORIGINAL VISUALIZER (STRICTLY 6 OPTIONS) ---
        if st.session_state.last_filtered_df is not None:
            df_p = st.session_state.last_filtered_df
            tab1, tab2 = st.tabs(["📉 Visual Insights", "🔮 Prediction Trend"])
            with tab1:
                # Wahi original selectbox options
                choice = st.selectbox("🎯 Switch Insight View", [
                    "1. Revenue Achievement Gauge", 
                    "2. Revenue Trend Line", 
                    "3. Actual vs Target Bar", 
                    "4. Footfall Trend Line",
                    "5. Monthly Share Pie", 
                    "6. Footfall Achievement Gauge"
                ])
                
                mets = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                results = df_p[mets].sum()
                
                if choice.startswith("1"):
                    ach = (results['Actual Revenue']/results['Target revenue']*100) if results['Target revenue']>0 else 0
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ach, title={'text':"Rev Achievement %"})).update_layout(height=350, template="plotly_dark"), use_container_width=True)
                elif choice.startswith("2"):
                    st.plotly_chart(px.line(df_p, x='Date_Obj', y='Actual Revenue', markers=True, template="plotly_dark"), use_container_width=True)
                elif choice.startswith("3"):
                    st.plotly_chart(px.bar(df_p, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], barmode='group', template="plotly_dark"), use_container_width=True)
                elif choice.startswith("4"):
                    st.plotly_chart(px.line(df_p, x='Date_Obj', y='Actual Footfall', markers=True, template="plotly_dark"), use_container_width=True)
                elif choice.startswith("5"):
                    st.plotly_chart(px.pie(df_p, values='Actual Revenue', names='Months', template="plotly_dark"), use_container_width=True)
                elif choice.startswith("6"):
                    ach_f = (results['Actual Footfall']/results['Target Footfall']*100) if results['Target Footfall']>0 else 0
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ach_f, title={'text':"FF Achievement %"})).update_layout(height=350, template="plotly_dark"), use_container_width=True)

                st.table(df_p[mets].sum().to_frame().T.style.format('{:,.0f}'))

            with tab2:
                st.plotly_chart(px.line(df_live, x='Date_Obj', y='Actual Revenue', title="2017-2030 Global Performance", template="plotly_dark"), use_container_width=True)

    else: st.info("Logged out.")

if __name__ == "__main__": main()
