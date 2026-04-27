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
            lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        
        return df.loc[mask].sort_values('Date_Obj')
    except:
        return pd.DataFrame()

# --- 2. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    df_live = load_excel_data()

    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")
        st.sidebar.info("Scope: July 2017 – June 2026")

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

        user_query = None
        if prompt:
            user_query = prompt
        elif voice_data:
            user_query = "Voice Command Received"

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            query_lower = user_query.lower()

            if any(greet in query_lower for greet in ["hi", "hello", "intro", "who are you", "salam", "introduce"]):
                intro_msg = (
                    "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\n"
                    "I am a highly intelligent Business Intelligence & Data Analyst assistant, "
                    "proudly **developed by Umair Nizam**. My architecture is optimized to track, "
                    "analyze, and visualize performance data for **Joyland Fortress**.\n\n"
                    "**My Expert Scope:**\n"
                    "* 📅 **Timeframe:** Data from July 2017 to June 2026.\n"
                    "* 💹 **Analytics:** Revenue & Footfall achievements and YoY comparisons.\n"
                    "* 📎 **Flexibility:** Attach your own files using the clip icon for instant analysis.\n\n"
                    "How can I assist your data-driven decisions today?"
                )
                st.session_state.messages.append({"content": intro_msg, "is_user": False})
                st.rerun()

            if df_live.empty:
                st.session_state.messages.append({"content": "❌ **Data Error:** Master file `RAW DATA.xlsx` not found.", "is_user": False})
                st.rerun()

            # --- ADVANCED DATE & COMPARISON EXTRACTION ---
            month_list = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in month_list if m in query_lower or m[:3] in query_lower]
            found_years = sorted([int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)])
            
            # Logic for specific comparisons (e.g., July 2023 vs Aug 2024)
            date_pairs = re.findall(r'(july|august|september|october|november|december|january|february|march|april|may|june)\s?(\20\d{2})', query_lower)
            
            variance_report = ""
            filtered_df = df_live.copy()

            if len(date_pairs) >= 2:
                # Comparison between two specific month-year points
                m1, y1 = date_pairs[0][0].capitalize(), int(date_pairs[0][1])
                m2, y2 = date_pairs[1][0].capitalize(), int(date_pairs[1][1])
                
                v1 = df_live[(df_live['Months'] == m1) & (df_live['Year'] == y1)]
                v2 = df_live[(df_live['Months'] == m2) & (df_live['Year'] == y2)]
                
                if not v1.empty and not v2.empty:
                    rev1, rev2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
                    diff = rev2 - rev1
                    perc = (diff / rev1 * 100) if rev1 > 0 else 0
                    variance_report = f"\n\n**Period Comparison:**\n* {m1} {y1}: **Rs. {rev1:,.0f}**\n* {m2} {y2}: **Rs. {rev2:,.0f}**\n* Variance: **Rs. {diff:,.0f}** ({perc:.1f}%)\n"
                    filtered_df = pd.concat([v1, v2])
            
            elif len(found_years) >= 2 and found_months:
                # Comparison between sum of same months across different years
                y1, y2 = found_years[0], found_years[1]
                v1 = df_live[(df_live['Year'] == y1) & (df_live['Months'].isin(found_months))]
                v2 = df_live[(df_live['Year'] == y2) & (df_live['Months'].isin(found_months))]
                
                if not v1.empty and not v2.empty:
                    rev1, rev2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
                    diff = rev2 - rev1
                    perc = (diff / rev1 * 100) if rev1 > 0 else 0
                    variance_report = f"\n\n**Multi-Month Comparison ({', '.join(found_months)}):**\n* {y1} Total: **Rs. {rev1:,.0f}**\n* {y2} Total: **Rs. {rev2:,.0f}**\n* Variance: **Rs. {diff:,.0f}** ({perc:.1f}%)\n"
                    filtered_df = pd.concat([v1, v2])
            else:
                if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
                if found_years: filtered_df = filtered_df[filtered_df['Year'].isin(found_years)]

            if not filtered_df.empty:
                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                results = filtered_df[metrics].sum()
                rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
                ff_ach = (results['Actual Footfall'] / results['Target Footfall'] * 100) if results['Target Footfall'] > 0 else 0

                report = (
                    f"### 📊 BI Analysis Result\n"
                    f"**Financial Performance:**\n"
                    f"* Actual Revenue: **Rs. {results['Actual Revenue']:,.0f}**\n"
                    f"* Achievement: **{rev_ach:.1f}%**\n\n"
                    f"**Footfall Analysis:**\n"
                    f"* Actual Footfall: **{results['Actual Footfall']:,.0f}**\n"
                    f"* Achievement: **{ff_ach:.1f}%**"
                    f"{variance_report}"
                )
                
                st.session_state.messages.append({"content": report, "is_user": False})

                # --- NEW CHART SELECTOR INTERFACE ---
                st.divider()
                chart_option = st.selectbox("🎯 Select Chart to Display", [
                    "1. Revenue Achievement Gauge",
                    "2. Footfall Achievement Gauge",
                    "3. Revenue: Actual vs Target (Bar)",
                    "4. Footfall Trend (Line)",
                    "5. Monthly Revenue Share (Pie)",
                    "6. Revenue Volume (Area)",
                    "7. Footfall vs Revenue (Correlation)",
                    "8. Revenue Target Funnel"
                ])

                if chart_option.startswith("1"):
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Rev Ach %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#00CC96"}})).update_layout(height=400, template="plotly_dark"), use_container_width=True)
                elif chart_option.startswith("2"):
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "FF Ach %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#636EFA"}})).update_layout(height=400, template="plotly_dark"), use_container_width=True)
                elif chart_option.startswith("3"):
                    st.plotly_chart(px.bar(filtered_df, x='Date_Obj', y=['Actual Revenue', 'Target revenue'], barmode='group', title="Revenue Comparison"), use_container_width=True)
                elif chart_option.startswith("4"):
                    st.plotly_chart(px.line(filtered_df, x='Date_Obj', y='Actual Footfall', markers=True, title="Footfall Trend"), use_container_width=True)
                elif chart_option.startswith("5"):
                    st.plotly_chart(px.pie(filtered_df, values='Actual Revenue', names='Months', hole=0.4, title="Revenue Share"), use_container_width=True)
                elif chart_option.startswith("6"):
                    st.plotly_chart(px.area(filtered_df, x='Date_Obj', y='Actual Revenue', title="Revenue Volume"), use_container_width=True)
                elif chart_option.startswith("7"):
                    st.plotly_chart(px.scatter(filtered_df, x='Actual Footfall', y='Actual Revenue', size='Actual Revenue', color='Months', title="Correlation"), use_container_width=True)
                elif chart_option.startswith("8"):
                    fig = go.Figure(go.Funnel(y=["Target", "Actual"], x=[results['Target revenue'], results['Actual Revenue']], textinfo="value+percent initial"))
                    fig.update_layout(title="Revenue Funnel", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

                st.table(filtered_df[metrics].sum().to_frame().T.style.format('{:,.0f}'))
                
            else:
                st.session_state.messages.append({"content": "No records found for this period.", "is_user": False})
                st.rerun()

    else:
        st.info("System Developed by **Umair Nizam**. Please log in to proceed.")

if __name__ == "__main__":
    main()
