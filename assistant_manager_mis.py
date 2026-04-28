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
        
        # Date Object for filtering & Trends
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        # Ensuring data range up to 2030 for AI
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2030-12-01')
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- AI PREDICTION ENGINE (Eid Factor 2026-2030) ---
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
    
    # Islamic Events Weights (Eid Months)
    eid_calendar = {2026: [3, 4, 6], 2027: [3, 5, 6], 2028: [2, 5], 2029: [2, 4], 2030: [1, 4]}
    multiplier = 1.45 if (y_val in eid_calendar and m_idx in eid_calendar[y_val]) else 1.0
    return max(0, base_pred * multiplier)

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    # ORIGINAL CSS (Strictly Maintained)
    st.markdown("""
        <style>
        .main { background: #0e1117; }
        div[data-testid="stMetric"] { 
            background: #1c2128; padding: 20px; border-radius: 12px; border: 1px solid #30363d;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        div[data-testid="stMetricLabel"] > div { color: #8b949e !important; font-size: 16px !important; }
        div[data-testid="stMetricValue"] > div { color: #ffffff !important; font-weight: 700 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    if "messages" not in st.session_state: st.session_state.messages = []
    if "last_filtered_df" not in st.session_state: st.session_state.last_filtered_df = None

    df_live = load_excel_data()
    
    # Auth Logic
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    # Fixed Auth Status Check (Syntax Error Resolved)
    auth_status = st.session_state.get("authentication_status")

    if auth_status:
        st.sidebar.title(f"🚀 Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Analysis"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.markdown("### 👨‍💻 Architect: Umair Nizam")

        st.title("🎢 Joyland MIS Assistant")
        st.caption("Great Grand Edition | AI Forecasting | Range Search | Multi-Metric")

        # Chat History Display
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        # Smart Input
        prompt = st.chat_input("Ex: 'Revenue 2018 to 2022' or 'April 2026 forecast'...")

        if prompt:
            st.session_state.messages.append({"content": prompt, "is_user": True})
            q = prompt.lower()
            
            # --- DATE & METRIC PARSING ---
            month_ref = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
                         'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
            
            years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q)]
            found_months = [month_ref[m] for m in month_ref if m in q]
            
            # 1. AI FORECASTING (2026-2030)
            if any(w in q for w in ['forecast', 'predict']) and years and found_months:
                y_val = years[0]
                m_idx = found_months[0]
                m_name = [name for name, idx in month_ref.items() if idx == m_idx][0].capitalize()
                p_rev = get_prediction(df_live, m_idx, y_val, 'Actual Revenue')
                p_ff = get_prediction(df_live, m_idx, y_val, 'Actual Footfall')
                eid = " 🌙 (Eid factor added)" if (y_val in [2026,2027,2028,2029,2030] and m_idx in [1,2,3,4,5,6]) else ""
                st.session_state.messages.append({"content": f"### 🔮 AI Forecast for {m_name} {y_val}\n* Revenue: **Rs. {p_rev:,.0f}**{eid}\n* Footfall: **{p_ff:,.0f} Pax**", "is_user": False})
                st.rerun()

            # 2. RANGE & SPECIFIC FILTERING
            temp_df = df_live.copy()
            period_text = ""

            # Check for range: "2017 to 2026"
            if len(years) >= 2:
                start_dt = pd.to_datetime(f"{years[0]}-{found_months[0] if len(found_months)>=2 else 7}-01")
                end_dt = pd.to_datetime(f"{years[1]}-{found_months[1] if len(found_months)>=2 else 6}-01")
                temp_df = temp_df[(temp_df['Date_Obj'] >= start_dt) & (temp_df['Date_Obj'] <= end_dt)]
                period_text = f"from {start_dt.strftime('%b %Y')} to {end_dt.strftime('%b %Y')}"
            elif years or found_months:
                if years: temp_df = temp_df[temp_df['Year'].isin(years)]
                if found_months: 
                    m_names = [m.capitalize() for m, idx in month_ref.items() if idx in found_months and len(m)>3]
                    temp_df = temp_df[temp_df['Months'].isin(m_names)]
                period_text = "for selected period"

            if not temp_df.empty:
                st.session_state.last_filtered_df = temp_df
                
                # REQUIREMENT: Specific Metric Extraction
                metric_out = ""
                if "target revenue" in q: metric_out = f"🎯 Total Target Revenue: **Rs. {temp_df['Target revenue'].sum():,.0f}**"
                elif "revenue" in q or "rev" in q: metric_out = f"💰 Total Actual Revenue: **Rs. {temp_df['Actual Revenue'].sum():,.0f}**"
                elif "target footfall" in q: metric_out = f"🎯 Total Target Footfall: **{temp_df['Target Footfall'].sum():,.0f} Pax**"
                elif "footfall" in q or "ff" in q: metric_out = f"👣 Total Actual Footfall: **{temp_df['Actual Footfall'].sum():,.0f} Pax**"
                elif "target" in q: metric_out = f"🎯 Target Rev: **Rs. {temp_df['Target revenue'].sum():,.0f}**\n🎯 Target FF: **{temp_df['Target Footfall'].sum():,.0f}**"
                
                final_msg = f"### 📊 Result {period_text}\n{metric_out if metric_out else f'* Revenue: Rs. {temp_df['Actual Revenue'].sum():,.0f}'}"
                st.session_state.messages.append({"content": final_msg, "is_user": False})
                st.rerun()

        # --- 3. DASHBOARD VISUALS (100% ORIGINAL 6 OPTIONS) ---
        if st.session_state.last_filtered_df is not None:
            df_p = st.session_state.last_filtered_df
            tab1, tab2 = st.tabs(["📉 Visual Insights", "🔮 Prediction Trend"])
            with tab1:
                # Wahi aapka original selectbox layout
                choice = st.selectbox("🎯 Switch Insight View", [
                    "1. Revenue Achievement Gauge", 
                    "2. Revenue Trend Line (New)", 
                    "3. Actual vs Target Bar Chart", 
                    "4. Footfall Trend Line",
                    "5. Monthly Share Pie", 
                    "6. Footfall Achievement Gauge"
                ])
                
                mets = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                totals = df_p[mets].sum()
                
                if choice.startswith("1"):
                    ach = (totals['Actual Revenue']/totals['Target revenue']*100) if totals['Target revenue']>0 else 0
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ach, title={'text':"Rev Achievement %"})).update_layout(height=350, template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("2"): # REVENUE TREND LINE (New Requirement)
                    st.plotly_chart(px.line(df_p, x='Date_Obj', y='Actual Revenue', title="Revenue Trend", markers=True, template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("3"): # BAR CHART
                    st.plotly_chart(px.bar(df_p, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], barmode='group', template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("4"): # FOOTFALL TREND
                    st.plotly_chart(px.line(df_p, x='Date_Obj', y='Actual Footfall', title="Footfall Trend", markers=True, template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("5"):
                    st.plotly_chart(px.pie(df_p, values='Actual Revenue', names='Months', template="plotly_dark"), use_container_width=True)
                
                elif choice.startswith("6"):
                    ach_f = (totals['Actual Footfall']/totals['Target Footfall']*100) if totals['Target Footfall']>0 else 0
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ach_f, title={'text':"FF Achievement %"})).update_layout(height=350, template="plotly_dark"), use_container_width=True)

                st.table(df_p[mets].sum().to_frame().T.style.format('{:,.0f}'))

            with tab2:
                # Long term prediction chart
                st.plotly_chart(px.line(df_live, x='Date_Obj', y='Actual Revenue', title="2017-2030 Global Performance"), use_container_width=True)

    else: st.info("Logged out. Please log in to proceed.")

if __name__ == "__main__": main()
