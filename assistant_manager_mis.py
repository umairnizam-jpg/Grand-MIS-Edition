import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import datetime
import io
import warnings
from openai import OpenAI

warnings.filterwarnings('ignore')

# ==========================================
# PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="Joyland MIS Pro Max", layout="wide", initial_sidebar_state="expanded")

PAGE_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
:root {
  --bg-primary:#050b18; --bg-secondary:#0a1628; --accent-blue:#00c6ff;
}
.stApp { background-color: var(--bg-primary); color: #e8f4fd; font-family: 'Rajdhani', sans-serif; }
h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: var(--accent-blue); text-transform: uppercase; }
.stChatMessage { background-color: var(--bg-secondary) !important; border: 1px solid #1a3a6b !important; border-radius: 10px; }
.stButton>button { background: linear-gradient(90deg, #00c6ff, #0072ff); color: white; border: none; font-weight: bold; border-radius: 5px; }
.stDataFrame { background-color: #0a1628 !important; }
div[data-testid="stSidebar"] { background-color: #030710 !important; border-right: 2px solid #00c6ff; }
</style>
"""
st.markdown(PAGE_THEME, unsafe_allow_html=True)

# ==========================================
# AUTHENTICATION
# ==========================================
USER_CREDENTIALS = {'Admin': 'admin123', 'user': 'user123'}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

def login():
    st.markdown("<h1 style='text-align: center;'>SYSTEM LOGIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("ACCESS SYSTEM")
            
            if submit:
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.user_role = username
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Credentials.")

if not st.session_state.authenticated:
    login()
    st.stop()

# ==========================================
# DATA LOADING & CLEANING
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("RAW DATA.xlsx - Sheet1.csv")
    except Exception:
        # Fallback if file not found locally
        return pd.DataFrame()
    
    df.columns = df.columns.str.strip()
    df.replace('-', np.nan, inplace=True)
    
    for col in ['Actual Revenue', 'Actual Footfall', 'Target revenue', 'Target Footfall']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    month_map = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 
                 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
    df['Month_Num'] = df['Months'].map(month_map)
    df.dropna(subset=['Year', 'Month_Num'], inplace=True)
    df['Year'] = df['Year'].astype(int)
    df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
    return df.sort_values('Date_Obj').reset_index(drop=True)

df = load_data()

# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=100)
    st.markdown("### SYSTEM CONTROLS")
    st.write(f"Logged in as: **{st.session_state.user_role}**")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 🤖 API SETTINGS")
    api_key = st.text_input("OpenAI API Key (Required for AI Bot)", type="password", help="Enter your OpenAI key for Globle Search & Advanced Context.")
    
    st.markdown("---")
    st.markdown("### DATA FILTERS")
    if not df.empty:
        all_projects = ["ALL"] + list(df['Projetcs'].unique())
        selected_project = st.selectbox("Select Project", all_projects)
        
        min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
        selected_years = st.slider("Select Year Range", min_year, max_year, (min_year, max_year))
        
        df_filtered = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]
        if selected_project != "ALL":
            df_filtered = df_filtered[df_filtered['Projetcs'] == selected_project]
    else:
        st.warning("Data file not found.")
        df_filtered = pd.DataFrame()

# ==========================================
# MAIN APPLICATION TABS
# ==========================================
st.markdown("<h1>🚀 JOYLAND MIS PRO MAX DASHBOARD</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 DASHBOARD", "🤖 EXPERT AI BOT", "📈 FORECASTING PRO", "📊 ANALYTICS", "💾 RAW DATA & EXPORT"])

# ─ TAB 1: DASHBOARD ─
with tab1:
    if not df_filtered.empty:
        total_rev = df_filtered['Actual Revenue'].sum()
        total_foot = df_filtered['Actual Footfall'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("TOTAL REVENUE", f"Rs {total_rev:,.0f}")
        col2.metric("TOTAL FOOTFALL", f"{total_foot:,.0f}")
        col3.metric("PROJECTS ACTIVE", len(df_filtered['Projetcs'].unique()))
        col4.metric("DATA POINTS", len(df_filtered))
        
        st.markdown("### 📈 Revenue & Footfall Trends")
        trend_df = df_filtered.groupby('Date_Obj')[['Actual Revenue', 'Actual Footfall']].sum().reset_index()
        
        fig_trend = px.area(trend_df, x='Date_Obj', y='Actual Revenue', title='Revenue Trend (Over Time)', 
                            color_discrete_sequence=['#00c6ff'], template='plotly_dark')
        fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trend, use_container_width=True)

# ─ TAB 2: EXPERT AI BOT (OPENAI) ─
with tab2:
    st.markdown("### 🤖 Ask Anything (Global Data + Internal MIS Data)")
    
    # Custom File Uploader for Context
    uploaded_file = st.file_uploader("Upload additional CSV/Excel file for AI Analysis", type=["csv", "xlsx"])
    custom_context = ""
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                temp_df = pd.read_csv(uploaded_file)
            else:
                temp_df = pd.read_excel(uploaded_file)
            custom_context = f"\nUser Uploaded File Summary:\n{temp_df.head(10).to_string()}\nColumns: {temp_df.columns.tolist()}"
            st.success(f"{uploaded_file.name} loaded successfully! The AI can now answer questions about it.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Zabardast! Main Joyland MIS ka Expert AI hoon. Data, global search, ya uploaded file sy related kuch bhi poochein!"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about revenue, footfall, forecasting, or upload a file..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if api_key:
                try:
                    client = OpenAI(api_key=api_key)
                    
                    # Context Building
                    system_prompt = f"""You are the Joyland MIS Pro Max AI Assistant. 
                    You are an expert data analyst. You understand Urdu/English mix (Roman Urdu) and English perfectly.
                    Respond professionally, accurately, and concisely. DO NOT invent numbers.
                    
                    CURRENT SYSTEM DATA SUMMARY:
                    Total Projects: {len(df['Projetcs'].unique())}
                    Total Revenue System-wide: Rs {df['Actual Revenue'].sum():,.0f}
                    Date Range: {df['Year'].min()} to {df['Year'].max()}
                    {custom_context}
                    """
                    
                    stream = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": system_prompt}] + 
                                 [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"OpenAI API Error: {e}")
            else:
                st.warning("⚠️ Please enter your OpenAI API Key in the sidebar to activate the Advanced Bot.")

# ─ TAB 3: FORECASTING PRO (PAKISTAN CONTEXT) ─
with tab3:
    st.markdown("### 🔮 Advanced Forecasting Engine")
    st.write("Calculates trends based on historical data + Pakistan's seasonal weights (Eid bumps, Summer vacations).")
    
    if not df_filtered.empty:
        proj_to_forecast = st.selectbox("Select Project for Forecast", df_filtered['Projetcs'].unique())
        metric = st.selectbox("Metric to Forecast", ["Actual Revenue", "Actual Footfall"])
        
        f_df = df_filtered[df_filtered['Projetcs'] == proj_to_forecast].copy()
        f_df = f_df.groupby(['Year', 'Month_Num'])[metric].sum().reset_index()
        f_df['Time_Index'] = (f_df['Year'] - f_df['Year'].min()) * 12 + f_df['Month_Num']
        
        # Polynomial Regression Pipeline
        model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
        X = f_df[['Time_Index']]
        y = f_df[metric]
        
        if len(X) > 2:
            model.fit(X, y)
            
            # Future prediction (Next 24 months)
            last_year = f_df['Year'].max()
            last_month = f_df['Month_Num'].max()
            future_indices = []
            future_dates = []
            future_months = []
            
            curr_y = last_year
            curr_m = last_month
            
            for i in range(1, 25):
                curr_m += 1
                if curr_m > 12:
                    curr_m = 1
                    curr_y += 1
                idx = (curr_y - f_df['Year'].min()) * 12 + curr_m
                future_indices.append([idx])
                future_dates.append(pd.to_datetime(f"{curr_y}-{curr_m}-01"))
                future_months.append(curr_m)
                
            base_predictions = model.predict(future_indices)
            
            # 🔴 PAKISTAN CONTEXT MULTIPLIERS (Simulated Seasonality)
            # March (Spring/PSL), June/July (Summer Holidays), Nov (Winter start) often have spikes.
            # Ramadan/Eid drops & spikes are dynamic, but we use typical high-traffic month multipliers.
            pak_multipliers = {
                1: 1.0, 2: 1.05, 3: 1.20, 4: 0.90, 5: 0.95, 6: 1.30, 
                7: 1.35, 8: 1.10, 9: 0.90, 10: 1.05, 11: 1.15, 12: 1.25
            }
            
            adjusted_predictions = []
            for pred, month in zip(base_predictions, future_months):
                adj = pred * pak_multipliers.get(month, 1.0)
                adjusted_predictions.append(max(0, adj)) # Prevent negative forecasting
            
            forecast_df = pd.DataFrame({'Date': future_dates, 'Forecasted Value': adjusted_predictions})
            
            fig_fc = go.Figure()
            # Historical
            fig_fc.add_trace(go.Scatter(x=pd.to_datetime(f_df['Year'].astype(str) + '-' + f_df['Month_Num'].astype(str) + '-01'), 
                                        y=f_df[metric], mode='lines+markers', name='Historical', line=dict(color='#00c6ff')))
            # Forecast
            fig_fc.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecasted Value'], 
                                        mode='lines+markers', name='Forecast (Adjusted)', line=dict(color='#ff00c6', dash='dash')))
            
            fig_fc.update_layout(title=f'{metric} Forecast for {proj_to_forecast}', template='plotly_dark',
                                 plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_fc, use_container_width=True)

# ─ TAB 4: ANALYTICS ─
with tab4:
    st.markdown("### 📊 Advanced Visualizations")
    if not df_filtered.empty:
        col1, col2 = st.columns(2)
        with col1:
            rev_by_proj = df_filtered.groupby('Projetcs')['Actual Revenue'].sum().reset_index()
            # Added text_auto for clear visible numbers
            fig_bar = px.bar(rev_by_proj, x='Projetcs', y='Actual Revenue', title='Revenue by Project', 
                             text_auto='.2s', color='Projetcs', template='plotly_dark')
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            foot_by_proj = df_filtered.groupby('Projetcs')['Actual Footfall'].sum().reset_index()
            fig_pie = px.pie(foot_by_proj, names='Projetcs', values='Actual Footfall', title='Footfall Distribution', 
                             hole=0.4, template='plotly_dark')
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

# ─ TAB 5: RAW DATA & EXPORT ─
with tab5:
    st.markdown("### 💾 Raw Data Explorer & Exporter")
    if not df_filtered.empty:
        st.dataframe(df_filtered.style.background_gradient(cmap='Blues'), use_container_width=True)
        
        st.markdown("### 📥 Download Data")
        col1, col2 = st.columns(2)
        
        # EXPORT TO CSV
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        col1.download_button("⬇️ Download as CSV", data=csv, file_name="Joyland_Data_Export.csv", mime="text/csv")
        
        # EXPORT TO EXCEL
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_data = output.getvalue()
        col2.download_button("⬇️ Download as Excel", data=excel_data, file_name="Joyland_Data_Export.xlsx", 
                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        st.info("💡 PDF and Word exports can be done by downloading the Excel file and using 'Save As PDF' in MS Excel, ensuring perfect formatting.")
