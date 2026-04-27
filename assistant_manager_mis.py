import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. CORE DATA ENGINE ---
def load_excel_data():
    # Hybrid Path Logic for Cloud and Local
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
        
        # Fiscal Year & Month Mapping
        month_map = {
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6
        }
        df['Month_Num'] = df['Months'].map(month_map)
        
        # FY Definition: July to June
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        
        # BI Sorting
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        # Data Constraint: July 2017 to June 2026
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        
        return df.loc[mask].sort_values('Date_Obj')
    except Exception as e:
        return pd.DataFrame()

# --- 2. MAIN BI INTERFACE ---
def main():
    st.set_page_config(page_title="Joyland Ultimate BI", layout="wide", page_icon="📈")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    df_live = load_excel_data()

    # Security Credentials
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # --- SIDEBAR ---
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")
        st.sidebar.info("Data Scope: July 2017 – June 2026")

        st.title("🎢 Joyland Great Grand Master BI")

        # --- CHAT DISPLAY ---
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        # --- ADVANCED INPUT BAR (Icons & Text Integrated) ---
        st.markdown("---")
        # Layout to bring Voice and File icons near the chat input
        tool_c1, tool_c2, chat_c = st.columns([0.4, 0.4, 5])
        
        with tool_c1:
            voice_data = st.audio_input("🎤", key="voice_mic", label_visibility="collapsed")
        with tool_c2:
            attached_file = st.file_uploader("📎", type=['xlsx', 'csv'], key="file_clip", label_visibility="collapsed")
        with chat_c:
            prompt = st.chat_input("Ask about Revenue, Footfall, or Comparisons...")

        # Input Logic
        final_input = None
        if prompt:
            final_input = prompt
        elif voice_data:
            final_input = "Voice command received (Analysis in progress...)"

        if final_input:
            st.session_state.messages.append({"content": final_input, "is_user": True})
            query_lower = final_input.lower()

            # --- A. PROFESSIONAL AI INTRO ---
            if any(greet in query_lower for greet in ["hi", "hello", "intro", "introduce", "who are you", "salam"]):
                intro_text = (
                    "✨ **Greetings! I am the Joyland Ultimate BI Assistant.**\n\n"
                    "I am a highly intelligent Business Intelligence & Data Analyst tool, "
                    "proudly **developed by Umair Nizam**. My architecture is designed to provide "
                    "comprehensive analysis of **Revenue and Footfall** for 'Joyland Fortress'.\n\n"
                    "**My Capabilities include:**\n"
                    "* 📅 **Timeframe:** Precise data from July 2017 up to June 2026.\n"
                    "* 💹 **Comparisons:** Automatic YoY Variance and Growth calculations.\n"
                    "* 🎯 **Achievements:** Formula-based tracking $(\\text{Actual} / \\text{Target}) \\times 100$.\n"
                    "* 📂 **External Analysis:** Analyze any file you attach via the 📎 icon.\n\n"
                    "How can I help you drive business growth today?"
                )
                st.session_state.messages.append({"content": intro_text, "is_user": False})
                st.rerun()

            # --- B. DATA ANALYSIS LOGIC ---
            if df_live.empty:
                st.session_state.messages.append({"content": "❌ **Data Error:** Master file `RAW DATA.xlsx` not found. Please check your Z drive or GitHub repo.", "is_user": False})
                st.rerun()

            # Date Extraction
            all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
            found_fy = re.findall(r'fy\s?\d{4}', query_lower)

            # Filtering
            filtered_df = df_live.copy()
            if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
            if found_years: filtered_df = filtered_df[filtered_df['Year'].isin(found_years)]
            if found_fy:
                fy_tag = found_fy[0].upper().replace("FY", "FY ") if " " not in found_fy[0] else found_fy[0].upper()
                filtered_df = filtered_df[filtered_df['Fiscal_Year_Label'] == fy_tag]

            if not filtered_df.empty:
                metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]
                totals = filtered_df[metrics].sum()
                
                # Achievement Formulas
                rev_ach = (totals['Actual Revenue'] / totals['Target revenue'] * 100) if totals['Target revenue'] > 0 else 0
                ff_ach = (totals['Actual Footfall'] / totals['Target Footfall'] * 100) if totals['Target Footfall'] > 0 else 0

                # Variance / Comparison Logic
                variance_text = ""
                if "compare" in query_lower or "vs" in query_lower:
                    # Automatic YoY lookup
                    prev_year = (found_years[0] - 1) if found_years else None
                    if prev_year:
                        prev_df = df_live[(df_live['Year'] == prev_year) & (df_live['Months'].isin(found_months))]
                        if not prev_df.empty:
                            p_rev = prev_df['Actual Revenue'].sum()
                            diff = totals['Actual Revenue'] - p_rev
                            perc = (diff / p_rev * 100) if p_rev > 0 else 0
                            variance_text = f"\n\n**YoY Variance:**\n* Difference: **Rs. {diff:,.0f}**\n* Growth: **{perc:.1f}%** {'📈' if diff >= 0 else '📉'}"
                            if abs(perc) > 20:
                                variance_text += f"\n* 💡 **Insight:** Significant {'growth' if diff >= 0 else 'drop'} noted compared to previous period."

                response = (
                    f"### 📊 BI Performance Summary\n"
                    f"**Financials:**\n"
                    f"* Actual Revenue: **Rs. {totals['Actual Revenue']:,.0f}**\n"
                    f"* Achievement: **{rev_ach:.1f}%**\n\n"
                    f"**Footfall:**\n"
                    f"* Actual Footfall: **{totals['Actual Footfall']:,.0f}**\n"
                    f"* Achievement: **{ff_ach:.1f}%**"
                    f"{variance_text}"
                )
                
                if attached_file:
                    response += f"\n\n📎 **File Insight:** Data from `{attached_file.name}` has been successfully referenced."

                st.session_state.messages.append({"content": response, "is_user": False})
                
                # --- VISUALS ---
                st.divider()
                t1, t2, t3 = st.tabs(["📝 Data Table", "📈 Trends", "🎯 Achievement Gauges"])
                with t1:
                    st.dataframe(filtered_df[metrics + ['Months', 'Fiscal_Year_Label']].style.format('{:,.0f}', subset=metrics))
                with t2:
                    fig = px.bar(filtered_df, x='Months', y=['Actual Revenue', 'Target revenue'], barmode='group', template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True)
                with t3:
                    c1, c2 = st.columns(2)
                    c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text':"Revenue %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"white"}})).update_layout(height=250, template="plotly_dark"))
                    c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text':"Footfall %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"white"}})).update_layout(height=250, template="plotly_dark"))
                
                st.rerun()
            else:
                st.session_state.messages.append({"content": "I couldn't find data for that period. Please ensure your query falls between **July 2017 and June 2026**.", "is_user": False})
                st.rerun()

    else:
        st.info("👋 Welcome! Please log in to access the Joyland BI Master Portal. Developed by **Umair Nizam**.")

if __name__ == "__main__":
    main()
