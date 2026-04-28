import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
#  JOYLAND MIS ASSISTANT  ·  v3.0 Ultra
#  Architect: Umair Nizam  |  Scope: 2017 – 2030
# ═══════════════════════════════════════════════════════════════

PAGE_THEME = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* ── Root Palette ── */
:root {
  --bg-primary:    #050b18;
  --bg-secondary:  #0a1628;
  --bg-card:       #0d1f3c;
  --bg-card2:      #091530;
  --border:        #1a3a6b;
  --border-glow:   #00c6ff;
  --accent-blue:   #00c6ff;
  --accent-gold:   #f5c518;
  --accent-green:  #00ff9d;
  --accent-red:    #ff4466;
  --accent-purple: #b660f5;
  --text-primary:  #e8f4fd;
  --text-secondary:#7a9cc0;
  --text-dim:      #3a5a80;
  --font-display:  'Orbitron', monospace;
  --font-body:     'Rajdhani', sans-serif;
  --font-mono:     'JetBrains Mono', monospace;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
  font-family: var(--font-body) !important;
  color: #e8f4fd !important;
}

/* ── Force all p, span, div text to be visible ── */
p, span, div, label {
  color: #e8f4fd !important;
}

.stMarkdown p, .stMarkdown span, .stMarkdown li {
  color: #ddeeff !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  line-height: 1.8 !important;
}

.main, .stApp, section[data-testid="stSidebar"] + div {
  background: var(--bg-primary) !important;
}

/* ── Animated Grid Background ── */
.main::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,198,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,198,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #050b18 0%, #071020 100%) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-blue), var(--accent-gold), transparent);
  animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* ── KPI Cards ── */
div[data-testid="stMetric"] {
  background: linear-gradient(135deg, #0f2544 0%, #0c1d38 100%) !important;
  border: 1px solid #2a5a9b !important;
  border-radius: 16px !important;
  padding: 24px 20px !important;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,198,255,0.25) !important;
  border-color: #00c6ff !important;
}
div[data-testid="stMetric"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #00c6ff, #f5c518);
}
div[data-testid="stMetricLabel"] > div {
  color: #a8d4f5 !important;
  font-family: var(--font-body) !important;
  font-size: 14px !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  font-weight: 700 !important;
}
div[data-testid="stMetricValue"] > div {
  color: #ffffff !important;
  font-family: var(--font-display) !important;
  font-size: 26px !important;
  font-weight: 900 !important;
  letter-spacing: 1px !important;
  text-shadow: 0 0 20px rgba(0,198,255,0.5) !important;
}
div[data-testid="stMetricDelta"] > div {
  color: #00ff9d !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  background: rgba(0,255,157,0.15) !important;
  padding: 3px 12px !important;
  border-radius: 20px !important;
  border: 1px solid rgba(0,255,157,0.4) !important;
}

/* ── Header Banner ── */
.hero-banner {
  background: linear-gradient(135deg, #050b18 0%, #071428 50%, #050b18 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 32px 40px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
  text-align: center;
}
.hero-banner::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 20% 50%, rgba(0,198,255,0.06) 0%, transparent 60%),
              radial-gradient(ellipse at 80% 50%, rgba(245,197,24,0.06) 0%, transparent 60%);
}
.hero-title {
  font-family: var(--font-display) !important;
  font-size: 42px !important;
  font-weight: 900 !important;
  letter-spacing: 6px !important;
  background: linear-gradient(135deg, #00c6ff 0%, #f5c518 50%, #00ff9d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
  text-shadow: none;
}
.hero-subtitle {
  font-family: var(--font-body) !important;
  color: #c8dff0 !important;
  font-size: 15px !important;
  letter-spacing: 4px !important;
  text-transform: uppercase !important;
  font-weight: 600 !important;
}
.hero-badge {
  display: inline-block;
  background: rgba(0,198,255,0.18);
  border: 1px solid rgba(0,198,255,0.5);
  border-radius: 20px;
  padding: 5px 18px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: #00e5ff;
  letter-spacing: 2px;
  margin-top: 12px;
  font-weight: 700;
}

/* ── Section Headers ── */
.section-header {
  font-family: var(--font-display) !important;
  font-size: 18px !important;
  font-weight: 700 !important;
  letter-spacing: 3px !important;
  color: #00e5ff !important;
  border-bottom: 1px solid #1a3a6b;
  padding-bottom: 10px;
  margin: 24px 0 16px 0;
  text-transform: uppercase;
  text-shadow: 0 0 15px rgba(0,229,255,0.4);
}

/* ── Chat Messages ── */
div[data-testid="stChatMessage"] {
  border-radius: 16px !important;
  margin: 8px 0 !important;
}
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] td {
  color: #e8f4fd !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  line-height: 1.8 !important;
}
div[data-testid="stChatMessage"] strong {
  color: #ffffff !important;
  font-weight: 800 !important;
}
div[data-testid="stChatMessage"] code {
  color: #00ff9d !important;
  background: rgba(0,255,157,0.1) !important;
  padding: 2px 6px !important;
  border-radius: 4px !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, rgba(0,198,255,0.15), rgba(0,198,255,0.05)) !important;
  border: 1px solid rgba(0,198,255,0.4) !important;
  color: var(--accent-blue) !important;
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  letter-spacing: 1.5px !important;
  border-radius: 10px !important;
  transition: all 0.3s ease !important;
  text-transform: uppercase !important;
  font-size: 12px !important;
}
.stButton > button:hover {
  background: rgba(0,198,255,0.25) !important;
  box-shadow: 0 0 20px rgba(0,198,255,0.3) !important;
  transform: translateY(-2px) !important;
}

/* ── Tabs ── */
div[data-baseweb="tab-list"] {
  background: var(--bg-card2) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  border: 1px solid var(--border) !important;
  gap: 4px !important;
}
div[data-baseweb="tab"] {
  font-family: var(--font-body) !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  letter-spacing: 1px !important;
  border-radius: 10px !important;
  color: #a8d4f5 !important;
}
div[aria-selected="true"] {
  background: rgba(0,198,255,0.2) !important;
  color: #00e5ff !important;
}

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
  background: var(--bg-card2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text-primary) !important;
  font-family: var(--font-body) !important;
}

/* ── Chat Input ── */
div[data-testid="stChatInput"] {
  background: #0f2544 !important;
  border: 1.5px solid #2a5a9b !important;
  border-radius: 16px !important;
}
div[data-testid="stChatInput"] textarea {
  background: #0f2544 !important;
  border: none !important;
  border-radius: 16px !important;
  color: #ffffff !important;
  font-family: var(--font-body) !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  caret-color: #00c6ff !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
  color: #6a9abf !important;
  font-style: italic !important;
  font-size: 14px !important;
}
div[data-testid="stChatInput"] textarea:focus {
  outline: none !important;
  box-shadow: none !important;
}
div[data-testid="stChatInput"]:focus-within {
  border-color: #00c6ff !important;
  box-shadow: 0 0 0 2px rgba(0,198,255,0.2), 0 0 20px rgba(0,198,255,0.1) !important;
}
/* Send button */
div[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, #00c6ff, #0090cc) !important;
  border-radius: 10px !important;
  border: none !important;
  color: #ffffff !important;
}
div[data-testid="stChatInput"] button:hover {
  background: linear-gradient(135deg, #00e5ff, #00c6ff) !important;
  box-shadow: 0 0 12px rgba(0,198,255,0.5) !important;
}

/* ── CRITICAL: Kill the white bottom bar / footer container ── */
div[data-testid="stBottom"] {
  background: #050b18 !important;
  border-top: 1px solid #1a3a6b !important;
  padding: 12px 16px !important;
}
div[data-testid="stBottom"] > div {
  background: #050b18 !important;
}
.stChatFloatingInputContainer,
div[class*="stChatFloatingInputContainer"] {
  background: #050b18 !important;
  border-top: 1px solid #1a3a6b !important;
}
/* Streamlit's sticky bottom wrapper */
div[data-testid="stAppViewBlockContainer"] {
  background: #050b18 !important;
}
footer, footer * {
  background: #050b18 !important;
  color: #3a5a80 !important;
  border-top: 1px solid #1a3a6b !important;
}
/* Any leftover white containers */
section.main > div,
.block-container {
  background: #050b18 !important;
}
/* Remove white flash on page edges */
body {
  background: #050b18 !important;
}
html {
  background: #050b18 !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Tables ── */
table { 
  background: var(--bg-card2) !important; 
  border-radius: 12px !important;
  overflow: hidden !important;
  font-family: var(--font-mono) !important;
}
th { 
  background: rgba(0,198,255,0.1) !important; 
  color: var(--accent-blue) !important;
  font-family: var(--font-body) !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
  font-size: 12px !important;
}
td { color: var(--text-primary) !important; font-size: 13px !important; }

/* ── Sidebar Elements ── */
section[data-testid="stSidebar"] .stMarkdown h3 {
  color: var(--accent-gold) !important;
  font-family: var(--font-display) !important;
  font-size: 14px !important;
  letter-spacing: 2px !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
  color: var(--text-secondary) !important;
  font-family: var(--font-body) !important;
}

/* ── Info / Alert Boxes ── */
div[data-testid="stAlert"] {
  background: rgba(0,198,255,0.06) !important;
  border: 1px solid rgba(0,198,255,0.2) !important;
  border-radius: 12px !important;
  font-family: var(--font-body) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* ── AI Insight Card ── */
.insight-card {
  background: linear-gradient(135deg, rgba(182,96,245,0.12), rgba(0,198,255,0.08));
  border: 1px solid rgba(182,96,245,0.4);
  border-radius: 16px;
  padding: 20px 24px;
  margin: 12px 0;
  font-family: var(--font-body);
  font-size: 15px;
  font-weight: 600;
  color: #ddeeff !important;
  line-height: 1.7;
  position: relative;
  overflow: hidden;
}
.insight-card::before {
  content: '◈ AI INSIGHT';
  font-family: var(--font-mono);
  font-size: 11px;
  color: #c890ff;
  letter-spacing: 3px;
  display: block;
  margin-bottom: 10px;
  font-weight: 700;
}

/* ── Status Pulse ── */
.status-live {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--accent-green);
  letter-spacing: 2px;
}
.pulse-dot {
  width: 8px; height: 8px;
  background: var(--accent-green);
  border-radius: 50%;
  display: inline-block;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(0,255,157,0.4); }
  50% { opacity: 0.8; transform: scale(1.1); box-shadow: 0 0 0 6px rgba(0,255,157,0); }
}

/* ── Forecast Tag ── */
.forecast-tag {
  background: linear-gradient(135deg, rgba(245,197,24,0.15), rgba(245,197,24,0.05));
  border: 1px solid rgba(245,197,24,0.3);
  border-radius: 8px;
  padding: 2px 12px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--accent-gold);
  letter-spacing: 2px;
  display: inline-block;
  margin-right: 8px;
}
</style>
"""

# ═══════════════════════════════════════════════════════════════
#  DATA ENGINE
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def load_excel_data():
    file_options = [
        "RAW DATA.xlsx",
        r"Z:\data\RAW DATA.xlsx",
        os.path.join(os.path.dirname(__file__), "RAW DATA.xlsx")
    ]
    file_path = next((p for p in file_options if os.path.exists(p)), None)
    if not file_path:
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        month_map = {
            'July': 7, 'August': 8, 'September': 9, 'October': 10,
            'November': 11, 'December': 12, 'January': 1, 'February': 2,
            'March': 3, 'April': 4, 'May': 5, 'June': 6
        }
        df['Month_Num'] = df['Months'].map(month_map)
        fiscal_order = ['July','August','September','October','November','December',
                        'January','February','March','April','May','June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        df['Date_Obj'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str) + '-01')
        mask = (df['Date_Obj'] >= '2017-07-01') & (df['Date_Obj'] <= '2030-12-01')
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] >= 7 else x['Year']-1}-{x['Year'] if x['Month_Num'] <= 6 else x['Year']+1}", axis=1)
        return df.loc[mask].sort_values('Date_Obj').reset_index(drop=True)
    except Exception as e:
        st.sidebar.error(f"Data load error: {e}")
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════
#  ADVANCED AI FORECASTING ENGINE
# ═══════════════════════════════════════════════════════════════
EID_CALENDAR = {
    2025: [3, 4, 6], 2026: [3, 4, 6],
    2027: [3, 5, 6], 2028: [2, 5],
    2029: [2, 4],    2030: [1, 4]
}
SUMMER_PEAK = [6, 7, 8]
WINTER_PEAK = [12, 1]

def generate_advanced_forecast(df, m_num, y_num, metric_col):
    df_clean = df.dropna(subset=[metric_col]).copy()
    if len(df_clean) < 3:
        return 0, 0, "Insufficient Data"

    # Polynomial regression (degree 2 for seasonality curve)
    X = np.array(range(len(df_clean))).reshape(-1, 1)
    y = df_clean[metric_col].values
    poly_model = make_pipeline(PolynomialFeatures(2), LinearRegression())
    poly_model.fit(X, y)

    start_date = df_clean['Date_Obj'].min()
    target_date = pd.to_datetime(f"{y_num}-{m_num}-01")
    months_diff = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    base_pred = max(0, poly_model.predict([[months_diff]])[0])

    # Multiplier stacking
    multiplier = 1.0
    event_notes = []

    if y_num in EID_CALENDAR and m_num in EID_CALENDAR[y_num]:
        multiplier *= 1.48
        event_notes.append("🌙 Eid Season Boost")
    if m_num in SUMMER_PEAK:
        multiplier *= 1.22
        event_notes.append("☀️ Summer Peak")
    if m_num in WINTER_PEAK:
        multiplier *= 1.15
        event_notes.append("❄️ Winter Festive")
    if m_num == 12:
        multiplier *= 1.10
        event_notes.append("🎆 Year-End Surge")

    final_pred = base_pred * multiplier

    # Confidence band (±12%)
    lower = final_pred * 0.88
    upper = final_pred * 1.12

    note_str = " | ".join(event_notes) if event_notes else "📈 Standard Projection"
    return final_pred, (lower, upper), note_str


def compute_ai_insights(df):
    """Generate automatic AI insights from data."""
    insights = []
    if df.empty:
        return insights

    # Best month
    if 'Actual Revenue' in df.columns and 'Months' in df.columns:
        monthly = df.groupby('Months', observed=True)['Actual Revenue'].sum()
        if not monthly.empty:
            best_m = monthly.idxmax()
            insights.append(f"🏆 **Peak Month:** {best_m} generates the highest revenue historically.")

    # YoY growth
    if 'Year' in df.columns and 'Actual Revenue' in df.columns:
        yearly = df.groupby('Year')['Actual Revenue'].sum().sort_index()
        if len(yearly) >= 2:
            last_two = yearly.iloc[-2:]
            growth = (last_two.iloc[-1] - last_two.iloc[-2]) / last_two.iloc[-2] * 100
            direction = "↑ growth" if growth > 0 else "↓ decline"
            insights.append(f"📊 **YoY Trend:** {abs(growth):.1f}% {direction} in latest fiscal year.")

    # Footfall efficiency
    if 'Actual Revenue' in df.columns and 'Actual Footfall' in df.columns:
        df2 = df.dropna(subset=['Actual Revenue', 'Actual Footfall'])
        if not df2.empty and df2['Actual Footfall'].sum() > 0:
            rev_per_pax = df2['Actual Revenue'].sum() / df2['Actual Footfall'].sum()
            insights.append(f"💡 **Revenue/Pax:** Rs. {rev_per_pax:,.0f} average spend per visitor.")

    return insights


# ═══════════════════════════════════════════════════════════════
#  PLOTLY DARK THEME CONFIG
# ═══════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(5,11,24,0)',
    plot_bgcolor='rgba(10,22,40,0.5)',
    font=dict(family='Rajdhani, sans-serif', color='#e8f4fd', size=13),
    title_font=dict(family='Orbitron, monospace', size=16, color='#00c6ff'),
    legend=dict(
        bgcolor='rgba(13,31,60,0.8)',
        bordercolor='#1a3a6b',
        borderwidth=1,
        font=dict(family='Rajdhani', size=12)
    ),
    xaxis=dict(
        gridcolor='rgba(26,58,107,0.4)',
        linecolor='#1a3a6b',
        tickfont=dict(family='JetBrains Mono', size=11, color='#7a9cc0')
    ),
    yaxis=dict(
        gridcolor='rgba(26,58,107,0.4)',
        linecolor='#1a3a6b',
        tickfont=dict(family='JetBrains Mono', size=11, color='#7a9cc0')
    ),
    margin=dict(l=20, r=20, t=50, b=20)
)

COLOR_PALETTE = ['#00c6ff', '#f5c518', '#00ff9d', '#ff4466', '#b660f5', '#ff8c42', '#4ecdc4']


# ═══════════════════════════════════════════════════════════════
#  CHART BUILDERS
# ═══════════════════════════════════════════════════════════════
def build_revenue_gauge(actual, target):
    pct = min((actual / target * 100) if target > 0 else 0, 150)
    color = '#00ff9d' if pct >= 100 else '#f5c518' if pct >= 75 else '#ff4466'
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        delta={'reference': 100, 'suffix': '%', 'font': {'size': 18, 'family': 'Rajdhani'}},
        number={'suffix': '%', 'font': {'size': 36, 'family': 'Orbitron', 'color': color}},
        title={'text': "Revenue Achievement", 'font': {'size': 14, 'family': 'Orbitron', 'color': '#7a9cc0'}},
        gauge={
            'axis': {'range': [0, 150], 'tickcolor': '#7a9cc0', 'tickfont': {'family': 'JetBrains Mono', 'size': 10}},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': 'rgba(13,31,60,0.8)',
            'borderwidth': 0,
            'threshold': {'line': {'color': '#00c6ff', 'width': 3}, 'thickness': 0.75, 'value': 100},
            'steps': [
                {'range': [0, 75], 'color': 'rgba(255,68,102,0.1)'},
                {'range': [75, 100], 'color': 'rgba(245,197,24,0.1)'},
                {'range': [100, 150], 'color': 'rgba(0,255,157,0.1)'}
            ]
        }
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=320)
    return fig


def build_trend_chart(df, y_col, color, title):
    fig = go.Figure()
    # Area fill
    fig.add_trace(go.Scatter(
        x=df['Date_Obj'], y=df[y_col],
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)',
        line=dict(color=color, width=2.5),
        name=y_col,
        hovertemplate='<b>%{x|%b %Y}</b><br>' + f'{y_col}: ' + '%{y:,.0f}<extra></extra>'
    ))
    # Moving average
    if len(df) >= 6:
        ma = df[y_col].rolling(3, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df['Date_Obj'], y=ma,
            line=dict(color='#f5c518', width=1.5, dash='dot'),
            name='3M Moving Avg',
            hovertemplate='<b>3M Avg:</b> %{y:,.0f}<extra></extra>'
        ))
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=380)
    return fig


def build_bar_chart(df, x, y_cols, title):
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        if col in df.columns:
            fig.add_trace(go.Bar(
                x=df[x], y=df[col], name=col,
                marker_color=COLOR_PALETTE[i % len(COLOR_PALETTE)],
                marker_line_width=0,
                hovertemplate=f'<b>%{{x}}</b><br>{col}: %{{y:,.0f}}<extra></extra>'
            ))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', title=title, height=380)
    return fig


def build_waterfall(df, metric):
    df_s = df.groupby('Months', observed=True)[metric].sum().reset_index()
    vals = df_s[metric].tolist()
    measures = ['relative'] * len(vals)
    fig = go.Figure(go.Waterfall(
        x=df_s['Months'].tolist(),
        y=vals,
        measure=measures,
        connector=dict(line=dict(color='#1a3a6b')),
        increasing=dict(marker_color='#00ff9d'),
        decreasing=dict(marker_color='#ff4466'),
        totals=dict(marker_color='#00c6ff'),
        hovertemplate='<b>%{x}</b><br>Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=f"{metric} – Monthly Waterfall", height=380)
    return fig


def build_heatmap(df):
    if df.empty or 'Year' not in df.columns:
        return None
    pivot = df.pivot_table(values='Actual Revenue', index='Year', columns='Months', aggfunc='sum', observed=True)
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, '#050b18'], [0.5, '#003a6b'], [1, '#00c6ff']],
        hoverongaps=False,
        hovertemplate='<b>%{y} – %{x}</b><br>Rs. %{z:,.0f}<extra></extra>'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue Heatmap: Year × Month", height=360)
    return fig


def build_comparison_chart(comp_data):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Revenue', x=comp_data['labels'], y=comp_data['revenue'],
        marker_color=['#00c6ff', '#f5c518'],
        marker_line_width=0,
        hovertemplate='<b>%{x}</b><br>Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        name='Footfall', x=comp_data['labels'], y=comp_data['footfall'],
        marker_color=['rgba(0,198,255,0.4)', 'rgba(245,197,24,0.4)'],
        marker_line_width=0,
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} Pax<extra></extra>'
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode='group',
        title="Period Comparison — Revenue vs Footfall",
        height=400,
        yaxis2=dict(
            overlaying='y', side='right',
            gridcolor='rgba(26,58,107,0.2)',
            tickfont=dict(family='JetBrains Mono', size=11, color='#f5c518')
        )
    )
    return fig


def build_scatter_rff(df):
    """Revenue vs Footfall scatter with regression line."""
    d = df.dropna(subset=['Actual Revenue', 'Actual Footfall'])
    if len(d) < 3:
        return None
    X = d['Actual Footfall'].values.reshape(-1, 1)
    y = d['Actual Revenue'].values
    m = LinearRegression().fit(X, y)
    x_line = np.linspace(X.min(), X.max(), 100)
    y_line = m.predict(x_line.reshape(-1, 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d['Actual Footfall'], y=d['Actual Revenue'],
        mode='markers',
        marker=dict(color='#00c6ff', size=8, opacity=0.7,
                    line=dict(color='#f5c518', width=1)),
        hovertemplate='<b>Footfall:</b> %{x:,.0f}<br><b>Revenue:</b> Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        line=dict(color='#f5c518', width=2, dash='dash'),
        name='Regression'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue vs Footfall — Regression Analysis", height=380)
    return fig


def build_fy_bar(df):
    if 'Fiscal_Year_Label' not in df.columns:
        return None
    d = df.groupby('Fiscal_Year_Label')[['Actual Revenue', 'Target revenue']].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Actual', x=d['Fiscal_Year_Label'], y=d['Actual Revenue'],
                         marker_color='#00c6ff', marker_line_width=0))
    if 'Target revenue' in d.columns:
        fig.add_trace(go.Bar(name='Target', x=d['Fiscal_Year_Label'], y=d['Target revenue'],
                             marker_color='rgba(245,197,24,0.4)', marker_line_width=0))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', title="Fiscal Year Performance", height=380)
    return fig


# ═══════════════════════════════════════════════════════════════
#  QUERY PARSING ENGINE
# ═══════════════════════════════════════════════════════════════
MONTH_MAP_FULL = {
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
    'jan':1,'feb':2,'mar':3,'apr':4,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12
}
MONTH_PATTERN = r'(july|august|september|october|november|december|january|february|march|april|may|june)'

def parse_and_filter(query_lower, df_live):
    """Parse query and return filtered dataframe + comparison data."""
    comp_viz_data = None
    variance_report = ""

    if "vs" in query_lower or " v " in query_lower:
        sep = "vs" if "vs" in query_lower else " v "
        parts = query_lower.split(sep)
        if len(parts) == 2:
            def get_period(text):
                p_months = [m.capitalize() for m in re.findall(MONTH_PATTERN, text)]
                p_years = [int(y) for y in re.findall(r'\b(20\d{2})\b', text)]
                if not p_years:
                    return pd.DataFrame(), ""
                mask = df_live['Year'].isin(p_years)
                if p_months:
                    mask &= df_live['Months'].isin(p_months)
                label_parts = []
                if p_months:
                    label_parts.append(', '.join(p_months))
                label_parts.append(str(p_years[0]))
                return df_live[mask], ' '.join(label_parts)
            v1, l1 = get_period(parts[0])
            v2, l2 = get_period(parts[1])
            if not v1.empty and not v2.empty:
                rev1, rev2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
                ff1, ff2 = v1['Actual Footfall'].sum(), v2['Actual Footfall'].sum()
                r_perc = (rev2-rev1)/rev1*100 if rev1 > 0 else 0
                f_perc = (ff2-ff1)/ff1*100 if ff1 > 0 else 0
                variance_report = (
                    f"\n\n**Revenue Change:** `{r_perc:+.1f}%`  |  **Footfall Change:** `{f_perc:+.1f}%`"
                )
                temp_df = pd.concat([v1, v2])
                comp_viz_data = {"labels": [l1, l2], "revenue": [rev1, rev2], "footfall": [ff1, ff2]}
                return temp_df, comp_viz_data, variance_report
    else:
        temp_df = df_live.copy()
        f_m = [m.capitalize() for m in re.findall(MONTH_PATTERN, query_lower)]
        f_y = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
        fy_match = re.findall(r'fy\s*(\d{2,4})', query_lower)

        if f_m:
            temp_df = temp_df[temp_df['Months'].isin(f_m)]
        if f_y:
            temp_df = temp_df[temp_df['Year'].isin(f_y)]
        if fy_match:
            fy_label_part = fy_match[0]
            temp_df = temp_df[temp_df['Fiscal_Year_Label'].str.contains(fy_label_part, na=False)]

        return temp_df, None, ""

    return df_live.copy(), None, ""


# ═══════════════════════════════════════════════════════════════
#  HELP TEXT
# ═══════════════════════════════════════════════════════════════
SAMPLE_QUERIES = [
    "Revenue July 2022",
    "Footfall August 2023 vs August 2024",
    "Forecast March 2027",
    "FY 2023 revenue",
    "Total 2024 footfall",
    "Predict December 2028"
]


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
def render_sidebar(df_live, auth_obj):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 16px 0 8px;'>
          <div style='font-family:Orbitron,monospace; font-size:11px; letter-spacing:4px; color:#7a9cc0;'>JOYLAND MIS</div>
          <div style='font-family:Orbitron,monospace; font-size:20px; font-weight:900; color:#00c6ff; margin:4px 0;'>CONTROL</div>
          <div style='font-family:Orbitron,monospace; font-size:9px; letter-spacing:3px; color:#3a5a80;'>INTELLIGENCE CENTER</div>
        </div>
        <div style='border-bottom:1px solid #1a3a6b; margin:8px 0 16px;'></div>
        """, unsafe_allow_html=True)

        analyst_name = st.session_state.get('name', 'Analyst')
        st.markdown(f"""
        <div style='background:rgba(0,198,255,0.06); border:1px solid rgba(0,198,255,0.2); border-radius:12px; padding:14px 16px; margin-bottom:16px;'>
          <div style='font-family:Rajdhani; font-size:11px; letter-spacing:2px; color:#7a9cc0; text-transform:uppercase; margin-bottom:4px;'>ACTIVE ANALYST</div>
          <div style='font-family:Orbitron; font-size:14px; color:#00c6ff; font-weight:700;'>{analyst_name}</div>
          <div class='status-live' style='margin-top:8px;'><span class='pulse-dot'></span> SYSTEM ONLINE</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ CLEAR HISTORY", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_filtered_df = None
            st.session_state.comparison_data = None
            st.rerun()

        auth_obj.logout('⏻  LOGOUT', 'sidebar')

        st.markdown("""<div style='border-bottom:1px solid #1a3a6b; margin:16px 0;'></div>""", unsafe_allow_html=True)

        # Data overview
        if not df_live.empty:
            total_months = len(df_live)
            date_range = f"{df_live['Date_Obj'].min().strftime('%Y')} – {df_live['Date_Obj'].max().strftime('%Y')}"
            st.markdown(f"""
            <div style='background:rgba(13,31,60,0.8); border:1px solid #1a3a6b; border-radius:12px; padding:14px; margin-bottom:12px;'>
              <div style='font-family:Rajdhani; font-size:11px; letter-spacing:2px; color:#a8d4f5; text-transform:uppercase; margin-bottom:8px; font-weight:700;'>DATA SCOPE</div>
              <div style='font-family:JetBrains Mono; font-size:13px; color:#e8f4fd; margin:5px 0; font-weight:600;'>📅 {date_range}</div>
              <div style='font-family:JetBrains Mono; font-size:13px; color:#e8f4fd; margin:5px 0; font-weight:600;'>📊 {total_months} Data Points</div>
              <div style='font-family:JetBrains Mono; font-size:13px; color:#e8f4fd; margin:5px 0; font-weight:600;'>🎯 AI Model: Poly-2 + LR</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background:rgba(13,31,60,0.8); border:1px solid #1a3a6b; border-radius:12px; padding:14px; margin-bottom:12px;'>
          <div style='font-family:Rajdhani; font-size:11px; letter-spacing:2px; color:#a8d4f5; text-transform:uppercase; margin-bottom:8px; font-weight:700;'>QUERY EXAMPLES</div>
        """, unsafe_allow_html=True)
        for q in SAMPLE_QUERIES:
            st.markdown(f"<div style='font-family:JetBrains Mono; font-size:12px; color:#c8dff0; margin:5px 0; font-weight:600;'>› {q}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center; padding:12px; font-family:Rajdhani; font-size:11px; color:#3a5a80; letter-spacing:1px;'>
          ARCHITECT: <span style='color:#f5c518; font-weight:700;'>UMAIR NIZAM</span><br>
          <span style='color:#1a3a6b;'>v3.0 ULTRA · 2017–2030</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Joyland MIS Assistant · Grand Master",
        layout="wide",
        page_icon="🎢",
        initial_sidebar_state="expanded"
    )
    st.markdown(PAGE_THEME, unsafe_allow_html=True)

    # Session state init
    defaults = {
        'messages': [],
        'last_filtered_df': None,
        'comparison_data': None,
        'show_insights': False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    df_live = load_excel_data()

    # ── AUTH ──
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    try:
        from streamlit_authenticator import Authenticate
        auth = Authenticate(credentials, "joyland_mis", "auth_key_v3", cookie_expiry_days=30)
        auth.login(location='main')
        is_auth = st.session_state.get("authentication_status")
    except ImportError:
        st.warning("streamlit-authenticator not installed. Running in demo mode.")
        is_auth = True
        auth = None

    if not is_auth:
        st.markdown("""
        <div style='max-width:400px; margin:80px auto; text-align:center;'>
          <div style='font-family:Orbitron,monospace; font-size:32px; font-weight:900;
               background:linear-gradient(135deg,#00c6ff,#f5c518);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px;'>
            JOYLAND MIS ASSISTANT
          </div>
          <div style='font-family:Rajdhani; font-size:13px; letter-spacing:3px; color:#7a9cc0; margin-bottom:32px;'>
            INTELLIGENCE PLATFORM
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── AUTHENTICATED VIEW ──
    if auth:
        render_sidebar(df_live, auth)

    # ── HERO BANNER ──
    st.markdown("""
    <div class='hero-banner'>
      <div class='hero-title'>JOYLAND  BI</div>
      <div class='hero-subtitle'>Advanced Business Intelligence & Predictive Analytics Platform</div>
      <div class='hero-badge'>⬡ AI-POWERED · SCOPE 2017–2030 · GRAND MASTER v3.0</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI PULSE ──
    if not df_live.empty:
        try:
            total_rev = df_live['Actual Revenue'].sum()
            total_ff  = df_live['Actual Footfall'].sum()
            avg_rev   = df_live['Actual Revenue'].mean()
            total_tgt = df_live['Target revenue'].sum() if 'Target revenue' in df_live.columns else 0
            ach_rate  = (total_rev / total_tgt * 100) if total_tgt > 0 else 0
            rev_per_pax = total_rev / total_ff if total_ff > 0 else 0

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("💰 Lifetime Revenue", f"Rs. {total_rev/1e6:.1f}M", "All-Time Actual")
            k2.metric("👥 Total Visitors", f"{total_ff/1e6:.2f}M Pax", "Cumulative Volume")
            k3.metric("📊 Avg Monthly Rev", f"Rs. {avg_rev/1e3:.0f}K", "Baseline Trend")
            k4.metric("🎯 Achievement Rate", f"{ach_rate:.1f}%", "vs Target")
            k5.metric("💡 Rev Per Visitor", f"Rs. {rev_per_pax:,.0f}", "Spend Index")
        except Exception:
            st.info("KPI cards require 'Actual Revenue', 'Actual Footfall', 'Target revenue' columns.")

    st.divider()

    # ── AI INSIGHTS BAR ──
    if not df_live.empty:
        insights = compute_ai_insights(df_live)
        if insights:
            st.markdown(f"""
            <div class='insight-card'>
              {'  ·  '.join(insights)}
            </div>
            """, unsafe_allow_html=True)

    # ── CHAT INTERFACE ──
    st.markdown("<div class='section-header'>◈ AI ANALYTICS ASSISTANT</div>", unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            role = "user" if msg["is_user"] else "assistant"
            with st.chat_message(role):
                st.markdown(msg["content"])

    prompt = st.chat_input("Ask: Revenue, Footfall, Forecasts, Comparisons, Trends…")

    if prompt:
        st.session_state.messages.append({"content": prompt, "is_user": True})
        query_lower = prompt.lower().strip()

        # ── GREETING / INTRO INTENT ──
        greeting_keywords = ['hi', 'hello', 'hey', 'salam', 'assalam', 'helo', 'hii', 'who are you',
                             'introduce', 'intro', 'aap kaun', 'tumhara naam', 'your name', 'about you',
                             'what are you', 'tell me about yourself', 'help']
        if any(query_lower.strip() == g or query_lower.startswith(g) for g in greeting_keywords):
            intro_msg = (
                "### 👋 Assalam o Alaikum! Welcome to **Joyland BI**\n\n"
                "---\n"
                "🤖 **I am the Joyland MIS Assistant** — an AI-powered Business Intelligence Bot built exclusively for **Joyland Amusement Park**.\n\n"
                "I was developed by **MIS Assistant Manager Umair Nizam** to help the management team make smarter, faster, data-driven decisions.\n\n"
                "---\n"
                "### 🧠 What I Can Do For You:\n\n"
                "| Capability | Example Query |\n"
                "|------------|---------------|\n"
                "| 💰 Revenue Analysis | `Revenue July 2023` |\n"
                "| 👥 Footfall Reports | `Footfall August 2024` |\n"
                "| 📊 Period Comparison | `August 2023 vs August 2024` |\n"
                "| 🔮 AI Forecasting | `Forecast March 2027` |\n"
                "| 📅 Fiscal Year Data | `FY 2023 revenue` |\n"
                "| 🌙 Event Predictions | `Predict December 2028` |\n\n"
                "---\n"
                "> *Scope: 2017 – 2030 · Model: Polynomial Regression + Seasonal AI Multipliers*\n\n"
                "**How can I assist you today? Just ask! 🚀**"
            )
            st.session_state.messages.append({"content": intro_msg, "is_user": False})
            st.rerun()

        # ── FORECAST INTENT ──
        forecast_keywords = ['forecast', 'predict', 'projection', 'estimate', 'btao', 'prediction', 'expected']
        if any(k in query_lower for k in forecast_keywords):
            found_m = next((m for m in MONTH_MAP_FULL if m in query_lower), None)
            found_y = re.findall(r'\b(202[5-9]|2030)\b', query_lower)
            if found_m and found_y:
                m_idx, y_val = MONTH_MAP_FULL[found_m], int(found_y[0])
                if not df_live.empty:
                    p_rev, (lr, ur), note_rev = generate_advanced_forecast(df_live, m_idx, y_val, 'Actual Revenue')
                    p_ff,  (lf, uf), note_ff  = generate_advanced_forecast(df_live, m_idx, y_val, 'Actual Footfall')
                    ans = (
                        f"### 🔮 AI Forecast — {found_m.capitalize()} {y_val}\n\n"
                        f"| Metric | Projection | Confidence Range |\n"
                        f"|--------|------------|------------------|\n"
                        f"| 💰 Revenue | **Rs. {p_rev:,.0f}** | Rs. {lr:,.0f} – Rs. {ur:,.0f} |\n"
                        f"| 👥 Footfall | **{p_ff:,.0f} Pax** | {lf:,.0f} – {uf:,.0f} |\n\n"
                        f"**Modifiers Applied:** {note_rev}\n\n"
                        f"> *Model: Polynomial Regression (deg 2) + Seasonal Event Multipliers*\n"
                        f"> *Confidence Band: ±12% (1σ)*"
                    )
                else:
                    ans = "⚠️ No data loaded. Please ensure RAW DATA.xlsx is available."
                st.session_state.messages.append({"content": ans, "is_user": False})
                st.rerun()
            else:
                st.session_state.messages.append({
                    "content": "🔮 **Forecast requires:** Month + Year (2025–2030)\n\n*Example: `Forecast March 2027`*",
                    "is_user": False
                })
                st.rerun()

        # ── DATA QUERY ──
        elif not df_live.empty:
            temp_df, comp_viz_data, variance_report = parse_and_filter(query_lower, df_live)
            st.session_state.last_filtered_df = temp_df
            st.session_state.comparison_data = comp_viz_data

            if not temp_df.empty:
                cols_present = [c for c in ['Actual Revenue', 'Actual Footfall', 'Target revenue', 'Target Footfall'] if c in temp_df.columns]
                res = temp_df[cols_present].sum()
                ach = ""
                if 'Actual Revenue' in res and 'Target revenue' in res and res['Target revenue'] > 0:
                    ach = f"\n* 🎯 Achievement: **{res['Actual Revenue']/res['Target revenue']*100:.1f}%**"
                response_md = (
                    f"### 📊 Analysis Result\n\n"
                    f"* 💰 Revenue: **Rs. {res.get('Actual Revenue', 0):,.0f}**\n"
                    f"* 👥 Footfall: **{res.get('Actual Footfall', 0):,.0f} Pax**{ach}"
                    f"{variance_report}\n\n"
                    f"*→ See Visual Insights tab below*"
                )
                st.session_state.messages.append({"content": response_md, "is_user": False})
            else:
                st.session_state.messages.append({
                    "content": "⚠️ No data matched your query. Try adjusting month/year filters.\n\n**Hint:** `Revenue July 2022` or `August 2023 vs August 2024`",
                    "is_user": False
                })
            st.rerun()
        else:
            st.session_state.messages.append({
                "content": "⚠️ Data file not found. Ensure **RAW DATA.xlsx** is in the app directory.",
                "is_user": False
            })
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    #  VISUALIZATION PANEL
    # ═══════════════════════════════════════════════════════════
    if st.session_state.last_filtered_df is not None and not st.session_state.last_filtered_df.empty:
        df_plot = st.session_state.last_filtered_df

        st.markdown("<div class='section-header'>◈ VISUAL INTELLIGENCE PANEL</div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs([
            "📉 Visual Insights",
            "🔬 Deep Analysis",
            "🔮 Forecast Center",
            "📋 Raw Data"
        ])

        # ── TAB 1: VISUAL INSIGHTS ──
        with tab1:
            if st.session_state.comparison_data:
                st.plotly_chart(build_comparison_chart(st.session_state.comparison_data), use_container_width=True)
                st.divider()

            metrics = {c: c for c in ['Actual Revenue', 'Target revenue', 'Actual Footfall', 'Target Footfall'] if c in df_plot.columns}
            res = df_plot[list(metrics)].sum()

            chart_option = st.selectbox("🎯 Select Visualization", [
                "1. Revenue Achievement Gauge",
                "2. Footfall Achievement Gauge",
                "3. Actual vs Target — Bar Chart",
                "4. Footfall Trend Line",
                "5. Revenue Area Volume",
                "6. Monthly Share — Pie Chart",
                "7. Waterfall Analysis",
                "8. Revenue vs Footfall Regression"
            ])

            if chart_option.startswith("1"):
                tgt_rev = res.get('Target revenue', 0)
                act_rev = res.get('Actual Revenue', 0)
                st.plotly_chart(build_revenue_gauge(act_rev, tgt_rev), use_container_width=True)

            elif chart_option.startswith("2"):
                tgt_ff = res.get('Target Footfall', 0)
                act_ff = res.get('Actual Footfall', 0)
                pct = (act_ff / tgt_ff * 100) if tgt_ff > 0 else 0
                color = '#00ff9d' if pct >= 100 else '#f5c518' if pct >= 75 else '#ff4466'
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=pct,
                    delta={'reference': 100, 'suffix': '%'},
                    number={'suffix': '%', 'font': {'size': 36, 'family': 'Orbitron', 'color': color}},
                    title={'text': "Footfall Achievement", 'font': {'size': 14, 'family': 'Orbitron', 'color': '#7a9cc0'}},
                    gauge={
                        'axis': {'range': [0, 150]},
                        'bar': {'color': color, 'thickness': 0.28},
                        'bgcolor': 'rgba(13,31,60,0.8)',
                        'borderwidth': 0,
                        'threshold': {'line': {'color': '#00c6ff', 'width': 3}, 'thickness': 0.75, 'value': 100},
                        'steps': [
                            {'range': [0, 75], 'color': 'rgba(255,68,102,0.1)'},
                            {'range': [75, 100], 'color': 'rgba(245,197,24,0.1)'},
                            {'range': [100, 150], 'color': 'rgba(0,255,157,0.1)'}
                        ]
                    }
                ))
                fig.update_layout(**PLOTLY_LAYOUT, height=320)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_option.startswith("3"):
                cols = [c for c in ['Actual Revenue', 'Target revenue'] if c in df_plot.columns]
                st.plotly_chart(build_bar_chart(df_plot, 'Months', cols, "Revenue: Actual vs Target"), use_container_width=True)

            elif chart_option.startswith("4"):
                if 'Actual Footfall' in df_plot.columns:
                    st.plotly_chart(build_trend_chart(df_plot, 'Actual Footfall', '#f5c518', 'Footfall Trend'), use_container_width=True)

            elif chart_option.startswith("5"):
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(build_trend_chart(df_plot, 'Actual Revenue', '#00c6ff', 'Revenue Volume Trend'), use_container_width=True)

            elif chart_option.startswith("6"):
                if 'Actual Revenue' in df_plot.columns:
                    fig = px.pie(df_plot, values='Actual Revenue', names='Months',
                                 color_discrete_sequence=COLOR_PALETTE, hole=0.45)
                    fig.update_traces(textposition='outside', textinfo='percent+label',
                                      textfont=dict(family='Rajdhani', size=12))
                    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue Distribution by Month", height=420)
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_option.startswith("7"):
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(build_waterfall(df_plot, 'Actual Revenue'), use_container_width=True)

            elif chart_option.startswith("8"):
                fig = build_scatter_rff(df_plot)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            # Summary table
            st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
            disp_cols = [c for c in ['Actual Revenue', 'Target revenue', 'Actual Footfall', 'Target Footfall'] if c in df_plot.columns]
            if disp_cols:
                summary = df_plot[disp_cols].sum().to_frame(name='Total').T
                st.dataframe(
                    summary.style.format('{:,.0f}').set_properties(**{
                        'background-color': '#0d1f3c',
                        'color': '#e8f4fd',
                        'border': '1px solid #1a3a6b',
                        'font-family': 'JetBrains Mono'
                    }),
                    use_container_width=True
                )

        # ── TAB 2: DEEP ANALYSIS ──
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                fy_fig = build_fy_bar(df_plot)
                if fy_fig:
                    st.plotly_chart(fy_fig, use_container_width=True)
            with c2:
                hm_fig = build_heatmap(df_plot)
                if hm_fig:
                    st.plotly_chart(hm_fig, use_container_width=True)

            # Monthly YoY comparison
            if 'Year' in df_plot.columns and 'Actual Revenue' in df_plot.columns:
                years = sorted(df_plot['Year'].dropna().unique())
                if len(years) >= 2:
                    fig_yoy = go.Figure()
                    for i, yr in enumerate(years):
                        yr_data = df_plot[df_plot['Year'] == yr]
                        fig_yoy.add_trace(go.Scatter(
                            x=yr_data['Months'].astype(str),
                            y=yr_data['Actual Revenue'],
                            name=str(int(yr)),
                            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2.5),
                            mode='lines+markers',
                            marker=dict(size=7)
                        ))
                    fig_yoy.update_layout(**PLOTLY_LAYOUT, title="Year-over-Year Monthly Comparison", height=420)
                    st.plotly_chart(fig_yoy, use_container_width=True)

        # ── TAB 3: FORECAST CENTER ──
        with tab3:
            st.markdown("<div class='section-header'>◈ PREDICTIVE ANALYTICS ENGINE</div>", unsafe_allow_html=True)

            # Full historical + projection chart
            if not df_live.empty and 'Actual Revenue' in df_live.columns:
                fig_full = go.Figure()
                fig_full.add_trace(go.Scatter(
                    x=df_live['Date_Obj'], y=df_live['Actual Revenue'],
                    name='Historical Revenue',
                    line=dict(color='#00c6ff', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0,198,255,0.06)',
                    hovertemplate='<b>%{x|%b %Y}</b><br>Rs. %{y:,.0f}<extra></extra>'
                ))
                # Trend line projection
                df_hist = df_live.dropna(subset=['Actual Revenue'])
                if len(df_hist) >= 5:
                    X = np.arange(len(df_hist)).reshape(-1, 1)
                    y_vals = df_hist['Actual Revenue'].values
                    poly_model = make_pipeline(PolynomialFeatures(2), LinearRegression())
                    poly_model.fit(X, y_vals)
                    future_steps = 24
                    all_steps = np.arange(len(df_hist) + future_steps).reshape(-1, 1)
                    trend = poly_model.predict(all_steps)
                    last_date = df_hist['Date_Obj'].max()
                    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, future_steps+1)]
                    all_dates = pd.concat([df_hist['Date_Obj'], pd.Series(future_dates)], ignore_index=True)
                    fig_full.add_trace(go.Scatter(
                        x=all_dates, y=np.maximum(trend, 0),
                        name='AI Trend Projection',
                        line=dict(color='#f5c518', width=2, dash='dot'),
                        hovertemplate='<b>%{x|%b %Y}</b><br>Projected: Rs. %{y:,.0f}<extra></extra>'
                    ))
                fig_full.update_layout(**PLOTLY_LAYOUT, title="2017–2030 Revenue Trajectory & AI Forecast", height=450)
                st.plotly_chart(fig_full, use_container_width=True)

                # Eid calendar info
                st.markdown("""
                <div style='background:rgba(245,197,24,0.06); border:1px solid rgba(245,197,24,0.2); border-radius:12px; padding:16px 20px; margin-top:8px;'>
                  <div style='font-family:Orbitron; font-size:12px; letter-spacing:3px; color:#f5c518; margin-bottom:10px;'>🌙 EID SEASON MULTIPLIER CALENDAR</div>
                  <div style='font-family:JetBrains Mono; font-size:12px; color:#7a9cc0; line-height:2;'>
                    2025 → Mar, Apr, Jun (+48%)&nbsp;&nbsp;|&nbsp;&nbsp;2026 → Mar, Apr, Jun (+48%)<br>
                    2027 → Mar, May, Jun (+48%)&nbsp;&nbsp;|&nbsp;&nbsp;2028 → Feb, May (+48%)<br>
                    2029 → Feb, Apr (+48%)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;2030 → Jan, Apr (+48%)
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # ── TAB 4: RAW DATA ──
        with tab4:
            st.markdown(f"<div style='font-family:Rajdhani; color:#7a9cc0; margin-bottom:12px; letter-spacing:1px;'>Showing {len(df_plot):,} records</div>", unsafe_allow_html=True)
            display_cols = [c for c in df_plot.columns if c not in ['Month_Num', 'Date_Obj']]
            st.dataframe(
                df_plot[display_cols].style.format({
                    c: '{:,.0f}' for c in display_cols if pd.api.types.is_numeric_dtype(df_plot[c])
                }).set_properties(**{
                    'background-color': '#0d1f3c',
                    'color': '#e8f4fd',
                    'border': '1px solid #1a3a6b'
                }),
                use_container_width=True,
                height=500
            )
            csv = df_plot.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ EXPORT CSV",
                data=csv,
                file_name=f"joyland_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime='text/csv',
                use_container_width=True
            )


if __name__ == "__main__":
    main()
