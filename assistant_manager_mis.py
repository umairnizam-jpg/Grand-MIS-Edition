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
                    "proudly **developed by Umair Nizam**.\n\n"
                    "**My Expert Scope:**\n"
                    "* 📅 **Timeframe:** July 2017 to June 2026.\n"
                    "* 💹 **Analytics:** Revenue & Footfall achievements and YoY comparisons.\n"
                    "How can I assist your data-driven decisions today?"
                )
                st.session_state.messages.append({"content": intro_msg, "is_user": False})
                st.rerun()

            if df_live.empty:
                st.session_state.messages.append({"content": "❌ **Data Error:** Master file not found.", "is_user": False})
                st.rerun()

            all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
            found_fy = re.findall(r'fy\s?\d{4}', query_lower)

            filtered_df = df_live.copy()
            if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
            if found_years: filtered_df = filtered_df[filtered_df['Year'].isin(found_years)]
            if found_fy:
                tag = found_fy[0].upper().replace("FY", "FY ") if " " not in found_fy[0] else found_fy[0].upper()
                filtered_df = filtered_df[filtered_df['Fiscal_Year_Label'] == tag]

            if not filtered_df.empty:
                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                results = filtered_df[metrics].sum()
                rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
                ff_ach = (results['Actual Footfall'] / results['Target Footfall'] * 100) if results['Target Footfall'] > 0 else 0

                # Report Text Generation
                report = f"### 📊 BI Analysis Result\n**Financial Achievement:** {rev_ach:.1f}% | **Footfall Achievement:** {ff_ach:.1f}%"
                st.session_state.messages.append({"content": report, "is_user": False})
                
                # --- NEW: 8 PROFESSIONAL CHART TYPES SECTION ---
                st.divider()
                st.subheader("📈 Professional Analytics Dashboard")
                
                # Row 1: Achievement Gauges
                c1, c2 = st.columns(2)
                with c1:
                    fig1 = go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Revenue Achievement %"}, gauge={'bar':{'color':"#00CC96"}}))
                    st.plotly_chart(fig1, use_container_width=True)
                with c2:
                    fig2 = go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "Footfall Achievement %"}, gauge={'bar':{'color':"#636EFA"}}))
                    st.plotly_chart(fig2, use_container_width=True)

                # Row 2: Revenue Trend & Comparison
                c3, c4 = st.columns(2)
                with c3:
                    # 3. Bar Chart: Actual vs Target Revenue
                    fig3 = px.bar(filtered_df, x='Months', y=['Actual Revenue', 'Target revenue'], barmode='group', title="Revenue: Actual vs Target", color_discrete_sequence=['#00CC96', '#EF553B'])
                    st.plotly_chart(fig3, use_container_width=True)
                with c4:
                    # 4. Line Chart: Revenue Trend
                    fig4 = px.line(filtered_df, x='Months', y='Actual Revenue', markers=True, title="Monthly Revenue Trend", line_shape="spline")
                    st.plotly_chart(fig4, use_container_width=True)

                # Row 3: Footfall & Proportions
                c5, c6 = st.columns(2)
                with c5:
                    # 5. Area Chart: Footfall Over Time
                    fig5 = px.area(filtered_df, x='Months', y='Actual Footfall', title="Footfall Volume Analysis", color_discrete_sequence=['#636EFA'])
                    st.plotly_chart(fig5, use_container_width=True)
                with c6:
                    # 6. Pie/Donut Chart: Revenue Contribution by Month
                    fig6 = px.pie(filtered_df, values='Actual Revenue', names='Months', hole=0.4, title="Revenue Contribution by Period")
                    st.plotly_chart(fig6, use_container_width=True)

                # Row 4: Advanced Analytics
                c7, c8 = st.columns(2)
                with c7:
                    # 7. Scatter Plot: Revenue vs Footfall Correlation
                    fig7 = px.scatter(filtered_df, x='Actual Footfall', y='Actual Revenue', size='Actual Revenue', color='Months', title="Correlation: Footfall vs Revenue")
                    st.plotly_chart(fig7, use_container_width=True)
                with c8:
                    # 8. Funnel Chart: Achievement Progress
                    fig8 = go.Figure(go.Funnel(y=["Target Revenue", "Actual Revenue"], x=[results['Target revenue'], results['Actual Revenue']], textinfo="value+percent initial"))
                    fig8.update_layout(title="Revenue Conversion Funnel")
                    st.plotly_chart(fig8, use_container_width=True)

                st.rerun()
            else:
                st.session_state.messages.append({"content": "No records found for this period.", "is_user": False})
                st.rerun()
    else:
        st.info("System Developed by **Umair Nizam**. Please log in to proceed.")

if __name__ == "__main__":
    main()
