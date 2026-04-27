import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. DATA ENGINE: BI ANALYST LOGIC ---
def load_excel_data():
    # Hybrid Path: Checks local folder first, then Z drive
    cloud_path = "RAW DATA.xlsx"
    local_path = r"Z:\data\RAW DATA.xlsx"
    
    file_path = cloud_path if os.path.exists(cloud_path) else local_path
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Mapping for Fiscal Logic
        month_map = {
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6
        }
        df['Month_Num'] = df['Months'].map(month_map)
        
        # FY Definition: July-June
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        
        # Sorting order for BI aggregation
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        # Data Constraint: July 2017 to June 2026
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2026-06-01')
        return df.loc[mask].sort_values('Date_Obj')
        
    except Exception as e:
        st.error(f"Critical Data Error: {e}")
        return pd.DataFrame()

# --- 2. THE INTELLIGENT ANALYST INTERFACE ---
def main():
    st.set_page_config(page_title="Joyland BI Assistant", layout="wide", page_icon="📈")
    df_live = load_excel_data()

    # Security
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # SIDEBAR
        st.sidebar.title(f"Analyst: {st.session_state['name']}")
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 🛠️ System Architect\n**Umair Nizam**")
        st.sidebar.info("Scope: July 2017 – June 2026")

        st.title("🎢 Joyland MIS Assistant")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.write(msg["content"])
            
        if prompt := st.chat_input("Ex: 'Compare FY 2024 to FY 2023' or 'Revenue March 2024'"):
            st.session_state.messages.append({"content": prompt, "is_user": True})
            with st.chat_message("user"): st.write(prompt)
            
            query_lower = prompt.lower()

            # --- PRE-ANALYSIS: DATE LIMIT CHECK ---
            future_years = [int(y) for y in re.findall(r'202[7-9]|20[3-9]\d', query_lower)]
            if future_years:
                msg = "⚠️ **Information:** My current data scope is only available up to **June 2026**. I cannot provide figures beyond this period."
                st.session_state.messages.append({"content": msg, "is_user": False})
                with st.chat_message("assistant"): st.warning(msg)
                return

            # --- SMART FILTERING LOGIC ---
            all_months = ['july', 'august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months if m in query_lower or m[:3] in query_lower]
            found_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
            found_fy = re.findall(r'fy\s?\d{4}', query_lower)
            
            curr_df = df_live.copy()
            
            # Apply Filters
            if found_months: curr_df = curr_df[curr_df['Months'].isin(found_months)]
            if found_years: curr_df = curr_df[curr_df['Year'].isin(found_years)]
            if found_fy: 
                # Clean FY string for matching (FY 2024 -> FY 2024)
                fy_tag = found_fy[0].upper().replace("FY", "FY ") if " " not in found_fy[0] else found_fy[0].upper()
                curr_df = curr_df[curr_df['Fiscal_Year_Label'] == fy_tag]

            # Metric Selection
            metrics = ["Actual Revenue", "Target revenue"] if "revenue" in query_lower else \
                      ["Actual Footfall", "Target Footfall"] if "footfall" in query_lower else \
                      ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]

            if not curr_df.empty:
                # --- CALCULATION LOGIC ---
                total_actual_rev = curr_df['Actual Revenue'].sum()
                total_target_rev = curr_df['Target revenue'].sum()
                total_actual_ff = curr_df['Actual Footfall'].sum()
                total_target_ff = curr_df['Target Footfall'].sum()
                
                rev_ach = (total_actual_rev / total_target_rev * 100) if total_target_rev > 0 else 0
                ff_ach = (total_actual_ff / total_target_ff * 100) if total_target_ff > 0 else 0

                # --- COMPARATIVE / YOY LOGIC ---
                yoy_report = ""
                if "compare" in query_lower or "vs" in query_lower:
                    # Look for previous year or fiscal year
                    if found_fy:
                        curr_fy_num = int(re.search(r'\d{4}', found_fy[0]).group())
                        prev_label = f"FY {curr_fy_num - 1}"
                        prev_df = df_live[df_live['Fiscal_Year_Label'] == prev_label]
                    elif found_years and found_months:
                        prev_year = found_years[0] - 1
                        prev_df = df_live[(df_live['Year'] == prev_year) & (df_live['Months'].isin(found_months))]
                    else:
                        prev_df = pd.DataFrame()

                    if not prev_df.empty:
                        p_rev = prev_df['Actual Revenue'].sum()
                        diff = total_actual_rev - p_rev
                        perc = (diff / p_rev * 100) if p_rev > 0 else 0
                        status = "Increase" if diff >= 0 else "Decrease"
                        yoy_report = f"\n\n**YoY Comparison:**\n* Previous Period: **Rs. {p_rev:,.0f}**\n* Variance: **Rs. {diff:,.0f}** ({abs(perc):.1f}% {status})"
                        if abs(perc) > 20: 
                            yoy_report += f"\n\n💡 **Insight:** Noticeable {status} of {abs(perc):.1f}% detected compared to the previous period."

                # --- RESPONSE PRESENTATION ---
                analysis_msg = (
                    f"### 📊 Performance Report\n"
                    f"**Analysis Period:** {found_months if found_months else 'Full Year'} {found_years if found_years else found_fy}\n\n"
                    f"**Financials:**\n"
                    f"* Actual Revenue: **Rs. {total_actual_rev:,.0f}**\n"
                    f"* Revenue Achievement: **{rev_ach:.1f}%**\n\n"
                    f"**Footfall:**\n"
                    f"* Actual Footfall: **{total_actual_ff:,.0f} visitors**\n"
                    f"* Footfall Achievement: **{ff_ach:.1f}%**"
                    f"{yoy_report}"
                )

                st.session_state.messages.append({"content": analysis_msg, "is_user": False})
                with st.chat_message("assistant"): st.markdown(analysis_msg)

                # Visual Matrix
                with st.expander("View Data Matrix"):
                    st.table(curr_df[['Fiscal_Year_Label', 'Months', 'Actual Revenue', 'Target revenue', 'Actual Footfall']].style.format({'Actual Revenue': '{:,.0f}', 'Target revenue': '{:,.0f}', 'Actual Footfall': '{:,.0f}'}))
                
                # Gauge Chart
                fig = go.Figure(go.Indicator(mode="gauge+number", value=rev_ach, title={'text': "Revenue Ach %"},
                                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "white"}, 'steps': [{'range': [0, 80], 'color': "red"}, {'range': [80, 100], 'color': "green"}]}))
                fig.update_layout(height=300, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("No data found for the requested period within the July 2017 - June 2026 scope.")

    else:
        st.info("Log in as Admin to access the Analyst Portal. Developed by Umair Nizam.")

if __name__ == "__main__":
    main()
