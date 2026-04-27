import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

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

    df_live = load_excel_data()

    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.last_filtered_df = None
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

            # Date Range Extraction
            found_years = sorted(list(set([int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)])))
            month_list = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in month_list if m in query_lower or m[:3] in query_lower]
            
            variance_report = ""
            temp_df = df_live.copy()

            # Logic for Fiscal Year/Range Comparison
            if len(found_years) >= 2:
                # Divide data into two periods based on years found
                y1, y2 = found_years[0], found_years[-1]
                v1 = df_live[df_live['Year'] == y1]
                v2 = df_live[df_live['Year'] == y2]
                
                # If months are specified, filter further
                if found_months:
                    v1 = v1[v1['Months'].isin(found_months)]
                    v2 = v2[v2['Months'].isin(found_months)]
                
                if not v1.empty and not v2.empty:
                    rev1, rev2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
                    ff1, ff2 = v1['Actual Footfall'].sum(), v2['Actual Footfall'].sum()
                    r_diff, f_diff = rev2 - rev1, ff2 - ff1
                    r_perc = (r_diff / rev1 * 100) if rev1 > 0 else 0
                    f_perc = (f_diff / ff1 * 100) if ff1 > 0 else 0
                    
                    variance_report = (
                        f"\n\n**Period Comparison:**\n"
                        f"* **{y1} Data:** Rev: Rs. {rev1:,.0f} | FF: {ff1:,.0f}\n"
                        f"* **{y2} Data:** Rev: Rs. {rev2:,.0f} | FF: {ff2:,.0f}\n"
                        f"--- \n"
                        f"**Variance:**\n"
                        f"* Revenue: **Rs. {r_diff:,.0f}** ({r_perc:.1f}%)\n"
                        f"* Footfall: **{f_diff:,.0f}** ({f_perc:.1f}%)\n"
                    )
                    temp_df = pd.concat([v1, v2])
            else:
                if found_months: temp_df = temp_df[temp_df['Months'].isin(found_months)]
                if found_years: temp_df = temp_df[temp_df['Year'].isin(found_years)]

            st.session_state.last_filtered_df = temp_df
            st.session_state.last_variance = variance_report
            
            if not temp_df.empty:
                res = temp_df[["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]].sum()
                rev_a = (res['Actual Revenue'] / res['Target revenue'] * 100) if res['Target revenue'] > 0 else 0
                ff_a = (res['Actual Footfall'] / res['Target Footfall'] * 100) if res['Target Footfall'] > 0 else 0
                
                report = (
                    f"### 📊 BI Analysis Result\n"
                    f"* Total Actual Revenue: **Rs. {res['Actual Revenue']:,.0f}** ({rev_a:.1f}% Ach)\n"
                    f"* Total Actual Footfall: **{res['Actual Footfall']:,.0f}** ({ff_a:.1f}% Ach)"
                    f"{variance_report}"
                )
                st.session_state.messages.append({"content": report, "is_user": False})
                st.rerun()

        # Visual Section (Persistent)
        if st.session_state.last_filtered_df is not None:
            df_plot = st.session_state.last_filtered_df
            metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
            results = df_plot[metrics].sum()
            rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
            ff_ach = (results['Actual Footfall'] / results['Target Footfall'] * 100) if results['Target Footfall'] > 0 else 0

            st.divider()
            chart_option = st.selectbox("🎯 Select Chart to Display", [
                "1. Revenue Achievement Gauge", "2. Footfall Achievement Gauge",
                "3. Revenue: Actual vs Target (Bar)", "4. Footfall Trend (Line)",
                "5. Monthly Revenue Share (Pie)", "6. Revenue Volume (Area)",
                "7. Footfall vs Revenue (Correlation)", "8. Revenue Target Funnel"
            ])

            if chart_option.startswith("1"):
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Rev Ach %"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00CC96"}})).update_layout(height=400, template="plotly_dark"), use_container_width=True)
            elif chart_option.startswith("2"):
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "FF Ach %"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#636EFA"}})).update_layout(height=400, template="plotly_dark"), use_container_width=True)
            elif chart_option.startswith("3"):
                st.plotly_chart(px.bar(df_plot, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], barmode='group', title="Revenue Comparison"), use_container_width=True)
            elif chart_option.startswith("4"):
                st.plotly_chart(px.line(df_plot, x='Date_Obj', y='Actual Footfall', markers=True, title="Footfall Trend"), use_container_width=True)
            elif chart_option.startswith("5"):
                st.plotly_chart(px.pie(df_plot, values='Actual Revenue', names='Months', hole=0.4, title="Revenue Share"), use_container_width=True)
            elif chart_option.startswith("6"):
                st.plotly_chart(px.area(df_plot, x='Date_Obj', y='Actual Revenue', title="Revenue Volume"), use_container_width=True)
            elif chart_option.startswith("7"):
                st.plotly_chart(px.scatter(df_plot, x='Actual Footfall', y='Actual Revenue', size='Actual Revenue', color='Months', title="Correlation"), use_container_width=True)
            elif chart_option.startswith("8"):
                fig = go.Figure(go.Funnel(y=["Target", "Actual"], x=[results['Target revenue'], results['Actual Revenue']], textinfo="value+percent initial"))
                fig.update_layout(title="Revenue Funnel", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            st.table(df_plot[metrics].sum().to_frame().T.style.format('{:,.0f}'))

    else:
        st.info("System Developed by **Umair Nizam**. Please log in to proceed.")

if __name__ == "__main__":
    main()
