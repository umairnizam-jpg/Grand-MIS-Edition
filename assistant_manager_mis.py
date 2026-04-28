import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- ERROR HANDLING FOR LIBRARIES ---
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

# --- 1. DATA ENGINE (Scope: 2017 - 2026) ---
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

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
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
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.last_filtered_df = None
            st.session_state.comparison_data = None
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")
        st.sidebar.info("Scope: July 2017 – March 2026")

        st.title("🎢 Joyland MIS Assistant")

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        st.markdown("---")
        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])

        with input_col:
            prompt = st.chat_input("Ask about Revenue, Footfall, Comparisons...")
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

            month_pattern = r'(july|august|september|october|november|december|january|february|march|april|may|june)'
            years_in_query = re.findall(r'\b(20\d{2})\b', query_lower)
            months_in_query = re.findall(month_pattern, query_lower)
            
            variance_report = ""
            temp_df = pd.DataFrame()
            comp_viz_data = None

            # Date Range Detection
            if " to " in query_lower or len(years_in_query) >= 2:
                if len(years_in_query) >= 2:
                    y_start, y_end = sorted([int(years_in_query[0]), int(years_in_query[-1])])
                    if len(months_in_query) >= 2:
                        m_start, m_end = months_in_query[0].capitalize(), months_in_query[-1].capitalize()
                        start_date = pd.to_datetime(f"{y_start}-{m_start}-01")
                        end_date = pd.to_datetime(f"{y_end}-{m_end}-01")
                    else:
                        start_date = pd.to_datetime(f"{y_start}-07-01")
                        end_date = pd.to_datetime(f"{y_end}-06-30")
                    temp_df = df_live[(df_live['Date_Obj'] >= start_date) & (df_live['Date_Obj'] <= end_date)]
            
            if temp_df.empty:
                matches = re.findall(rf'{month_pattern}\s*(20\d{{2}})', query_lower)
                if len(matches) >= 2:
                    # Comparison Logic
                    found_years = sorted(list(set([int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)])))
                    found_months = [m.capitalize() for m in re.findall(month_pattern, query_lower)]
                    if len(found_years) >= 2 and found_months:
                        y1, y2 = found_years[0], found_years[1]
                        v1 = df_live[(df_live['Year'] == y1) & (df_live['Months'].isin(found_months))]
                        v2 = df_live[(df_live['Year'] == y2) & (df_live['Months'].isin(found_months))]
                        if not v1.empty and not v2.empty:
                            rev1, rev2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
                            ff1, ff2 = v1['Actual Footfall'].sum(), v2['Actual Footfall'].sum()
                            r_diff, f_diff = rev2 - rev1, ff2 - ff1
                            r_perc = (r_diff / rev1 * 100) if rev1 > 0 else 0
                            f_perc = (f_diff / ff1 * 100) if ff1 > 0 else 0
                            variance_report = f"\n\n**Growth:** Revenue: Rs. {r_diff:,.0f} ({r_perc:.1f}%) | FF: {f_diff:,.0f} ({f_perc:.1f}%)"
                            temp_df = pd.concat([v1, v2])
                            comp_viz_data = {"labels": [str(y1), str(y2)], "revenue": [rev1, rev2], "footfall": [ff1, ff2]}
                else:
                    # Filtered logic
                    temp_df = df_live.copy()
                    if months_in_query: temp_df = temp_df[temp_df['Months'].isin([m.capitalize() for m in months_in_query])]
                    if years_in_query: temp_df = temp_df[temp_df['Year'].isin([int(y) for y in years_in_query])]

            st.session_state.last_filtered_df = temp_df
            st.session_state.last_variance = variance_report
            st.session_state.comparison_data = comp_viz_data
            
            if not temp_df.empty:
                res = temp_df[["Actual Revenue", "Actual Footfall"]].sum()
                report = f"### 📊 Result\n* Revenue: **Rs. {res['Actual Revenue']:,.0f}**\n* Footfall: **{res['Actual Footfall']:,.0f}**{variance_report}"
                st.session_state.messages.append({"content": report, "is_user": False})
                st.rerun()

        if st.session_state.last_filtered_df is not None and not st.session_state.last_filtered_df.empty:
            df_plot = st.session_state.last_filtered_df
            metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
            results = df_plot[metrics].sum()
            
            st.divider()
            chart_option = st.selectbox("🎯 Select Chart", [
                "1. Revenue Achievement Gauge", "2. Actual Revenue (Bar Chart)", 
                "3. Revenue vs Target (Bar)", "4. Footfall Trend (Line)", 
                "5. Revenue Trend (Line)", "6. Revenue Share (Pie)"
            ])

            if chart_option.startswith("1"):
                rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Rev Ach %"})).update_layout(height=350, template="plotly_dark"), use_container_width=True)
            
            elif chart_option.startswith("2"): # REVENUE BAR CHART ADDED
                st.plotly_chart(px.bar(df_plot, x='Date_Obj', y='Actual Revenue', color='Months', title="Actual Revenue by Month"), use_container_width=True)
                
            elif chart_option.startswith("3"):
                st.plotly_chart(px.bar(df_plot, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], barmode='group', title="Revenue vs Target"), use_container_width=True)
            
            elif chart_option.startswith("4"):
                st.plotly_chart(px.line(df_plot, x='Date_Obj', y='Actual Footfall', markers=True, title="Footfall Trend"), use_container_width=True)
            
            elif chart_option.startswith("5"):
                st.plotly_chart(px.line(df_plot, x='Date_Obj', y='Actual Revenue', markers=True, title="Revenue Trend"), use_container_width=True)
            
            elif chart_option.startswith("6"):
                st.plotly_chart(px.pie(df_plot, values='Actual Revenue', names='Months', hole=0.4, title="Revenue Share"), use_container_width=True)

            st.table(df_plot[metrics].sum().to_frame().T.style.format('{:,.0f}'))

    else:
        st.info("System Developed by **Umair Nizam**. Please log in to proceed.")

if __name__ == "__main__":
    main()
