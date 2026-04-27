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
    # Detects file on GitHub (Cloud) or Z: Drive (Local Office)
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
        
        # Fiscal Year Definition (July to June)
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        
        # Proper BI Sorting order
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        # Date Constraint: July 2017 to June 2026
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

    # Security Layer
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # SIDEBAR (Minimalist)
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")
        st.sidebar.info("Scope: July 2017 – June 2026")

        st.title("🎢 Joyland Great Grand Master BI")

        # --- CHAT INTERFACE ---
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        # --- ADVANCED UI CHAT BAR (Icons on Right) ---
        st.markdown("---")
        # Layout: Text Input (Left) | Mic & File (Right)
        input_col, mic_col, clip_col = st.columns([5, 0.4, 0.4])

        with input_col:
            prompt = st.chat_input("Ask about Revenue, Footfall, Comparisons...")
        
        with mic_col:
            voice_data = st.audio_input("🎤", key="v_mic", label_visibility="collapsed")
            
        with clip_col:
            attached_file = st.file_uploader("📎", type=['xlsx', 'csv'], key="f_clip", label_visibility="collapsed")

        # Process Input
        user_query = None
        if prompt:
            user_query = prompt
        elif voice_data:
            user_query = "Voice Command Received"

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            query_lower = user_query.lower()

            # --- A. PROFESSIONAL INTRODUCTION LOGIC ---
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

            # --- B. CORE ANALYTICS LOGIC ---
            if df_live.empty:
                st.session_state.messages.append({"content": "❌ **Data Error:** Master file `RAW DATA.xlsx` not found. Please ensure it is in the repository or Z drive.", "is_user": False})
                st.rerun()

            # Date Extraction
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
                # Calculations
                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                results = filtered_df[metrics].sum()
                
                # Achievement Formula: (Actual / Target) * 100
                rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
                ff_ach = (results['Actual Footfall'] / results['Target Footfall'] * 100) if results['Target Footfall'] > 0 else 0

                # Comparative Analysis (YoY)
                variance_report = ""
                if "compare" in query_lower or "vs" in query_lower:
                    if found_years:
                        prev_y = found_years[0] - 1
                        prev_df = df_live[(df_live['Year'] == prev_y) & (df_live['Months'].isin(found_months))]
                        if not prev_df.empty:
                            p_rev = prev_df['Actual Revenue'].sum()
                            diff = results['Actual Revenue'] - p_rev
                            perc = (diff / p_rev * 100) if p_rev > 0 else 0
                            variance_report = f"\n\n**YoY Comparison:**\n* Variance: **Rs. {diff:,.0f}** ({perc:.1f}% {'Increase' if diff >= 0 else 'Decrease'})\n"
                            if abs(perc) > 20:
                                variance_report += f"* 💡 **Insight:** Significant {'growth' if diff >= 0 else 'drop'} detected compared to last year."

                report = (
                    f"### 📊 BI Analysis Result\n"
                    f"**Financial Performance:**\n"
                    f"* Actual Revenue: **Rs. {results['Actual Revenue']:,.0f}**\n"
                    f"* Target Revenue: Rs. {results['Target revenue']:,.0f}\n"
                    f"* Achievement: **{rev_ach:.1f}%**\n\n"
                    f"**Footfall Analysis:**\n"
                    f"* Actual Footfall: **{results['Actual Footfall']:,.0f}**\n"
                    f"* Target Footfall: {results['Target Footfall']:,.0f}\n"
                    f"* Achievement: **{ff_ach:.1f}%**"
                    f"{variance_report}"
                )
                
                if attached_file:
                    report += f"\n\n📎 **Attachment:** File `{attached_file.name}` recognized."

                st.session_state.messages.append({"content": report, "is_user": False})
                
                # --- VISUALS (8 Professional Charts) ---
                st.divider()
                
                # 1 & 2: Achievement Gauges
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Rev Ach %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#00CC96"}})).update_layout(height=300, template="plotly_dark"), use_container_width=True)
                with c2:
                    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "FF Ach %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#636EFA"}})).update_layout(height=300, template="plotly_dark"), use_container_width=True)

                # 3 & 4: Comparisons and Trends
                c3, c4 = st.columns(2)
                with c3:
                    fig3 = px.bar(filtered_df, x='Months', y=['Actual Revenue', 'Target revenue'], barmode='group', title="Revenue: Actual vs Target", color_discrete_sequence=['#00CC96', '#EF553B'])
                    st.plotly_chart(fig3, use_container_width=True)
                with c4:
                    fig4 = px.line(filtered_df, x='Months', y='Actual Footfall', markers=True, title="Footfall Trend Line", line_shape="spline")
                    st.plotly_chart(fig4, use_container_width=True)

                # 5 & 6: Distribution and Volume
                c5, c6 = st.columns(2)
                with c5:
                    fig5 = px.pie(filtered_df, values='Actual Revenue', names='Months', hole=0.4, title="Monthly Revenue Share")
                    st.plotly_chart(fig5, use_container_width=True)
                with c6:
                    fig6 = px.area(filtered_df, x='Months', y='Actual Revenue', title="Revenue Volume Area Chart", color_discrete_sequence=['#AB63FA'])
                    st.plotly_chart(fig6, use_container_width=True)

                # 7 & 8: Relationship and Target Progress
                c7, c8 = st.columns(2)
                with c7:
                    fig7 = px.scatter(filtered_df, x='Actual Footfall', y='Actual Revenue', size='Actual Revenue', color='Months', title="Correlation: Footfall vs Revenue")
                    st.plotly_chart(fig7, use_container_width=True)
                with c8:
                    fig8 = go.Figure(go.Funnel(y=["Target", "Actual"], x=[results['Target revenue'], results['Actual Revenue']], textinfo="value+percent initial"))
                    fig8.update_layout(title="Revenue Target Funnel", template="plotly_dark")
                    st.plotly_chart(fig8, use_container_width=True)

                # Original Data Table
                st.table(filtered_df[metrics].sum().to_frame().T.style.format('{:,.0f}'))
                
                st.rerun()
            else:
                st.session_state.messages.append({"content": "No records found for this period within the 2017-2026 scope.", "is_user": False})
                st.rerun()

    else:
        st.info("System Developed by **Umair Nizam**. Please log in to proceed.")

if __name__ == "__main__":
    main()
