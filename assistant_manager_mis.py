import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. CORE DATA ENGINE (Advanced BI Logic) ---
def load_excel_data():
    # Hybrid Path: Office Network or Cloud Deployment
    cloud_path = "RAW DATA.xlsx"
    local_path = r"Z:\data\RAW DATA.xlsx"
    file_path = cloud_path if os.path.exists(cloud_path) else local_path
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Fiscal Mapping
        month_map = {
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6
        }
        df['Month_Num'] = df['Months'].map(month_map)
        
        # FY Definition (July to June)
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        
        # Proper BI Sorting
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        # Data Constraint: 2017-2026
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        
        return df.loc[mask].sort_values('Date_Obj')
    except Exception as e:
        st.error(f"Critical Data Error: {e}")
        return pd.DataFrame()

# --- 2. THE INTELLIGENT AI ASSISTANT ---
def main():
    st.set_page_config(page_title="Joyland BI Grand Master", layout="wide", page_icon="📈")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    df_live = load_excel_data()

    # Authentication
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # SIDEBAR
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect\n**Umair Nizam**")
        st.sidebar.info("Scope: July 2017 – June 2026")

        st.title("🎢 Joyland Great Grand Master BI")

        # --- CHAT CONTAINER ---
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message("user" if msg["is_user"] else "assistant"):
                    st.markdown(msg["content"])

        # --- ADVANCED INPUT BAR (Voice + File + Text) ---
        st.divider()
        input_col1, input_col2 = st.columns([1, 4])
        
        with input_col1:
            audio_cmd = st.audio_input("🎤 Voice Command")
        with input_col2:
            attached_file = st.file_uploader("📎 Attach Analysis File", type=['xlsx', 'csv', 'pdf'], label_visibility="collapsed")

        prompt = st.chat_input("Ask: 'Compare FY 2024 Revenue with FY 2023' or 'Mar 2021 Footfall'...")

        # Input Consolidation
        user_query = prompt if prompt else ("Voice command received..." if audio_cmd else None)

        if user_query:
            st.session_state.messages.append({"content": user_query, "is_user": True})
            
            query_lower = user_query.lower()
            
            # Smart Logic Filtering
            all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
            found_fy = re.findall(r'fy\s?\d{4}', query_lower)

            # Date Range Check (Constraint Rule)
            future_check = [y for y in found_years if y > 2026]
            if future_check:
                st.session_state.messages.append({"content": "⚠️ Data is only available up to **June 2026**. I cannot analyze future dates.", "is_user": False})
                st.rerun()

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
                
                rev_ach = (results['Actual Revenue'] / results['Target revenue'] * 100) if results['Target revenue'] > 0 else 0
                ff_ach = (results['Actual Footfall'] / results['Target Footfall'] * 100) if results['Target Footfall'] > 0 else 0

                # Comparative Logic (YoY)
                comparison_text = ""
                if "compare" in query_lower or "vs" in query_lower:
                    prev_fy = f"FY {int(re.search(r'\d{4}', found_fy[0]).group()) - 1}" if found_fy else None
                    if prev_fy:
                        prev_df = df_live[df_live['Fiscal_Year_Label'] == prev_fy]
                        if not prev_df.empty:
                            p_rev = prev_df['Actual Revenue'].sum()
                            diff = results['Actual Revenue'] - p_rev
                            perc = (diff / p_rev * 100) if p_rev > 0 else 0
                            comparison_text = f"\n\n**YoY Variance Analysis:**\n* Variance: Rs. {diff:,.0f} ({perc:.1f}% {'Increase' if diff >= 0 else 'Decrease'})"
                            if abs(perc) > 20:
                                comparison_text += f"\n* 💡 **Insight:** Significant {'growth' if diff >= 0 else 'drop'} detected compared to {prev_fy}."

                analysis_msg = (
                    f"### 📊 BI Performance Report\n"
                    f"**Financials:**\n"
                    f"* Actual Revenue: **Rs. {results['Actual Revenue']:,.0f}**\n"
                    f"* Target Revenue: Rs. {results['Target revenue']:,.0f}\n"
                    f"* Achievement: **{rev_ach:.1f}%**\n\n"
                    f"**Footfall:**\n"
                    f"* Actual Footfall: **{results['Actual Footfall']:,.0f}**\n"
                    f"* Target Footfall: {results['Target Footfall']:,.0f}\n"
                    f"* Achievement: **{ff_ach:.1f}%**"
                    f"{comparison_text}"
                )
                
                if attached_file:
                    analysis_msg += f"\n\n📎 **Attached File Analysis:** File `{attached_file.name}` integrated into session."

                st.session_state.messages.append({"content": analysis_msg, "is_user": False})
                st.rerun()

            else:
                st.session_state.messages.append({"content": "I couldn't find any data for that specific request within my 2017-2026 scope.", "is_user": False})
                st.rerun()

        # --- PERSISTENT ANALYTICS (Charts) ---
        if not filtered_df.empty:
            st.divider()
            t1, t2, t3 = st.tabs(["🌎 Data Matrix", "📈 Trends", "🎯 Achievement"])
            with t1:
                st.table(filtered_df.pivot_table(index=['Fiscal_Year_Label', 'Months'], values=['Actual Revenue', 'Target revenue', 'Actual Footfall', 'Target Footfall'], aggfunc='sum').style.format('{:,.0f}'))
            with t2:
                fig = px.line(filtered_df, x='Months', y=['Actual Revenue', 'Target revenue'], markers=True, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            with t3:
                c1, c2 = st.columns(2)
                c1.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Revenue Ach %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"white"}})).update_layout(height=250, template="plotly_dark"), use_container_width=True)
                c2.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=ff_ach, title={'text': "Footfall Ach %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"white"}})).update_layout(height=250, template="plotly_dark"), use_container_width=True)

    else:
        st.info("System Ready. Please log in to the Joyland BI Portal.")

if __name__ == "__main__":
    main()
