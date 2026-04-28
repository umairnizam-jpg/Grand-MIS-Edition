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
    if not file_path: return pd.DataFrame()
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        month_map = {'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
                     'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6}
        df['Month_Num'] = df['Months'].map(month_map)
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2030-12-01')
        return df.loc[mask].sort_values('Date_Obj')
    except: return pd.DataFrame()

# --- AI PREDICTION (Eid Calendar Included) ---
def get_prediction(df, m_idx, y_val, col):
    df_clean = df.dropna(subset=[col])
    if df_clean.empty: return 0
    X = np.array(range(len(df_clean))).reshape(-1, 1)
    y = df_clean[col].values
    model = LinearRegression().fit(X, y)
    months_diff = (y_val - df_clean['Date_Obj'].min().year) * 12 + (m_idx - df_clean['Date_Obj'].min().month)
    base_pred = model.predict([[months_diff]])[0]
    eid_months = {2026: [3, 4, 6], 2027: [3, 5, 6], 2028: [2, 5], 2029: [2, 4], 2030: [1, 4]}
    multiplier = 1.45 if (y_val in eid_months and m_idx in eid_months[y_val]) else 1.0
    return max(0, base_pred * multiplier)

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    # --- CSS FIX FOR VISIBILITY (Labels ab bilkul saaf nazar ayenge) ---
    st.markdown("""
        <style>
        .main { background: #0e1117; }
        div[data-testid="stMetric"] { 
            background: #1c2128 !important; 
            padding: 20px !important; 
            border-radius: 12px !important; 
            border: 1px solid #30363d !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        }
        /* Bright Blue color for top labels */
        div[data-testid="stMetricLabel"] > div { 
            color: #58a6ff !important; 
            font-size: 16px !important; 
            font-weight: 700 !important;
            text-transform: uppercase;
        }
        /* Pure White for numbers */
        div[data-testid="stMetricValue"] > div { color: #ffffff !important; font-weight: 800 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    if "messages" not in st.session_state: st.session_state.messages = []
    if "last_filtered_df" not in st.session_state: st.session_state.last_filtered_df = None

    df_live = load_excel_data()
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    # FIX for Line 70 SyntaxError (Walrus operator replaced)
    auth_status = st.session_state.get("authentication_status")

    if auth_status:
        st.sidebar.title(f"🚀 Analyst: {st.session_state['name']}")
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")

        st.title("🎢 Joyland MIS Assistant")
        
        # --- METRIC ROW (Fixed Contrast) ---
        if not df_live.empty:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Life-Time Revenue", f"Rs. {df_live['Actual Revenue'].sum():,.0f}")
            m2.metric("Total Footfall", f"{df_live['Actual Footfall'].sum():,.0f}")
            m3.metric("Avg Monthly Revenue", f"Rs. {df_live['Actual Revenue'].mean():,.0f}")
            m4.metric("Data Scope", "2017-2030")

        st.divider()

        # Chat and Logic
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ex: 'Revenue 2017 to 2026'...")

        if prompt:
            st.session_state.messages.append({"content": prompt, "is_user": True})
            q = prompt.lower()
            month_ref = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12,
                         'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,'october':10,'november':11,'december':12}
            years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q)]
            found_months = [month_ref[m] for m in month_ref if m in q]

            # AI Forecast
            if any(w in q for w in ['forecast', 'predict']) and years and found_months:
                p_rev = get_prediction(df_live, found_months[0], years[0], 'Actual Revenue')
                p_ff = get_prediction(df_live, found_months[0], years[0], 'Actual Footfall')
                st.session_state.messages.append({"content": f"🔮 **AI Forecast for {years[0]}:**\n* Rev: Rs. {p_rev:,.0f}\n* FF: {p_ff:,.0f}", "is_user": False})
                st.rerun()

            # Range Filter
            temp_df = df_live.copy()
            if len(years) >= 2:
                s_dt = pd.to_datetime(f"{years[0]}-{found_months[0] if len(found_months)>=2 else 7}-01")
                e_dt = pd.to_datetime(f"{years[1]}-{found_months[1] if len(found_months)>=2 else 6}-01")
                temp_df = temp_df[(temp_df['Date_Obj'] >= s_dt) & (temp_df['Date_Obj'] <= e_dt)]
            elif years or found_months:
                if years: temp_df = temp_df[temp_df['Year'].isin(years)]
                if found_months: temp_df = temp_df[temp_df['Month_Num'].isin(found_months)]

            if not temp_df.empty:
                st.session_state.last_filtered_df = temp_df
                ans = f"📊 **Period Analysis:**\n* Total Revenue: Rs. {temp_df['Actual Revenue'].sum():,.0f}\n* Total Footfall: {temp_df['Actual Footfall'].sum():,.0f}"
                st.session_state.messages.append({"content": ans, "is_user": False})
                st.rerun()

        # Visualizer
        if st.session_state.last_filtered_df is not None:
            df_p = st.session_state.last_filtered_df
            choice = st.selectbox("🎯 Visualizer", ["1. Revenue Achievement", "2. Revenue Trend Line", "3. Actual vs Target Bar", "4. Footfall Trend", "5. Revenue Pie", "6. Footfall Achievement"])
            mets = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
            
            if choice.startswith("1"):
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=(df_p['Actual Revenue'].sum()/df_p['Target revenue'].sum()*100))).update_layout(template="plotly_dark"))
            elif choice.startswith("2"):
                st.plotly_chart(px.line(df_p, x='Date_Obj', y='Actual Revenue', template="plotly_dark"))
            elif choice.startswith("3"):
                st.plotly_chart(px.bar(df_p, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], barmode='group', template="plotly_dark"))
            elif choice.startswith("4"):
                st.plotly_chart(px.line(df_p, x='Date_Obj', y='Actual Footfall', template="plotly_dark"))
            elif choice.startswith("5"):
                st.plotly_chart(px.pie(df_p, values='Actual Revenue', names='Months', template="plotly_dark"))
            elif choice.startswith("6"):
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=(df_p['Actual Footfall'].sum()/df_p['Target Footfall'].sum()*100))).update_layout(template="plotly_dark"))

            st.table(df_p[mets].sum().to_frame().T.style.format('{:,.0f}'))

    else: st.info("Developed by **Umair Nizam**. Please log in.")

if __name__ == "__main__": main()
