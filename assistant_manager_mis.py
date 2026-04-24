import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate

# --- 1. DATA ENGINE: THE CORE LOGIC ---
def load_excel_data():
    file_path = r"Z:\data\RAW DATA.xlsx" 
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Month to Number mapping for fiscal calculations
        month_map = {
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6
        }
        df['Month_Num'] = df['Months'].map(month_map)
        
        # Fiscal Quarter Mapping (Joyland Cycle)
        def get_fiscal_quarter(m):
            if m in [7, 8, 9]: return "Q1"
            if m in [10, 11, 12]: return "Q2"
            if m in [1, 2, 3]: return "Q3"
            if m in [4, 5, 6]: return "Q4"
            return "N/A"
        df['Quarter'] = df['Month_Num'].apply(get_fiscal_quarter)
        
        # Fiscal Year Calculation (July starts the next FY)
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY{x['Year'] if x['Month_Num'] <= 6 else x['Year'] + 1}", axis=1
        )
        
        # Chronological Sorting order
        fiscal_order = ['July', 'August', 'September', 'October', 'November', 'December', 
                        'January', 'February', 'March', 'April', 'May', 'June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        
        return df.sort_values(['Year', 'Month_Num'])
    except Exception as e:
        st.error(f"Critical Data Error: {e}")
        return pd.DataFrame()

# --- 2. THE INTELLIGENT INTERFACE ---
def main():
    st.set_page_config(page_title="Joyland Great Grand MIS", layout="wide", page_icon="🎢")
    df_live = load_excel_data()

    # Authentication Security
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    auth = Authenticate(credentials, "joyland_mis", "auth_key", cookie_expiry_days=30)
    auth.login(location='main')

    if st.session_state.get("authentication_status"):
        # --- SIDEBAR BRANDING ---
        st.sidebar.title(f"Welcome, {st.session_state['name']}")
        if st.sidebar.button("🗑️ Clear Analysis"):
            st.session_state.messages = []
            st.rerun()
        auth.logout('Logout', 'sidebar')
        st.sidebar.divider()
        st.sidebar.markdown("### 👨‍💻 System Architect")
        st.sidebar.success("**Umair Nizam**")
        st.sidebar.info("Timeline: 2017 - 2026\nCycle: July to June")

        st.title("🎢 Joyland MIS Assistant")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.write(msg["content"])
            
        # --- CHAT INPUT & LOGIC ---
        if prompt := st.chat_input("Ask: 'Revenue of Mar 2021' or 'Compare Q1 vs Q2'"):
            st.session_state.messages.append({"content": prompt, "is_user": True})
            with st.chat_message("user"): st.write(prompt)
            
            query_lower = prompt.lower()

            # A. PRETTY INTRODUCTION
            if any(k in query_lower for k in ['who are you', 'intro', 'hello', 'hi', 'your name']):
                intro = (
                    "✨ **Greetings! I am the Joyland Great Grand MIS.**\n\n"
                    "Developed by **Umair Nizam**, I am your high-precision data partner. "
                    "I can provide exact numbers for any month, calculate growth across years, "
                    "and analyze targets/budgets for Revenue and Footfall since 2017."
                )
                st.session_state.messages.append({"content": intro, "is_user": False})
                with st.chat_message("assistant"): st.markdown(intro)
                return

            # B. ADVANCED DATA FILTERING
            all_months_list = ['july', 'august', 'september', 'october', 'november', 'december', 
                               'january', 'february', 'march', 'april', 'may', 'june']
            found_months = [m.capitalize() for m in all_months_list if m in query_lower or m[:3] in query_lower]
            found_years = re.findall(r'\b(20\d{2})\b', query_lower)
            found_fy = re.findall(r'fy\d{4}', query_lower)
            found_q = re.findall(r'q[1-4]', query_lower)
            p_list = [p for p in df_live['Projetcs'].unique() if str(p).lower() in query_lower]

            filtered_df = df_live.copy()
            if found_months: filtered_df = filtered_df[filtered_df['Months'].isin(found_months)]
            if found_years: filtered_df = filtered_df[filtered_df['Year'].isin([int(y) for y in found_years])]
            if found_fy: filtered_df = filtered_df[filtered_df['Fiscal_Year_Label'].str.lower().isin(found_fy)]
            if found_q: filtered_df = filtered_df[filtered_df['Quarter'].str.lower().isin(found_q)]
            if p_list: filtered_df = filtered_df[filtered_df['Projetcs'].isin(p_list)]

            # Metric Detection (Revenue, Footfall, Target, Budget)
            req_metrics = []
            if "revenue" in query_lower or "budget" in query_lower:
                req_metrics = ["Actual Revenue", "Target revenue"]
            elif "footfall" in query_lower:
                req_metrics = ["Actual Footfall", "Target Footfall"]
            else:
                req_metrics = ["Actual Revenue", "Target revenue", "Actual Footfall", "Target Footfall"]

            if not filtered_df.empty:
                # C. ACHIEVEMENT & YOY GROWTH LOGIC
                current_fy_str = filtered_df['Fiscal_Year_Label'].iloc[0]
                prev_fy_val = int(current_fy_str.replace("FY", "")) - 1
                prev_fy_label = f"FY{prev_fy_val}"
                
                prev_df = df_live[df_live['Fiscal_Year_Label'] == prev_fy_label]
                if found_months: prev_df = prev_df[prev_df['Months'].isin(found_months)]
                if found_q: prev_df = prev_df[prev_df['Quarter'].str.lower().isin(found_q)]

                # Build Text Analysis
                analysis_text = f"### 📊 Analysis for {current_fy_str}\n"
                for m in [met for met in req_metrics if "Actual" in met]:
                    c_val = filtered_df[m].sum()
                    t_col = m.replace("Actual", "Target")
                    unit = "Rs. " if "Revenue" in m else ""
                    
                    # Target Achievement
                    if t_col in filtered_df.columns:
                        t_val = filtered_df[t_col].sum()
                        ach = (c_val / t_val * 100) if t_val > 0 else 0
                        analysis_text += f"* **{m}:** {unit}{c_val:,.0f} / {unit}{t_val:,.0f} target (**{ach:.1f}% Achievement**)\n"
                    
                    # YoY Growth
                    if not prev_df.empty:
                        p_val = prev_df[m].sum()
                        diff = c_val - p_val
                        perc = (diff / p_val * 100) if p_val > 0 else 0
                        icon = "📈" if diff >= 0 else "📉"
                        analysis_text += f"   * *YoY:* Last Year {prev_fy_label} was {unit}{p_val:,.0f}. (Result: {icon} **{abs(perc):.1f}% {('Increase' if diff >= 0 else 'Decrease')}**)\n"

                st.session_state.messages.append({"content": analysis_text, "is_user": False})
                with st.chat_message("assistant"): st.markdown(analysis_text)

                # D. THE GREAT GRAND BI GALLERY
                st.divider()
                tabs = st.tabs(["🌎 Universal Matrix", "📊 Performance Chart", "🎯 Target Gauge", "🌀 Sunburst", "📂 Raw Table"])
                
                with tabs[0]:
                    st.subheader("Universal Comparison: Every Year, Quarter, & Month")
                    matrix = filtered_df.pivot_table(index=['Fiscal_Year_Label', 'Quarter', 'Months'], values=req_metrics, aggfunc='sum')
                    st.dataframe(matrix.style.format('{:,.0f}'), use_container_width=True)

                with tabs[1]:
                    fig1 = px.bar(filtered_df, x='Months', y=req_metrics, barmode='group', template="plotly_dark", title="Trend Analysis")
                    st.plotly_chart(fig1, use_container_width=True)

                with tabs[2]:
                    main_ach = (filtered_df[req_metrics[0]].sum() / filtered_df[req_metrics[1]].sum() * 100) if filtered_df[req_metrics[1]].sum() > 0 else 0
                    fig2 = go.Figure(go.Indicator(mode="gauge+number", value=main_ach, title={'text': f"{req_metrics[0]} Ach %"},
                        gauge={'axis': {'range': [0, 100]}, 'steps': [{'range': [0, 80], 'color': "orange"}, {'range': [80, 100], 'color': "green"}], 'bar':{'color':"white"}}))
                    fig2.update_layout(template="plotly_dark", height=350); st.plotly_chart(fig2, use_container_width=True)

                with tabs[3]:
                    fig3 = px.sunburst(filtered_df, path=['Fiscal_Year_Label', 'Quarter', 'Months', 'Projetcs'], values=req_metrics[0], template="plotly_dark")
                    st.plotly_chart(fig3, use_container_width=True)

                with tabs[4]:
                    # Format numbers but keep text readable
                    st.dataframe(filtered_df.style.format(subset=req_metrics, formatter="{:,.0f}"), use_container_width=True)
            else:
                st.warning("No historical data matched your request. Please check Month/Year spelling.")

    else:
        st.info("👋 Welcome! Please log in to the Joyland Master Portal. Developed by Umair Nizam.")

if __name__ == "__main__":
    main()