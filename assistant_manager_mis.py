import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import json
import requests
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
#  JOYLAND MIS ASSISTANT  ·  v7.0 GENERATIVE AI
#  Architect: Umair Nizam  |  Scope: 2017 – 2030
#  AI Engine: Claude claude-sonnet-4-20250514 (Generative) + Pakistan Events
#  Interface: Matched to joyland_mis_theme_preview.html
# ═══════════════════════════════════════════════════════════════

# ─── ANTHROPIC API CONFIG ────────────────────────────────────
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL   = "claude-sonnet-4-20250514"
ANTHROPIC_VERSION = "2023-06-01"

# Put your key here OR set env var ANTHROPIC_API_KEY
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

PAGE_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --bg0: #02060f; --bg1: #060d1e; --bg2: #091428; --bg3: #0c1b35; --bg4: #101f3a;
  --glass: rgba(9,20,40,0.92); --border: rgba(0,180,255,0.12); --border2: rgba(0,180,255,0.25);
  --border3: rgba(0,180,255,0.40); --cyan: #00c6ff; --cyan-dim: rgba(0,198,255,0.15);
  --gold: #f5c518; --gold-dim: rgba(245,197,24,0.12); --green: #00ff9d;
  --green-dim: rgba(0,255,157,0.12); --red: #ff3355; --purple: #c084fc;
  --orange: #ff9432; --text1: #f0f8ff; --text2: #8ab4d4; --text3: #3d6080;
  --font-display: 'Orbitron', monospace; --font-body: 'Rajdhani', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

html, body, .stApp, .main, [class*="css"], section.main > div, .block-container {
  background: var(--bg0) !important; color: var(--text1) !important;
  font-family: var(--font-body) !important;
}
[style*="background: white"],[style*="background-color: white"],
[data-testid="stAppViewContainer"],[data-testid="stHeader"] {
  background: var(--bg0) !important; background-color: var(--bg0) !important;
}
.main::before {
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: linear-gradient(rgba(0,198,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,198,255,0.025) 1px, transparent 1px);
  background-size: 48px 48px;
}
p, span, div, label, li, td, th, a { color: var(--text1) !important; }
.stMarkdown p, .stMarkdown span, .stMarkdown li {
  color: #ddeeff !important; font-size: 15px !important;
  font-weight: 500 !important; line-height: 1.8 !important;
}
h1, h2, h3 { color: var(--text1) !important; }

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #020912 0%, #050d1c 100%) !important;
  border-right: 1px solid var(--border2) !important;
}
section[data-testid="stSidebar"] * { background-color: transparent !important; }
section[data-testid="stSidebar"]::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--gold), transparent);
  animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }

div[data-testid="stMetric"] {
  background: linear-gradient(135deg, var(--bg3) 0%, var(--bg2) 100%) !important;
  border: 1px solid var(--border2) !important; border-radius: 18px !important;
  padding: 22px 18px !important; position: relative; overflow: hidden;
  transition: transform .3s, box-shadow .3s, border-color .3s !important;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-5px) !important;
  box-shadow: 0 20px 60px rgba(0,198,255,0.18) !important;
  border-color: var(--border3) !important;
}
div[data-testid="stMetric"]::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--gold), transparent);
  border-radius: 18px 18px 0 0;
}
div[data-testid="stMetricLabel"] > div {
  color: var(--text2) !important; font-family: var(--font-body) !important;
  font-size: 11px !important; letter-spacing: 2px !important;
  text-transform: uppercase !important; font-weight: 700 !important;
}
div[data-testid="stMetricValue"] > div {
  color: #ffffff !important; font-family: var(--font-display) !important;
  font-size: 22px !important; font-weight: 900 !important;
  text-shadow: 0 0 24px rgba(0,198,255,0.45) !important;
}

.stButton > button {
  background: linear-gradient(135deg, rgba(0,198,255,0.12), rgba(0,198,255,0.04)) !important;
  border: 1px solid rgba(0,198,255,0.35) !important; color: var(--cyan) !important;
  font-family: var(--font-body) !important; font-weight: 700 !important;
  letter-spacing: 2px !important; border-radius: 10px !important;
  text-transform: uppercase !important; font-size: 11px !important;
  transition: all .3s ease !important;
}
.stButton > button:hover {
  background: rgba(0,198,255,0.22) !important;
  box-shadow: 0 0 24px rgba(0,198,255,0.25) !important;
  transform: translateY(-2px) !important; border-color: var(--cyan) !important;
}

div[data-baseweb="tab-list"] {
  background: var(--bg2) !important; border-radius: 12px !important;
  padding: 4px !important; border: 1px solid var(--border) !important; gap: 3px !important;
}
div[data-baseweb="tab"] {
  font-family: var(--font-body) !important; font-weight: 700 !important;
  font-size: 12px !important; letter-spacing: 1px !important;
  border-radius: 8px !important; color: var(--text2) !important;
  transition: all .2s !important; background: transparent !important;
  text-transform: uppercase !important;
}
div[aria-selected="true"] {
  background: rgba(0,198,255,0.15) !important; color: var(--cyan) !important;
  box-shadow: 0 0 16px rgba(0,198,255,0.12) !important;
}
div[role="tabpanel"], div[role="tabpanel"] > div, div[data-baseweb="tab-panel"] {
  background: var(--bg0) !important; padding-top: 16px !important;
}

div[data-baseweb="select"] > div, div[data-baseweb="select"] > div > div {
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  border-radius: 10px !important; color: var(--text1) !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div[class*="singleValue"],
div[data-baseweb="select"] div[class*="placeholder"], div[data-baseweb="select"] svg {
  color: var(--text1) !important; fill: var(--text2) !important;
  font-family: var(--font-body) !important; font-weight: 600 !important;
}
div[data-baseweb="popover"], ul[role="listbox"], div[role="listbox"], [data-baseweb="menu"] {
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  border-radius: 14px !important; box-shadow: 0 12px 48px rgba(0,0,0,0.8) !important;
}
li[role="option"], div[role="option"] {
  background: var(--bg2) !important; color: var(--text1) !important;
  font-family: var(--font-body) !important; font-size: 14px !important; font-weight: 600 !important;
}
li[role="option"]:hover, li[aria-selected="true"] {
  background: rgba(0,198,255,0.12) !important; color: var(--cyan) !important;
}

div[data-testid="stChatInput"] {
  background: var(--bg2) !important; border: 1.5px solid var(--border2) !important;
  border-radius: 14px !important;
}
div[data-testid="stChatInput"] textarea {
  background: var(--bg2) !important; border: none !important;
  color: var(--text1) !important; font-family: var(--font-body) !important;
  font-size: 14px !important; caret-color: var(--cyan) !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color: var(--text3) !important; }
div[data-testid="stChatInput"]:focus-within {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px rgba(0,198,255,0.12) !important;
}
div[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, var(--cyan), #0090cc) !important;
  border-radius: 10px !important; border: none !important;
}
div[data-testid="stBottom"], .stChatFloatingInputContainer {
  background: var(--bg0) !important; border-top: 1px solid var(--border) !important;
}
footer, footer * { background: var(--bg0) !important; color: var(--text3) !important; }

div[data-testid="stChatMessage"] { background: transparent !important; border: none !important; }
div[data-testid="stChatMessage"] > div {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: 14px !important;
}
div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] li, div[data-testid="stChatMessage"] td {
  color: var(--text1) !important; font-size: 14px !important;
  font-weight: 500 !important; line-height: 1.8 !important;
}
div[data-testid="stChatMessage"] strong { color: #ffffff !important; font-weight: 800 !important; }
div[data-testid="stChatMessage"] code {
  color: var(--green) !important; background: rgba(0,255,157,0.08) !important;
  padding: 2px 7px !important; border-radius: 5px !important;
  font-family: var(--font-mono) !important; border: 1px solid rgba(0,255,157,0.2) !important;
}

div[data-testid="stPlotlyChart"], .js-plotly-plot, .js-plotly-plot .plotly .main-svg,
.plot-container > svg, .svg-container svg {
  background: transparent !important; background-color: transparent !important;
}
.modebar { background: var(--bg2) !important; border-radius: 8px !important; }

div[data-testid="stDataFrame"], .stDataFrame {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: 14px !important; overflow: hidden !important;
}
[data-testid="stDataFrame"] canvas { filter: invert(1) hue-rotate(180deg); }
[data-testid="stDataFrame"] > div > div { background: #091428 !important; border-radius: 14px !important; }
[data-testid="stDataFrame"] [role="columnheader"] {
  background: rgba(0,198,255,0.07) !important; color: #00c6ff !important;
  font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important;
}
[data-testid="stDataFrame"] [role="gridcell"] {
  background: #091428 !important; color: #e8f4fd !important;
  border-color: rgba(0,180,255,0.06) !important;
}

div[data-testid="stExpander"], details[data-testid="stExpander"] {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
details[data-testid="stExpander"] summary {
  color: var(--cyan) !important; font-family: var(--font-body) !important; font-weight: 700 !important;
}

div[data-testid="stAlert"] {
  background: rgba(0,198,255,0.05) !important; border: 1px solid rgba(0,198,255,0.2) !important;
  border-radius: 12px !important; color: var(--text1) !important;
}

div[data-testid="stDownloadButton"] button {
  background: linear-gradient(135deg, rgba(0,255,157,0.1), rgba(0,255,157,0.04)) !important;
  border: 1px solid rgba(0,255,157,0.3) !important; color: var(--green) !important;
  font-family: var(--font-body) !important; font-weight: 700 !important;
  letter-spacing: 2px !important; border-radius: 10px !important; text-transform: uppercase !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: rgba(0,198,255,0.2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,198,255,0.45); }
hr { border-color: var(--border) !important; }

/* CUSTOM COMPONENTS */
.hero-banner {
  position: relative;
  background: linear-gradient(135deg, #02060f 0%, #080f20 50%, #02060f 100%);
  border: 1px solid var(--border2); border-radius: 24px;
  padding: 32px 40px; margin-bottom: 24px; text-align: center; overflow: hidden;
}
.hero-banner::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse 60% 40% at 20% 0%, rgba(0,198,255,0.08) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 80% 100%, rgba(245,197,24,0.06) 0%, transparent 70%);
}
.hero-banner::after {
  content: ''; position: absolute; top: -1px; left: 20%; right: 20%; height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--gold), transparent);
}
.hero-title {
  font-family: var(--font-display) !important; font-size: 32px !important;
  font-weight: 900 !important; letter-spacing: 6px !important;
  background: linear-gradient(135deg, #00d4ff 0%, #f5c518 45%, #00ff9d 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; margin: 0 0 8px 0; position: relative;
}
.hero-subtitle {
  font-family: var(--font-body) !important; color: var(--text2) !important;
  font-size: 11px !important; letter-spacing: 5px !important;
  text-transform: uppercase !important; font-weight: 600 !important;
  position: relative; margin-top: 6px;
}
.hero-badge {
  display: inline-block; background: rgba(0,198,255,0.10);
  border: 1px solid rgba(0,198,255,0.30); border-radius: 20px; padding: 4px 16px;
  font-family: var(--font-mono); font-size: 10px; color: var(--cyan);
  letter-spacing: 2px; margin-top: 12px; font-weight: 700; position: relative;
}

.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card {
  background: linear-gradient(135deg, rgba(9,20,40,0.95), rgba(6,13,30,0.95));
  border: 1px solid var(--border); border-radius: 16px; padding: 18px 14px;
  position: relative; overflow: hidden;
  transition: transform .3s, box-shadow .3s, border-color .3s;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,198,255,0.15); border-color: rgba(0,198,255,0.4); }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 16px 16px 0 0; }
.kpi-card.cyan::before { background: linear-gradient(90deg, transparent, #00c6ff, transparent); }
.kpi-card.gold::before { background: linear-gradient(90deg, transparent, #f5c518, transparent); }
.kpi-card.green::before { background: linear-gradient(90deg, transparent, #00ff9d, transparent); }
.kpi-card.purple::before { background: linear-gradient(90deg, transparent, #c084fc, transparent); }
.kpi-card.orange::before { background: linear-gradient(90deg, transparent, #ff9432, transparent); }
.kpi-label { font-size: 10px; letter-spacing: 2px; color: var(--text2); text-transform: uppercase; font-weight: 700; margin-bottom: 8px; font-family: var(--font-body); }
.kpi-val { font-family: var(--font-display); font-size: 18px; font-weight: 900; line-height: 1; }
.kpi-card.cyan .kpi-val { color: var(--cyan); text-shadow: 0 0 20px rgba(0,198,255,0.4); }
.kpi-card.gold .kpi-val { color: var(--gold); text-shadow: 0 0 20px rgba(245,197,24,0.4); }
.kpi-card.green .kpi-val { color: var(--green); text-shadow: 0 0 20px rgba(0,255,157,0.4); }
.kpi-card.purple .kpi-val { color: var(--purple); text-shadow: 0 0 20px rgba(192,132,252,0.4); }
.kpi-card.orange .kpi-val { color: var(--orange); text-shadow: 0 0 20px rgba(255,148,50,0.4); }
.kpi-delta { font-size: 10px; font-weight: 700; margin-top: 8px; display: inline-block; padding: 2px 8px; border-radius: 12px; font-family: var(--font-body); }
.kpi-delta.pos { background: rgba(0,255,157,0.12); color: var(--green); border: 1px solid rgba(0,255,157,0.3); }
.kpi-delta.neg { background: rgba(255,51,85,0.12); color: var(--red); border: 1px solid rgba(255,51,85,0.3); }
.kpi-delta.neu { background: rgba(0,198,255,0.10); color: var(--cyan); border: 1px solid rgba(0,198,255,0.25); }

.section-header {
  font-family: var(--font-display) !important; font-size: 12px !important;
  font-weight: 700 !important; letter-spacing: 3px !important; color: var(--cyan) !important;
  border-bottom: 1px solid rgba(0,198,255,0.12); padding-bottom: 8px; margin: 20px 0 14px;
  text-transform: uppercase; text-shadow: 0 0 16px rgba(0,198,255,0.35);
  display: flex; align-items: center; gap: 10px;
}
.section-header::before { content: '◈'; color: var(--cyan); text-shadow: 0 0 10px rgba(0,198,255,0.6); }

.insight-card {
  background: linear-gradient(135deg, rgba(192,132,252,0.08), rgba(0,198,255,0.05));
  border: 1px solid rgba(192,132,252,0.25); border-radius: 16px; padding: 16px 20px;
  margin-bottom: 20px; position: relative; overflow: hidden;
}
.insight-card::before {
  content: '◈  GENERATIVE AI INTELLIGENCE · CLAUDE claude-sonnet-4-20250514';
  font-family: var(--font-mono); font-size: 9px;
  color: var(--purple); letter-spacing: 3px; display: block; margin-bottom: 8px; font-weight: 700;
}
.insight-card p { font-size: 13px; color: #ddeeff; line-height: 1.7; font-weight: 500; }
.insight-card strong { color: #fff; font-weight: 800; }
.insight-card::after {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--purple), transparent);
}

.status-live {
  display: inline-flex; align-items: center; gap: 8px; font-family: var(--font-mono);
  font-size: 10px; color: var(--green); letter-spacing: 2px;
}
.pulse-dot {
  width: 8px; height: 8px; background: var(--green); border-radius: 50%; display: inline-block;
  animation: pulsate 1.5s infinite;
}
@keyframes pulsate {
  0%, 100% { opacity:1; transform:scale(1); box-shadow: 0 0 0 0 rgba(0,255,157,0.4); }
  50% { opacity:.8; transform:scale(1.15); box-shadow: 0 0 0 6px rgba(0,255,157,0); }
}

.forecast-box {
  background: linear-gradient(135deg, rgba(245,197,24,0.06), rgba(245,197,24,0.02));
  border: 1px solid rgba(245,197,24,0.25); border-radius: 16px; padding: 20px; margin-bottom: 16px;
}
.forecast-box .fhead { font-family: var(--font-display); font-size: 11px; letter-spacing: 3px; color: var(--gold); margin-bottom: 14px; }
.forecast-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.forecast-metric { background: rgba(0,0,0,0.3); border-radius: 10px; padding: 14px; border: 1px solid rgba(255,255,255,0.05); }
.forecast-metric .fm-label { font-size: 10px; letter-spacing: 1px; color: var(--text2); margin-bottom: 6px; font-weight: 700; }
.forecast-metric .fm-val { font-family: var(--font-display); font-size: 20px; font-weight: 900; margin-bottom: 4px; }
.forecast-metric .fm-range { font-family: var(--font-mono); font-size: 9px; color: var(--text3); }
.forecast-metric.rev .fm-val { color: var(--cyan); }
.forecast-metric.ff  .fm-val { color: var(--gold); }

.ai-thinking {
  display: flex; align-items: center; gap: 12px; padding: 12px 16px;
  background: rgba(192,132,252,0.08); border: 1px solid rgba(192,132,252,0.2);
  border-radius: 12px; margin: 8px 0;
  font-family: var(--font-mono); font-size: 11px; color: var(--purple); letter-spacing: 1px;
}
.thinking-dots span {
  display: inline-block; width: 6px; height: 6px; background: var(--purple);
  border-radius: 50%; margin: 0 2px; animation: bounce 1.4s infinite ease-in-out;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1.0); opacity: 1; }
}

.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-family: var(--font-mono); font-size: 10px; font-weight: 700; }
.badge.good { background: rgba(0,255,157,0.12); color: var(--green); border: 1px solid rgba(0,255,157,0.3); }
.badge.warn { background: rgba(245,197,24,0.12); color: var(--gold); border: 1px solid rgba(245,197,24,0.3); }
.badge.bad  { background: rgba(255,51,85,0.12); color: var(--red); border: 1px solid rgba(255,51,85,0.3); }
</style>
"""

# ═══════════════════════════════════════════════════════════════
#  DATA LOADING
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    file_options = [
        "RAW DATA.xlsx", "RAW_DATA.xlsx",
        os.path.join(os.path.dirname(__file__), "RAW DATA.xlsx"),
        os.path.join(os.path.dirname(__file__), "RAW_DATA.xlsx"),
    ]
    file_path = next((p for p in file_options if os.path.exists(p)), None)
    if not file_path:
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        df.rename(columns={'Projetcs': 'Project'}, inplace=True)
        month_map = {'July':7,'August':8,'September':9,'October':10,'November':11,'December':12,
                     'January':1,'February':2,'March':3,'April':4,'May':5,'June':6}
        fiscal_order = ['July','August','September','October','November','December',
                        'January','February','March','April','May','June']
        df['Month_Num'] = df['Months'].map(month_map)
        df['Months'] = pd.Categorical(df['Months'], categories=fiscal_order, ordered=True)
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)
        mask_fix = df['Month_Num'] <= 6
        df.loc[mask_fix, 'Year'] = df.loc[mask_fix, 'Year'] + 1
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
#  PAKISTAN EVENTS & SEASONAL ENGINE
# ═══════════════════════════════════════════════════════════════
EID_FITR_MONTHS  = {2020:[5],2021:[5],2022:[5],2023:[4],2024:[4],2025:[3],2026:[3],2027:[3],2028:[2],2029:[2],2030:[1]}
EID_ADHA_MONTHS  = {2020:[7],2021:[7],2022:[7],2023:[6],2024:[6],2025:[6],2026:[5],2027:[5],2028:[5],2029:[4],2030:[4]}
SEASONAL_FACTORS = {1:1.08,2:0.95,3:1.05,4:1.12,5:0.72,6:1.25,7:1.35,8:1.15,9:0.85,10:0.92,11:1.05,12:1.28}

def compute_pakistan_multiplier(month_num, year):
    mult = SEASONAL_FACTORS.get(month_num, 1.0); notes = []
    if year in EID_FITR_MONTHS and month_num in EID_FITR_MONTHS[year]: mult *= 1.45; notes.append("🌙 Eid ul Fitr +45%")
    if year in EID_ADHA_MONTHS and month_num in EID_ADHA_MONTHS[year]: mult *= 1.38; notes.append("🐑 Eid ul Adha +38%")
    if month_num in [5,10]: mult *= 0.88; notes.append("📚 Exam Season -12%")
    if month_num in [7,8]: mult *= 0.92; notes.append("🌧️ Monsoon -8%")
    if month_num == 8:  mult *= 1.08; notes.append("🇵🇰 Independence Day +8%")
    if month_num == 12: mult *= 1.10; notes.append("🎆 Year-End +10%")
    if month_num == 1:  mult *= 1.05; notes.append("🎊 New Year +5%")
    return mult, " | ".join(notes) if notes else "📈 Standard Season"

def generate_advanced_forecast(df, m_num, y_num, metric_col, project=None):
    src = df if project is None else df[df['Project'] == project]
    src = src[src[metric_col] > 100].dropna(subset=[metric_col, 'Date_Obj']).copy()
    if len(src) < 6: return 0, (0, 0), "Insufficient data"
    same_month = src[src['Month_Num'] == m_num].copy(); base_same = 0
    if len(same_month) >= 3:
        same_month = same_month.sort_values('Date_Obj')
        X_sm = np.arange(len(same_month)).reshape(-1,1)
        model_sm = LinearRegression().fit(X_sm, same_month[metric_col].values)
        steps = y_num - same_month['Year'].max()
        base_same = max(0, model_sm.predict([[len(same_month)-1+steps]])[0])
    src_sorted = src.sort_values('Date_Obj')
    X_all = np.arange(len(src_sorted)).reshape(-1,1)
    poly = make_pipeline(PolynomialFeatures(2), LinearRegression())
    poly.fit(X_all, src_sorted[metric_col].values)
    start_date = src_sorted['Date_Obj'].min()
    target_date = pd.Timestamp(f"{y_num}-{m_num:02d}-01")
    months_diff = (target_date.year - start_date.year)*12 + (target_date.month - start_date.month)
    base_poly = max(0, poly.predict([[months_diff]])[0])
    base = (0.60*base_same + 0.40*base_poly) if base_same > 0 else base_poly
    pk_mult, notes = compute_pakistan_multiplier(m_num, y_num)
    avg_seasonal = SEASONAL_FACTORS.get(m_num, 1.0)
    final = (base / avg_seasonal) * pk_mult
    ci_pct = min(max(np.std(same_month[metric_col].values)/np.mean(same_month[metric_col].values) if len(same_month)>=3 else 0.15, 0.08), 0.20)
    return final, (final*(1-ci_pct), final*(1+ci_pct)), notes


# ═══════════════════════════════════════════════════════════════
#  DATA CONTEXT BUILDER  (fed to Claude as system context)
# ═══════════════════════════════════════════════════════════════
def fmt_rev(v):
    if v >= 1e9: return f"Rs. {v/1e9:.2f}B"
    if v >= 1e6: return f"Rs. {v/1e6:.1f}M"
    return f"Rs. {v:,.0f}"

def build_data_context(df):
    """Generates a rich text summary of the dataset to inject into the AI system prompt."""
    if df.empty:
        return "No data loaded. Tell user to place RAW DATA.xlsx in the app directory."

    total_rev = df['Actual Revenue'].sum()
    total_ff  = df['Actual Footfall'].sum()
    total_tgt = df['Target revenue'].sum()
    ach_pct   = total_rev/total_tgt*100 if total_tgt > 0 else 0
    rpp       = total_rev/total_ff if total_ff > 0 else 0

    yearly = df.groupby('Year').agg({'Actual Revenue':'sum','Actual Footfall':'sum','Target revenue':'sum'}).reset_index()
    yearly = yearly[yearly['Year']>2015].sort_values('Year')
    yearly_str = "\n".join([
        f"  {int(r['Year'])}: Revenue={fmt_rev(r['Actual Revenue'])}, Footfall={r['Actual Footfall']/1e3:.0f}K, "
        f"Target={fmt_rev(r['Target revenue'])}, Achievement={r['Actual Revenue']/r['Target revenue']*100:.1f}%"
        if r['Target revenue']>0 else
        f"  {int(r['Year'])}: Revenue={fmt_rev(r['Actual Revenue'])}, Footfall={r['Actual Footfall']/1e3:.0f}K"
        for _, r in yearly.iterrows()
    ])

    proj = df.groupby('Project').agg({'Actual Revenue':'sum','Actual Footfall':'sum'}).reset_index()
    proj = proj[proj['Actual Revenue']>0].sort_values('Actual Revenue', ascending=False)
    proj_str = "\n".join([
        f"  {r['Project']}: Revenue={fmt_rev(r['Actual Revenue'])}, Footfall={r['Actual Footfall']/1e3:.0f}K"
        for _, r in proj.iterrows()
    ])

    month_rev = df.groupby('Months', observed=True)['Actual Revenue'].sum().sort_values(ascending=False)
    month_str = " | ".join([f"{m}: {fmt_rev(v)}" for m, v in month_rev.items()])

    # Recent months (last 6)
    recent = df.sort_values('Date_Obj').tail(6)
    recent_str = "\n".join([
        f"  {r['Date_Obj'].strftime('%b %Y')} ({r.get('Project','N/A')}): Rev={fmt_rev(r['Actual Revenue'])}, FF={r['Actual Footfall']:,.0f}"
        for _, r in recent.iterrows()
    ])

    context = f"""
=== JOYLAND AMUSEMENT PARK — BUSINESS INTELLIGENCE DATABASE ===
Scope: 2017–2026 | Projects: 7 | Pakistan (Lahore) | Fiscal Year: July–June

--- LIFETIME KPIs ---
Total Revenue:    {fmt_rev(total_rev)}
Total Footfall:   {total_ff/1e6:.2f}M visitors
Avg Achievement:  {ach_pct:.1f}% of targets
Revenue/Visitor:  Rs. {rpp:,.0f}
CAGR 2017–2025:   ~33%/year

--- ANNUAL PERFORMANCE ---
{yearly_str}

--- PROJECT BREAKDOWN (All-Time) ---
{proj_str}

--- MONTHLY REVENUE (All-Time Totals, sorted by revenue) ---
{month_str}

--- RECENT 6 MONTHS ---
{recent_str}

--- PAKISTAN SEASONAL EVENTS (used in forecasting) ---
Eid ul Fitr months: 2025→Mar, 2026→Mar, 2027→Mar, 2028→Feb, 2029→Feb, 2030→Jan (+45% footfall)
Eid ul Adha months: 2025→Jun, 2026→May, 2027→May, 2028→May, 2029→Apr, 2030→Apr (+38% footfall)
Exam Season (low): May (Boards), October (Midterms) → -12%
Monsoon: Jul–Aug → -8% | Independence Day Aug 14 → +8%
December festive → +28% | Summer peak Jul → +35%

--- COVID-19 IMPACT ---
2020: Complete closure Apr–Jul 2020. Full year revenue dropped 40% YoY (Rs. 779.9M → Rs. 467.2M)
Recovery: 2021→Rs.657M (+40.5%), 2022→Rs.1.6B (record), 2023→Rs.2.1B, 2024→Rs.2.5B, 2025→Rs.2.96B

--- PROJECTS ---
Joyland Fortress (flagship), JAP-OD (outdoor), SS-PKG, SS-FSM, SS-JAP, B-PKG, B-EMP (bounce empire)
"""
    return context.strip()

def build_chat_history_for_api(messages, max_turns=10):
    """Convert streamlit messages to Anthropic API format (last N turns)."""
    api_msgs = []
    for m in messages[-max_turns*2:]:
        role = "user" if m["is_user"] else "assistant"
        api_msgs.append({"role": role, "content": m["content"]})
    return api_msgs


# ═══════════════════════════════════════════════════════════════
#  GENERATIVE AI ENGINE  —  Claude claude-sonnet-4-20250514
# ═══════════════════════════════════════════════════════════════
def call_claude_api(user_query: str, df: pd.DataFrame, history: list) -> str:
    """
    Sends user query + full data context + conversation history to Claude.
    Returns the AI-generated response string.
    """
    api_key = st.session_state.get("api_key", ANTHROPIC_API_KEY)
    if not api_key:
        return (
            "⚠️ **No Anthropic API Key found.**\n\n"
            "Please enter your API key in the sidebar to enable Generative AI responses.\n\n"
            "Get your key from: https://console.anthropic.com"
        )

    data_context = build_data_context(df)

    system_prompt = f"""You are the **Joyland MIS AI Assistant** — an elite Business Intelligence analyst for Joyland Amusement Park, Lahore, Pakistan. You were built by MIS Assistant Manager **Umair Nizam**.

You have complete access to Joyland's historical data from 2017–2026 across 7 projects. You must answer ALL questions in English with precision, insight, and a professional analytical tone.

{data_context}

=== YOUR CAPABILITIES ===
1. **Data Analysis**: Revenue, footfall, targets, achievements, trends, comparisons
2. **Forecasting**: Use the Pakistan event calendar and seasonal patterns above to reason about future performance
3. **Business Insights**: Explain why metrics moved, identify patterns, suggest strategies
4. **Comparisons**: Year-over-year, month-over-month, project-vs-project
5. **Pakistan Context**: Eid, Ramadan, PSL, monsoon, school calendars, holidays
6. **General Business Questions**: Strategy, operations, marketing, pricing, capacity planning
7. **Conversational**: Answer follow-up questions naturally using conversation history

=== RESPONSE FORMAT RULES ===
- Use **Markdown** formatting: headers, bold, tables, bullet points
- For data queries → use tables with clear columns
- For forecasts → state the estimate with reasoning and confidence range
- For trends → describe the pattern and key drivers
- For strategy questions → give structured recommendations
- Always be specific with numbers from the data
- Use emojis sparingly but effectively (📈 💰 👥 🎯 ✅ ⚠️)
- Keep responses focused and actionable, not generic
- If asked something you don't have data for, say so clearly and reason from what you know

=== PERSONALITY ===
- Professional but conversational
- Data-driven and precise
- Pakistan-aware (understand local culture, events, economy)
- Proactive: if the user asks about a month, also mention relevant events in that month
- Never say "I don't have access to real data" — you DO have the data above

Remember: You are a generative AI, not a keyword matcher. Understand intent, generate insights, ask clarifying questions when needed."""

    # Build conversation history for multi-turn
    api_messages = build_chat_history_for_api(history)
    # Add current user query if not already last
    if not api_messages or api_messages[-1]["role"] != "user":
        api_messages.append({"role": "user", "content": user_query})

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1500,
        "system": system_prompt,
        "messages": api_messages,
    }

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }

    try:
        resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data["content"][0]["text"]
        elif resp.status_code == 401:
            return "❌ **Invalid API Key.** Please check your Anthropic API key in the sidebar."
        elif resp.status_code == 429:
            return "⚠️ **Rate limit reached.** Please wait a moment and try again."
        else:
            return f"❌ **API Error {resp.status_code}:** {resp.text[:300]}"
    except requests.exceptions.Timeout:
        return "⚠️ **Request timed out.** The AI is taking too long — please try again."
    except Exception as e:
        return f"❌ **Connection Error:** {str(e)}"


# ═══════════════════════════════════════════════════════════════
#  PLOTLY CONFIG & CHARTS (unchanged from v6)
# ═══════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(9,20,40,0.6)',
    font=dict(family='Rajdhani, sans-serif', color='#e8f4fd', size=13),
    title_font=dict(family='Orbitron, monospace', size=15, color='#00c6ff'),
    legend=dict(bgcolor='rgba(6,13,30,0.9)', bordercolor='rgba(0,180,255,0.2)', borderwidth=1),
    xaxis=dict(gridcolor='rgba(0,180,255,0.08)', linecolor='rgba(0,180,255,0.15)',
               tickfont=dict(family='JetBrains Mono', size=11, color='#8ab4d4')),
    yaxis=dict(gridcolor='rgba(0,180,255,0.08)', linecolor='rgba(0,180,255,0.15)',
               tickfont=dict(family='JetBrains Mono', size=11, color='#8ab4d4')),
    margin=dict(l=60, r=40, t=70, b=60),
    hoverlabel=dict(bgcolor='rgba(9,20,40,0.95)', bordercolor='rgba(0,198,255,0.3)',
                    font=dict(family='JetBrains Mono', size=12, color='#e8f4fd'))
)
COLORS = ['#00c6ff','#f5c518','#00ff9d','#ff4466','#b660f5','#ff8c42','#4ecdc4']
PROJECT_COLORS = {
    'Joyland Fortress':'#00c6ff','JAP-OD':'#f5c518','SS-PKG':'#00ff9d',
    'SS-FSM':'#ff4466','SS-JAP':'#b660f5','B-PKG':'#ff8c42','B-EMP':'#4ecdc4',
}

def chart_yearly_bar(df):
    yearly = df.groupby('Year').agg({'Actual Revenue':'sum','Target revenue':'sum'}).reset_index()
    yearly = yearly[yearly['Year'] > 2015]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=yearly['Year'].astype(str), y=yearly['Actual Revenue'],
        name='Actual Revenue', marker_color='#00c6ff',
        text=[fmt_rev(v) for v in yearly['Actual Revenue']], textposition='outside',
        textfont=dict(family='JetBrains Mono',size=10,color='#00c6ff')))
    fig.add_trace(go.Bar(x=yearly['Year'].astype(str), y=yearly['Target revenue'],
        name='Target Revenue', marker_color='rgba(245,197,24,0.4)',
        marker_line=dict(color='#f5c518',width=1)))
    yearly['ach'] = np.where(yearly['Target revenue']>0, yearly['Actual Revenue']/yearly['Target revenue']*100, 0)
    fig.add_trace(go.Scatter(x=yearly['Year'].astype(str), y=yearly['ach'],
        name='Achievement %', yaxis='y2', line=dict(color='#00ff9d',width=2.5,dash='dot'),
        mode='lines+markers+text', marker=dict(size=8,color='#00ff9d'),
        text=[f"{v:.0f}%" for v in yearly['ach']], textposition='top center',
        textfont=dict(family='JetBrains Mono',size=10,color='#00ff9d')))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group',
        title="Annual Revenue: Actual vs Target + Achievement %", height=480,
        yaxis2=dict(overlaying='y', side='right', title='Achievement %',
                    tickformat='.0f', ticksuffix='%',
                    tickfont=dict(family='JetBrains Mono',size=11,color='#00ff9d')))
    return fig

def chart_trend(df, col, color, title):
    df = df[df[col]>0].sort_values('Date_Obj')
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date_Obj'], y=df[col], fill='tozeroy',
        fillcolor=f'rgba({r},{g},{b},0.08)', line=dict(color=color,width=2.5),
        mode='lines+markers', marker=dict(size=6,color=color)))
    if len(df)>=6:
        fig.add_trace(go.Scatter(x=df['Date_Obj'], y=df[col].rolling(3,min_periods=1).mean(),
            line=dict(color='#f5c518',width=1.5,dash='dot'), name='3M Avg'))
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=420)
    return fig

def chart_heatmap(df):
    pivot = df.pivot_table(values='Actual Revenue', index='Year', columns='Months', aggfunc='sum', observed=True)
    fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        text=[[fmt_rev(v) if pd.notna(v) and v>0 else '' for v in row] for row in pivot.values],
        texttemplate='%{text}', textfont=dict(family='JetBrains Mono',size=9,color='white'),
        colorscale=[[0,'#050b18'],[0.3,'#0a3060'],[0.6,'#0060b0'],[1,'#00c6ff']]))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue Heatmap: Year × Month", height=420)
    return fig

def chart_project(df):
    d = df.groupby('Project').agg({'Actual Revenue':'sum','Actual Footfall':'sum'}).reset_index()
    d = d[d['Actual Revenue']>0].sort_values('Actual Revenue', ascending=False)
    colors = [PROJECT_COLORS.get(p,'#00c6ff') for p in d['Project']]
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Revenue', x=d['Project'], y=d['Actual Revenue'],
        marker_color=colors, text=[fmt_rev(v) for v in d['Actual Revenue']],
        textposition='outside', textfont=dict(family='JetBrains Mono',size=10)))
    fig.update_layout(**PLOTLY_LAYOUT, title="Project Revenue Comparison", height=440)
    return fig

def chart_forecast_trajectory(df):
    hist = df[df['Actual Revenue']>0].sort_values('Date_Obj')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist['Date_Obj'], y=hist['Actual Revenue'],
        name='Actual Revenue', fill='tozeroy', fillcolor='rgba(0,198,255,0.06)',
        line=dict(color='#00c6ff',width=2), mode='lines+markers', marker=dict(size=4)))
    if len(hist)>=8:
        last_date = hist['Date_Obj'].max()
        future_dates = [last_date + pd.DateOffset(months=i) for i in range(1,37)]
        forecast_vals = [generate_advanced_forecast(df, fd.month, fd.year, 'Actual Revenue')[0] for fd in future_dates]
        fig.add_trace(go.Scatter(x=future_dates, y=forecast_vals, name='AI Forecast',
            line=dict(color='#f5c518',width=2,dash='dot'), mode='lines+markers',
            marker=dict(size=5,symbol='diamond',color='#f5c518')))
        fig.add_trace(go.Scatter(
            x=future_dates+future_dates[::-1],
            y=[v*1.15 for v in forecast_vals]+[max(0,v*0.85) for v in forecast_vals][::-1],
            fill='toself', fillcolor='rgba(245,197,24,0.06)',
            line=dict(color='rgba(245,197,24,0)'), name='Confidence ±15%'))
    fig.add_vrect(x0="2020-03-01", x1="2021-07-01", fillcolor="rgba(255,68,102,0.06)",
        annotation_text="COVID-19", line_width=0,
        annotation_font=dict(color='#ff4466',size=11))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue Trajectory 2017–2028 (AI Forecast)", height=500)
    return fig


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
def render_sidebar(df):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:16px 0 8px;'>
          <div style='font-family:Orbitron,monospace;font-size:10px;letter-spacing:4px;color:#7a9cc0;'>JOYLAND MIS</div>
          <div style='font-family:Orbitron,monospace;font-size:18px;font-weight:900;color:#00c6ff;margin:4px 0;'>CONTROL</div>
          <div style='font-family:Orbitron,monospace;font-size:9px;letter-spacing:3px;color:#3a5a80;'>GENERATIVE AI · v7.0</div>
        </div>
        <div style='border-bottom:1px solid rgba(0,180,255,0.2);margin:8px 0 16px;'></div>
        """, unsafe_allow_html=True)

        # ─── API KEY INPUT ───
        st.markdown("""
        <div style='font-family:Rajdhani;font-size:9px;letter-spacing:2px;color:#7a9cc0;
             text-transform:uppercase;margin-bottom:6px;font-weight:700;'>
          🔑 ANTHROPIC API KEY
        </div>
        """, unsafe_allow_html=True)

        current_key = st.session_state.get("api_key", ANTHROPIC_API_KEY)
        api_key_input = st.text_input(
            "API Key", value=current_key,
            type="password", label_visibility="collapsed",
            placeholder="sk-ant-api03-..."
        )
        if api_key_input:
            st.session_state["api_key"] = api_key_input
            if api_key_input.startswith("sk-ant"):
                st.markdown("""
                <div style='background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.2);
                     border-radius:8px;padding:6px 10px;margin-top:4px;
                     font-family:JetBrains Mono,monospace;font-size:10px;color:#00ff9d;'>
                  ✅ API KEY ACTIVE — GENERATIVE AI ENABLED
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:rgba(255,51,85,0.08);border:1px solid rgba(255,51,85,0.2);
                     border-radius:8px;padding:6px 10px;margin-top:4px;
                     font-family:JetBrains Mono,monospace;font-size:10px;color:#ff3355;'>
                  ⚠️ INVALID KEY FORMAT
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='border-bottom:1px solid rgba(0,180,255,0.1);margin:12px 0;'></div>", unsafe_allow_html=True)

        if st.button("🗑️ CLEAR CHAT", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("<div style='border-bottom:1px solid rgba(0,180,255,0.1);margin:12px 0;'></div>", unsafe_allow_html=True)

        if not df.empty:
            records = len(df)
            projects = df['Project'].nunique()
            min_yr = int(df['Year'].min()); max_yr = int(df['Year'].max())
            st.markdown(f"""
            <div style='background:rgba(12,27,53,0.8);border:1px solid rgba(0,180,255,0.15);border-radius:12px;padding:14px;margin-bottom:12px;'>
              <div style='font-family:Rajdhani;font-size:9px;letter-spacing:2px;color:#8ab4d4;text-transform:uppercase;margin-bottom:8px;font-weight:700;'>DATA SCOPE</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#f0f8ff;margin:5px 0;'>📅 {min_yr} – {max_yr}</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#f0f8ff;margin:5px 0;'>📊 {records:,} Records</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#f0f8ff;margin:5px 0;'>🏢 {projects} Projects</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#00ff9d;margin:5px 0;'>🤖 Claude claude-sonnet-4-20250514 ACTIVE</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background:rgba(12,27,53,0.8);border:1px solid rgba(0,180,255,0.15);border-radius:12px;padding:14px;'>
          <div style='font-family:Rajdhani;font-size:9px;letter-spacing:2px;color:#8ab4d4;text-transform:uppercase;margin-bottom:8px;font-weight:700;'>EXAMPLE QUERIES</div>
        """, unsafe_allow_html=True)
        examples = [
            "Why did revenue drop in May 2023?",
            "Which project should we invest more in?",
            "How will Eid in March 2026 affect Q3?",
            "Compare Q1 2024 vs Q1 2025",
            "What's our revenue per visitor trend?",
            "Predict December 2027 revenue",
            "Which months have the worst performance?",
            "How did COVID affect us compared to peers?",
            "Suggest a revenue improvement strategy",
            "Forecast full year 2027",
        ]
        for ex in examples:
            st.markdown(f"<div style='font-family:JetBrains Mono;font-size:10px;color:#c8dff0;margin:4px 0;'>› {ex}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center;padding:12px;font-family:Rajdhani;font-size:10px;color:#3d6080;letter-spacing:1px;margin-top:16px;'>
          ARCHITECT: <span style='color:#f5c518;font-weight:700;'>UMAIR NIZAM</span><br>
          <span style='color:#1a3a6b;'>v7.0 GENERATIVE AI · 2017–2030</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Joyland MIS Assistant · v7.0 Generative AI",
        layout="wide", page_icon="🎢",
        initial_sidebar_state="expanded"
    )
    st.markdown(PAGE_THEME, unsafe_allow_html=True)

    for k, v in {'messages':[], 'api_key': ANTHROPIC_API_KEY}.items():
        if k not in st.session_state:
            st.session_state[k] = v

    df = load_data()
    render_sidebar(df)

    # ── HERO BANNER ──
    st.markdown("""
    <div class='hero-banner'>
      <div class='hero-title'>JOYLAND  MIS  ASSISTANT</div>
      <div class='hero-subtitle'>Generative AI · Business Intelligence · Predictive Analytics</div>
      <div class='hero-badge'>⬡ CLAUDE claude-sonnet-4-20250514 · DATA 2017–2026 · FORECAST 2030 · v7.0 GENERATIVE AI</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI CARDS ──
    if not df.empty:
        try:
            total_rev = df['Actual Revenue'].sum()
            total_ff  = df['Actual Footfall'].sum()
            total_tgt = df['Target revenue'].sum()
            ach = total_rev/total_tgt*100 if total_tgt > 0 else 0
            rpp = total_rev/total_ff if total_ff > 0 else 0
            max_yr = df['Year'].max()
            last_yr = df[df['Year']==max_yr]['Actual Revenue'].sum()
            prev_yr = df[df['Year']==max_yr-1]['Actual Revenue'].sum()
            yoy_g = (last_yr-prev_yr)/prev_yr*100 if prev_yr > 0 else 0
            delta_sign = "pos" if yoy_g >= 0 else "neg"
            delta_arrow = "↑" if yoy_g >= 0 else "↓"
            st.markdown(f"""
            <div class='kpi-grid'>
              <div class='kpi-card cyan'>
                <div class='kpi-label'>Lifetime Revenue</div>
                <div class='kpi-val'>{fmt_rev(total_rev)}</div>
                <div class='kpi-delta pos'>↑ 2017–2026</div>
              </div>
              <div class='kpi-card gold'>
                <div class='kpi-label'>Total Visitors</div>
                <div class='kpi-val'>{total_ff/1e6:.2f}M</div>
                <div class='kpi-delta pos'>↑ Cumulative</div>
              </div>
              <div class='kpi-card green'>
                <div class='kpi-label'>Avg Achievement</div>
                <div class='kpi-val'>{ach:.1f}%</div>
                <div class='kpi-delta neu'>vs All Targets</div>
              </div>
              <div class='kpi-card purple'>
                <div class='kpi-label'>Rev / Visitor</div>
                <div class='kpi-val'>Rs. {rpp:,.0f}</div>
                <div class='kpi-delta neu'>Lifetime Avg</div>
              </div>
              <div class='kpi-card orange'>
                <div class='kpi-label'>YoY Growth</div>
                <div class='kpi-val'>{yoy_g:+.1f}%</div>
                <div class='kpi-delta {delta_sign}'>{delta_arrow} {max_yr-1}→{max_yr}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass

    # ── AI INSIGHT BADGE ──
    api_active = bool(st.session_state.get("api_key",""))
    ai_status = "🟢 GENERATIVE AI ONLINE · Claude claude-sonnet-4-20250514" if api_active else "🟡 ENTER API KEY IN SIDEBAR TO ENABLE GENERATIVE AI"
    st.markdown(f"""
    <div class='insight-card'>
      <p>{ai_status} — Ask <strong>any</strong> question in natural language.
      Full conversation memory · Pakistan event-aware · Multi-turn reasoning ·
      Data 2017–2026 · Forecast to 2030</p>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──
    tab_chat, tab_charts, tab_forecast, tab_data = st.tabs([
        "🤖 AI Chat", "📊 Visual Intelligence", "🔮 Forecast Engine", "📋 Raw Data"
    ])

    # ════════════════════════════════════════════════
    #  TAB 1 — GENERATIVE AI CHAT
    # ════════════════════════════════════════════════
    with tab_chat:
        st.markdown("<div class='section-header'>GENERATIVE AI ANALYTICS ASSISTANT</div>", unsafe_allow_html=True)

        # Render chat history
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["is_user"] else "assistant"):
                st.markdown(msg["content"])

        # Chat input
        prompt = st.chat_input(
            "Ask anything: Why did revenue drop? Forecast 2027? Which project to grow? What's our best month?…"
        )

        if prompt:
            # Show user message
            st.session_state.messages.append({"content": prompt, "is_user": True})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Show thinking indicator + call API
            with st.chat_message("assistant"):
                with st.spinner("🤖 Claude claude-sonnet-4-20250514 is analyzing your data…"):
                    response = call_claude_api(prompt, df, st.session_state.messages[:-1])
                st.markdown(response)

            st.session_state.messages.append({"content": response, "is_user": False})

    # ════════════════════════════════════════════════
    #  TAB 2 — VISUAL INTELLIGENCE
    # ════════════════════════════════════════════════
    with tab_charts:
        if df.empty:
            st.warning("No data loaded. Place RAW DATA.xlsx in the app directory.")
        else:
            st.markdown("<div class='section-header'>VISUAL INTELLIGENCE PANEL</div>", unsafe_allow_html=True)

            chart_opt = st.selectbox("Select Visualization", [
                "Annual Revenue vs Target + Achievement",
                "Revenue Trend (Time Series)",
                "Footfall Trend (Time Series)",
                "Revenue Heatmap: Year × Month",
                "Project Revenue Comparison",
            ])

            if chart_opt.startswith("Annual"):
                st.plotly_chart(chart_yearly_bar(df), use_container_width=True)
            elif chart_opt.startswith("Revenue Trend"):
                st.plotly_chart(chart_trend(df, 'Actual Revenue', '#00c6ff', 'Revenue Trend 2017–2026'), use_container_width=True)
            elif chart_opt.startswith("Footfall"):
                st.plotly_chart(chart_trend(df, 'Actual Footfall', '#f5c518', 'Footfall Trend 2017–2026'), use_container_width=True)
            elif chart_opt.startswith("Revenue Heatmap"):
                st.plotly_chart(chart_heatmap(df), use_container_width=True)
            elif chart_opt.startswith("Project"):
                st.plotly_chart(chart_project(df), use_container_width=True)

    # ════════════════════════════════════════════════
    #  TAB 3 — FORECAST ENGINE
    # ════════════════════════════════════════════════
    with tab_forecast:
        st.markdown("<div class='section-header'>ADVANCED PREDICTIVE ANALYTICS ENGINE</div>", unsafe_allow_html=True)
        if not df.empty:
            st.plotly_chart(chart_forecast_trajectory(df), use_container_width=True)

            st.markdown("#### 🔮 Manual Forecast Generator")
            col1, col2, col3 = st.columns(3)
            MONTH_MAP_FULL = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                              'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
            with col1:
                m_sel = st.selectbox("Month", list(MONTH_MAP_FULL.keys()))
            with col2:
                y_sel = st.selectbox("Year", list(range(2025,2031)))
            with col3:
                p_sel = st.selectbox("Project", ['All Projects'] + sorted(df['Project'].unique().tolist()))

            if st.button("🔮 GENERATE FORECAST + AI EXPLANATION", use_container_width=True):
                m_idx = MONTH_MAP_FULL[m_sel]
                df_src = df if p_sel == 'All Projects' else df[df['Project']==p_sel]
                p_rev,(lr,ur),note_rev = generate_advanced_forecast(df_src, m_idx, y_sel, 'Actual Revenue')
                p_ff,(lf,uf),_          = generate_advanced_forecast(df_src, m_idx, y_sel, 'Actual Footfall')
                pk_mult, pk_notes = compute_pakistan_multiplier(m_idx, y_sel)

                st.markdown(f"""
                <div class='forecast-box'>
                  <div class='fhead'>◈ AI FORECAST — {m_sel.upper()} {y_sel} ({p_sel})</div>
                  <div class='forecast-grid'>
                    <div class='forecast-metric rev'>
                      <div class='fm-label'>💰 REVENUE PROJECTION</div>
                      <div class='fm-val'>{fmt_rev(p_rev)}</div>
                      <div class='fm-range'>Range: {fmt_rev(lr)} – {fmt_rev(ur)}</div>
                    </div>
                    <div class='forecast-metric ff'>
                      <div class='fm-label'>👥 FOOTFALL PROJECTION</div>
                      <div class='fm-val'>{p_ff:,.0f}</div>
                      <div class='fm-range'>Range: {lf:,.0f} – {uf:,.0f}</div>
                    </div>
                  </div>
                  <div style='margin-top:12px;font-family:Rajdhani,sans-serif;font-size:13px;color:#a8d4f5;'>
                    <strong>Event Modifiers:</strong> {note_rev}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # ── AI explanation of this forecast ──
                with st.spinner("🤖 Generating AI explanation…"):
                    forecast_question = (
                        f"Explain the forecast for {m_sel} {y_sel} for {p_sel}. "
                        f"The model predicts Revenue: {fmt_rev(p_rev)} (range {fmt_rev(lr)}–{fmt_rev(ur)}) "
                        f"and Footfall: {p_ff:,.0f}. "
                        f"Event modifiers: {note_rev}. "
                        f"Explain WHY these numbers make sense, what events or seasonality drive them, "
                        f"what risks could cause under/over-performance, and what management should prepare for."
                    )
                    ai_explanation = call_claude_api(forecast_question, df, [])
                st.markdown("#### 🤖 AI Explanation")
                st.markdown(ai_explanation)

                st.markdown("""
                <div style='background:rgba(245,197,24,0.05);border:1px solid rgba(245,197,24,0.2);border-radius:12px;padding:16px;margin-top:16px;'>
                  <div style='font-family:Orbitron,monospace;font-size:11px;letter-spacing:3px;color:#f5c518;margin-bottom:10px;'>🌙 PAKISTAN EVENT CALENDAR</div>
                  <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#7a9cc0;line-height:2;'>
                    <strong>Eid ul Fitr:</strong> 2025→Mar | 2026→Mar | 2027→Mar | 2028→Feb | 2029→Feb | 2030→Jan<br>
                    <strong>Eid ul Adha:</strong> 2025→Jun | 2026→May | 2027→May | 2028→May | 2029→Apr | 2030→Apr<br>
                    <strong>Exam Season (low):</strong> May · October &nbsp;|&nbsp; <strong>Monsoon:</strong> Jul–Aug &nbsp;|&nbsp; <strong>Winter Peak:</strong> December
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    #  TAB 4 — RAW DATA
    # ════════════════════════════════════════════════
    with tab_data:
        if df.empty:
            st.warning("No data loaded.")
        else:
            display_cols = [c for c in df.columns if c not in ['Month_Num','Date_Obj','Fiscal_Year_Label']]
            num_cols = [c for c in display_cols if pd.api.types.is_numeric_dtype(df[c])]
            st.dataframe(
                df[display_cols].style.format({c:'{:,.0f}' for c in num_cols})
                .set_properties(**{'background-color':'#091428','color':'#f0f8ff','border':'1px solid rgba(0,180,255,0.15)'}),
                use_container_width=True, height=500
            )
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ EXPORT CSV", data=csv,
                file_name=f"joyland_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime='text/csv', use_container_width=True)

    # ── FOOTER ──
    records = len(df) if not df.empty else 0
    projects = df['Project'].nunique() if not df.empty else 0
    st.markdown(f"""
    <div style='text-align:center;padding:20px 0 10px;margin-top:24px;border-top:1px solid rgba(0,180,255,0.1);'>
      <div style='display:flex;justify-content:center;align-items:center;gap:8px;
           font-family:JetBrains Mono,monospace;font-size:10px;color:#00ff9d;letter-spacing:2px;'>
        <span style='width:8px;height:8px;background:#00ff9d;border-radius:50%;display:inline-block;animation:pulsate 1.5s infinite;'></span>
        GENERATIVE AI ENGINE ONLINE · CLAUDE claude-sonnet-4-20250514 · ARCHITECT: UMAIR NIZAM
      </div>
      <div style='font-family:JetBrains Mono,monospace;font-size:9px;color:#3d6080;margin-top:6px;letter-spacing:2px;'>
        2017–2030 · {records:,} RECORDS · {projects} PROJECTS · v7.0 GENERATIVE AI
      </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
