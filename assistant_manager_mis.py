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
        
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] >= 7 else x['Year'] - 1}-{x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2030-12-01')
        
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- ADVANCED AI FORECASTING ENGINE ---
def generate_event_forecast(df, m_num, y_num, metric_col):
    df_clean = df.dropna(subset=[metric_col])
    if df_clean.empty: return 0
    X = np.array(range(len(df_clean))).reshape(-1, 1)
    y = df_clean[metric_col].values
    model = LinearRegression().fit(X, y)
    
    start_date = df_clean['Date_Obj'].min()
    target_date = pd.to_datetime(f"{y_num}-{m_num}-01")
    months_diff = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    base_pred = model.predict([[months_diff]])[0]
    
    # Islamic Events Multiplier (Eid Context 2026-2030)
    eid_calendar = {
        2026: [3, 4, 6], 2027: [3, 5, 6], 2028: [2, 5], 2029: [2, 4], 2030: [1, 4]
    }
    multiplier = 1.45 if (y_num in eid_calendar and m_num in eid_calendar[y_num]) else 1.0
    return max(0, base_pred * multiplier)

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    # --- CSS (100% Same Fixed Colors) ---
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
        div[data-testid="stMetricDelta"] > div { color: #3fb950 !important; background: rgba(63, 185, 80, 0.1); padding: 2px 8px; border-radius: 5px; }
        </style>
    """, unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_filtered_df" not in st.session_state:
        st.session_state.last_filtered_df = None
    if "comparison_data" not in st.session_state:
        st.session_state.comparison_data = None
    if "last_variance" not in st.session_state:
        st.session_state.last_variance = ""

    df_live = load_excel_data()

    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"🚀 Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Analysis History"):
            st.session_state.messages = []
            st.session_state.last_filtered_df = None
            st.session_state.comparison_data = None
            st.rerun()
        
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")
        st.sidebar.info("Operational Scope: 2017 – 2030")

        st.title("🎢 Joyland MIS Assistant")
        st.caption("Grand Master BI Edition | AI Event-Aware Predictions")

        if not df_live.empty:
            st.subheader("📍 Real-Time Performance Pulse")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Life-Time Revenue", f"Rs. {df_live['Actual Revenue'].sum():,.0f}", "Global Actual")
            k2.metric("Total Footfall", f"{df_live['Actual Footfall'].sum():,.0f} Pax", "Global Volume")
            k3.metric("Avg. Monthly Revenue", f"Rs. {df_live['Actual Revenue'].mean():,.0f}", "Trendline")
            k4.metric("AI Forecasting", "2030 Ready", "Islamic-Aware")

        st.divider()

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])
        with input_col:
            prompt = st.chat_input("Ex: 'July to Sep 2023 vs July to Sep 2024' or 'April 2026 forecast'...")
        with mic_col:
            st.audio_input("🎤", key="v_mic", label_visibility="collapsed")
        with clip_col:
            st.file_uploader("📎", type=['xlsx', 'csv'], key="f_clip", label_visibility="collapsed")

        if prompt:
            st.session_state.messages.append({"content": prompt, "is_user": True})
            query_lower = prompt.lower()
            
            # --- 1. AI FORECASTING LOGIC ---
            month_map_full = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
                             'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
            
            if any(f in query_lower for f in ['forecast', 'predict', 'btao', 'prediction']):
                found_m = next((m for m in month_map_full if m in query_lower), None)
                found_y = re.findall(r'\b(202[5-9]|2030)\b', query_lower)
                if found_m and found_y:
                    m_idx, y_val = month_map_full[found_m], int(found_y[0])
                    p_rev = generate_event_forecast(df_live, m_idx, y_val, 'Actual Revenue')
                    p_ff = generate_event_forecast(df_live, m_idx, y_val, 'Actual Footfall')
                    eid_alert = " 🌙 **(Islamic Event Month detected)**" if (y_val in [2026,2027,2028,2029,2030] and m_idx in [1,2,3,4,5,6]) else ""
                    ans = (f"### 🔮 AI Forecast: {found_m.capitalize()} {y_val}\n"
                           f"* Projected Revenue: **Rs. {p_rev:,.0f}**{eid_alert}\n"
                           f"* Projected Footfall: **{p_ff:,.0f} Pax**\n--- \n"
                           f"Note: Adjusted for historical trends and festive peaks.")
                    st.session_state.messages.append({"content": ans, "is_user": False})
                    st.rerun()

            # --- 2. ADVANCED COMPARISON ENGINE (Original Logic) ---
            month_pattern = r'(july|august|september|october|november|december|january|february|march|april|may|june)'
            variance_report = ""
            temp_df = df_live.copy()
            comp_viz_data = None

            if "vs" in query_lower:
                parts = query_lower.split("vs")
                if len(parts) == 2:
                    def get_period_df(text):
                        p_months = [m.capitalize() for m in re.findall(month_pattern, text)]
                        p_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', text)]
                        if not p_years: return pd.DataFrame(), ""
                        mask = (df_live['Year'].isin(p_years)) & (df_live['Months'].isin(p_months))
                        return df_live[mask], f"{', '.join(p_months)} {p_years[0]}"
                    
                    v1, l1 = get_period_df(parts[0])
                    v2, l2 = get_period_df(parts[1])
                    if not v1.empty and not v2.empty:
                        rev1, rev2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
                        ff1, ff2 = v1['Actual Footfall'].sum(), v2['Actual Footfall'].sum()
                        r_diff, f_diff = rev2 - rev1, ff2 - ff1
                        r_perc = (r_diff / rev1 * 100) if rev1 > 0 else 0
                        f_perc = (f_diff / ff1 * 100) if ff1 > 0 else 0
                        variance_report = (f"\n\n**Strategic Growth:**\n* Revenue: **Rs. {r_diff:,.0f}** ({r_perc:+.1f}%)\n"
                                           f"* Footfall: **{f_diff:,.0f}** ({f_perc:+.1f}%)")
                        temp_df = pd.concat([v1, v2])
                        comp_viz_data = {"labels": [l1, l2], "revenue": [rev1, rev2], "footfall": [ff1, ff2]}
            else:
                f_m = [m.capitalize() for m in re.findall(month_pattern, query_lower)]
                f_y = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
                if f_m: temp_df = temp_df[temp_df['Months'].isin(f_m)]
                if f_y: temp_df = temp_df[temp_df['Year'].isin(f_y)]

            st.session_state.last_filtered_df = temp_df
            st.session_state.comparison_data = comp_viz_data
            
            if not temp_df.empty:
                res = temp_df[["Actual Revenue", "Actual Footfall"]].sum()
                report = f"### 📊 Analysis Result\n* Total Revenue: **Rs. {res['Actual Revenue']:,.0f}**\n* Total Footfall: **{res['Actual Footfall']:,.0f}**{variance_report}"
                st.session_state.messages.append({"content": report, "is_user": False})
                st.rerun()

        # --- 3. DASHBOARD VISUALS (Achievement, Pie, Bar, Trend) ---
        if st.session_state.last_filtered_df is not None:
            df_plot = st.session_state.last_filtered_df
            tab1, tab2 = st.tabs(["📉 Data Insights", "🔮 Trend Analysis"])
            
            with tab1:
                if st.session_state.comparison_data:
                    c_data = st.session_state.comparison_data
                    fig_comp = go.Figure([
                        go.Bar(name='Revenue', x=c_data['labels'], y=c_data['revenue'], marker_color='#00CC96', textposition='auto'),
                        go.Bar(name='Footfall', x=c_data['labels'], y=c_data['footfall'], marker_color='#636EFA', textposition='auto')
                    ])
                    fig_comp.update_layout(barmode='group', title="Comparison Analysis", template="plotly_dark")
                    st.plotly_chart(fig_comp, use_container_width=True)

                c1, c2 = st.columns(2)
                with c1:
                    chart_sel = st.selectbox("🎯 Switch Chart", ["Actual vs Target", "Monthly Revenue Share", "Achievement Gauge"])
                    metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                    res_sum = df_plot[metrics].sum()
                    
                    if "Gauge" in chart_sel:
                        ach = (res_sum['Actual Revenue'] / res_sum['Target revenue'] * 100) if res_sum['Target revenue'] > 0 else 0
                        st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ach, title={'text':"Rev Achievement %"}, gauge={'bar':{'color':"#00CC96"}})).update_layout(height=300, template="plotly_dark"), use_container_width=True)
                    elif "Share" in chart_sel:
                        st.plotly_chart(px.pie(df_plot, values='Actual Revenue', names='Months', title="Revenue Share"), use_container_width=True)
                    else:
                        st.plotly_chart(px.bar(df_plot, x='Months', y=['Actual Revenue', 'Target revenue'], barmode='group'), use_container_width=True)
                
                with c2:
                    st.write("### Data Table")
                    st.table(df_plot[metrics].sum().to_frame().T.style.format('{:,.0f}'))

            with tab2:
                st.plotly_chart(px.line(df_live, x='Date_Obj', y='Actual Revenue', title="Long-Term Trend (2017-2030)"), use_container_width=True)

    else:
        st.markdown("<h1 style='text-align: center; color: #00CC96;'>Joyland BI Grand Master</h1>", unsafe_allow_html=True)
        st.info("Log in to access Umair Nizam's MIS Architecture.")

if __name__ == "__main__":
    main()
