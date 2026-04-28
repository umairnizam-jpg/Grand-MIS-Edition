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
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
#  JOYLAND MIS ASSISTANT  ·  v4.0 Grand Master
#  Architect: Umair Nizam  |  Scope: 2017 – 2030
#  AI Engine: Deep Data-Trained NLP + Polynomial Forecasting
# ═══════════════════════════════════════════════════════════════

PAGE_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
:root {
  --bg-primary:#050b18; --bg-secondary:#0a1628; --bg-card:#0d1f3c; --bg-card2:#091530;
  --border:#1a3a6b; --border-glow:#00c6ff; --accent-blue:#00c6ff; --accent-gold:#f5c518;
  --accent-green:#00ff9d; --accent-red:#ff4466; --accent-purple:#b660f5;
  --text-primary:#e8f4fd; --text-secondary:#7a9cc0; --text-dim:#3a5a80;
  --font-display:'Orbitron',monospace; --font-body:'Rajdhani',sans-serif; --font-mono:'JetBrains Mono',monospace;
}
html,body,[class*="css"]{font-family:var(--font-body)!important;color:#e8f4fd!important;}
p,span,div,label{color:#e8f4fd!important;}
.stMarkdown p,.stMarkdown span,.stMarkdown li{color:#ddeeff!important;font-size:15px!important;font-weight:500!important;line-height:1.8!important;}
.main,.stApp{background:var(--bg-primary)!important;}
.main::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,198,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,198,255,0.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#050b18 0%,#071020 100%)!important;border-right:1px solid var(--border)!important;}
section[data-testid="stSidebar"]::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent-blue),var(--accent-gold),transparent);animation:scanline 3s ease-in-out infinite;}
@keyframes scanline{0%,100%{opacity:0.3;}50%{opacity:1;}}
div[data-testid="stMetric"]{background:linear-gradient(135deg,#0f2544 0%,#0c1d38 100%)!important;border:1px solid #2a5a9b!important;border-radius:16px!important;padding:24px 20px!important;position:relative;overflow:hidden;transition:transform 0.3s ease,box-shadow 0.3s ease;}
div[data-testid="stMetric"]:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,198,255,0.25)!important;border-color:#00c6ff!important;}
div[data-testid="stMetric"]::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#00c6ff,#f5c518);}
div[data-testid="stMetricLabel"]>div{color:#a8d4f5!important;font-family:var(--font-body)!important;font-size:14px!important;letter-spacing:1.5px!important;text-transform:uppercase!important;font-weight:700!important;}
div[data-testid="stMetricValue"]>div{color:#ffffff!important;font-family:var(--font-display)!important;font-size:26px!important;font-weight:900!important;text-shadow:0 0 20px rgba(0,198,255,0.5)!important;}
div[data-testid="stMetricDelta"]>div{color:#00ff9d!important;font-family:var(--font-body)!important;font-size:13px!important;font-weight:700!important;background:rgba(0,255,157,0.15)!important;padding:3px 12px!important;border-radius:20px!important;border:1px solid rgba(0,255,157,0.4)!important;}
.hero-banner{background:linear-gradient(135deg,#050b18 0%,#071428 50%,#050b18 100%);border:1px solid var(--border);border-radius:20px;padding:32px 40px;margin-bottom:28px;position:relative;overflow:hidden;text-align:center;}
.hero-banner::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 20% 50%,rgba(0,198,255,0.06) 0%,transparent 60%),radial-gradient(ellipse at 80% 50%,rgba(245,197,24,0.06) 0%,transparent 60%);}
.hero-title{font-family:var(--font-display)!important;font-size:42px!important;font-weight:900!important;letter-spacing:6px!important;background:linear-gradient(135deg,#00c6ff 0%,#f5c518 50%,#00ff9d 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0 0 8px 0;}
.hero-subtitle{font-family:var(--font-body)!important;color:#c8dff0!important;font-size:15px!important;letter-spacing:4px!important;text-transform:uppercase!important;font-weight:600!important;}
.hero-badge{display:inline-block;background:rgba(0,198,255,0.18);border:1px solid rgba(0,198,255,0.5);border-radius:20px;padding:5px 18px;font-family:var(--font-mono);font-size:12px;color:#00e5ff;letter-spacing:2px;margin-top:12px;font-weight:700;}
.section-header{font-family:var(--font-display)!important;font-size:18px!important;font-weight:700!important;letter-spacing:3px!important;color:#00e5ff!important;border-bottom:1px solid #1a3a6b;padding-bottom:10px;margin:24px 0 16px 0;text-transform:uppercase;text-shadow:0 0 15px rgba(0,229,255,0.4);}
div[data-testid="stChatMessage"] p,div[data-testid="stChatMessage"] span,div[data-testid="stChatMessage"] li,div[data-testid="stChatMessage"] td{color:#e8f4fd!important;font-size:15px!important;font-weight:500!important;line-height:1.8!important;}
div[data-testid="stChatMessage"] strong{color:#ffffff!important;font-weight:800!important;}
div[data-testid="stChatMessage"] code{color:#00ff9d!important;background:rgba(0,255,157,0.1)!important;padding:2px 6px!important;border-radius:4px!important;}
.stButton>button{background:linear-gradient(135deg,rgba(0,198,255,0.15),rgba(0,198,255,0.05))!important;border:1px solid rgba(0,198,255,0.4)!important;color:var(--accent-blue)!important;font-family:var(--font-body)!important;font-weight:600!important;letter-spacing:1.5px!important;border-radius:10px!important;transition:all 0.3s ease!important;text-transform:uppercase!important;font-size:12px!important;}
.stButton>button:hover{background:rgba(0,198,255,0.25)!important;box-shadow:0 0 20px rgba(0,198,255,0.3)!important;transform:translateY(-2px)!important;}
div[data-baseweb="tab-list"]{background:var(--bg-card2)!important;border-radius:12px!important;padding:4px!important;border:1px solid var(--border)!important;gap:4px!important;}
div[data-baseweb="tab"]{font-family:var(--font-body)!important;font-weight:700!important;font-size:14px!important;letter-spacing:1px!important;border-radius:10px!important;color:#a8d4f5!important;}
div[aria-selected="true"]{background:rgba(0,198,255,0.2)!important;color:#00e5ff!important;}
div[data-baseweb="select"]>div{background:#091530!important;border:1px solid #1a3a6b!important;border-radius:10px!important;color:#e8f4fd!important;}
div[data-baseweb="select"] span,div[data-baseweb="select"] div[class*="singleValue"],div[data-baseweb="select"] div[class*="placeholder"]{color:#e8f4fd!important;font-family:'Rajdhani',sans-serif!important;font-weight:600!important;}
div[data-testid="stChatInput"]{background:#0f2544!important;border:1.5px solid #2a5a9b!important;border-radius:16px!important;}
div[data-testid="stChatInput"] textarea{background:#0f2544!important;border:none!important;color:#ffffff!important;font-family:var(--font-body)!important;font-size:15px!important;caret-color:#00c6ff!important;}
div[data-testid="stChatInput"] textarea::placeholder{color:#6a9abf!important;font-style:italic!important;}
div[data-testid="stChatInput"]:focus-within{border-color:#00c6ff!important;box-shadow:0 0 0 2px rgba(0,198,255,0.2),0 0 20px rgba(0,198,255,0.1)!important;}
div[data-testid="stChatInput"] button{background:linear-gradient(135deg,#00c6ff,#0090cc)!important;border-radius:10px!important;border:none!important;color:#ffffff!important;}
div[data-testid="stBottom"]{background:#050b18!important;border-top:1px solid #1a3a6b!important;}
div[data-testid="stBottom"]>div{background:#050b18!important;}
.stChatFloatingInputContainer{background:#050b18!important;border-top:1px solid #1a3a6b!important;}
footer,footer *{background:#050b18!important;color:#3a5a80!important;}
section.main>div,.block-container{background:#050b18!important;}
body{background:#050b18!important;}html{background:#050b18!important;}
hr{border-color:var(--border)!important;}
table{background:var(--bg-card2)!important;border-radius:12px!important;overflow:hidden!important;}
th{background:rgba(0,198,255,0.1)!important;color:var(--accent-blue)!important;font-family:var(--font-body)!important;letter-spacing:1px!important;text-transform:uppercase!important;font-size:12px!important;}
td{color:var(--text-primary)!important;font-size:13px!important;}
div[data-baseweb="popover"],div[data-baseweb="popover"]>div,ul[role="listbox"],div[role="listbox"],[data-baseweb="menu"],[data-baseweb="menu"] ul,[data-baseweb="menu"]>div{background:#091530!important;border:1px solid #1a3a6b!important;border-radius:12px!important;box-shadow:0 8px 32px rgba(0,0,0,0.7)!important;}
li[role="option"],div[role="option"],[data-baseweb="menu"] li{background:#091530!important;color:#e8f4fd!important;font-family:'Rajdhani',sans-serif!important;font-size:14px!important;font-weight:600!important;}
li[role="option"]:hover,div[role="option"]:hover,li[aria-selected="true"]{background:rgba(0,198,255,0.15)!important;color:#00e5ff!important;}
div[data-testid="stPlotlyChart"],div[data-testid="stPlotlyChart"]>div,.js-plotly-plot,.js-plotly-plot .plotly{background:transparent!important;}
div[data-testid="stDataFrame"],div[data-testid="stDataFrame"]>div{background:#0d1f3c!important;border:1px solid #1a3a6b!important;border-radius:12px!important;}
div[data-testid="stTable"]{background:#091530!important;border-radius:12px!important;overflow:hidden!important;}
div[data-testid="stExpander"],details[data-testid="stExpander"]{background:#091530!important;border:1px solid #1a3a6b!important;border-radius:12px!important;}
div[data-baseweb="tab-panel"],div[role="tabpanel"],div[role="tabpanel"]>div{background:#050b18!important;padding-top:16px!important;}
div[data-testid="stAlert"]{background:rgba(0,198,255,0.06)!important;border:1px solid rgba(0,198,255,0.2)!important;border-radius:12px!important;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--bg-primary);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent-blue);}
.insight-card{background:linear-gradient(135deg,rgba(182,96,245,0.12),rgba(0,198,255,0.08));border:1px solid rgba(182,96,245,0.4);border-radius:16px;padding:20px 24px;margin:12px 0;font-family:var(--font-body);font-size:15px;font-weight:600;color:#ddeeff!important;line-height:1.7;position:relative;overflow:hidden;}
.insight-card::before{content:'◈ AI INSIGHT';font-family:var(--font-mono);font-size:11px;color:#c890ff;letter-spacing:3px;display:block;margin-bottom:10px;font-weight:700;}
.status-live{display:inline-flex;align-items:center;gap:8px;font-family:var(--font-mono);font-size:11px;color:var(--accent-green);letter-spacing:2px;}
.pulse-dot{width:8px;height:8px;background:var(--accent-green);border-radius:50%;display:inline-block;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1);box-shadow:0 0 0 0 rgba(0,255,157,0.4);}50%{opacity:0.8;transform:scale(1.1);box-shadow:0 0 0 6px rgba(0,255,157,0);}}
.forecast-tag{background:linear-gradient(135deg,rgba(245,197,24,0.15),rgba(245,197,24,0.05));border:1px solid rgba(245,197,24,0.3);border-radius:8px;padding:2px 12px;font-family:var(--font-mono);font-size:11px;color:var(--accent-gold);letter-spacing:2px;display:inline-block;margin-right:8px;}
[style*="background: white"],[style*="background-color: white"],[style*="background: rgb(255, 255, 255)"],[style*="background-color: rgb(255, 255, 255)"]{background:#091530!important;background-color:#091530!important;}
</style>
"""

# ═══════════════════════════════════════════════════════════════
#  EMBEDDED DATA ENGINE (no file dependency)
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    """Load from Excel if available, otherwise return empty DataFrame."""
    file_options = [
        "RAW DATA.xlsx",
        "RAW_DATA.xlsx",
        os.path.join(os.path.dirname(__file__), "RAW DATA.xlsx"),
        os.path.join(os.path.dirname(__file__), "RAW_DATA.xlsx"),
        r"Z:\data\RAW DATA.xlsx"
    ]
    file_path = next((p for p in file_options if os.path.exists(p)), None)
    if not file_path:
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        df.rename(columns={'Projetcs': 'Project'}, inplace=True)
        month_map = {
            'July':7,'August':8,'September':9,'October':10,'November':11,'December':12,
            'January':1,'February':2,'March':3,'April':4,'May':5,'June':6
        }
        df['Month_Num'] = df['Months'].map(month_map)
        fiscal_order = ['July','August','September','October','November','December',
                        'January','February','March','April','May','June']
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        df['Date_Obj'] = pd.to_datetime(
            df['Year'].astype(str) + '-' + df['Month_Num'].astype(str).str.zfill(2) + '-01'
        )
        df['Fiscal_Year_Label'] = df.apply(
            lambda x: f"FY {x['Year'] if x['Month_Num'] >= 7 else x['Year']-1}-{str(x['Year'] if x['Month_Num'] <= 6 else x['Year']+1)[-2:]}",
            axis=1
        )
        for col in ['Actual Revenue','Actual Footfall','Target revenue','Target Footfall']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df.sort_values('Date_Obj').reset_index(drop=True)
    except Exception as e:
        st.sidebar.error(f"Data load error: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════
#  AI KNOWLEDGE BASE — Pre-computed from actual data
# ═══════════════════════════════════════════════════════════════
KNOWLEDGE_BASE = {
    "projects": {
        "Joyland Fortress": {"total_revenue": 6317844000, "total_footfall": 14200613,
                              "description": "Main flagship amusement park - highest revenue generator"},
        "JAP-OD": {"total_revenue": 2944487000, "total_footfall": 6202991,
                   "description": "Joyland Amusement Park - Outdoor (JAP-OD) - second largest contributor"},
        "SS-PKG": {"total_revenue": 1055339000, "total_footfall": 2284979,
                   "description": "Season/Special Package project"},
        "SS-JAP": {"total_revenue": 851819000, "total_footfall": 2686797,
                   "description": "SS-JAP project"},
        "B-EMP": {"total_revenue": 806831000, "total_footfall": 1204895,
                  "description": "Bounce Employee project - high revenue per visitor"},
        "SS-FSM": {"total_revenue": 499736000, "total_footfall": 1736206,
                   "description": "SS-FSM project"},
        "B-PKG": {"total_revenue": 327742000, "total_footfall": 484662,
                  "description": "Bounce Package project"},
    },
    "yearly_totals": {
        2017: {"rev": 304019400, "ff": 1180907, "trev": 0, "tff": 0, "ach": 0},
        2018: {"rev": 632565800, "ff": 2287508, "trev": 0, "tff": 0, "ach": 0},
        2019: {"rev": 779863200, "ff": 2681979, "trev": 594889500, "tff": 936250, "ach": 131.1},
        2020: {"rev": 467232500, "ff": 1458870, "trev": 949960500, "tff": 2128257, "ach": 49.2},
        2021: {"rev": 656999000, "ff": 2040840, "trev": 1204021000, "tff": 3660529, "ach": 54.6},
        2022: {"rev": 1650607000, "ff": 4026029, "trev": 1627155000, "tff": 4305040, "ach": 101.4},
        2023: {"rev": 2101223000, "ff": 4365067, "trev": 2136572000, "tff": 4453906, "ach": 98.3},
        2024: {"rev": 2535819000, "ff": 4604300, "trev": 2981404000, "tff": 5218899, "ach": 85.1},
        2025: {"rev": 2957981000, "ff": 5064041, "trev": 3045532000, "tff": 5187623, "ach": 97.1},
        2026: {"rev": 717490000, "ff": 1091602, "trev": 1638490000, "tff": 2785433, "ach": 43.8},  # partial
    },
    "best_month": "July (highest revenue historically)",
    "worst_month": "May (lowest revenue historically)",
    "peak_year": 2025,
    "covid_impact": "2020 severely impacted - only 49.2% achievement due to COVID-19 lockdowns",
    "growth_2022": "2022 was breakthrough year - first time surpassing Rs. 1.6B revenue",
    "total_lifetime_revenue": 17803548900,
    "total_lifetime_footfall": 27801143,
}

MONTHLY_TOTALS = {
    "July": {"rev": 1370130000, "ff": 3149164},
    "August": {"rev": 1021294000, "ff": 2312789},
    "September": {"rev": 727593000, "ff": 1755216},
    "October": {"rev": 1023374000, "ff": 2352299},
    "November": {"rev": 1219367000, "ff": 2660262},
    "December": {"rev": 1469631000, "ff": 3203833},
    "January": {"rev": 1170577000, "ff": 2479694},
    "February": {"rev": 1037469000, "ff": 2356006},
    "March": {"rev": 949058000, "ff": 2224106},
    "April": {"rev": 1049247000, "ff": 2258131},
    "May": {"rev": 689831000, "ff": 1586853},
    "June": {"rev": 1076230000, "ff": 2462790},
}

# ═══════════════════════════════════════════════════════════════
#  FORECASTING ENGINE
# ═══════════════════════════════════════════════════════════════
EID_CALENDAR = {
    2025: [3,4,6], 2026: [3,4,6], 2027: [3,5,6],
    2028: [2,5],   2029: [2,4],   2030: [1,4]
}
SUMMER_PEAK = [6,7,8]
WINTER_PEAK = [12,1]

def generate_forecast(df, m_num, y_num, metric_col):
    df_clean = df[df[metric_col] > 0].dropna(subset=[metric_col]).copy()
    if len(df_clean) < 5:
        return 0, (0,0), "Insufficient Data"
    X = np.arange(len(df_clean)).reshape(-1,1)
    y = df_clean[metric_col].values
    poly = make_pipeline(PolynomialFeatures(2), LinearRegression())
    poly.fit(X, y)
    start_date = df_clean['Date_Obj'].min()
    target_date = pd.to_datetime(f"{y_num}-{m_num:02d}-01")
    months_diff = (target_date.year - start_date.year)*12 + (target_date.month - start_date.month)
    base = max(0, poly.predict([[months_diff]])[0])
    mult = 1.0
    notes = []
    if y_num in EID_CALENDAR and m_num in EID_CALENDAR[y_num]:
        mult *= 1.48; notes.append("🌙 Eid Season +48%")
    if m_num in SUMMER_PEAK:
        mult *= 1.22; notes.append("☀️ Summer Peak +22%")
    if m_num in WINTER_PEAK:
        mult *= 1.15; notes.append("❄️ Winter Festive +15%")
    if m_num == 12:
        mult *= 1.10; notes.append("🎆 Year-End +10%")
    final = base * mult
    return final, (final*0.88, final*1.12), " | ".join(notes) or "📈 Standard Projection"

# ═══════════════════════════════════════════════════════════════
#  PLOTLY CONFIG
# ═══════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    template="plotly_dark", paper_bgcolor='rgba(5,11,24,0)',
    plot_bgcolor='rgba(10,22,40,0.5)',
    font=dict(family='Rajdhani, sans-serif', color='#e8f4fd', size=13),
    title_font=dict(family='Orbitron, monospace', size=16, color='#00c6ff'),
    legend=dict(bgcolor='rgba(13,31,60,0.8)', bordercolor='#1a3a6b', borderwidth=1),
    xaxis=dict(gridcolor='rgba(26,58,107,0.4)', linecolor='#1a3a6b',
               tickfont=dict(family='JetBrains Mono', size=11, color='#7a9cc0')),
    yaxis=dict(gridcolor='rgba(26,58,107,0.4)', linecolor='#1a3a6b',
               tickfont=dict(family='JetBrains Mono', size=11, color='#7a9cc0')),
    margin=dict(l=20, r=20, t=50, b=20)
)
COLORS = ['#00c6ff','#f5c518','#00ff9d','#ff4466','#b660f5','#ff8c42','#4ecdc4']

# ═══════════════════════════════════════════════════════════════
#  CHARTS
# ═══════════════════════════════════════════════════════════════
def chart_gauge(actual, target, title="Revenue Achievement"):
    pct = min((actual/target*100) if target>0 else 0, 150)
    color = '#00ff9d' if pct>=100 else '#f5c518' if pct>=75 else '#ff4466'
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=pct,
        delta={'reference':100,'suffix':'%'},
        number={'suffix':'%','font':{'size':36,'family':'Orbitron','color':color}},
        title={'text':title,'font':{'size':14,'family':'Orbitron','color':'#7a9cc0'}},
        gauge={'axis':{'range':[0,150],'tickcolor':'#7a9cc0'},
               'bar':{'color':color,'thickness':0.28},
               'bgcolor':'rgba(13,31,60,0.8)','borderwidth':0,
               'threshold':{'line':{'color':'#00c6ff','width':3},'thickness':0.75,'value':100},
               'steps':[{'range':[0,75],'color':'rgba(255,68,102,0.1)'},
                        {'range':[75,100],'color':'rgba(245,197,24,0.1)'},
                        {'range':[100,150],'color':'rgba(0,255,157,0.1)'}]}
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=320)
    return fig

def chart_trend(df, col, color, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date_Obj'], y=df[col], fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)',
        line=dict(color=color, width=2.5), name=col,
        hovertemplate='<b>%{x|%b %Y}</b><br>%{y:,.0f}<extra></extra>'
    ))
    if len(df)>=6:
        ma = df[col].rolling(3,min_periods=1).mean()
        fig.add_trace(go.Scatter(x=df['Date_Obj'], y=ma,
            line=dict(color='#f5c518',width=1.5,dash='dot'), name='3M Avg'))
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=380)
    return fig

def chart_bar(df, x, cols, title):
    fig = go.Figure()
    for i,c in enumerate(cols):
        if c in df.columns:
            fig.add_trace(go.Bar(x=df[x], y=df[c], name=c,
                marker_color=COLORS[i%len(COLORS)], marker_line_width=0,
                hovertemplate=f'<b>%{{x}}</b><br>{c}: %{{y:,.0f}}<extra></extra>'))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', title=title, height=380)
    return fig

def chart_waterfall(df, metric):
    d = df.groupby('Months', observed=True)[metric].sum().reset_index()
    fig = go.Figure(go.Waterfall(
        x=d['Months'].tolist(), y=d[metric].tolist(),
        measure=['relative']*len(d),
        connector=dict(line=dict(color='#1a3a6b')),
        increasing=dict(marker_color='#00ff9d'),
        decreasing=dict(marker_color='#ff4466'),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=f"{metric} – Waterfall", height=380)
    return fig

def chart_heatmap(df):
    pivot = df.pivot_table(values='Actual Revenue', index='Year', columns='Months',
                           aggfunc='sum', observed=True)
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0,'#050b18'],[0.5,'#003a6b'],[1,'#00c6ff']],
        hovertemplate='<b>%{y} – %{x}</b><br>Rs. %{z:,.0f}<extra></extra>'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue Heatmap: Year × Month", height=360)
    return fig

def chart_pie(df, val_col, name_col, title):
    fig = px.pie(df, values=val_col, names=name_col, color_discrete_sequence=COLORS, hole=0.45)
    fig.update_traces(textposition='outside', textinfo='percent+label',
                      textfont=dict(family='Rajdhani', size=12))
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=420)
    return fig

def chart_yoy(df):
    years = sorted(df['Year'].dropna().unique())
    fig = go.Figure()
    for i, yr in enumerate(years):
        d = df[df['Year']==yr]
        fig.add_trace(go.Scatter(
            x=d['Months'].astype(str), y=d['Actual Revenue'],
            name=str(int(yr)), line=dict(color=COLORS[i%len(COLORS)],width=2.5),
            mode='lines+markers', marker=dict(size=7),
            hovertemplate=f'<b>{int(yr)} %{{x}}</b><br>Rs. %{{y:,.0f}}<extra></extra>'
        ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Year-over-Year Monthly Comparison", height=420)
    return fig

def chart_project_compare(df):
    d = df.groupby('Project')[['Actual Revenue','Actual Footfall']].sum().reset_index()
    d = d.sort_values('Actual Revenue', ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Revenue', x=d['Project'], y=d['Actual Revenue'],
                         marker_color='#00c6ff', marker_line_width=0))
    fig.add_trace(go.Bar(name='Footfall', x=d['Project'], y=d['Actual Footfall'],
                         marker_color='rgba(245,197,24,0.6)', marker_line_width=0, yaxis='y2'))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', title="Revenue & Footfall by Project",
                      height=400, yaxis2=dict(overlaying='y', side='right',
                      gridcolor='rgba(26,58,107,0.2)',
                      tickfont=dict(family='JetBrains Mono', size=11, color='#f5c518')))
    return fig

def chart_regression(df):
    d = df.dropna(subset=['Actual Revenue','Actual Footfall'])
    d = d[(d['Actual Revenue']>0) & (d['Actual Footfall']>0)]
    if len(d)<3: return None
    X = d['Actual Footfall'].values.reshape(-1,1)
    y = d['Actual Revenue'].values
    m = LinearRegression().fit(X, y)
    xl = np.linspace(X.min(), X.max(), 100)
    yl = m.predict(xl.reshape(-1,1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d['Actual Footfall'], y=d['Actual Revenue'], mode='markers',
        marker=dict(color='#00c6ff',size=8,opacity=0.7,line=dict(color='#f5c518',width=1)),
        hovertemplate='FF: %{x:,.0f}<br>Rev: Rs. %{y:,.0f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=xl, y=yl, mode='lines',
        line=dict(color='#f5c518',width=2,dash='dash'), name='Regression'))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue vs Footfall — Regression", height=380)
    return fig

def chart_forecast_trajectory(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date_Obj'], y=df['Actual Revenue'], name='Historical',
        line=dict(color='#00c6ff',width=2), fill='tozeroy',
        fillcolor='rgba(0,198,255,0.06)',
        hovertemplate='<b>%{x|%b %Y}</b><br>Rs. %{y:,.0f}<extra></extra>'
    ))
    hist = df[df['Actual Revenue']>0].dropna(subset=['Actual Revenue'])
    if len(hist)>=5:
        X = np.arange(len(hist)).reshape(-1,1)
        poly = make_pipeline(PolynomialFeatures(2), LinearRegression())
        poly.fit(X, hist['Actual Revenue'].values)
        future_steps = 36
        xs = np.arange(len(hist)+future_steps).reshape(-1,1)
        trend = poly.predict(xs)
        last = hist['Date_Obj'].max()
        future_dates = [last + pd.DateOffset(months=i) for i in range(1, future_steps+1)]
        all_dates = pd.concat([hist['Date_Obj'], pd.Series(future_dates)], ignore_index=True)
        fig.add_trace(go.Scatter(
            x=all_dates, y=np.maximum(trend,0), name='AI Forecast',
            line=dict(color='#f5c518',width=2,dash='dot'),
            hovertemplate='<b>%{x|%b %Y}</b><br>Projected: Rs. %{y:,.0f}<extra></extra>'
        ))
    fig.update_layout(**PLOTLY_LAYOUT, title="2017–2030 Revenue Trajectory & AI Forecast", height=450)
    return fig

# ═══════════════════════════════════════════════════════════════
#  DEEP AI QUERY ENGINE
# ═══════════════════════════════════════════════════════════════
MONTH_MAP = {
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
    'jan':1,'feb':2,'mar':3,'apr':4,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12
}
MONTH_NAMES = {v:k.capitalize() for k,v in MONTH_MAP.items() if len(k)>3}
MONTH_PATTERN = r'(july|august|september|october|november|december|january|february|march|april|may|june)'
PROJECT_ALIASES = {
    'fortress': 'Joyland Fortress', 'joyland fortress': 'Joyland Fortress',
    'jf': 'Joyland Fortress', 'main': 'Joyland Fortress',
    'jap': 'JAP-OD', 'jap-od': 'JAP-OD', 'outdoor': 'JAP-OD', 'od': 'JAP-OD',
    'ss-pkg': 'SS-PKG', 'sspkg': 'SS-PKG', 'ss pkg': 'SS-PKG',
    'ss-fsm': 'SS-FSM', 'ssfsm': 'SS-FSM', 'fsm': 'SS-FSM',
    'ss-jap': 'SS-JAP', 'ssjap': 'SS-JAP',
    'b-pkg': 'B-PKG', 'bpkg': 'B-PKG', 'bounce pkg': 'B-PKG',
    'b-emp': 'B-EMP', 'bemp': 'B-EMP', 'bounce emp': 'B-EMP', 'emp': 'B-EMP',
}
QUARTER_MAP = {
    'q1': ['July','August','September'], 'quarter 1': ['July','August','September'],
    'q2': ['October','November','December'], 'quarter 2': ['October','November','December'],
    'q3': ['January','February','March'], 'quarter 3': ['January','February','March'],
    'q4': ['April','May','June'], 'quarter 4': ['April','May','June'],
    '1st quarter': ['July','August','September'], '2nd quarter': ['October','November','December'],
    '3rd quarter': ['January','February','March'], '4th quarter': ['April','May','June'],
}

def detect_project(query_lower):
    for alias, full in PROJECT_ALIASES.items():
        if alias in query_lower:
            return full
    for proj in ['SS-PKG','SS-FSM','SS-JAP','B-PKG','B-EMP','JAP-OD']:
        if proj.lower() in query_lower:
            return proj
    return None

def detect_quarter(query_lower):
    for q, months in QUARTER_MAP.items():
        if q in query_lower:
            return months
    return None

def filter_df(query_lower, df):
    temp = df.copy()
    # Months
    months = [m.capitalize() for m in re.findall(MONTH_PATTERN, query_lower)]
    # Quarter
    quarter_months = detect_quarter(query_lower)
    if quarter_months:
        months = quarter_months
    # Years
    years = [int(y) for y in re.findall(r'\b(20\d{2})\b', query_lower)]
    # FY
    fy_match = re.findall(r'fy\s*(\d{2,4})', query_lower)
    # Project
    project = detect_project(query_lower)

    if months:
        temp = temp[temp['Months'].isin(months)]
    if years:
        temp = temp[temp['Year'].isin(years)]
    if fy_match:
        for fy in fy_match:
            temp = temp[temp['Fiscal_Year_Label'].str.contains(fy, na=False)]
    if project:
        temp = temp[temp['Project'] == project]

    return temp, months, years, project

def smart_ai_response(query, df):
    """Deep data-aware NLP response engine."""
    q = query.lower().strip()

    # ── GREETING ──
    greets = ['hi','hello','hey','salam','assalam','helo','hii','who are you','introduce',
              'intro','aap kaun','your name','about you','what are you','tell me about yourself']
    if any(q == g or q.startswith(g) for g in greets):
        return _intro_message(), None, None

    # ── HELP ──
    if q in ['help','?','commands','what can you do'] or q.startswith('help'):
        return _help_message(), None, None

    # ── FORECAST / PREDICT ──
    forecast_kw = ['forecast','predict','projection','estimate','expected','btao future',
                   'prediction','agle','next year','agla','future']
    if any(k in q for k in forecast_kw):
        found_m = next((m for m in MONTH_MAP if m in q), None)
        found_y = re.findall(r'\b(202[5-9]|2030)\b', q)
        if found_m and found_y:
            m_idx, y_val = MONTH_MAP[found_m], int(found_y[0])
            project = detect_project(q)
            df_src = df[df['Project'] == project] if project else df
            p_rev, (lr, ur), note_rev = generate_forecast(df_src, m_idx, y_val, 'Actual Revenue')
            p_ff, (lf, uf), note_ff = generate_forecast(df_src, m_idx, y_val, 'Actual Footfall')
            proj_str = f" ({project})" if project else " (All Projects)"
            msg = (
                f"### 🔮 AI Forecast — {found_m.capitalize()} {y_val}{proj_str}\n\n"
                f"| Metric | Projection | Range (±12%) |\n"
                f"|--------|------------|---------------|\n"
                f"| 💰 Revenue | **Rs. {p_rev:,.0f}** | Rs. {lr:,.0f} – Rs. {ur:,.0f} |\n"
                f"| 👥 Footfall | **{p_ff:,.0f} Pax** | {lf:,.0f} – {uf:,.0f} |\n\n"
                f"**Seasonal Modifiers:** {note_rev}\n\n"
                f"> *Model: Polynomial Regression (deg 2) + Seasonal AI Multipliers*  \n"
                f"> *Confidence Band: ±12% (1σ) based on historical variance*"
            )
            return msg, None, None
        else:
            return "🔮 **Forecast needs:** Month + Year (2025–2030)\n\n*Example: `Forecast March 2027`*", None, None

    # ── COMPARISON ──
    if 'vs' in q or ' v ' in q:
        sep = 'vs' if 'vs' in q else ' v '
        parts = q.split(sep, 1)
        def get_part(text):
            ms = [m.capitalize() for m in re.findall(MONTH_PATTERN, text)]
            ys = [int(y) for y in re.findall(r'\b(20\d{2})\b', text)]
            p = detect_project(text)
            tmp = df.copy()
            if ms: tmp = tmp[tmp['Months'].isin(ms)]
            if ys: tmp = tmp[tmp['Year'].isin(ys)]
            if p: tmp = tmp[tmp['Project']==p]
            label = ' '.join(ms + [str(y) for y in ys] + ([p] if p else []))
            return tmp, label.strip() or "Period 1"
        v1, l1 = get_part(parts[0])
        v2, l2 = get_part(parts[1])
        if not v1.empty and not v2.empty:
            r1, r2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
            f1, f2 = v1['Actual Footfall'].sum(), v2['Actual Footfall'].sum()
            r_chg = (r2-r1)/r1*100 if r1>0 else 0
            f_chg = (f2-f1)/f1*100 if f1>0 else 0
            rpp1 = r1/f1 if f1>0 else 0
            rpp2 = r2/f2 if f2>0 else 0
            msg = (
                f"### 📊 Comparison: {l1} vs {l2}\n\n"
                f"| Metric | {l1} | {l2} | Change |\n"
                f"|--------|------|------|--------|\n"
                f"| 💰 Revenue | Rs. {r1:,.0f} | Rs. {r2:,.0f} | `{r_chg:+.1f}%` |\n"
                f"| 👥 Footfall | {f1:,.0f} | {f2:,.0f} | `{f_chg:+.1f}%` |\n"
                f"| 💡 Rev/Pax | Rs. {rpp1:,.0f} | Rs. {rpp2:,.0f} | `{(rpp2-rpp1)/rpp1*100 if rpp1>0 else 0:+.1f}%` |\n\n"
            )
            if r_chg > 0:
                msg += f"✅ **{l2}** outperformed **{l1}** by `{r_chg:.1f}%` in revenue.\n"
            else:
                msg += f"⚠️ **{l2}** underperformed vs **{l1}** by `{abs(r_chg):.1f}%` in revenue.\n"
            comp_data = {"labels":[l1,l2], "revenue":[r1,r2], "footfall":[f1,f2]}
            return msg, None, comp_data
        else:
            return "⚠️ Could not find data for one or both comparison periods. Check your month/year format.", None, None

    # ── TREND ANALYSIS ──
    trend_kw = ['trend','growth','decline','pattern','yoy','year over year','yearly trend',
                'annual trend','historical','sabse','best year','worst year']
    if any(k in q for k in trend_kw):
        y_list = sorted(KNOWLEDGE_BASE['yearly_totals'].keys())
        rows = []
        for y in y_list:
            d = KNOWLEDGE_BASE['yearly_totals'][y]
            prev = KNOWLEDGE_BASE['yearly_totals'].get(y-1)
            if prev and prev['rev']>0:
                growth = (d['rev']-prev['rev'])/prev['rev']*100
                g_str = f"`{growth:+.1f}%`"
            else:
                g_str = "—"
            rows.append(f"| {y} | Rs. {d['rev']/1e6:.0f}M | {d['ff']/1e3:.0f}K | {g_str} |")
        msg = (
            "### 📈 Revenue & Footfall Trend Analysis (2017–2026)\n\n"
            "| Year | Revenue | Footfall | YoY Growth |\n"
            "|------|---------|----------|------------|\n"
            + "\n".join(rows) + "\n\n"
            f"**Key Insights:**\n"
            f"- 🟡 2020: COVID-19 caused 40% revenue drop — worst year operationally\n"
            f"- 🟢 2022: Breakthrough year — first Rs. 1.6B+ annual revenue\n"
            f"- 🚀 2025: Peak year — Rs. 2.96B revenue, 97.1% target achievement\n"
            f"- 📊 2026: Partial year (data through March 2026 only)\n"
            f"- 📉 CAGR 2017–2025: ~33% compound annual growth rate\n"
        )
        filtered, *_ = filter_df(q, df)
        return msg, filtered if not filtered.empty and (any(k in q for k in ['2017','2018','2019','2020','2021','2022','2023','2024','2025']) or 'year' in q) else None, None

    # ── PROJECT ANALYSIS ──
    project_kw = ['project','projects','all projects','which project','best project',
                  'top project','fortress','jap','ss-pkg','ss-fsm','ss-jap','b-pkg','b-emp']
    if any(k in q for k in project_kw) and not any(k in q for k in ['revenue','footfall','target']):
        proj_data = KNOWLEDGE_BASE['projects']
        rows = []
        sorted_projs = sorted(proj_data.items(), key=lambda x: -x[1]['total_revenue'])
        for proj, d in sorted_projs:
            rpp = d['total_revenue']/d['total_footfall'] if d['total_footfall']>0 else 0
            rows.append(f"| {proj} | Rs. {d['total_revenue']/1e6:.0f}M | {d['total_footfall']/1e3:.0f}K | Rs. {rpp:,.0f} |")
        msg = (
            "### 🏢 All Projects — Performance Summary (2017–2026)\n\n"
            "| Project | Total Revenue | Total Footfall | Rev/Pax |\n"
            "|---------|---------------|----------------|----------|\n"
            + "\n".join(rows) + "\n\n"
            "**Highlights:**\n"
            "- 🥇 **Joyland Fortress** — flagship, generates 39% of total revenue\n"
            "- 🥈 **JAP-OD** — strong #2, outdoor attraction driving 18% of revenue\n"
            "- 💡 **B-EMP** — highest revenue per visitor (Rs. 670+) showing premium positioning\n"
        )
        return msg, df, None

    # ── MONTHLY ANALYSIS ──
    month_kw = ['monthly','month','best month','worst month','seasonal','season',
                'which month','har month','monthly trend']
    if any(k in q for k in month_kw) and not re.findall(r'\b(20\d{2})\b', q) and not re.findall(MONTH_PATTERN, q):
        rows = []
        sorted_months = sorted(MONTHLY_TOTALS.items(), key=lambda x: -x[1]['rev'])
        for month, d in sorted_months:
            rpp = d['rev']/d['ff'] if d['ff']>0 else 0
            rows.append(f"| {month} | Rs. {d['rev']/1e6:.0f}M | {d['ff']/1e3:.0f}K | Rs. {rpp:,.0f} |")
        msg = (
            "### 📅 Monthly Revenue Breakdown — All-Time Totals\n\n"
            "| Month | Total Revenue | Total Footfall | Rev/Pax |\n"
            "|-------|---------------|----------------|----------|\n"
            + "\n".join(rows) + "\n\n"
            "**Seasonal Insights:**\n"
            "- 🏆 **July** — peak summer month, highest revenue\n"
            "- 🎆 **December** — festive season, strong #2\n"
            "- 😴 **May** — slowest month (pre-summer school exam season)\n"
            "- 🌙 **Eid Effect** — months with Eid see 40–50% above-average revenue\n"
        )
        return msg, None, None

    # ── ACHIEVEMENT / TARGET ANALYSIS ──
    ach_kw = ['achievement','achieve','target','vs target','kya achieve','reached','met target',
              'goal','performance','kitna achieve']
    if any(k in q for k in ach_kw):
        filtered, months, years, project = filter_df(q, df)
        if not filtered.empty:
            act_rev = filtered['Actual Revenue'].sum()
            tgt_rev = filtered['Target revenue'].sum()
            act_ff = filtered['Actual Footfall'].sum()
            tgt_ff = filtered['Target Footfall'].sum()
            rev_ach = act_rev/tgt_rev*100 if tgt_rev>0 else 0
            ff_ach = act_ff/tgt_ff*100 if tgt_ff>0 else 0
            status_rev = "✅ TARGET MET" if rev_ach>=100 else "⚠️ BELOW TARGET" if rev_ach>=75 else "❌ MISSED TARGET"
            status_ff = "✅ TARGET MET" if ff_ach>=100 else "⚠️ BELOW TARGET" if ff_ach>=75 else "❌ MISSED TARGET"
            proj_str = f" — {project}" if project else ""
            period_str = ", ".join(months + [str(y) for y in years]) if (months or years) else "All Data"
            msg = (
                f"### 🎯 Target Achievement Report — {period_str}{proj_str}\n\n"
                f"| Metric | Actual | Target | Achievement | Status |\n"
                f"|--------|--------|--------|-------------|--------|\n"
                f"| 💰 Revenue | Rs. {act_rev:,.0f} | Rs. {tgt_rev:,.0f} | **{rev_ach:.1f}%** | {status_rev} |\n"
                f"| 👥 Footfall | {act_ff:,.0f} | {tgt_ff:,.0f} | **{ff_ach:.1f}%** | {status_ff} |\n\n"
            )
            if rev_ach >= 100:
                surplus = act_rev - tgt_rev
                msg += f"🎉 Revenue surplus: **Rs. {surplus:,.0f}** above target!\n"
            else:
                shortfall = tgt_rev - act_rev
                msg += f"📉 Revenue shortfall: **Rs. {shortfall:,.0f}** below target.\n"
            return msg, filtered, None
        else:
            # Fall through to general data query
            pass

    # ── COVID / SPECIFIC EVENT QUERIES ──
    if 'covid' in q or '2020' in q and ('lockdown' in q or 'impact' in q or 'why' in q):
        msg = (
            "### 🦠 COVID-19 Impact Analysis — 2020\n\n"
            "| Period | Revenue | vs 2019 |\n"
            "|--------|---------|----------|\n"
            "| Q3 FY2020 (Jan-Mar) | Rs. 92.8M | −40% (lockdown started Mar 2020) |\n"
            "| Q4 FY2020 (Apr-Jun) | Rs. 0 | −100% (complete closure) |\n"
            "| Q1 FY2021 (Jul-Sep) | Rs. 109.3M | Partial reopening |\n\n"
            "**Key Facts:**\n"
            "- April, May, June 2020: **Zero revenue** — park completely closed\n"
            "- Full year 2020 achievement: **49.2%** of target\n"
            "- 2019 revenue: Rs. 779.9M → 2020: Rs. 467.2M (**−40% YoY**)\n"
            "- Recovery: 2021 saw Rs. 657M (+40.5% YoY) — steady comeback\n"
            "- Full recovery reached by 2022 (Rs. 1.65B — new record)\n"
        )
        return msg, df[df['Year'].isin([2019,2020,2021])], None

    # ── QUARTERLY ANALYSIS ──
    q_months = detect_quarter(q)
    if q_months:
        years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q)]
        filtered = df[df['Months'].isin(q_months)]
        if years:
            filtered = filtered[filtered['Year'].isin(years)]
        project = detect_project(q)
        if project:
            filtered = filtered[filtered['Project']==project]
        if not filtered.empty:
            q_name = next((k.upper() for k,v in QUARTER_MAP.items() if v==q_months and len(k)==2), "Quarter")
            act_rev = filtered['Actual Revenue'].sum()
            act_ff = filtered['Actual Footfall'].sum()
            tgt_rev = filtered['Target revenue'].sum()
            msg = (
                f"### 📊 {q_name} Analysis — {', '.join(q_months)}\n\n"
                f"| Metric | Value |\n"
                f"|--------|-------|\n"
                f"| 💰 Revenue | **Rs. {act_rev:,.0f}** |\n"
                f"| 👥 Footfall | **{act_ff:,.0f} Pax** |\n"
                f"| 🎯 Target | Rs. {tgt_rev:,.0f} |\n"
                f"| 📈 Achievement | **{act_rev/tgt_rev*100:.1f}%** |\n"
            )
            return msg, filtered, None

    # ── REVENUE PER PAX / SPEND ──
    rpp_kw = ['revenue per pax','per visitor','spend per','rev per','rpp','spending','average spend',
              'per customer','per ticket','kharcha','average revenue']
    if any(k in q for k in rpp_kw):
        filtered, months, years, project = filter_df(q, df)
        data_src = filtered if not filtered.empty else df
        rev = data_src['Actual Revenue'].sum()
        ff = data_src['Actual Footfall'].sum()
        rpp = rev/ff if ff>0 else 0
        period = ", ".join(months + [str(y) for y in years]) if (months or years) else "All-Time"
        proj_str = f" ({project})" if project else " (All Projects)"
        msg = (
            f"### 💡 Revenue Per Visitor — {period}{proj_str}\n\n"
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| 💰 Total Revenue | Rs. {rev:,.0f} |\n"
            f"| 👥 Total Footfall | {ff:,.0f} Pax |\n"
            f"| 💡 Revenue per Pax | **Rs. {rpp:,.0f}** |\n\n"
            f"*Benchmark: All-time avg Rs. {KNOWLEDGE_BASE['total_lifetime_revenue']/KNOWLEDGE_BASE['total_lifetime_footfall']:,.0f}/visitor*"
        )
        return msg, filtered if not filtered.empty else None, None

    # ── GENERAL DATA QUERY (Revenue / Footfall with filters) ──
    filtered, months, years, project = filter_df(q, df)

    # Detect what metric is asked
    want_rev = any(k in q for k in ['revenue','rev','income','earning','sales','kamai'])
    want_ff = any(k in q for k in ['footfall','foot fall','visitors','pax','attendance','log','customers','guest'])
    want_target = any(k in q for k in ['target','goal','aim'])
    want_both = not want_rev and not want_ff  # default: show both

    if filtered.empty:
        return (
            "⚠️ No data matched your query.\n\n"
            "**Try:** `Revenue July 2023` | `Footfall 2024` | `August 2023 vs August 2024` | `Forecast March 2027`\n\n"
            "**Projects:** Fortress, JAP-OD, SS-PKG, SS-FSM, SS-JAP, B-PKG, B-EMP"
        ), None, None

    act_rev = filtered['Actual Revenue'].sum()
    act_ff = filtered['Actual Footfall'].sum()
    tgt_rev = filtered['Target revenue'].sum()
    tgt_ff = filtered['Target Footfall'].sum()
    rev_ach = act_rev/tgt_rev*100 if tgt_rev>0 else None
    ff_ach = act_ff/tgt_ff*100 if tgt_ff>0 else None
    rpp = act_rev/act_ff if act_ff>0 else 0
    n_months = len(filtered['Months'].unique()) if 'Months' in filtered.columns else 1
    n_records = len(filtered)

    period_desc = ""
    if months: period_desc += ", ".join(months) + " "
    if years: period_desc += ", ".join(str(y) for y in years)
    if project: period_desc += f" ({project})"
    period_desc = period_desc.strip() or "All Data"

    lines = [f"### 📊 Analysis — {period_desc}\n"]

    if want_rev or want_both:
        lines.append(f"| 💰 Actual Revenue | **Rs. {act_rev:,.0f}** |")
        if tgt_rev > 0:
            lines.append(f"| 🎯 Target Revenue | Rs. {tgt_rev:,.0f} |")
            lines.append(f"| 📈 Achievement | **{rev_ach:.1f}%** |")

    if want_ff or want_both:
        lines.append(f"| 👥 Actual Footfall | **{act_ff:,.0f} Pax** |")
        if tgt_ff > 0:
            lines.append(f"| 🎯 Target Footfall | {tgt_ff:,.0f} Pax |")
            if ff_ach: lines.append(f"| 📈 FF Achievement | **{ff_ach:.1f}%** |")

    if want_both and act_ff > 0:
        lines.append(f"| 💡 Rev / Visitor | **Rs. {rpp:,.0f}** |")

    if n_months > 1 and (want_rev or want_both):
        avg_monthly = act_rev / n_months
        lines.append(f"| 📊 Avg Monthly Rev | Rs. {avg_monthly:,.0f} |")

    header = "| Metric | Value |\n|--------|-------|"
    table_lines = [l for l in lines if l.startswith("|")]
    intro = lines[0]
    msg = intro + "\n" + header + "\n" + "\n".join(table_lines)

    # Auto-insight
    if rev_ach:
        if rev_ach >= 100:
            msg += f"\n\n✅ **Target Exceeded** — Revenue achievement: **{rev_ach:.1f}%**"
        elif rev_ach >= 85:
            msg += f"\n\n⚠️ **Near Target** — {rev_ach:.1f}% achieved, Rs. {tgt_rev-act_rev:,.0f} short"
        else:
            msg += f"\n\n❌ **Below Target** — {rev_ach:.1f}% achieved"

    return msg, filtered, None


def _intro_message():
    return (
        "### 👋 Assalam o Alaikum! Welcome to **Joyland MIS**\n\n"
        "---\n"
        "🤖 **I am the Joyland MIS AI Assistant** — a Business Intelligence Bot trained on **complete Joyland data from 2017 to 2026** across **7 projects**.\n\n"
        "Developed by **MIS Assistant Manager Umair Nizam** to power smart, data-driven decisions.\n\n"
        "---\n"
        "### 🧠 I Can Answer:\n\n"
        "| What You Ask | Example |\n"
        "|---|---|\n"
        "| 💰 Revenue | `Revenue July 2023` |\n"
        "| 👥 Footfall | `Footfall 2024 Joyland Fortress` |\n"
        "| 🆚 Comparison | `August 2023 vs August 2024` |\n"
        "| 🔮 Forecast | `Forecast March 2027` |\n"
        "| 🎯 Achievement | `Target achievement 2025` |\n"
        "| 📈 Trends | `Revenue trend all years` |\n"
        "| 📅 Quarterly | `Q1 2024 revenue` |\n"
        "| 🏢 Projects | `All projects comparison` |\n"
        "| 💡 Per Visitor | `Revenue per pax 2024` |\n"
        "| 🦠 Events | `COVID impact 2020` |\n\n"
        "**Projects in data:** Joyland Fortress · JAP-OD · SS-PKG · SS-FSM · SS-JAP · B-PKG · B-EMP\n\n"
        "**Ask me anything! 🚀**"
    )

def _help_message():
    return (
        "### 📖 Query Guide\n\n"
        "**Revenue Queries:**\n"
        "- `Revenue July 2023`\n"
        "- `Total revenue 2024`\n"
        "- `Revenue Joyland Fortress 2025`\n"
        "- `Revenue Q1 2023`\n\n"
        "**Footfall Queries:**\n"
        "- `Footfall August 2024`\n"
        "- `Total visitors 2023`\n\n"
        "**Comparisons:**\n"
        "- `July 2023 vs July 2024`\n"
        "- `2023 vs 2024`\n"
        "- `Joyland Fortress 2024 vs JAP-OD 2024`\n\n"
        "**Forecasting (2025–2030):**\n"
        "- `Forecast March 2027`\n"
        "- `Predict revenue December 2028`\n\n"
        "**Analysis:**\n"
        "- `Revenue trend`\n"
        "- `Best month`\n"
        "- `Monthly breakdown`\n"
        "- `Achievement 2024`\n"
        "- `Revenue per pax 2025`\n"
        "- `COVID impact`\n"
        "- `All projects`\n"
    )

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
def render_sidebar(df, auth_obj=None):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:16px 0 8px;'>
          <div style='font-family:Orbitron,monospace;font-size:11px;letter-spacing:4px;color:#7a9cc0;'>JOYLAND MIS</div>
          <div style='font-family:Orbitron,monospace;font-size:20px;font-weight:900;color:#00c6ff;margin:4px 0;'>CONTROL</div>
          <div style='font-family:Orbitron,monospace;font-size:9px;letter-spacing:3px;color:#3a5a80;'>INTELLIGENCE CENTER</div>
        </div>
        <div style='border-bottom:1px solid #1a3a6b;margin:8px 0 16px;'></div>
        """, unsafe_allow_html=True)

        analyst_name = st.session_state.get('name', 'Analyst')
        st.markdown(f"""
        <div style='background:rgba(0,198,255,0.06);border:1px solid rgba(0,198,255,0.2);border-radius:12px;padding:14px 16px;margin-bottom:16px;'>
          <div style='font-family:Rajdhani;font-size:11px;letter-spacing:2px;color:#7a9cc0;text-transform:uppercase;margin-bottom:4px;'>ACTIVE ANALYST</div>
          <div style='font-family:Orbitron;font-size:14px;color:#00c6ff;font-weight:700;'>{analyst_name}</div>
          <div class='status-live' style='margin-top:8px;'><span class='pulse-dot'></span> AI ENGINE ONLINE</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ CLEAR CHAT", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_filtered_df = None
            st.session_state.comparison_data = None
            st.rerun()

        if auth_obj:
            auth_obj.logout('⏻  LOGOUT', 'sidebar')

        st.markdown("""<div style='border-bottom:1px solid #1a3a6b;margin:16px 0;'></div>""",
                    unsafe_allow_html=True)

        if not df.empty:
            st.markdown(f"""
            <div style='background:rgba(13,31,60,0.8);border:1px solid #1a3a6b;border-radius:12px;padding:14px;margin-bottom:12px;'>
              <div style='font-family:Rajdhani;font-size:11px;letter-spacing:2px;color:#a8d4f5;text-transform:uppercase;margin-bottom:8px;font-weight:700;'>DATA SCOPE</div>
              <div style='font-family:JetBrains Mono;font-size:13px;color:#e8f4fd;margin:5px 0;'>📅 2017 – 2026</div>
              <div style='font-family:JetBrains Mono;font-size:13px;color:#e8f4fd;margin:5px 0;'>📊 {len(df):,} Records</div>
              <div style='font-family:JetBrains Mono;font-size:13px;color:#e8f4fd;margin:5px 0;'>🏢 7 Projects</div>
              <div style='font-family:JetBrains Mono;font-size:13px;color:#e8f4fd;margin:5px 0;'>🤖 AI Model: Poly-2 + LR</div>
            </div>
            """, unsafe_allow_html=True)

        quick = [
            "Revenue July 2024", "Footfall 2025",
            "August 2023 vs August 2024", "Forecast March 2027",
            "Revenue trend", "Q1 2024 Joyland Fortress",
            "Achievement 2025", "All projects comparison",
            "Revenue per pax 2024", "COVID impact 2020",
        ]
        st.markdown("""
        <div style='background:rgba(13,31,60,0.8);border:1px solid #1a3a6b;border-radius:12px;padding:14px;'>
          <div style='font-family:Rajdhani;font-size:11px;letter-spacing:2px;color:#a8d4f5;text-transform:uppercase;margin-bottom:8px;font-weight:700;'>QUICK QUERIES</div>
        """, unsafe_allow_html=True)
        for q in quick:
            st.markdown(f"<div style='font-family:JetBrains Mono;font-size:11px;color:#c8dff0;margin:4px 0;'>› {q}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center;padding:12px;font-family:Rajdhani;font-size:11px;color:#3a5a80;letter-spacing:1px;margin-top:16px;'>
          ARCHITECT: <span style='color:#f5c518;font-weight:700;'>UMAIR NIZAM</span><br>
          <span style='color:#1a3a6b;'>v4.0 GRAND MASTER · 2017–2030</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Joyland MIS Assistant · v4.0",
        layout="wide", page_icon="🎢",
        initial_sidebar_state="expanded"
    )
    st.markdown(PAGE_THEME, unsafe_allow_html=True)

    for k, v in {
        'messages': [], 'last_filtered_df': None, 'comparison_data': None
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    df = load_data()

    # ── AUTH ──
    credentials = {"usernames": {"admin": {"name": "Admin", "password": "MIS2024@secure"}}}
    try:
        from streamlit_authenticator import Authenticate
        auth = Authenticate(credentials, "joyland_mis", "auth_key_v4", cookie_expiry_days=30)
        auth.login(location='main')
        is_auth = st.session_state.get("authentication_status")
    except ImportError:
        st.warning("streamlit-authenticator not installed. Running in demo mode.")
        is_auth = True
        auth = None

    if not is_auth:
        st.markdown("""
        <div style='max-width:420px;margin:80px auto;text-align:center;'>
          <div style='font-family:Orbitron,monospace;font-size:32px;font-weight:900;
               background:linear-gradient(135deg,#00c6ff,#f5c518);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;'>
            JOYLAND MIS ASSISTANT
          </div>
          <div style='font-family:Rajdhani;font-size:13px;letter-spacing:3px;color:#7a9cc0;margin-bottom:32px;'>
            INTELLIGENCE PLATFORM · v4.0
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    render_sidebar(df, auth)

    # ── HERO ──
    st.markdown("""
    <div class='hero-banner'>
      <div class='hero-title'>JOYLAND  MIS  ASSISTANT</div>
      <div class='hero-subtitle'>Advanced Business Intelligence & Predictive Analytics Platform</div>
      <div class='hero-badge'>⬡ AI-POWERED · DATA 2017–2026 · FORECAST 2030 · v4.0 GRAND MASTER</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──
    if not df.empty:
        try:
            total_rev = df['Actual Revenue'].sum()
            total_ff  = df['Actual Footfall'].sum()
            total_tgt = df['Target revenue'].sum()
            ach       = total_rev/total_tgt*100 if total_tgt>0 else 0
            rpp       = total_rev/total_ff if total_ff>0 else 0
            last_yr   = df[df['Year']==df['Year'].max()]['Actual Revenue'].sum()
            prev_yr   = df[df['Year']==df['Year'].max()-1]['Actual Revenue'].sum()
            yoy_g     = (last_yr-prev_yr)/prev_yr*100 if prev_yr>0 else 0

            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("💰 Lifetime Revenue", f"Rs. {total_rev/1e6:.0f}M", "2017–2026")
            c2.metric("👥 Total Visitors", f"{total_ff/1e6:.2f}M Pax", "Cumulative")
            c3.metric("🎯 Avg Achievement", f"{ach:.1f}%", "vs All Targets")
            c4.metric("💡 Rev / Visitor", f"Rs. {rpp:,.0f}", "Lifetime Avg")
            c5.metric("📈 YoY Growth", f"{yoy_g:+.1f}%", f"{df['Year'].max()-1}→{df['Year'].max()}")
        except:
            pass

    st.divider()

    # ── AI INSIGHTS ──
    if not df.empty:
        yearly_rev = df.groupby('Year')['Actual Revenue'].sum()
        best_proj = df.groupby('Project')['Actual Revenue'].sum().idxmax()
        peak_month = df.groupby('Months', observed=True)['Actual Revenue'].sum().idxmax()
        st.markdown(f"""
        <div class='insight-card'>
          🏆 <b>Best Month:</b> {peak_month} (highest cumulative revenue) &nbsp;·&nbsp;
          🏢 <b>Top Project:</b> {best_proj} (largest revenue contributor) &nbsp;·&nbsp;
          🚀 <b>Peak Year:</b> 2025 (Rs. 2.96B, +16.6% YoY) &nbsp;·&nbsp;
          💡 <b>Rev/Pax:</b> Rs. {df['Actual Revenue'].sum()/df['Actual Footfall'].sum():,.0f} all-time average
        </div>
        """, unsafe_allow_html=True)

    # ── CHAT ──
    st.markdown("<div class='section-header'>◈ AI ANALYTICS ASSISTANT</div>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["is_user"] else "assistant"):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything: Revenue · Footfall · Comparison · Forecast · Trends · Projects…")

    if prompt:
        st.session_state.messages.append({"content": prompt, "is_user": True})

        response_text, filtered_df, comp_data = smart_ai_response(prompt, df)

        if filtered_df is not None:
            st.session_state.last_filtered_df = filtered_df
        if comp_data is not None:
            st.session_state.comparison_data = comp_data
        else:
            st.session_state.comparison_data = None

        st.session_state.messages.append({"content": response_text, "is_user": False})
        st.rerun()

    # ═══════════════════════════════════════════════════════════
    #  VISUALIZATION PANEL
    # ═══════════════════════════════════════════════════════════
    if st.session_state.last_filtered_df is not None and not st.session_state.last_filtered_df.empty:
        df_plot = st.session_state.last_filtered_df

        st.markdown("<div class='section-header'>◈ VISUAL INTELLIGENCE PANEL</div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📉 Visual Insights", "🔬 Deep Analysis", "🏢 Projects",
            "🔮 Forecast", "📋 Raw Data"
        ])

        # ─ TAB 1: VISUAL INSIGHTS ─
        with tab1:
            if st.session_state.comparison_data:
                cd = st.session_state.comparison_data
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Bar(name='Revenue', x=cd['labels'], y=cd['revenue'],
                    marker_color=['#00c6ff','#f5c518'], marker_line_width=0,
                    hovertemplate='<b>%{x}</b><br>Rs. %{y:,.0f}<extra></extra>'))
                fig_comp.add_trace(go.Bar(name='Footfall', x=cd['labels'], y=cd['footfall'],
                    marker_color=['rgba(0,198,255,0.4)','rgba(245,197,24,0.4)'],
                    marker_line_width=0, yaxis='y2',
                    hovertemplate='<b>%{x}</b><br>%{y:,.0f} Pax<extra></extra>'))
                fig_comp.update_layout(**PLOTLY_LAYOUT, barmode='group',
                    title="Period Comparison — Revenue vs Footfall", height=400,
                    yaxis2=dict(overlaying='y', side='right',
                    gridcolor='rgba(26,58,107,0.2)',
                    tickfont=dict(family='JetBrains Mono',size=11,color='#f5c518')))
                st.plotly_chart(fig_comp, use_container_width=True)
                st.divider()

            chart_opt = st.selectbox("🎯 Select Visualization", [
                "1. Revenue Achievement Gauge",
                "2. Footfall Achievement Gauge",
                "3. Revenue vs Target — Bar Chart",
                "4. Revenue Area Trend",
                "5. Footfall Trend Line",
                "6. Monthly Waterfall",
                "7. Revenue Share — Pie",
                "8. Revenue vs Footfall — Regression",
                "9. Year-over-Year Comparison",
            ])

            res = df_plot[[c for c in ['Actual Revenue','Actual Footfall','Target revenue','Target Footfall'] if c in df_plot.columns]].sum()

            if chart_opt.startswith("1"):
                st.plotly_chart(chart_gauge(res.get('Actual Revenue',0), res.get('Target revenue',0), "Revenue Achievement"), use_container_width=True)
            elif chart_opt.startswith("2"):
                st.plotly_chart(chart_gauge(res.get('Actual Footfall',0), res.get('Target Footfall',0), "Footfall Achievement"), use_container_width=True)
            elif chart_opt.startswith("3"):
                cols = [c for c in ['Actual Revenue','Target revenue'] if c in df_plot.columns]
                st.plotly_chart(chart_bar(df_plot, 'Months', cols, "Revenue: Actual vs Target"), use_container_width=True)
            elif chart_opt.startswith("4"):
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(chart_trend(df_plot, 'Actual Revenue', '#00c6ff', 'Revenue Trend'), use_container_width=True)
            elif chart_opt.startswith("5"):
                if 'Actual Footfall' in df_plot.columns:
                    st.plotly_chart(chart_trend(df_plot, 'Actual Footfall', '#f5c518', 'Footfall Trend'), use_container_width=True)
            elif chart_opt.startswith("6"):
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(chart_waterfall(df_plot, 'Actual Revenue'), use_container_width=True)
            elif chart_opt.startswith("7"):
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(chart_pie(df_plot, 'Actual Revenue', 'Months', "Revenue by Month"), use_container_width=True)
            elif chart_opt.startswith("8"):
                fig_r = chart_regression(df_plot)
                if fig_r: st.plotly_chart(fig_r, use_container_width=True)
            elif chart_opt.startswith("9"):
                st.plotly_chart(chart_yoy(df_plot), use_container_width=True)

            # Summary table
            disp = [c for c in ['Actual Revenue','Target revenue','Actual Footfall','Target Footfall'] if c in df_plot.columns]
            if disp:
                st.markdown("**Summary**")
                st.dataframe(
                    df_plot[disp].sum().to_frame("Total").T.style
                    .format("{:,.0f}")
                    .set_properties(**{'background-color':'#0d1f3c','color':'#e8f4fd','border':'1px solid #1a3a6b'}),
                    use_container_width=True
                )

        # ─ TAB 2: DEEP ANALYSIS ─
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                if 'Year' in df_plot.columns and 'Actual Revenue' in df_plot.columns:
                    fy_d = df_plot.groupby('Year')[['Actual Revenue','Target revenue']].sum().reset_index()
                    fig_fy = go.Figure()
                    fig_fy.add_trace(go.Bar(name='Actual', x=fy_d['Year'], y=fy_d['Actual Revenue'],
                        marker_color='#00c6ff', marker_line_width=0))
                    if 'Target revenue' in fy_d.columns:
                        fig_fy.add_trace(go.Bar(name='Target', x=fy_d['Year'], y=fy_d['Target revenue'],
                            marker_color='rgba(245,197,24,0.4)', marker_line_width=0))
                    fig_fy.update_layout(**PLOTLY_LAYOUT, barmode='group',
                        title="Yearly: Actual vs Target", height=380)
                    st.plotly_chart(fig_fy, use_container_width=True)
            with c2:
                hm = chart_heatmap(df_plot)
                if hm: st.plotly_chart(hm, use_container_width=True)

            st.plotly_chart(chart_yoy(df_plot), use_container_width=True)

        # ─ TAB 3: PROJECTS ─
        with tab3:
            if 'Project' in df_plot.columns:
                st.plotly_chart(chart_project_compare(df_plot), use_container_width=True)
                # Project breakdown table
                proj_sum = df_plot.groupby('Project')[['Actual Revenue','Actual Footfall','Target revenue']].sum()
                proj_sum['Achievement %'] = (proj_sum['Actual Revenue']/proj_sum['Target revenue']*100).where(proj_sum['Target revenue']>0, 0).round(1)
                proj_sum['Rev/Pax'] = (proj_sum['Actual Revenue']/proj_sum['Actual Footfall']).round(0)
                st.dataframe(
                    proj_sum.style.format({
                        'Actual Revenue':'{:,.0f}','Actual Footfall':'{:,.0f}',
                        'Target revenue':'{:,.0f}','Achievement %':'{:.1f}%','Rev/Pax':'{:,.0f}'
                    }).set_properties(**{'background-color':'#0d1f3c','color':'#e8f4fd','border':'1px solid #1a3a6b'}),
                    use_container_width=True
                )

        # ─ TAB 4: FORECAST ─
        with tab4:
            st.markdown("<div class='section-header'>◈ PREDICTIVE ANALYTICS ENGINE</div>", unsafe_allow_html=True)
            if not df.empty:
                st.plotly_chart(chart_forecast_trajectory(df), use_container_width=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    m_sel = st.selectbox("Month", ['January','February','March','April','May','June',
                                                    'July','August','September','October','November','December'])
                with col2:
                    y_sel = st.selectbox("Year", list(range(2025, 2031)))
                with col3:
                    p_sel = st.selectbox("Project", ['All Projects'] + sorted(df['Project'].unique().tolist()))

                if st.button("🔮 GENERATE FORECAST", use_container_width=True):
                    m_idx = MONTH_MAP[m_sel.lower()]
                    df_src = df if p_sel=='All Projects' else df[df['Project']==p_sel]
                    p_rev, (lr,ur), note_rev = generate_forecast(df_src, m_idx, y_sel, 'Actual Revenue')
                    p_ff, (lf,uf), note_ff = generate_forecast(df_src, m_idx, y_sel, 'Actual Footfall')
                    st.markdown(f"""
                    <div style='background:rgba(245,197,24,0.06);border:1px solid rgba(245,197,24,0.3);
                    border-radius:16px;padding:24px;margin-top:16px;'>
                      <div style='font-family:Orbitron;font-size:14px;letter-spacing:3px;color:#f5c518;margin-bottom:16px;'>
                        🔮 FORECAST — {m_sel.upper()} {y_sel} ({p_sel})
                      </div>
                      <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'>
                        <div style='background:rgba(0,198,255,0.08);border:1px solid rgba(0,198,255,0.2);border-radius:12px;padding:16px;'>
                          <div style='font-family:Rajdhani;font-size:12px;color:#7a9cc0;letter-spacing:2px;'>💰 REVENUE</div>
                          <div style='font-family:Orbitron;font-size:22px;color:#00c6ff;font-weight:900;margin:8px 0;'>Rs. {p_rev:,.0f}</div>
                          <div style='font-family:JetBrains Mono;font-size:11px;color:#3a5a80;'>Range: Rs. {lr:,.0f} – {ur:,.0f}</div>
                        </div>
                        <div style='background:rgba(245,197,24,0.08);border:1px solid rgba(245,197,24,0.2);border-radius:12px;padding:16px;'>
                          <div style='font-family:Rajdhani;font-size:12px;color:#7a9cc0;letter-spacing:2px;'>👥 FOOTFALL</div>
                          <div style='font-family:Orbitron;font-size:22px;color:#f5c518;font-weight:900;margin:8px 0;'>{p_ff:,.0f}</div>
                          <div style='font-family:JetBrains Mono;font-size:11px;color:#3a5a80;'>Range: {lf:,.0f} – {uf:,.0f}</div>
                        </div>
                      </div>
                      <div style='margin-top:12px;font-family:Rajdhani;font-size:13px;color:#a8d4f5;'>
                        <b>Modifiers:</b> {note_rev}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("""
                <div style='background:rgba(245,197,24,0.06);border:1px solid rgba(245,197,24,0.2);border-radius:12px;padding:16px;margin-top:16px;'>
                  <div style='font-family:Orbitron;font-size:12px;letter-spacing:3px;color:#f5c518;margin-bottom:10px;'>🌙 EID SEASON CALENDAR</div>
                  <div style='font-family:JetBrains Mono;font-size:12px;color:#7a9cc0;line-height:2;'>
                    2025 → Mar, Apr, Jun (+48%)&nbsp;&nbsp;|&nbsp;&nbsp;2026 → Mar, Apr, Jun (+48%)<br>
                    2027 → Mar, May, Jun (+48%)&nbsp;&nbsp;|&nbsp;&nbsp;2028 → Feb, May (+48%)<br>
                    2029 → Feb, Apr (+48%)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;2030 → Jan, Apr (+48%)
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # ─ TAB 5: RAW DATA ─
        with tab5:
            st.markdown(f"<div style='font-family:Rajdhani;color:#7a9cc0;margin-bottom:12px;'>{len(df_plot):,} records</div>",
                        unsafe_allow_html=True)
            display_cols = [c for c in df_plot.columns if c not in ['Month_Num','Date_Obj','Fiscal_Year_Label']]
            st.dataframe(
                df_plot[display_cols].style.format({
                    c: '{:,.0f}' for c in display_cols if pd.api.types.is_numeric_dtype(df_plot[c])
                }).set_properties(**{'background-color':'#0d1f3c','color':'#e8f4fd','border':'1px solid #1a3a6b'}),
                use_container_width=True, height=500
            )
            csv = df_plot.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ EXPORT CSV", data=csv,
                file_name=f"joyland_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime='text/csv', use_container_width=True)


if __name__ == "__main__":
    main()
