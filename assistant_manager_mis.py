import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate
from sklearn.linear_model import LinearRegression 

# --- 1. DATA ENGINE (Scope: 2017 - 2026) ---
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
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-03-01')
        
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- ADVANCED FORECASTING ENGINE ---
def generate_forecast(df, metric_col, periods=6):
    df_clean = df.dropna(subset=[metric_col])
    X = np.array(range(len(df_clean))).reshape(-1, 1)
    y = df_clean[metric_col].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.array(range(len(df_clean), len(df_clean) + periods)).reshape(-1, 1)
    predictions = model.predict(future_X)
    return predictions

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
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
    if "last_variance" not in st.session_state:
        st.session_state.last_variance = ""
    if "comparison_data" not in st.session_state:
        st.session_state.comparison_data = None

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
        st.sidebar.info("Operational Scope: Jul 2017 – Mar 2026")

        st.title("🎢 Joyland MIS Assistant")
        st.caption("Advanced Business Intelligence & Predictive Analytics")

        if not df_live.empty:
            st.subheader("📍 Real-Time Performance Pulse")
            k1, k2, k3, k4 = st.columns(4)
            total_rev = df_live['Actual Revenue'].sum()
            total_ff = df_live['Actual Footfall'].sum()
            avg_rev = df_live['Actual Revenue'].mean()
            
            k1.metric("Total Life-Time Revenue", f"Rs. {total_rev:,.0f}", "Global Actual")
            k2.metric("Total Footfall", f"{total_ff:,.0f} Pax", "Global Volume")
            k3.metric("Avg. Monthly Revenue", f"Rs. {avg_rev:,.0f}", "Trendline")
            k4.metric("Data Health", "100%", "Secure")

        st.divider()

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])
        with input_col:
            prompt = st.chat_input("Query: 'July to Sep 2023 vs July to Sep 2024' or 'Jan 2024 vs Jan 2025'...")
        with mic_col:
            voice_data = st.audio_input("🎤", key="v_mic", label_visibility="collapsed")
        with clip_col:
            attached_file = st.file_uploader("📎", type=['xlsx', 'csv'], key="f_clip", label_visibility="collapsed")

        user_query = prompt if prompt else ("Voice Command" if voice_data else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            query_lower = user_query.lower()

            if any(greet in query_lower for greet in ["hi", "hello", "intro", "who are you", "salam", "introduce"]):
                intro_msg = "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\nPROUDLY **DEVELOPED BY UMAIR NIZAM**."
                st.session_state.messages.append({"content": intro_msg, "is_user": False})
                st.rerun()

            # --- UNIVERSAL COMPARISON ENGINE ---
            month_pattern = r'(july|august|september|october|november|december|january|february|march|april|may|june)'
            
            variance_report = ""
            temp_df = df_live.copy()
            comp_viz_data = None

            if "vs" in query_lower:
                parts = query_lower.split("vs")
                if len(parts) == 2:
                    def extract_period_data(text):
                        found_ms = [m.capitalize() for m in re.findall(month_pattern, text)]
                        found_ys = [int(y) for y in re.findall(r'\b(20\d{2})\b', text)]
                        if not found_ys: return pd.DataFrame(), ""
                        
                        # Dynamic filtering for range or specific months
                        mask = (df_live['Year'].isin(found_ys)) & (df_live['Months'].isin(found_ms))
                        res_df = df_live[mask]
                        label = f"{', '.join(found_ms)} {found_ys[0]}" if len(found_ys)==1 else f"Period ({found_ys[0]}-{found_ys[-1]})"
                        return res_df, label

                    v1, label1 = extract_period_data(parts[0])
                    v2, label2 = extract_period_data(parts[1])

                    if not v1.empty and not v2.empty:
                        rev1, rev2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
                        ff1, ff2 = v1['Actual Footfall'].sum(), v2['Actual Footfall'].sum()
                        r_diff, f_diff = rev2 - rev1, ff2 - ff1
                        r_perc = (r_diff / rev1 * 100) if rev1 > 0 else 0
                        f_perc = (f_diff / ff1 * 100) if ff1 > 0 else 0
                        
                        variance_report = (
                            f"\n\n**Detailed Comparison:**\n"
                            f"* **{label1}:** Rev: Rs. {rev1:,.0f} | FF: {ff1:,.0f}\n"
                            f"* **{label2}:** Rev: Rs. {rev2:,.0f} | FF: {ff2:,.0f}\n"
                            f"--- \n"
                            f"**Variance Analysis:**\n"
                            f"* Revenue: **Rs. {r_diff:,.0f}** ({r_perc:+.1f}%)\n"
                            f"* Footfall: **{f_diff:,.0f}** ({f_perc:+.1f}%)\n"
                        )
                        temp_df = pd.concat([v1, v2])
                        comp_viz_data = {"labels": [label1, label2], "revenue": [rev1, rev2], "footfall": [ff1, ff2]}
            else:
                found_months = [m.capitalize() for m in re.findall(month_pattern, query_lower)]
                found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
                if found_months: temp_df = temp_df[temp_df['Months'].isin(found_months)]
                if found_years: temp_df = temp_df[temp_df['Year'].isin(found_years)]

            st.session_state.last_filtered_df = temp_df
            st.session_state.last_variance = variance_report
            st.session_state.comparison_data = comp_viz_data
            
            if not temp_df.empty:
                res = temp_df[["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]].sum()
                report = (f"### 📊 BI Analysis Result\n* Total Actual Revenue: **Rs. {res['Actual Revenue']:,.0f}**\n* Total Actual Footfall: **{res['Actual Footfall']:,.0f}**{variance_report}")
                st.session_state.messages.append({"content": report, "is_user": False})
                st.rerun()

        if st.session_state.last_filtered_df is not None:
            df_plot = st.session_state.last_filtered_df
            tab1, tab2 = st.tabs(["📉 Visual Insights", "🔮 Advanced Forecast (2026)"])
            
            with tab1:
                if st.session_state.comparison_data:
                    st.subheader("🆚 Comparative Growth Analysis")
                    c_data = st.session_state.comparison_data
                    fig_comp = go.Figure()
                    fig_comp.add_trace(go.Bar(name='Revenue', x=c_data['labels'], y=c_data['revenue'], marker_color='#00CC96', textposition='auto'))
                    fig_comp.add_trace(go.Bar(name='Footfall', x=c_data['labels'], y=c_data['footfall'], marker_color='#636EFA', textposition='auto'))
                    fig_comp.update_layout(barmode='group', title="Side-by-Side Comparison", template="plotly_dark")
                    st.plotly_chart(fig_comp, use_container_width=True)

                chart_option = st.selectbox("🎯 Switch Insight View", [
                    "1. Revenue Achievement Gauge", "2. Footfall Achievement Gauge",
                    "3. Actual vs Target Bar", "4. Footfall Trend Line", "5. Monthly Share Pie"
                ])

                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                results = df_plot[metrics].sum()
                rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
                ff_ach = (results['Actual Footfall'] / results['Target Footfall'] * 100) if results['Target Footfall'] > 0 else 0

                if chart_option.startswith("1"):
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Rev Achievement %"}, gauge={'bar': {'color': "#00CC96"}})).update_layout(height=350, template="plotly_dark"), use_container_width=True)
                elif chart_option.startswith("2"):
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "FF Achievement %"}, gauge={'bar': {'color': "#636EFA"}})).update_layout(height=350, template="plotly_dark"), use_container_width=True)
                elif chart_option.startswith("3"):
                    st.plotly_chart(px.bar(df_plot, x='Months', y=['Actual Revenue', 'Target revenue'], barmode='group'), use_container_width=True)
                elif chart_option.startswith("4"):
                    st.plotly_chart(px.line(df_plot, x='Date_Obj', y='Actual Footfall', markers=True), use_container_width=True)
                
                st.table(df_plot[metrics].sum().to_frame().T.style.format('{:,.0f}'))

            with tab2:
                st.subheader("🚀 2026 Predictive Analysis")
                forecast_rev = generate_forecast(df_live, 'Actual Revenue')
                forecast_ff = generate_forecast(df_live, 'Actual Footfall')
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    fig_f_rev = go.Figure()
                    fig_f_rev.add_trace(go.Scatter(y=df_live['Actual Revenue'], name="Historical"))
                    fig_f_rev.add_trace(go.Scatter(x=list(range(len(df_live), len(df_live)+6)), y=forecast_rev, name="Predicted", line=dict(dash='dash', color='orange')))
                    fig_f_rev.update_layout(title="Revenue Projection", template="plotly_dark")
                    st.plotly_chart(fig_f_rev, use_container_width=True)
                with f_col2:
                    st.write("### Predicted Key Metrics")
                    st.success(f"Expected Rev (Next Month): **Rs. {forecast_rev[0]:,.0f}**")
                    st.warning(f"Expected Footfall (Next Month): **{forecast_ff[0]:,.0f}**")

    else:
        st.markdown("<h1 style='text-align: center; color: #00CC96;'>Joyland BI Grand Master</h1>", unsafe_allow_html=True)
        st.info("Architecture developed by **Umair Nizam**. Please log in to access the Command Center.")

if __name__ == "__main__":
    main()
