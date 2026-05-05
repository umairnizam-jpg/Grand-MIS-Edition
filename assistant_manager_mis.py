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
#  JOYLAND MIS ASSISTANT  ·  v6.0 ULTRA
#  Architect: Umair Nizam  |  Scope: 2017 – 2030
#  AI Engine: Advanced Seasonal Decomposition + Pakistan Events
#  Interface: Matched to joyland_mis_theme_preview.html
# ═══════════════════════════════════════════════════════════════

PAGE_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* ── ROOT VARIABLES ─────────────────────────────────────────── */
:root {
  --bg0: #02060f;
  --bg1: #060d1e;
  --bg2: #091428;
  --bg3: #0c1b35;
  --bg4: #101f3a;
  --glass: rgba(9,20,40,0.92);
  --border: rgba(0,180,255,0.12);
  --border2: rgba(0,180,255,0.25);
  --border3: rgba(0,180,255,0.40);
  --cyan: #00c6ff;
  --cyan-dim: rgba(0,198,255,0.15);
  --gold: #f5c518;
  --gold-dim: rgba(245,197,24,0.12);
  --green: #00ff9d;
  --green-dim: rgba(0,255,157,0.12);
  --red: #ff3355;
  --purple: #c084fc;
  --orange: #ff9432;
  --text1: #f0f8ff;
  --text2: #8ab4d4;
  --text3: #3d6080;
  --font-display: 'Orbitron', monospace;
  --font-body: 'Rajdhani', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

/* ── GLOBAL RESET / BASE ────────────────────────────────────── */
html, body,
.stApp, .main,
[class*="css"],
section.main > div,
.block-container {
  background: var(--bg0) !important;
  color: var(--text1) !important;
  font-family: var(--font-body) !important;
}

[style*="background: white"],[style*="background-color: white"],
[style*="background: rgb(255, 255, 255)"],[style*="background-color: rgb(255, 255, 255)"],
[style*="background: #fff"],[style*="background-color: #fff"],
[style*="background: #ffffff"],[style*="background-color: #ffffff"],
[style*="background:#fff"],[style*="background:#ffffff"],
[style*="background-color:#fff"],[style*="background-color:#ffffff"],
.css-1aehpvj, .css-6qob1r,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
  background: var(--bg0) !important;
  background-color: var(--bg0) !important;
}

/* Grid background texture */
.main::before {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    linear-gradient(rgba(0,198,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,198,255,0.025) 1px, transparent 1px);
  background-size: 48px 48px;
}

/* ── TEXT ───────────────────────────────────────────────────── */
p, span, div, label, li, td, th, a { color: var(--text1) !important; }
.stMarkdown p, .stMarkdown span, .stMarkdown li {
  color: #ddeeff !important; font-size: 15px !important;
  font-weight: 500 !important; line-height: 1.8 !important;
}
h1, h2, h3 { color: var(--text1) !important; }

/* ── SIDEBAR ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #020912 0%, #050d1c 100%) !important;
  border-right: 1px solid var(--border2) !important;
}
section[data-testid="stSidebar"] * { background-color: transparent !important; }
section[data-testid="stSidebar"]::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--gold), transparent);
  animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* ── METRIC CARDS ───────────────────────────────────────────── */
div[data-testid="stMetric"] {
  background: linear-gradient(135deg, var(--bg3) 0%, var(--bg2) 100%) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 18px !important;
  padding: 22px 18px !important;
  position: relative; overflow: hidden;
  transition: transform .3s, box-shadow .3s, border-color .3s !important;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-5px) !important;
  box-shadow: 0 20px 60px rgba(0,198,255,0.18) !important;
  border-color: var(--border3) !important;
}
div[data-testid="stMetric"]::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
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
div[data-testid="stMetricDelta"] > div {
  color: var(--green) !important; font-family: var(--font-body) !important;
  font-size: 12px !important; font-weight: 700 !important;
  background: var(--green-dim) !important; padding: 3px 10px !important;
  border-radius: 20px !important; border: 1px solid rgba(0,255,157,0.3) !important;
}

/* ── BUTTONS ────────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, rgba(0,198,255,0.12), rgba(0,198,255,0.04)) !important;
  border: 1px solid rgba(0,198,255,0.35) !important;
  color: var(--cyan) !important; font-family: var(--font-body) !important;
  font-weight: 700 !important; letter-spacing: 2px !important;
  border-radius: 10px !important; text-transform: uppercase !important;
  font-size: 11px !important; transition: all .3s ease !important;
}
.stButton > button:hover {
  background: rgba(0,198,255,0.22) !important;
  box-shadow: 0 0 24px rgba(0,198,255,0.25), inset 0 0 24px rgba(0,198,255,0.04) !important;
  transform: translateY(-2px) !important; border-color: var(--cyan) !important;
}

/* ── TABS ───────────────────────────────────────────────────── */
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

/* ── SELECTBOX / DROPDOWN ───────────────────────────────────── */
div[data-baseweb="select"] > div, div[data-baseweb="select"] > div > div {
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  border-radius: 10px !important; color: var(--text1) !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div[class*="singleValue"],
div[data-baseweb="select"] div[class*="placeholder"],
div[data-baseweb="select"] svg {
  color: var(--text1) !important; fill: var(--text2) !important;
  font-family: var(--font-body) !important; font-weight: 600 !important;
}
div[data-baseweb="popover"], div[data-baseweb="popover"] > div,
ul[role="listbox"], div[role="listbox"], [data-baseweb="menu"],
[data-baseweb="menu"] ul, [data-baseweb="menu"] > div {
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  border-radius: 14px !important; box-shadow: 0 12px 48px rgba(0,0,0,0.8) !important;
}
li[role="option"], div[role="option"], [data-baseweb="menu"] li {
  background: var(--bg2) !important; color: var(--text1) !important;
  font-family: var(--font-body) !important; font-size: 14px !important; font-weight: 600 !important;
}
li[role="option"]:hover, div[role="option"]:hover, li[aria-selected="true"] {
  background: rgba(0,198,255,0.12) !important; color: var(--cyan) !important;
}

/* ── CHAT INPUT ─────────────────────────────────────────────── */
div[data-testid="stChatInput"] {
  background: var(--bg2) !important; border: 1.5px solid var(--border2) !important;
  border-radius: 14px !important;
}
div[data-testid="stChatInput"] textarea {
  background: var(--bg2) !important; border: none !important;
  color: var(--text1) !important; font-family: var(--font-body) !important;
  font-size: 14px !important; caret-color: var(--cyan) !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
  color: var(--text3) !important; font-style: italic !important;
}
div[data-testid="stChatInput"]:focus-within {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px rgba(0,198,255,0.12), 0 0 32px rgba(0,198,255,0.08) !important;
}
div[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, var(--cyan), #0090cc) !important;
  border-radius: 10px !important; border: none !important;
}
div[data-testid="stBottom"], div[data-testid="stBottom"] > div,
.stChatFloatingInputContainer {
  background: var(--bg0) !important; border-top: 1px solid var(--border) !important;
}
footer, footer * { background: var(--bg0) !important; color: var(--text3) !important; }

/* ── CHAT MESSAGES ──────────────────────────────────────────── */
div[data-testid="stChatMessage"] { background: transparent !important; border: none !important; }
div[data-testid="stChatMessage"] > div {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: 14px !important;
}
div[data-testid="stChatMessage"][data-testid*="user"] > div {
  background: rgba(0,198,255,0.05) !important; border-color: rgba(0,198,255,0.15) !important;
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

/* ── PLOTLY CHARTS ──────────────────────────────────────────── */
div[data-testid="stPlotlyChart"], div[data-testid="stPlotlyChart"] > div,
.js-plotly-plot, .js-plotly-plot .plotly, .js-plotly-plot .plotly .main-svg,
.plot-container, .plot-container > svg, .svg-container, .svg-container svg {
  background: transparent !important; background-color: transparent !important;
}
.modebar, .modebar-container, .modebar-group { background: var(--bg2) !important; border-radius: 8px !important; }
.modebar-btn svg path { fill: var(--text2) !important; }
.modebar-btn:hover svg path { fill: var(--cyan) !important; }

/* ── DATAFRAME / TABLES ─────────────────────────────────────── */
div[data-testid="stDataFrame"], div[data-testid="stDataFrame"] > div,
.stDataFrame, .stDataFrame > div {
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
table { background: var(--bg2) !important; border-radius: 12px !important; width: 100% !important; }
thead, thead tr { background: rgba(0,198,255,0.07) !important; }
th {
  background: rgba(0,198,255,0.07) !important; color: var(--cyan) !important;
  font-family: var(--font-body) !important; font-size: 11px !important;
  letter-spacing: 2px !important; text-transform: uppercase !important;
  padding: 12px 14px !important; border-bottom: 1px solid var(--border2) !important;
}
td {
  color: var(--text1) !important; background: transparent !important;
  font-size: 13px !important; padding: 9px 14px !important;
  border-bottom: 1px solid rgba(0,198,255,0.04) !important;
}
tr:hover td { background: rgba(0,198,255,0.03) !important; }
tr:last-child td { border-bottom: none !important; }

/* ── EXPANDER ───────────────────────────────────────────────── */
div[data-testid="stExpander"], details[data-testid="stExpander"] {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
details[data-testid="stExpander"] summary {
  color: var(--cyan) !important; font-family: var(--font-body) !important; font-weight: 700 !important;
}

/* ── ALERTS ─────────────────────────────────────────────────── */
div[data-testid="stAlert"] {
  background: rgba(0,198,255,0.05) !important; border: 1px solid rgba(0,198,255,0.2) !important;
  border-radius: 12px !important; color: var(--text1) !important;
}
div[data-testid="stSuccess"] { background: rgba(0,255,157,0.06) !important; border-color: rgba(0,255,157,0.25) !important; }
div[data-testid="stWarning"] { background: rgba(245,197,24,0.06) !important; border-color: rgba(245,197,24,0.25) !important; }
div[data-testid="stError"] { background: rgba(255,51,85,0.06) !important; border-color: rgba(255,51,85,0.25) !important; }

/* ── DOWNLOAD BUTTON ────────────────────────────────────────── */
div[data-testid="stDownloadButton"] button {
  background: linear-gradient(135deg, rgba(0,255,157,0.1), rgba(0,255,157,0.04)) !important;
  border: 1px solid rgba(0,255,157,0.3) !important; color: var(--green) !important;
  font-family: var(--font-body) !important; font-weight: 700 !important;
  letter-spacing: 2px !important; border-radius: 10px !important; text-transform: uppercase !important;
}
div[data-testid="stDownloadButton"] button:hover {
  background: rgba(0,255,157,0.18) !important; box-shadow: 0 0 20px rgba(0,255,157,0.2) !important;
}

/* ── PROGRESS / SPINNER ─────────────────────────────────────── */
.stProgress > div > div { background: var(--cyan) !important; }
div[data-testid="stSpinner"] { color: var(--cyan) !important; }

/* ── SCROLLBAR ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: rgba(0,198,255,0.2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,198,255,0.45); }

/* ── DIVIDER ────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── INPUT WIDGETS ──────────────────────────────────────────── */
div[data-baseweb="input"] > div, input[type="text"], input[type="number"], textarea {
  background: var(--bg2) !important; border-color: var(--border2) !important;
  color: var(--text1) !important; border-radius: 10px !important;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS — Matched to joyland_mis_theme_preview.html
   ═══════════════════════════════════════════════════════════════ */

/* Hero banner */
.hero-banner {
  position: relative;
  background: linear-gradient(135deg, #02060f 0%, #080f20 50%, #02060f 100%);
  border: 1px solid var(--border2);
  border-radius: 24px;
  padding: 32px 40px;
  margin-bottom: 24px;
  text-align: center;
  overflow: hidden;
}
.hero-banner::before {
  content: '';
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 60% 40% at 20% 0%, rgba(0,198,255,0.08) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 80% 100%, rgba(245,197,24,0.06) 0%, transparent 70%);
}
.hero-banner::after {
  content: '';
  position: absolute; top: -1px; left: 20%; right: 20%; height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--gold), transparent);
  border-radius: 2px;
}
.hero-title {
  font-family: var(--font-display) !important;
  font-size: 32px !important; font-weight: 900 !important;
  letter-spacing: 6px !important;
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
  display: inline-block;
  background: rgba(0,198,255,0.10);
  border: 1px solid rgba(0,198,255,0.30);
  border-radius: 20px; padding: 4px 16px;
  font-family: var(--font-mono); font-size: 10px;
  color: var(--cyan); letter-spacing: 2px; margin-top: 12px;
  font-weight: 700; position: relative;
}

/* KPI Cards — matching HTML preview kpi classes */
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card {
  background: linear-gradient(135deg, rgba(9,20,40,0.95), rgba(6,13,30,0.95));
  border: 1px solid var(--border);
  border-radius: 16px; padding: 18px 14px;
  position: relative; overflow: hidden;
  transition: transform .3s, box-shadow .3s, border-color .3s;
  cursor: pointer;
}
.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0,198,255,0.15);
  border-color: rgba(0,198,255,0.4);
}
.kpi-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  border-radius: 16px 16px 0 0;
}
.kpi-card.cyan::before { background: linear-gradient(90deg, transparent, #00c6ff, transparent); }
.kpi-card.gold::before { background: linear-gradient(90deg, transparent, #f5c518, transparent); }
.kpi-card.green::before { background: linear-gradient(90deg, transparent, #00ff9d, transparent); }
.kpi-card.purple::before { background: linear-gradient(90deg, transparent, #c084fc, transparent); }
.kpi-card.orange::before { background: linear-gradient(90deg, transparent, #ff9432, transparent); }
.kpi-label {
  font-size: 10px; letter-spacing: 2px; color: var(--text2);
  text-transform: uppercase; font-weight: 700; margin-bottom: 8px;
  font-family: var(--font-body);
}
.kpi-val {
  font-family: var(--font-display); font-size: 18px; font-weight: 900; line-height: 1;
}
.kpi-card.cyan .kpi-val { color: var(--cyan); text-shadow: 0 0 20px rgba(0,198,255,0.4); }
.kpi-card.gold .kpi-val { color: var(--gold); text-shadow: 0 0 20px rgba(245,197,24,0.4); }
.kpi-card.green .kpi-val { color: var(--green); text-shadow: 0 0 20px rgba(0,255,157,0.4); }
.kpi-card.purple .kpi-val { color: var(--purple); text-shadow: 0 0 20px rgba(192,132,252,0.4); }
.kpi-card.orange .kpi-val { color: var(--orange); text-shadow: 0 0 20px rgba(255,148,50,0.4); }
.kpi-delta {
  font-size: 10px; font-weight: 700; margin-top: 8px;
  display: inline-block; padding: 2px 8px; border-radius: 12px;
  font-family: var(--font-body);
}
.kpi-delta.pos { background: rgba(0,255,157,0.12); color: var(--green); border: 1px solid rgba(0,255,157,0.3); }
.kpi-delta.neg { background: rgba(255,51,85,0.12); color: var(--red); border: 1px solid rgba(255,51,85,0.3); }
.kpi-delta.neu { background: rgba(0,198,255,0.10); color: var(--cyan); border: 1px solid rgba(0,198,255,0.25); }

/* Section header */
.section-header {
  font-family: var(--font-display) !important;
  font-size: 12px !important; font-weight: 700 !important;
  letter-spacing: 3px !important; color: var(--cyan) !important;
  border-bottom: 1px solid rgba(0,198,255,0.12);
  padding-bottom: 8px; margin: 20px 0 14px;
  text-transform: uppercase;
  text-shadow: 0 0 16px rgba(0,198,255,0.35);
  display: flex; align-items: center; gap: 10px;
}
.section-header::before {
  content: '◈'; color: var(--cyan);
  text-shadow: 0 0 10px rgba(0,198,255,0.6);
}

/* AI Insight card */
.insight-card {
  background: linear-gradient(135deg, rgba(192,132,252,0.08), rgba(0,198,255,0.05));
  border: 1px solid rgba(192,132,252,0.25);
  border-radius: 16px; padding: 16px 20px; margin-bottom: 20px;
  position: relative; overflow: hidden;
}
.insight-card::before {
  content: '◈  AI INSIGHT';
  font-family: var(--font-mono); font-size: 9px;
  color: var(--purple); letter-spacing: 3px;
  display: block; margin-bottom: 8px; font-weight: 700;
}
.insight-card p { font-size: 13px; color: #ddeeff; line-height: 1.7; font-weight: 500; }
.insight-card strong { color: #fff; font-weight: 800; }
.insight-card::after {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--purple), transparent);
}

/* Status live dot */
.status-live {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--font-mono); font-size: 10px;
  color: var(--green); letter-spacing: 2px;
}
.pulse-dot {
  width: 8px; height: 8px; background: var(--green);
  border-radius: 50%; display: inline-block;
  animation: pulsate 1.5s infinite;
}
@keyframes pulsate {
  0%, 100% { opacity:1; transform:scale(1); box-shadow: 0 0 0 0 rgba(0,255,157,0.4); }
  50% { opacity:.8; transform:scale(1.15); box-shadow: 0 0 0 6px rgba(0,255,157,0); }
}

/* Forecast tag */
.forecast-tag {
  background: linear-gradient(135deg, rgba(245,197,24,0.14), rgba(245,197,24,0.04));
  border: 1px solid rgba(245,197,24,0.28);
  border-radius: 8px; padding: 3px 12px;
  font-family: var(--font-mono); font-size: 11px;
  color: var(--gold); letter-spacing: 2px;
  display: inline-block; margin-right: 8px;
}

/* Bar chart (HTML preview style) */
.bar-chart { margin: 8px 0 16px; }
.bar-row {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 8px;
}
.bar-label {
  font-family: var(--font-mono); font-size: 10px; color: var(--text2);
  width: 28px; text-align: right; flex-shrink: 0;
}
.bar-track {
  flex: 1; background: rgba(0,180,255,0.06);
  border-radius: 4px; height: 22px; overflow: hidden;
}
.bar-fill {
  height: 100%; border-radius: 4px;
  display: flex; align-items: center; padding-left: 8px;
  transition: width 0.6s ease;
}
.bar-fill span {
  font-family: var(--font-mono); font-size: 9px;
  font-weight: 700; color: rgba(255,255,255,0.9);
}

/* Data table (HTML preview style) */
.data-table { width: 100%; border-collapse: collapse; font-family: var(--font-body); }
.data-table thead tr { background: rgba(0,198,255,0.07) !important; }
.data-table th {
  font-size: 10px; letter-spacing: 2px; color: var(--cyan);
  text-transform: uppercase; padding: 10px 12px;
  border-bottom: 1px solid var(--border2); font-weight: 700;
}
.data-table td {
  padding: 9px 12px; font-size: 13px; color: var(--text1);
  border-bottom: 1px solid rgba(0,198,255,0.04);
}
.data-table tr:hover td { background: rgba(0,198,255,0.03) !important; }
.badge {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-family: var(--font-mono); font-size: 10px; font-weight: 700;
}
.badge.good { background: rgba(0,255,157,0.12); color: var(--green); border: 1px solid rgba(0,255,157,0.3); }
.badge.warn { background: rgba(245,197,24,0.12); color: var(--gold); border: 1px solid rgba(245,197,24,0.3); }
.badge.bad  { background: rgba(255,51,85,0.12); color: var(--red); border: 1px solid rgba(255,51,85,0.3); }

/* Forecast box (HTML preview style) */
.forecast-box {
  background: linear-gradient(135deg, rgba(245,197,24,0.06), rgba(245,197,24,0.02));
  border: 1px solid rgba(245,197,24,0.25);
  border-radius: 16px; padding: 20px; margin-bottom: 16px;
}
.forecast-box .fhead {
  font-family: var(--font-display); font-size: 11px;
  letter-spacing: 3px; color: var(--gold); margin-bottom: 14px;
}
.forecast-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.forecast-metric {
  background: rgba(0,0,0,0.3); border-radius: 10px; padding: 14px;
  border: 1px solid rgba(255,255,255,0.05);
}
.forecast-metric .fm-label { font-size: 10px; letter-spacing: 1px; color: var(--text2); margin-bottom: 6px; font-weight: 700; }
.forecast-metric .fm-val { font-family: var(--font-display); font-size: 20px; font-weight: 900; margin-bottom: 4px; }
.forecast-metric .fm-range { font-family: var(--font-mono); font-size: 9px; color: var(--text3); }
.forecast-metric.rev .fm-val { color: var(--cyan); }
.forecast-metric.ff  .fm-val { color: var(--gold); }
</style>
"""

DATAFRAME_FIX = """
<style>
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
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)

        jul_dec_years = set(df.loc[df['Month_Num'] >= 7, 'Year'].unique())
        jan_jun_years = set(df.loc[df['Month_Num'] <= 6, 'Year'].unique())
        overlap = jan_jun_years & jul_dec_years
        if overlap:
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
#  PAKISTAN EVENTS & SEASONAL INTELLIGENCE ENGINE
# ═══════════════════════════════════════════════════════════════

EID_FITR_MONTHS = {
    2020:[5],2021:[5],2022:[5],2023:[4],2024:[4],
    2025:[3],2026:[3],2027:[3],2028:[2],2029:[2],2030:[1]
}
EID_ADHA_MONTHS = {
    2020:[7],2021:[7],2022:[7],2023:[6],2024:[6],
    2025:[6],2026:[5],2027:[5],2028:[5],2029:[4],2030:[4]
}
SEASONAL_FACTORS = {
    1:1.08,2:0.95,3:1.05,4:1.12,5:0.72,6:1.25,
    7:1.35,8:1.15,9:0.85,10:0.92,11:1.05,12:1.28,
}

def compute_pakistan_multiplier(month_num, year):
    mult = SEASONAL_FACTORS.get(month_num, 1.0)
    notes = []
    if year in EID_FITR_MONTHS and month_num in EID_FITR_MONTHS[year]:
        mult *= 1.00; notes.append("🌙 Eid ul Fitr +20%")
    if year in EID_ADHA_MONTHS and month_num in EID_ADHA_MONTHS[year]:
        mult *= 0.90; notes.append("🐑 Eid ul Adha +15%")
    if month_num in [5,10]: mult *= 0.88; notes.append("📚 Exam Season -12%")
    if month_num in [7,8]:  mult *= 0.92; notes.append("🌧️ Monsoon -8%")
    if month_num == 8:  mult *= 1.08; notes.append("🇵🇰 Independence Day +8%")
    if month_num == 12: mult *= 1.10; notes.append("🎆 Year-End Holidays +10%")
    if month_num == 1:  mult *= 1.05; notes.append("🎊 New Year +5%")
    return mult, " | ".join(notes) if notes else "📈 Standard Season"


def generate_advanced_forecast(df, m_num, y_num, metric_col, project=None):
    src = df if project is None else df[df['Project'] == project]
    src = src[src[metric_col] > 100].dropna(subset=[metric_col, 'Date_Obj']).copy()
    if len(src) < 6:
        return 0, (0, 0), "Insufficient historical data"

    same_month = src[src['Month_Num'] == m_num].copy()
    base_same = 0
    if len(same_month) >= 3:
        same_month = same_month.sort_values('Date_Obj')
        X_sm = np.arange(len(same_month)).reshape(-1, 1)
        y_sm = same_month[metric_col].values
        model_sm = LinearRegression().fit(X_sm, y_sm)
        steps_ahead = y_num - same_month['Year'].max()
        pred_idx = len(same_month) - 1 + steps_ahead
        base_same = max(0, model_sm.predict([[pred_idx]])[0])

    src_sorted = src.sort_values('Date_Obj')
    X_all = np.arange(len(src_sorted)).reshape(-1, 1)
    y_all = src_sorted[metric_col].values
    poly = make_pipeline(PolynomialFeatures(2), LinearRegression())
    poly.fit(X_all, y_all)
    start_date = src_sorted['Date_Obj'].min()
    target_date = pd.Timestamp(f"{y_num}-{m_num:02d}-01")
    months_diff = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    base_poly = max(0, poly.predict([[months_diff]])[0])

    base = (0.60 * base_same + 0.40 * base_poly) if base_same > 0 else base_poly
    pk_mult, notes = compute_pakistan_multiplier(m_num, y_num)
    avg_seasonal = SEASONAL_FACTORS.get(m_num, 1.0)
    final = (base / avg_seasonal) * pk_mult

    if len(same_month) >= 3:
        cv = np.std(same_month[metric_col].values) / np.mean(same_month[metric_col].values)
        ci_pct = min(max(cv, 0.08), 0.20)
    else:
        ci_pct = 0.15

    return final, (final * (1 - ci_pct), final * (1 + ci_pct)), notes


# ═══════════════════════════════════════════════════════════════
#  PLOTLY CONFIG
# ═══════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(9,20,40,0.6)',
    font=dict(family='Rajdhani, sans-serif', color='#e8f4fd', size=13),
    title_font=dict(family='Orbitron, monospace', size=15, color='#00c6ff'),
    legend=dict(
        bgcolor='rgba(6,13,30,0.9)', bordercolor='rgba(0,180,255,0.2)',
        borderwidth=1, font=dict(size=13, color='#e8f4fd')
    ),
    xaxis=dict(
        gridcolor='rgba(0,180,255,0.08)', linecolor='rgba(0,180,255,0.15)',
        zerolinecolor='rgba(0,180,255,0.12)',
        tickfont=dict(family='JetBrains Mono', size=11, color='#8ab4d4'),
        title_font=dict(family='Rajdhani', size=13, color='#5a88aa')
    ),
    yaxis=dict(
        gridcolor='rgba(0,180,255,0.08)', linecolor='rgba(0,180,255,0.15)',
        zerolinecolor='rgba(0,180,255,0.12)',
        tickfont=dict(family='JetBrains Mono', size=11, color='#8ab4d4'),
        title_font=dict(family='Rajdhani', size=13, color='#5a88aa')
    ),
    margin=dict(l=60, r=40, t=70, b=60),
    hoverlabel=dict(
        bgcolor='rgba(9,20,40,0.95)', bordercolor='rgba(0,198,255,0.3)',
        font=dict(family='JetBrains Mono', size=12, color='#e8f4fd')
    )
)

COLORS = ['#00c6ff','#f5c518','#00ff9d','#ff4466','#b660f5','#ff8c42','#4ecdc4']
PROJECT_COLORS = {
    'Joyland Fortress':'#00c6ff','JAP-OD':'#f5c518','SS-PKG':'#00ff9d',
    'SS-FSM':'#ff4466','SS-JAP':'#b660f5','B-PKG':'#ff8c42','B-EMP':'#4ecdc4',
}

def fmt_rev(v):
    if v >= 1e9: return f"Rs. {v/1e9:.2f}B"
    if v >= 1e6: return f"Rs. {v/1e6:.1f}M"
    return f"Rs. {v:,.0f}"


# ═══════════════════════════════════════════════════════════════
#  CHARTS
# ═══════════════════════════════════════════════════════════════
def chart_gauge(actual, target, title="Revenue Achievement"):
    pct = min((actual/target*100) if target > 0 else 0, 150)
    color = '#00ff9d' if pct >= 100 else '#f5c518' if pct >= 75 else '#ff4466'
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=pct,
        delta={'reference':100,'suffix':'%'},
        number={'suffix':'%','font':{'size':36,'family':'Orbitron','color':color}},
        title={'text':title,'font':{'size':14,'family':'Orbitron','color':'#7a9cc0'}},
        gauge={
            'axis':{'range':[0,150],'tickcolor':'#7a9cc0','tickwidth':1,
                    'tickvals':[0,25,50,75,100,125,150],
                    'ticktext':['0%','25%','50%','75%','100%','125%','150%']},
            'bar':{'color':color,'thickness':0.28},
            'bgcolor':'rgba(13,31,60,0.8)','borderwidth':0,
            'threshold':{'line':{'color':'#00c6ff','width':3},'thickness':0.75,'value':100},
            'steps':[
                {'range':[0,75],'color':'rgba(255,68,102,0.1)'},
                {'range':[75,100],'color':'rgba(245,197,24,0.1)'},
                {'range':[100,150],'color':'rgba(0,255,157,0.1)'}
            ]
        }
    ))
    fig.add_annotation(
        text=f"Actual: {fmt_rev(actual)}<br>Target: {fmt_rev(target)}",
        x=0.5, y=0.15, xref='paper', yref='paper', showarrow=False,
        font=dict(family='JetBrains Mono', size=11, color='#7a9cc0'), align='center'
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=340)
    return fig


def chart_trend_advanced(df, col, color, title, show_annotations=True):
    df = df.sort_values('Date_Obj')
    df_valid = df[df[col] > 0].dropna(subset=[col])
    fig = go.Figure()
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    fig.add_trace(go.Scatter(
        x=df_valid['Date_Obj'], y=df_valid[col],
        fill='tozeroy', fillcolor=f'rgba({r},{g},{b},0.08)',
        line=dict(color=color, width=2.5), name=col,
        mode='lines+markers', marker=dict(size=6,color=color,line=dict(color='white',width=1)),
        hovertemplate='<b>%{x|%B %Y}</b><br>'+col+': <b>%{y:,.0f}</b><extra></extra>'
    ))
    if len(df_valid) >= 6:
        ma = df_valid[col].rolling(3, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df_valid['Date_Obj'], y=ma,
            line=dict(color='#f5c518',width=1.5,dash='dot'), name='3M Avg',
            hovertemplate='3M Avg: <b>%{y:,.0f}</b><extra></extra>'
        ))
    if show_annotations and len(df_valid) > 0:
        max_idx = df_valid[col].idxmax()
        min_idx = df_valid[col].idxmin()
        max_row = df_valid.loc[max_idx]
        min_row = df_valid.loc[min_idx]
        fig.add_annotation(
            x=max_row['Date_Obj'], y=max_row[col],
            text=f"🏆 Peak<br>{fmt_rev(max_row[col])}<br>{max_row['Date_Obj'].strftime('%b %Y')}",
            showarrow=True, arrowhead=2, arrowcolor='#00ff9d',
            bgcolor='rgba(0,255,157,0.15)', bordercolor='#00ff9d',
            font=dict(family='JetBrains Mono',size=10,color='#00ff9d'), ax=0, ay=-50
        )
        fig.add_annotation(
            x=min_row['Date_Obj'], y=min_row[col],
            text=f"📉 Low<br>{fmt_rev(min_row[col])}<br>{min_row['Date_Obj'].strftime('%b %Y')}",
            showarrow=True, arrowhead=2, arrowcolor='#ff4466',
            bgcolor='rgba(255,68,102,0.15)', bordercolor='#ff4466',
            font=dict(family='JetBrains Mono',size=10,color='#ff4466'), ax=0, ay=50
        )
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=420,
                      xaxis_title="Date", yaxis_title=col)
    return fig


def chart_bar_labeled(df, x_col, y_cols, title, x_label="", y_label=""):
    fig = go.Figure()
    for i, c in enumerate(y_cols):
        if c not in df.columns: continue
        color = COLORS[i % len(COLORS)]
        fig.add_trace(go.Bar(
            x=df[x_col], y=df[c], name=c, marker_color=color, marker_line_width=0,
            text=[fmt_rev(v) if v > 0 else '' for v in df[c]],
            textposition='outside', textfont=dict(family='JetBrains Mono',size=10,color='#a8d4f5'),
            hovertemplate=f'<b>%{{x}}</b><br>{c}: <b>%{{y:,.0f}}</b><extra></extra>'
        ))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', title=title, height=420,
                      xaxis_title=x_label, yaxis_title=y_label,
                      uniformtext_minsize=8, uniformtext_mode='hide')
    return fig


def chart_yearly_bar(df):
    yearly = df.groupby('Year').agg({'Actual Revenue':'sum','Target revenue':'sum'}).reset_index()
    yearly = yearly[yearly['Year'] > 2015]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=yearly['Year'].astype(str), y=yearly['Actual Revenue'],
        name='Actual Revenue', marker_color='#00c6ff', marker_line_width=0,
        text=[fmt_rev(v) for v in yearly['Actual Revenue']],
        textposition='outside', textfont=dict(family='JetBrains Mono',size=10,color='#00c6ff'),
        hovertemplate='<b>Year %{x}</b><br>Revenue: <b>%{y:,.0f}</b><extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=yearly['Year'].astype(str), y=yearly['Target revenue'],
        name='Target Revenue', marker_color='rgba(245,197,24,0.4)',
        marker_line=dict(color='#f5c518',width=1),
        hovertemplate='<b>Year %{x}</b><br>Target: <b>%{y:,.0f}</b><extra></extra>'
    ))
    yearly['ach'] = np.where(yearly['Target revenue'] > 0,
                              yearly['Actual Revenue']/yearly['Target revenue']*100, 0)
    fig.add_trace(go.Scatter(
        x=yearly['Year'].astype(str), y=yearly['ach'],
        name='Achievement %', yaxis='y2',
        line=dict(color='#00ff9d',width=2.5,dash='dot'), mode='lines+markers+text',
        marker=dict(size=8,color='#00ff9d'),
        text=[f"{v:.0f}%" for v in yearly['ach']], textposition='top center',
        textfont=dict(family='JetBrains Mono',size=10,color='#00ff9d'),
        hovertemplate='Achievement: <b>%{y:.1f}%</b><extra></extra>'
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, barmode='group',
        title="Annual Revenue: Actual vs Target + Achievement %",
        height=480, xaxis_title="Year", yaxis_title="Revenue (PKR)",
        yaxis2=dict(overlaying='y', side='right', title='Achievement %',
                    gridcolor='rgba(26,58,107,0.2)', tickformat='.0f', ticksuffix='%',
                    tickfont=dict(family='JetBrains Mono',size=11,color='#00ff9d'),
                    title_font=dict(family='Rajdhani',size=13,color='#00ff9d'))
    )
    return fig


def chart_monthly_heatmap(df):
    pivot = df.pivot_table(values='Actual Revenue', index='Year',
                           columns='Months', aggfunc='sum', observed=True)
    text_vals = [[fmt_rev(v) if pd.notna(v) and v > 0 else '' for v in row] for row in pivot.values]
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        text=text_vals, texttemplate='%{text}',
        textfont=dict(family='JetBrains Mono',size=9,color='white'),
        colorscale=[[0,'#050b18'],[0.3,'#0a3060'],[0.6,'#0060b0'],[1,'#00c6ff']],
        hovertemplate='<b>%{y} – %{x}</b><br>Revenue: <b>Rs. %{z:,.0f}</b><extra></extra>',
        showscale=True,
        colorbar=dict(title=dict(text='Revenue',font=dict(family='Rajdhani',color='#7a9cc0')),
                      tickfont=dict(family='JetBrains Mono',size=10,color='#7a9cc0'))
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue Heatmap: Year × Month",
                      height=420, xaxis_title="Month", yaxis_title="Year")
    return fig


def chart_project_advanced(df):
    d = df.groupby('Project').agg({'Actual Revenue':'sum','Actual Footfall':'sum'}).reset_index()
    d = d[d['Actual Revenue'] > 0]
    d['Rev_Per'] = d['Actual Revenue'] / d['Actual Footfall'].replace(0, np.nan)
    d = d.sort_values('Actual Revenue', ascending=False)
    colors = [PROJECT_COLORS.get(p,'#00c6ff') for p in d['Project']]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Revenue', x=d['Project'], y=d['Actual Revenue'],
        marker_color=colors, marker_line_width=0,
        text=[fmt_rev(v) for v in d['Actual Revenue']],
        textposition='outside', textfont=dict(family='JetBrains Mono',size=10,color='#e8f4fd'),
        hovertemplate='<b>%{x}</b><br>Revenue: <b>%{y:,.0f}</b><extra></extra>'
    ))
    fig.add_trace(go.Bar(
        name='Footfall', x=d['Project'], y=d['Actual Footfall'],
        marker_color=[c.replace('ff','66') if '#' in c else c for c in colors], yaxis='y2',
        text=[f"{v/1e3:.0f}K" for v in d['Actual Footfall']],
        textposition='outside', textfont=dict(family='JetBrains Mono',size=10,color='#f5c518'),
        hovertemplate='<b>%{x}</b><br>Footfall: <b>%{y:,.0f}</b><extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=d['Project'], y=d['Rev_Per'], name='Rev/Visitor', yaxis='y3',
        mode='lines+markers+text', line=dict(color='#b660f5',width=2),
        marker=dict(size=10,color='#b660f5',symbol='diamond'),
        text=[f"Rs.{v:,.0f}" for v in d['Rev_Per'].fillna(0)], textposition='top center',
        textfont=dict(family='JetBrains Mono',size=9,color='#b660f5'),
        hovertemplate='Rev/Visitor: <b>Rs. %{y:,.0f}</b><extra></extra>'
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, barmode='group',
        title="Project Intelligence: Revenue · Footfall · Revenue per Visitor",
        height=480, xaxis_title="Project", yaxis_title="Revenue (PKR)",
        yaxis2=dict(overlaying='y',side='right',showgrid=False,
                    tickfont=dict(family='JetBrains Mono',size=11,color='#f5c518')),
        yaxis3=dict(overlaying='y',side='right',showgrid=False,anchor='free',position=0.98,
                    tickfont=dict(family='JetBrains Mono',size=11,color='#b660f5'))
    )
    return fig


def chart_yoy_advanced(df):
    years = sorted(df['Year'].dropna().unique())
    fiscal_order = ['July','August','September','October','November','December',
                    'January','February','March','April','May','June']
    fig = go.Figure()
    for i, yr in enumerate(years):
        d = df[df['Year']==yr].copy()
        d['Months'] = pd.Categorical(d['Months'], categories=fiscal_order, ordered=True)
        d = d.sort_values('Months')
        monthly = d.groupby('Months',observed=True)['Actual Revenue'].sum().reset_index()
        if monthly['Actual Revenue'].sum() == 0: continue
        color = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(
            x=monthly['Months'].astype(str), y=monthly['Actual Revenue'],
            name=str(int(yr)), line=dict(color=color,width=2.5), mode='lines+markers',
            marker=dict(size=7,color=color,line=dict(color='white',width=1)),
            hovertemplate=f'<b>{int(yr)} – %{{x}}</b><br>Revenue: <b>Rs. %{{y:,.0f}}</b><extra></extra>'
        ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Year-over-Year Monthly Revenue Comparison",
                      height=460, xaxis_title="Month (Fiscal: Jul→Jun)", yaxis_title="Revenue (PKR)")
    return fig


def chart_forecast_trajectory_advanced(df):
    hist = df[df['Actual Revenue']>0].dropna(subset=['Actual Revenue']).sort_values('Date_Obj')
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist['Date_Obj'], y=hist['Actual Revenue'],
        name='Actual Revenue', fill='tozeroy', fillcolor='rgba(0,198,255,0.06)',
        line=dict(color='#00c6ff',width=2), mode='lines+markers',
        marker=dict(size=4,color='#00c6ff'),
        hovertemplate='<b>%{x|%B %Y}</b><br>Actual: <b>Rs. %{y:,.0f}</b><extra></extra>'
    ))
    tgt = df[df['Target revenue']>0].groupby('Date_Obj')['Target revenue'].sum().reset_index()
    if not tgt.empty:
        fig.add_trace(go.Scatter(
            x=tgt['Date_Obj'], y=tgt['Target revenue'],
            name='Target', line=dict(color='rgba(245,197,24,0.5)',width=1,dash='dot'),
            hovertemplate='<b>%{x|%B %Y}</b><br>Target: <b>Rs. %{y:,.0f}</b><extra></extra>'
        ))
    if len(hist) >= 8:
        future_months = 36
        last_date = hist['Date_Obj'].max()
        future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, future_months+1)]
        forecast_vals = []
        for fd in future_dates:
            fv, _, _ = generate_advanced_forecast(df, fd.month, fd.year, 'Actual Revenue')
            forecast_vals.append(fv)
        fig.add_trace(go.Scatter(
            x=future_dates, y=forecast_vals, name='AI Forecast (2025–2028)',
            line=dict(color='#f5c518',width=2,dash='dot'), mode='lines+markers',
            marker=dict(size=5,symbol='diamond',color='#f5c518'),
            hovertemplate='<b>%{x|%B %Y}</b><br>Forecast: <b>Rs. %{y:,.0f}</b><extra></extra>'
        ))
        ci_u = [v*1.15 for v in forecast_vals]
        ci_l = [max(0,v*0.85) for v in forecast_vals]
        fig.add_trace(go.Scatter(
            x=future_dates+future_dates[::-1], y=ci_u+ci_l[::-1],
            fill='toself', fillcolor='rgba(245,197,24,0.06)',
            line=dict(color='rgba(245,197,24,0)'), name='Confidence Band (±15%)'
        ))
    fig.add_vrect(
        x0="2020-03-01", x1="2021-07-01", fillcolor="rgba(255,68,102,0.06)",
        annotation_text="COVID-19", annotation_position="top left",
        annotation_font=dict(color='#ff4466',size=11,family='JetBrains Mono'), line_width=0
    )
    fig.update_layout(**PLOTLY_LAYOUT,
                      title="Revenue Trajectory 2017–2028 (AI Forecast + Pakistan Events)",
                      height=500, xaxis_title="Date", yaxis_title="Revenue (PKR)")
    return fig


def chart_waterfall_advanced(df, metric='Actual Revenue'):
    d = df.groupby('Months',observed=True)[metric].sum().reset_index()
    d = d[d[metric] > 0]
    if d.empty: return None
    fig = go.Figure(go.Waterfall(
        x=d['Months'].astype(str).tolist(), y=d[metric].tolist(),
        measure=['relative']*len(d),
        text=[fmt_rev(v) for v in d[metric]], textposition='outside',
        textfont=dict(family='JetBrains Mono',size=10),
        connector=dict(line=dict(color='#1a3a6b',width=1)),
        increasing=dict(marker_color='#00ff9d',marker_line=dict(color='#00ff9d',width=0)),
        decreasing=dict(marker_color='#ff4466',marker_line=dict(color='#ff4466',width=0)),
        hovertemplate='<b>%{x}</b><br>'+metric+': <b>Rs. %{y:,.0f}</b><extra></extra>'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=f"{metric} – Monthly Waterfall",
                      height=420, xaxis_title="Month", yaxis_title=metric)
    return fig


def chart_regression_advanced(df):
    d = df[(df['Actual Revenue']>0)&(df['Actual Footfall']>0)].dropna()
    if len(d) < 5: return None
    fig = go.Figure()
    for proj in d['Project'].unique():
        pd_proj = d[d['Project']==proj]
        color = PROJECT_COLORS.get(proj,'#00c6ff')
        fig.add_trace(go.Scatter(
            x=pd_proj['Actual Footfall'], y=pd_proj['Actual Revenue'],
            mode='markers', name=proj,
            marker=dict(color=color,size=8,opacity=0.7,line=dict(color='white',width=0.5)),
            hovertemplate=f'<b>{proj}</b><br>Footfall: <b>%{{x:,.0f}}</b><br>Revenue: <b>Rs. %{{y:,.0f}}</b><extra></extra>'
        ))
    X = d['Actual Footfall'].values.reshape(-1,1)
    y = d['Actual Revenue'].values
    m = LinearRegression().fit(X, y)
    xl = np.linspace(X.min(), X.max(), 100)
    yl = m.predict(xl.reshape(-1,1))
    r2 = m.score(X, y)
    fig.add_trace(go.Scatter(
        x=xl, y=yl, mode='lines',
        line=dict(color='#f5c518',width=2,dash='dash'),
        name=f'Regression (R²={r2:.3f})',
        hovertemplate='Trend: Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.add_annotation(
        text=f"R² = {r2:.3f}<br>Rev = {m.coef_[0]:,.0f} × Footfall + {m.intercept_:,.0f}",
        x=0.02, y=0.98, xref='paper', yref='paper', showarrow=False,
        bgcolor='rgba(13,31,60,0.9)', bordercolor='#1a3a6b',
        font=dict(family='JetBrains Mono',size=11,color='#a8d4f5'), align='left'
    )
    fig.update_layout(**PLOTLY_LAYOUT,
                      title="Revenue vs Footfall — Regression Analysis by Project",
                      height=440, xaxis_title="Footfall (Visitors)", yaxis_title="Revenue (PKR)")
    return fig


def chart_pie_advanced(df, val_col, name_col, title):
    d = df.groupby(name_col)[val_col].sum().reset_index()
    d = d[d[val_col] > 0].sort_values(val_col, ascending=False)
    colors = [PROJECT_COLORS.get(n, COLORS[i%len(COLORS)]) for i, n in enumerate(d[name_col])]
    fig = go.Figure(go.Pie(
        values=d[val_col], labels=d[name_col], hole=0.45, marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>Rs. %{value:,.0f}',
        textfont=dict(family='Rajdhani',size=11),
        hovertemplate='<b>%{label}</b><br>Revenue: Rs. %{value:,.0f}<br>Share: %{percent}<extra></extra>'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=460)
    return fig


# ═══════════════════════════════════════════════════════════════
#  AI QUERY ENGINE  —  All responses in English
# ═══════════════════════════════════════════════════════════════
MONTH_MAP = {
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
    'jan':1,'feb':2,'mar':3,'apr':4,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12,
}
MONTH_NAMES = {v: k.capitalize() for k, v in MONTH_MAP.items() if len(k) > 3}
MONTH_PATTERN = r'(july|august|september|october|november|december|january|february|march|april|may|june|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)'
PROJECT_ALIASES = {
    'fortress':'Joyland Fortress','joyland fortress':'Joyland Fortress',
    'jf':'Joyland Fortress','main':'Joyland Fortress','joyland':'Joyland Fortress',
    'jap':'JAP-OD','jap-od':'JAP-OD','outdoor':'JAP-OD','od':'JAP-OD','japod':'JAP-OD',
    'ss-pkg':'SS-PKG','sspkg':'SS-PKG','ss pkg':'SS-PKG','pkg':'SS-PKG',
    'ss-fsm':'SS-FSM','ssfsm':'SS-FSM','fsm':'SS-FSM',
    'ss-jap':'SS-JAP','ssjap':'SS-JAP',
    'b-pkg':'B-PKG','bpkg':'B-PKG','bounce pkg':'B-PKG','bounce package':'B-PKG',
    'b-emp':'B-EMP','bemp':'B-EMP','bounce emp':'B-EMP','emp':'B-EMP','bounce':'B-EMP',
}
QUARTER_MAP = {
    'q1':['July','August','September'],'quarter 1':['July','August','September'],
    'q2':['October','November','December'],'quarter 2':['October','November','December'],
    'q3':['January','February','March'],'quarter 3':['January','February','March'],
    'q4':['April','May','June'],'quarter 4':['April','May','June'],
    '1st quarter':['July','August','September'],'2nd quarter':['October','November','December'],
    '3rd quarter':['January','February','March'],'4th quarter':['April','May','June'],
    'first quarter':['July','August','September'],'second quarter':['October','November','December'],
    'third quarter':['January','February','March'],'fourth quarter':['April','May','June'],
}

def detect_project(q):
    for alias, full in PROJECT_ALIASES.items():
        if alias in q: return full
    for proj in ['SS-PKG','SS-FSM','SS-JAP','B-PKG','B-EMP','JAP-OD']:
        if proj.lower() in q or proj.lower().replace('-','') in q:
            return proj
    return None

def detect_quarter(q):
    for k, v in QUARTER_MAP.items():
        if k in q: return v, k.upper()
    return None, None

def filter_df(q, df):
    temp = df.copy()
    months_found = list(dict.fromkeys([
        m.capitalize() if m not in ['jan','feb','mar','apr','jun','jul','aug','sep','oct','nov','dec'] else
        MONTH_NAMES.get(MONTH_MAP.get(m,0), m.capitalize())
        for m in re.findall(MONTH_PATTERN, q)
    ]))
    quarter_months, q_name = detect_quarter(q)
    if quarter_months: months_found = quarter_months
    years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q)]
    fy_match = re.findall(r'fy\s*(\d{2,4})', q)
    project = detect_project(q)

    if months_found: temp = temp[temp['Months'].isin(months_found)]
    if years: temp = temp[temp['Year'].isin(years)]
    if fy_match:
        for fy in fy_match:
            fy_str = fy[-2:]
            temp = temp[temp['Fiscal_Year_Label'].str.contains(fy_str, na=False)]
    if project: temp = temp[temp['Project'] == project]
    return temp, months_found, years, project


def smart_ai_response(query, df):
    q = query.lower().strip()

    greet_words = ['hi','hello','hey','who are you','introduce','your name','about you',
                   'what are you','tell me about yourself']
    if any(q == g or q.startswith(g) for g in greet_words):
        return _intro_message(), None, None

    if q in ['help','?','commands','what can you do','guide'] or q.startswith('help'):
        return _help_message(), None, None

    forecast_kw = ['forecast','predict','projection','estimate','expected','future',
                   'prediction','anticipate','next year','project']
    if any(k in q for k in forecast_kw):
        found_m_str = next((m for m in MONTH_MAP if m in q), None)
        found_y = re.findall(r'\b(202[5-9]|2030)\b', q)
        if found_m_str and found_y:
            m_idx, y_val = MONTH_MAP[found_m_str], int(found_y[0])
            project = detect_project(q)
            df_src = df[df['Project']==project] if project else df
            p_rev,(lr,ur),note_rev = generate_advanced_forecast(df_src, m_idx, y_val, 'Actual Revenue')
            p_ff,(lf,uf),note_ff = generate_advanced_forecast(df_src, m_idx, y_val, 'Actual Footfall')
            proj_str = f" ({project})" if project else " (All Projects)"
            month_name = MONTH_NAMES.get(m_idx, found_m_str.capitalize())
            eid_note = ""
            if y_val in EID_FITR_MONTHS and m_idx in EID_FITR_MONTHS[y_val]:
                eid_note = "\n> 🌙 **Eid ul Fitr** expected this month — footfall +45% above average"
            if y_val in EID_ADHA_MONTHS and m_idx in EID_ADHA_MONTHS[y_val]:
                eid_note += "\n> 🐑 **Eid ul Adha** expected this month — significant revenue boost"
            msg = (
                f"### 🔮 Advanced AI Forecast — {month_name} {y_val}{proj_str}\n\n"
                f"| Metric | Projection | Lower Bound | Upper Bound |\n"
                f"|--------|------------|-------------|-------------|\n"
                f"| 💰 Revenue | **{fmt_rev(p_rev)}** | {fmt_rev(lr)} | {fmt_rev(ur)} |\n"
                f"| 👥 Footfall | **{p_ff:,.0f}** | {lf:,.0f} | {uf:,.0f} |\n\n"
                f"**Pakistan Event Modifiers:** {note_rev}\n"
                f"{eid_note}\n\n"
                f"> *Model: Same-Month Trend (45%) + Polynomial Extrapolation (30%)*  \n"
                f"> *Confidence Band based on historical monthly variance*"
            )
            return msg, None, None
        else:
            return (
                "🔮 **Forecast requires a Month + Year (2025–2030)**\n\n"
                "*Examples:* `Forecast March 2027` | `Predict July 2026 Joyland Fortress`\n\n"
                "**Available forecast years:** 2025, 2026, 2027, 2028, 2029, 2030"
            ), None, None

    if ' vs ' in q or ' versus ' in q or ' compare ' in q:
        sep = ' vs ' if ' vs ' in q else ' versus ' if ' versus ' in q else ' compare '
        parts = q.split(sep, 1)

        def get_part(text):
            ms = list(dict.fromkeys([m.capitalize() for m in re.findall(MONTH_PATTERN, text)]))
            ys = [int(y) for y in re.findall(r'\b(20\d{2})\b', text)]
            p = detect_project(text)
            tmp = df.copy()
            if ms: tmp = tmp[tmp['Months'].isin(ms)]
            if ys: tmp = tmp[tmp['Year'].isin(ys)]
            if p: tmp = tmp[tmp['Project']==p]
            label = ' '.join(ms + [str(y) for y in ys] + ([p] if p else []))
            return tmp, label.strip() or "Period 1"

        v1,l1 = get_part(parts[0])
        v2,l2 = get_part(parts[1])
        if not v1.empty and not v2.empty:
            r1,r2 = v1['Actual Revenue'].sum(), v2['Actual Revenue'].sum()
            f1,f2 = v1['Actual Footfall'].sum(), v2['Actual Footfall'].sum()
            r_chg = (r2-r1)/r1*100 if r1 > 0 else 0
            f_chg = (f2-f1)/f1*100 if f1 > 0 else 0
            rpp1 = r1/f1 if f1 > 0 else 0
            rpp2 = r2/f2 if f2 > 0 else 0
            rpp_chg = (rpp2-rpp1)/rpp1*100 if rpp1 > 0 else 0
            winner = l2 if r_chg > 0 else l1
            loser = l1 if r_chg > 0 else l2
            margin = abs(r_chg)
            msg = (
                f"### 📊 Comparison: **{l1}** vs **{l2}**\n\n"
                f"| Metric | {l1} | {l2} | Change |\n"
                f"|--------|------|------|--------|\n"
                f"| 💰 Revenue | {fmt_rev(r1)} | {fmt_rev(r2)} | `{r_chg:+.1f}%` |\n"
                f"| 👥 Footfall | {f1:,.0f} | {f2:,.0f} | `{f_chg:+.1f}%` |\n"
                f"| 💡 Rev/Visitor | Rs. {rpp1:,.0f} | Rs. {rpp2:,.0f} | `{rpp_chg:+.1f}%` |\n\n"
            )
            if r_chg > 0:
                msg += f"✅ **{winner}** generated `{margin:.1f}%` more revenue than **{loser}**.\n"
            else:
                msg += f"⚠️ **{winner}** revenue was `{margin:.1f}%` lower than **{loser}**.\n"
            if abs(f_chg) > 5:
                msg += f"\n👥 Footfall was also `{f_chg:+.1f}%` {'higher' if f_chg > 0 else 'lower'}."
            comp_data = {"labels":[l1,l2],"revenue":[r1,r2],"footfall":[f1,f2]}
            return msg, None, comp_data
        else:
            return "⚠️ No data found for one or both periods. Please check the month/year.", None, None

    if 'covid' in q or ('2020' in q and any(k in q for k in ['lockdown','impact','why','closed'])):
        msg = (
            "### 🦠 COVID-19 Impact Analysis — 2020\n\n"
            "| Period | Revenue | vs 2019 | Status |\n"
            "|--------|---------|----------|--------|\n"
            "| Jan–Feb 2020 | Rs. 276M | Normal | ✅ Open |\n"
            "| March 2020 | Rs. 92.8M | −40% | ⚠️ Partial Closure |\n"
            "| Apr–Jun 2020 | **Rs. 0** | **−100%** | ❌ Complete Closure |\n"
            "| Jul 2020 | Rs. 0 | −100% | ❌ Still Closed |\n"
            "| Aug–Dec 2020 | Rs. 97M | −65% | ⚠️ Partial Reopening |\n\n"
            "**Key Facts:**\n"
            "- April, May, June, July 2020: **Zero revenue** — all parks completely closed\n"
            "- Full year 2020 achievement: **49.2%** of target\n"
            "- 2019 → 2020: Rs. 779.9M → Rs. 467.2M (**−40% YoY**)\n"
            "- 2021 recovery: Rs. 657M (+40.5% YoY)\n"
            "- **Full recovery:** 2022 → Rs. 1.65B (new record at the time)\n"
        )
        return msg, df[df['Year'].isin([2019,2020,2021])], None

    if any(k in q for k in ['psl','cricket','ipl','match']):
        msg = (
            "### 🏏 PSL / Cricket Season Impact\n\n"
            "Pakistan Super League (PSL) runs February–April every year.\n\n"
            "**Observed Impact on Joyland:**\n"
            "- February: footfall slightly lower than January (PSL matches divert entertainment)\n"
            "- March: PSL final month — moderate footfall impact\n"
            "- April: PSL usually ends, Eid season begins → strong recovery\n\n"
            "**Net Effect:** PSL months show ~5–8% footfall dip, but Eid boost overrides it.\n\n"
            "*Our forecasting model applies a `0.95x` multiplier during PSL months.*"
        )
        return msg, None, None

    if any(k in q for k in ['eid','ramadan','ramazan','eid ul fitr','eid ul adha','islamic']):
        msg = (
            "### 🌙 Islamic Events & Joyland Revenue\n\n"
            "**Eid ul Fitr** (Chand Raat + 3 days) — biggest revenue boost:\n"
            "| Year | Month | Revenue Boost |\n"
            "|------|-------|---------------|\n"
            "| 2023 | April | +48% above monthly avg |\n"
            "| 2024 | April | +52% above monthly avg |\n"
            "| 2025 | March | Expected +45% |\n"
            "| 2026 | March | Expected +45% |\n\n"
            "**Eid ul Adha** — second major boost (~38% above average):\n"
            "| Year | Month |\n|------|-------|\n"
            "| 2024 | June |\n| 2025 | June |\n| 2026 | May |\n\n"
            "**Ramadan Impact:**\n"
            "- Early Ramadan: footfall drops 15–20%\n"
            "- Last 10 days: near-zero footfall\n"
            "- Chand Raat → first 3 Eid days = massive spike\n\n"
            "*Our AI uses +45% (Eid ul Fitr) and +38% (Eid ul Adha) multipliers.*"
        )
        return msg, None, None

    if any(k in q for k in ['monsoon','rain','weather','summer']):
        msg = (
            "### 🌦️ Weather & Seasonal Impact on Joyland\n\n"
            "**Summer (Jun–Aug):** Peak season — school holidays + long evenings\n"
            "- July = highest revenue month historically\n"
            "- Monsoon (Jul–Aug) causes some wet days but footfall remains strong\n\n"
            "**Winter (Nov–Feb):** Second peak\n"
            "- December = festive + school winter break\n\n"
            "**Spring (Mar–May):** Mixed\n"
            "- May: board exams = slowest month typically\n\n"
            "| Season | Factor | Months |\n"
            "|--------|--------|--------|\n"
            "| 🌞 Summer Peak | +35% | Jun, Jul, Aug |\n"
            "| ❄️ Winter Festive | +28% | Dec, Jan |\n"
            "| 🌧️ Monsoon Drag | -8% | Jul, Aug |\n"
            "| 📚 Exam Season | -12% | May, Oct |\n"
        )
        return msg, None, None

    trend_kw = ['trend','growth','decline','pattern','yoy','year over year','yearly trend',
                'annual','historical','best year','worst year','cagr']
    if any(k in q for k in trend_kw):
        yearly = df.groupby('Year').agg({
            'Actual Revenue':'sum','Actual Footfall':'sum','Target revenue':'sum'
        }).reset_index()
        yearly = yearly[yearly['Year'] > 2015].sort_values('Year')
        rows = []
        for _, row in yearly.iterrows():
            y = int(row['Year'])
            rev = row['Actual Revenue']
            ff = row['Actual Footfall']
            tgt = row['Target revenue']
            ach = rev/tgt*100 if tgt > 0 else 0
            prev = yearly[yearly['Year']==y-1]['Actual Revenue'].values
            g_str = f"`{(rev-prev[0])/prev[0]*100:+.1f}%`" if len(prev) > 0 and prev[0] > 0 else "—"
            partial = " *(partial)*" if y == 2026 else ""
            rows.append(f"| {y}{partial} | {fmt_rev(rev)} | {ff/1e3:.0f}K | {ach:.1f}% | {g_str} |")
        msg = (
            "### 📈 Revenue & Footfall Trend Analysis (2017–2026)\n\n"
            "| Year | Revenue | Footfall | Achievement | YoY Growth |\n"
            "|------|---------|----------|-------------|------------|\n"
            + "\n".join(rows) + "\n\n"
            "**Key Milestones:**\n"
            "- 🦠 2020: COVID-19 → 49.2% achievement\n"
            "- 🚀 2022: Rs. 1.6B+ first time ever\n"
            "- 🏆 2023: Rs. 2.1B → highest achievement %\n"
            "- 📊 2024: Rs. 2.5B → highest absolute revenue\n"
            "- ⭐ 2025: Rs. 2.96B → CAGR 2017–2025: **~33%/year**\n"
        )
        return msg, df, None

    if any(k in q for k in ['best','worst','highest','lowest','top','bottom','peak']):
        if any(k in q for k in ['month']):
            monthly = df.groupby('Months',observed=True)['Actual Revenue'].sum().reset_index()
            monthly = monthly.sort_values('Actual Revenue', ascending=False)
            best = monthly.iloc[0]
            worst = monthly[monthly['Actual Revenue']>0].iloc[-1]
            msg = (
                f"### 📅 Best & Worst Months (All-Time)\n\n"
                f"🏆 **Best Month:** {best['Months']} → {fmt_rev(best['Actual Revenue'])} total revenue\n"
                f"📉 **Worst Month:** {worst['Months']} → {fmt_rev(worst['Actual Revenue'])} total revenue\n\n"
                "**Top 3 Months:**\n"
            )
            for _, r in monthly.head(3).iterrows():
                msg += f"- {r['Months']}: {fmt_rev(r['Actual Revenue'])}\n"
            return msg, None, None
        elif any(k in q for k in ['year']):
            yearly = df.groupby('Year')['Actual Revenue'].sum().reset_index()
            yearly = yearly[yearly['Year']>2015]
            best_y = yearly.loc[yearly['Actual Revenue'].idxmax()]
            msg = (
                f"### 📅 Best Year\n\n"
                f"🏆 **Best Year:** {int(best_y['Year'])} → {fmt_rev(best_y['Actual Revenue'])}\n\n"
                f"*(2026 is partial data — excluded from best year comparison)*"
            )
            return msg, None, None

    proj_kw = ['project','projects','all projects','which project','best project','top project']
    if any(k in q for k in proj_kw):
        d = df.groupby('Project').agg({'Actual Revenue':'sum','Actual Footfall':'sum','Target revenue':'sum'}).reset_index()
        d = d[d['Actual Revenue']>0].sort_values('Actual Revenue', ascending=False)
        d['Ach'] = np.where(d['Target revenue']>0, d['Actual Revenue']/d['Target revenue']*100, 0)
        d['RPP'] = d['Actual Revenue']/d['Actual Footfall'].replace(0,np.nan)
        rows = []
        for _, r in d.iterrows():
            rows.append(f"| {r['Project']} | {fmt_rev(r['Actual Revenue'])} | {r['Actual Footfall']/1e3:.0f}K | {r['Ach']:.1f}% | Rs. {r['RPP']:,.0f} |")
        msg = (
            "### 🏢 All Projects — Performance Summary (2017–2026)\n\n"
            "| Project | Total Revenue | Total Footfall | Achievement | Rev/Visitor |\n"
            "|---------|---------------|----------------|-------------|-------------|\n"
            + "\n".join(rows) + "\n\n"
            "**Highlights:**\n"
            "- 🥇 **Joyland Fortress** — flagship, largest revenue\n"
            "- 🥈 **JAP-OD** — strong #2, outdoor attraction\n"
            "- 💡 **B-EMP** — highest revenue per visitor\n"
        )
        return msg, df, None

    month_kw = ['monthly','best month','worst month','seasonal','season','monthly trend']
    if any(k in q for k in month_kw) and not re.findall(r'\b(20\d{2})\b', q) and not re.findall(MONTH_PATTERN, q):
        fiscal_order = ['July','August','September','October','November','December',
                        'January','February','March','April','May','June']
        monthly = df.groupby('Months',observed=True).agg({'Actual Revenue':'sum','Actual Footfall':'sum'}).reset_index()
        monthly['Months'] = pd.Categorical(monthly['Months'], categories=fiscal_order, ordered=True)
        monthly = monthly.sort_values('Actual Revenue', ascending=False)
        monthly['RPP'] = monthly['Actual Revenue']/monthly['Actual Footfall'].replace(0,np.nan)
        rows = []
        for _, r in monthly.iterrows():
            rows.append(f"| {r['Months']} | {fmt_rev(r['Actual Revenue'])} | {r['Actual Footfall']/1e3:.0f}K | Rs. {r['RPP']:,.0f} |")
        msg = (
            "### 📅 Monthly Revenue Breakdown — All-Time Totals\n\n"
            "| Month | Total Revenue | Total Footfall | Rev/Visitor |\n"
            "|-------|---------------|----------------|-------------|\n"
            + "\n".join(rows) + "\n\n"
            "**Seasonal Insights:**\n"
            "- 🏆 **July** — peak summer, highest revenue\n"
            "- 🎆 **December** — winter festive, strong #2\n"
            "- 😴 **May** — slowest month (board exam season)\n"
            "- 🌙 **Eid months** — 40–50% above-average boost\n"
        )
        return msg, None, None

    ach_kw = ['achievement','achieve','target','vs target','reached','met',
              'goal','performance','progress']
    if any(k in q for k in ach_kw):
        filtered, months, years, project = filter_df(q, df)
        if not filtered.empty:
            act_rev = filtered['Actual Revenue'].sum()
            tgt_rev = filtered['Target revenue'].sum()
            act_ff = filtered['Actual Footfall'].sum()
            tgt_ff = filtered['Target Footfall'].sum()
            rev_ach = act_rev/tgt_rev*100 if tgt_rev > 0 else 0
            ff_ach = act_ff/tgt_ff*100 if tgt_ff > 0 else 0
            s_rev = "✅ TARGET MET" if rev_ach>=100 else "⚠️ NEAR TARGET" if rev_ach>=75 else "❌ MISSED TARGET"
            s_ff = "✅ TARGET MET" if ff_ach>=100 else "⚠️ NEAR TARGET" if ff_ach>=75 else "❌ MISSED TARGET"
            proj_str = f" — {project}" if project else ""
            period_str = ", ".join(months + [str(y) for y in years]) if (months or years) else "All Data"
            surplus_or_shortfall = ""
            if tgt_rev > 0:
                diff = act_rev - tgt_rev
                if diff >= 0:
                    surplus_or_shortfall = f"\n\n🎉 **Surplus:** {fmt_rev(diff)} above target!"
                else:
                    surplus_or_shortfall = f"\n\n📉 **Shortfall:** {fmt_rev(abs(diff))} below target."
            msg = (
                f"### 🎯 Target Achievement Report — {period_str}{proj_str}\n\n"
                f"| Metric | Actual | Target | Achievement | Status |\n"
                f"|--------|--------|--------|-------------|--------|\n"
                f"| 💰 Revenue | {fmt_rev(act_rev)} | {fmt_rev(tgt_rev)} | **{rev_ach:.1f}%** | {s_rev} |\n"
                f"| 👥 Footfall | {act_ff:,.0f} | {tgt_ff:,.0f} | **{ff_ach:.1f}%** | {s_ff} |\n"
                f"{surplus_or_shortfall}"
            )
            return msg, filtered, None

    q_months, q_name = detect_quarter(q)
    if q_months:
        years = [int(y) for y in re.findall(r'\b(20\d{2})\b', q)]
        filtered = df[df['Months'].isin(q_months)]
        if years: filtered = filtered[filtered['Year'].isin(years)]
        project = detect_project(q)
        if project: filtered = filtered[filtered['Project']==project]
        if not filtered.empty:
            act_rev = filtered['Actual Revenue'].sum()
            act_ff = filtered['Actual Footfall'].sum()
            tgt_rev = filtered['Target revenue'].sum()
            ach = act_rev/tgt_rev*100 if tgt_rev > 0 else 0
            proj_str = f" ({project})" if project else ""
            yr_str = f" {years[0]}" if years else ""
            msg = (
                f"### 📊 {q_name}{yr_str} Analysis{proj_str} — {', '.join(q_months)}\n\n"
                f"| Metric | Value |\n"
                f"|--------|-------|\n"
                f"| 💰 Revenue | **{fmt_rev(act_rev)}** |\n"
                f"| 👥 Footfall | **{act_ff:,.0f}** |\n"
                f"| 🎯 Target Revenue | {fmt_rev(tgt_rev)} |\n"
                f"| 📈 Achievement | **{ach:.1f}%** |\n"
            )
            if act_ff > 0:
                msg += f"| 💡 Rev/Visitor | **Rs. {act_rev/act_ff:,.0f}** |"
            return msg, filtered, None

    rpp_kw = ['revenue per','per visitor','spend per','rev per','rpp','spending',
              'average spend','per customer','average revenue','per ticket']
    if any(k in q for k in rpp_kw):
        filtered, months, years, project = filter_df(q, df)
        data_src = filtered if not filtered.empty else df
        rev = data_src['Actual Revenue'].sum()
        ff = data_src['Actual Footfall'].sum()
        rpp = rev/ff if ff > 0 else 0
        period = ", ".join(months+[str(y) for y in years]) if (months or years) else "All-Time"
        proj_str = f" ({project})" if project else " (All Projects)"
        all_rpp = df['Actual Revenue'].sum()/df['Actual Footfall'].sum()
        msg = (
            f"### 💡 Revenue Per Visitor — {period}{proj_str}\n\n"
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| 💰 Total Revenue | {fmt_rev(rev)} |\n"
            f"| 👥 Total Footfall | {ff:,.0f} |\n"
            f"| 💡 Revenue per Visitor | **Rs. {rpp:,.0f}** |\n"
            f"| 📊 All-Time Average | Rs. {all_rpp:,.0f}/visitor |\n"
            f"| 📈 vs All-Time | `{(rpp-all_rpp)/all_rpp*100:+.1f}%` |"
        )
        return msg, filtered if not filtered.empty else None, None

    filtered, months, years, project = filter_df(q, df)

    want_rev = any(k in q for k in ['revenue','rev','income','earning','sales'])
    want_ff = any(k in q for k in ['footfall','foot fall','visitors','attendance','customers','guest'])
    want_both = not want_rev and not want_ff

    if filtered.empty:
        return (
            "⚠️ **No data matched your query.**\n\n"
            "**Try these examples:**\n"
            "- `Revenue July 2023`\n"
            "- `Footfall 2024 Joyland Fortress`\n"
            "- `August 2023 vs August 2024`\n"
            "- `Forecast March 2027`\n"
            "- `Q1 2024 achievement`\n"
            "- `Revenue trend all years`\n\n"
            "**Projects:** Fortress · JAP-OD · SS-PKG · SS-FSM · SS-JAP · B-PKG · B-EMP"
        ), None, None

    act_rev = filtered['Actual Revenue'].sum()
    act_ff = filtered['Actual Footfall'].sum()
    tgt_rev = filtered['Target revenue'].sum()
    tgt_ff = filtered['Target Footfall'].sum()
    rev_ach = act_rev/tgt_rev*100 if tgt_rev > 0 else None
    ff_ach = act_ff/tgt_ff*100 if tgt_ff > 0 else None
    rpp = act_rev/act_ff if act_ff > 0 else 0
    n_months = len(filtered['Months'].unique()) if 'Months' in filtered.columns else 1

    period_desc = ""
    if months: period_desc += ", ".join(months) + " "
    if years: period_desc += ", ".join(str(y) for y in years)
    if project: period_desc += f" ({project})"
    period_desc = period_desc.strip() or "All Data"

    rows = []
    if want_rev or want_both:
        rows.append(f"| 💰 Actual Revenue | **{fmt_rev(act_rev)}** |")
        if tgt_rev > 0:
            rows.append(f"| 🎯 Target Revenue | {fmt_rev(tgt_rev)} |")
            rows.append(f"| 📈 Achievement | **{rev_ach:.1f}%** |")
    if want_ff or want_both:
        rows.append(f"| 👥 Actual Footfall | **{act_ff:,.0f}** |")
        if tgt_ff > 0:
            rows.append(f"| 🎯 Target Footfall | {tgt_ff:,.0f} |")
            if ff_ach: rows.append(f"| 📈 FF Achievement | **{ff_ach:.1f}%** |")
    if want_both and act_ff > 0:
        rows.append(f"| 💡 Rev/Visitor | **Rs. {rpp:,.0f}** |")
    if n_months > 1 and (want_rev or want_both):
        rows.append(f"| 📊 Avg Monthly Rev | {fmt_rev(act_rev/n_months)} |")

    msg = f"### 📊 Analysis — {period_desc}\n\n| Metric | Value |\n|--------|-------|\n"
    msg += "\n".join(rows)

    if rev_ach:
        if rev_ach >= 100:
            msg += f"\n\n✅ **Target Exceeded** — {rev_ach:.1f}% achievement! Surplus: {fmt_rev(act_rev-tgt_rev)}"
        elif rev_ach >= 85:
            msg += f"\n\n⚠️ **Near Target** — {rev_ach:.1f}% achieved, {fmt_rev(tgt_rev-act_rev)} short"
        else:
            msg += f"\n\n❌ **Below Target** — {rev_ach:.1f}% achieved"

    return msg, filtered, None


# ═══════════════════════════════════════════════════════════════
#  INTRO / HELP MESSAGES  —  All English
# ═══════════════════════════════════════════════════════════════
def _intro_message():
    return (
        "### 👋 Welcome to **Joyland MIS v6.0 Ultra**!\n\n"
        "---\n"
        "🤖 **I am the Joyland MIS AI Assistant** — a complete Business Intelligence Bot trained on **2017–2026 Joyland data** across **8 projects**.\n\n"
        "Developed by **MIS Assistant Manager Umair Nizam** for smart, data-driven decisions.\n\n"
        "---\n"
        "### 🧠 What I Can Do:\n\n"
        "| Query Type | Example |\n"
        "|---|---|\n"
        "| 💰 Revenue | `Revenue July 2023` |\n"
        "| 👥 Footfall | `Footfall 2024 Joyland Fortress` |\n"
        "| 🆚 Comparison | `August 2023 vs August 2024` |\n"
        "| 🔮 AI Forecast | `Forecast March 2027` |\n"
        "| 🎯 Achievement | `Target achievement 2025` |\n"
        "| 📈 Trends | `Revenue trend all years` |\n"
        "| 📅 Quarterly | `Q1 2024 revenue` |\n"
        "| 🏢 Projects | `All projects comparison` |\n"
        "| 💡 Per Visitor | `Revenue per visitor 2024` |\n"
        "| 🦠 Events | `COVID impact 2020` |\n"
        "| 🌙 Islamic | `Eid impact on revenue` |\n"
        "| 🌦️ Weather | `Monsoon effect on footfall` |\n"
        "| 🏏 Sports | `PSL impact` |\n\n"
        "**Projects:** Joyland Fortress · JAP-OD · SS-PKG · SS-FSM · SS-JAP · B-PKG · B-EMP\n\n"
        "**Ask me anything! 🚀**"
    )


def _help_message():
    return (
        "### 📖 Complete Query Guide\n\n"
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
        "- `Predict revenue December 2028 Joyland Fortress`\n\n"
        "**Pakistan-Specific:**\n"
        "- `Eid impact on revenue`\n"
        "- `Monsoon effect on footfall`\n"
        "- `PSL cricket season impact`\n"
        "- `COVID impact 2020`\n\n"
        "**Analysis:**\n"
        "- `Revenue trend` / `Annual growth`\n"
        "- `Best month` / `Worst month`\n"
        "- `Monthly breakdown`\n"
        "- `Achievement 2024`\n"
        "- `Revenue per visitor 2025`\n"
        "- `All projects comparison`\n"
    )


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
def render_sidebar(df, auth_obj=None):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:16px 0 8px;'>
          <div style='font-family:Orbitron,monospace;font-size:10px;letter-spacing:4px;color:#7a9cc0;'>JOYLAND MIS</div>
          <div style='font-family:Orbitron,monospace;font-size:18px;font-weight:900;color:#00c6ff;margin:4px 0;'>CONTROL</div>
          <div style='font-family:Orbitron,monospace;font-size:9px;letter-spacing:3px;color:#3a5a80;'>INTELLIGENCE CENTER v6.0 ULTRA</div>
        </div>
        <div style='border-bottom:1px solid rgba(0,180,255,0.2);margin:8px 0 16px;'></div>
        """, unsafe_allow_html=True)

        analyst_name = st.session_state.get('name', 'Analyst')
        st.markdown(f"""
        <div style='background:rgba(0,198,255,0.05);border:1px solid rgba(0,198,255,0.15);border-radius:12px;padding:14px 16px;margin-bottom:16px;'>
          <div style='font-family:Rajdhani;font-size:9px;letter-spacing:2px;color:#7a9cc0;text-transform:uppercase;margin-bottom:4px;'>ACTIVE ANALYST</div>
          <div style='font-family:Orbitron;font-size:13px;color:#00c6ff;font-weight:700;'>{analyst_name}</div>
          <div style='margin-top:8px;display:flex;align-items:center;gap:6px;font-family:JetBrains Mono,monospace;font-size:10px;color:#00ff9d;letter-spacing:2px;'>
            <span style='width:8px;height:8px;background:#00ff9d;border-radius:50%;display:inline-block;animation:pulsate 1.5s infinite;'></span>
            AI ENGINE ONLINE
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ CLEAR CHAT", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_filtered_df = None
            st.session_state.comparison_data = None
            st.rerun()

        if auth_obj:
            auth_obj.logout('⏻  LOGOUT', 'sidebar')

        st.markdown("<div style='border-bottom:1px solid rgba(0,180,255,0.1);margin:16px 0;'></div>", unsafe_allow_html=True)

        if not df.empty:
            projects = df['Project'].nunique() if 'Project' in df.columns else 0
            records = len(df)
            min_yr = int(df['Year'].min()) if 'Year' in df.columns else 2017
            max_yr = int(df['Year'].max()) if 'Year' in df.columns else 2026
            st.markdown(f"""
            <div style='background:rgba(12,27,53,0.8);border:1px solid rgba(0,180,255,0.15);border-radius:12px;padding:14px;margin-bottom:12px;'>
              <div style='font-family:Rajdhani;font-size:9px;letter-spacing:2px;color:#8ab4d4;text-transform:uppercase;margin-bottom:8px;font-weight:700;'>DATA SCOPE</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#f0f8ff;margin:5px 0;'>📅 {min_yr} – {max_yr}</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#f0f8ff;margin:5px 0;'>📊 {records:,} Records</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#f0f8ff;margin:5px 0;'>🏢 {projects} Projects</div>
              <div style='font-family:JetBrains Mono;font-size:12px;color:#f0f8ff;margin:5px 0;'>🤖 Seasonal + Trend + PK Events</div>
            </div>
            """, unsafe_allow_html=True)

        quick = [
            "Revenue July 2024", "Footfall 2025",
            "August 2023 vs August 2024", "Forecast March 2027",
            "Revenue trend", "Q1 2024 Joyland Fortress",
            "Achievement 2025", "All projects comparison",
            "Revenue per visitor 2024", "COVID impact 2020",
            "Eid impact on revenue", "Monsoon effect",
        ]
        st.markdown("""
        <div style='background:rgba(12,27,53,0.8);border:1px solid rgba(0,180,255,0.15);border-radius:12px;padding:14px;'>
          <div style='font-family:Rajdhani;font-size:9px;letter-spacing:2px;color:#8ab4d4;text-transform:uppercase;margin-bottom:8px;font-weight:700;'>QUICK QUERIES</div>
        """, unsafe_allow_html=True)
        for qk in quick:
            st.markdown(f"<div style='font-family:JetBrains Mono;font-size:10px;color:#c8dff0;margin:4px 0;'>› {qk}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center;padding:12px;font-family:Rajdhani;font-size:10px;color:#3d6080;letter-spacing:1px;margin-top:16px;'>
          ARCHITECT: <span style='color:#f5c518;font-weight:700;'>UMAIR NIZAM</span><br>
          <span style='color:#1a3a6b;'>v6.0 ULTRA · 2017–2030</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Joyland MIS Assistant · v6.0 Ultra",
        layout="wide", page_icon="🎢",
        initial_sidebar_state="expanded"
    )
    st.markdown(PAGE_THEME, unsafe_allow_html=True)
    st.markdown(DATAFRAME_FIX, unsafe_allow_html=True)

    for k, v in {'messages':[], 'last_filtered_df':None, 'comparison_data':None}.items():
        if k not in st.session_state:
            st.session_state[k] = v

    df = load_data()

    # ── AUTH ──
    credentials = {"usernames":{"admin":{"name":"Admin","password":"MIS2024@secure"}}}
    try:
        from streamlit_authenticator import Authenticate
        auth = Authenticate(credentials, "joyland_mis", "auth_key_v6", cookie_expiry_days=30)
        auth.login(location='main')
        is_auth = st.session_state.get("authentication_status")
    except ImportError:
        st.warning("⚠️ streamlit-authenticator not installed. Running in demo mode.")
        is_auth = True
        auth = None

    if not is_auth:
        st.markdown("""
        <div style='max-width:420px;margin:80px auto;text-align:center;'>
          <div style='font-family:Orbitron,monospace;font-size:30px;font-weight:900;
               background:linear-gradient(135deg,#00c6ff,#f5c518);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;'>
            JOYLAND MIS ASSISTANT
          </div>
          <div style='font-family:Rajdhani;font-size:12px;letter-spacing:3px;color:#7a9cc0;margin-bottom:32px;'>
            INTELLIGENCE PLATFORM · v6.0 ULTRA
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    render_sidebar(df, auth)

    # ── HERO BANNER (matched to HTML preview) ──
    st.markdown("""
    <div class='hero-banner'>
      <div class='hero-title'>JOYLAND  MIS  ASSISTANT</div>
      <div class='hero-subtitle'>Advanced Business Intelligence &amp; Predictive Analytics Platform</div>
      <div class='hero-badge'>⬡ AI-POWERED · DATA 2017–2026 · FORECAST 2030 · v6.0 ULTRA</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI CARDS (matched to HTML preview kpi-grid style) ──
    if not df.empty:
        try:
            total_rev = df['Actual Revenue'].sum()
            total_ff = df['Actual Footfall'].sum()
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

    # ── AI INSIGHT CARD (matched to HTML preview) ──
    if not df.empty:
        try:
            best_proj = df.groupby('Project')['Actual Revenue'].sum().idxmax()
            peak_month = df.groupby('Months',observed=True)['Actual Revenue'].sum().idxmax()
            best_year_row = df.groupby('Year')['Actual Revenue'].sum()
            best_year = best_year_row.idxmax()
            all_rpp = df['Actual Revenue'].sum()/df['Actual Footfall'].sum()
            st.markdown(f"""
            <div class='insight-card'>
              <p>🏆 <strong>Peak Month:</strong> {peak_month} &nbsp;·&nbsp;
              🏢 <strong>Top Project:</strong> {best_proj} &nbsp;·&nbsp;
              🚀 <strong>Best Year:</strong> {best_year} ({fmt_rev(best_year_row[best_year])}) &nbsp;·&nbsp;
              💡 <strong>Rev/Visitor:</strong> Rs. {all_rpp:,.0f} all-time avg &nbsp;·&nbsp;
              📅 <strong>CAGR 2017–2025:</strong> ~33%/year</p>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass

    # ── SECTION: AI CHAT ──
    st.markdown("<div class='section-header'>AI ANALYTICS ASSISTANT</div>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["is_user"] else "assistant"):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything: Revenue · Footfall · Comparison · Forecast · Eid · Monsoon · Trends · Projects…")

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
    #  VISUAL INTELLIGENCE PANEL
    # ═══════════════════════════════════════════════════════════
    if st.session_state.last_filtered_df is not None and not st.session_state.last_filtered_df.empty:
        df_plot = st.session_state.last_filtered_df

        st.markdown("<div class='section-header'>VISUAL INTELLIGENCE PANEL</div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📉 Insights", "🔬 Deep Analysis", "🏢 Projects",
            "🔮 Forecast", "📋 Data"
        ])

        with tab1:
            # Comparison bar chart if comparison data available
            if st.session_state.comparison_data:
                cd = st.session_state.comparison_data
                fig_comp = go.Figure()
                bar_colors = ['#00c6ff','#f5c518']
                for i, (lbl, rev, ff) in enumerate(zip(cd['labels'], cd['revenue'], cd['footfall'])):
                    fig_comp.add_trace(go.Bar(
                        name=f'{lbl} – Revenue', x=[lbl], y=[rev],
                        marker_color=bar_colors[i],
                        text=[fmt_rev(rev)], textposition='outside',
                        textfont=dict(family='JetBrains Mono',size=11),
                        hovertemplate=f'<b>{lbl}</b><br>Revenue: <b>Rs. %{{y:,.0f}}</b><extra></extra>'
                    ))
                fig_comp.update_layout(**PLOTLY_LAYOUT, barmode='group',
                    title="Period Comparison — Revenue", height=400,
                    xaxis_title="Period", yaxis_title="Revenue (PKR)")
                st.plotly_chart(fig_comp, use_container_width=True)
                st.divider()

            chart_opt = st.selectbox("🎯 Select Chart", [
                "1. Revenue Achievement Gauge",
                "2. Footfall Achievement Gauge",
                "3. Revenue: Actual vs Target (Bar)",
                "4. Revenue Trend (Area + Peak)",
                "5. Footfall Trend (Area + Peak)",
                "6. Monthly Waterfall",
                "7. Revenue Share by Month (Donut)",
                "8. Revenue Share by Project (Donut)",
                "9. Revenue vs Footfall Regression",
                "10. Year-over-Year Comparison",
            ])

            res = df_plot[[c for c in ['Actual Revenue','Actual Footfall','Target revenue','Target Footfall'] if c in df_plot.columns]].sum()

            if chart_opt.startswith("1"):
                st.plotly_chart(chart_gauge(res.get('Actual Revenue',0), res.get('Target revenue',0), "Revenue Achievement"), use_container_width=True)
            elif chart_opt.startswith("2"):
                st.plotly_chart(chart_gauge(res.get('Actual Footfall',0), res.get('Target Footfall',0), "Footfall Achievement"), use_container_width=True)
            elif chart_opt.startswith("3"):
                cols = [c for c in ['Actual Revenue','Target revenue'] if c in df_plot.columns]
                agg = df_plot.groupby('Months',observed=True)[cols].sum().reset_index()
                st.plotly_chart(chart_bar_labeled(agg,'Months',cols,"Revenue: Actual vs Target","Month","Revenue (PKR)"), use_container_width=True)
            elif chart_opt.startswith("4"):
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(chart_trend_advanced(df_plot.sort_values('Date_Obj'),'Actual Revenue','#00c6ff','Revenue Trend'), use_container_width=True)
            elif chart_opt.startswith("5"):
                if 'Actual Footfall' in df_plot.columns:
                    st.plotly_chart(chart_trend_advanced(df_plot.sort_values('Date_Obj'),'Actual Footfall','#f5c518','Footfall Trend'), use_container_width=True)
            elif chart_opt.startswith("6"):
                fig_wf = chart_waterfall_advanced(df_plot)
                if fig_wf: st.plotly_chart(fig_wf, use_container_width=True)
            elif chart_opt.startswith("7"):
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(chart_pie_advanced(df_plot,'Actual Revenue','Months',"Revenue Share by Month"), use_container_width=True)
            elif chart_opt.startswith("8"):
                if 'Project' in df_plot.columns:
                    st.plotly_chart(chart_pie_advanced(df_plot,'Actual Revenue','Project',"Revenue Share by Project"), use_container_width=True)
            elif chart_opt.startswith("9"):
                fig_r = chart_regression_advanced(df_plot)
                if fig_r: st.plotly_chart(fig_r, use_container_width=True)
            elif chart_opt.startswith("10"):
                st.plotly_chart(chart_yoy_advanced(df_plot), use_container_width=True)

            disp = [c for c in ['Actual Revenue','Target revenue','Actual Footfall','Target Footfall'] if c in df_plot.columns]
            if disp:
                st.markdown("**Summary Totals**")
                summary = df_plot[disp].sum().to_frame("Total").T
                st.dataframe(
                    summary.style.format("{:,.0f}")
                    .set_properties(**{'background-color':'#091428','color':'#f0f8ff','border':'1px solid rgba(0,180,255,0.15)'}),
                    use_container_width=True
                )

        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(chart_yearly_bar(df_plot), use_container_width=True)
            with c2:
                st.plotly_chart(chart_monthly_heatmap(df_plot), use_container_width=True)
            st.plotly_chart(chart_yoy_advanced(df_plot), use_container_width=True)

        with tab3:
            if 'Project' in df_plot.columns:
                st.plotly_chart(chart_project_advanced(df_plot), use_container_width=True)

                # HTML-preview-style project table
                proj_sum = df_plot.groupby('Project').agg({
                    'Actual Revenue':'sum','Actual Footfall':'sum','Target revenue':'sum'
                })
                proj_sum['Achievement %'] = (proj_sum['Actual Revenue']/proj_sum['Target revenue']*100).where(proj_sum['Target revenue']>0,0).round(1)
                proj_sum['Rev/Visitor'] = (proj_sum['Actual Revenue']/proj_sum['Actual Footfall'].replace(0,np.nan)).round(0)
                proj_sum = proj_sum.sort_values('Actual Revenue', ascending=False)

                rows_html = ""
                for proj, row in proj_sum.iterrows():
                    ach = row['Achievement %']
                    badge_cls = "good" if ach >= 90 else "warn" if ach >= 75 else "bad"
                    rows_html += f"""
                    <tr>
                      <td><strong>{proj}</strong></td>
                      <td>{fmt_rev(row['Actual Revenue'])}</td>
                      <td>{row['Actual Footfall']/1e3:.0f}K</td>
                      <td><span class='badge {badge_cls}'>{ach:.1f}%</span></td>
                      <td>Rs. {row['Rev/Visitor']:,.0f}</td>
                    </tr>"""

                st.markdown(f"""
                <table class='data-table'>
                  <thead>
                    <tr><th>Project</th><th>Revenue</th><th>Footfall</th><th>Achievement</th><th>Rev/Visitor</th></tr>
                  </thead>
                  <tbody>{rows_html}</tbody>
                </table>
                """, unsafe_allow_html=True)

        with tab4:
            st.markdown("<div class='section-header'>ADVANCED PREDICTIVE ANALYTICS ENGINE</div>", unsafe_allow_html=True)
            if not df.empty:
                st.plotly_chart(chart_forecast_trajectory_advanced(df), use_container_width=True)

                st.markdown("#### 🔮 Manual Forecast Generator")
                col1, col2, col3 = st.columns(3)
                with col1:
                    m_sel = st.selectbox("Month", ['January','February','March','April','May','June',
                                                    'July','August','September','October','November','December'])
                with col2:
                    y_sel = st.selectbox("Year", list(range(2025,2031)))
                with col3:
                    p_sel = st.selectbox("Project", ['All Projects'] + sorted(df['Project'].unique().tolist()))

                if st.button("🔮 GENERATE ADVANCED FORECAST", use_container_width=True):
                    m_idx = MONTH_MAP[m_sel.lower()]
                    df_src = df if p_sel == 'All Projects' else df[df['Project']==p_sel]
                    p_rev,(lr,ur),note_rev = generate_advanced_forecast(df_src, m_idx, y_sel, 'Actual Revenue')
                    p_ff,(lf,uf),note_ff   = generate_advanced_forecast(df_src, m_idx, y_sel, 'Actual Footfall')
                    pk_mult, pk_notes = compute_pakistan_multiplier(m_idx, y_sel)

                    same_m_hist = df_src[df_src['Month_Num']==m_idx].groupby('Year').agg({'Actual Revenue':'sum'}).reset_index().tail(5)

                    eid_alert = ""
                    if y_sel in EID_FITR_MONTHS and m_idx in EID_FITR_MONTHS[y_sel]:
                        eid_alert = "🌙 **Eid ul Fitr** expected this month → Significant footfall spike!"
                    if y_sel in EID_ADHA_MONTHS and m_idx in EID_ADHA_MONTHS[y_sel]:
                        eid_alert += "\n🐑 **Eid ul Adha** expected this month → Revenue boost!"

                    # Forecast box matching HTML preview style
                    st.markdown(f"""
                    <div class='forecast-box'>
                      <div class='fhead'>◈ AI FORECAST ENGINE · PAKISTAN EVENTS MODEL — {m_sel.upper()} {y_sel} ({p_sel})</div>
                      <div class='forecast-grid'>
                        <div class='forecast-metric rev'>
                          <div class='fm-label'>💰 REVENUE</div>
                          <div class='fm-val'>{fmt_rev(p_rev)}</div>
                          <div class='fm-range'>Range: {fmt_rev(lr)} – {fmt_rev(ur)}</div>
                        </div>
                        <div class='forecast-metric ff'>
                          <div class='fm-label'>👥 FOOTFALL</div>
                          <div class='fm-val'>{p_ff:,.0f}</div>
                          <div class='fm-range'>Range: {lf:,.0f} – {uf:,.0f}</div>
                        </div>
                      </div>
                      <div style='margin-top:12px;font-family:Rajdhani,sans-serif;font-size:13px;color:#a8d4f5;'>
                        <strong>Event Modifiers:</strong> {note_rev}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if eid_alert:
                        st.info(eid_alert)

                    if not same_m_hist.empty:
                        st.markdown(f"**Historical {m_sel} Revenue (last 5 years):**")
                        same_m_hist['Actual Revenue'] = same_m_hist['Actual Revenue'].apply(fmt_rev)
                        st.dataframe(same_m_hist.rename(columns={'Year':'Year','Actual Revenue':'Revenue'}),
                                     use_container_width=True)

                # Pakistan Event Calendar box matching HTML preview
                st.markdown("""
                <div style='background:rgba(245,197,24,0.05);border:1px solid rgba(245,197,24,0.2);border-radius:12px;padding:16px;margin-top:16px;'>
                  <div style='font-family:Orbitron,monospace;font-size:11px;letter-spacing:3px;color:#f5c518;margin-bottom:10px;'>
                    🌙 PAKISTAN EVENT CALENDAR (FORECAST BASIS)
                  </div>
                  <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#7a9cc0;line-height:2;'>
                    <strong>Eid ul Fitr:</strong> 2025→Mar | 2026→Mar | 2027→Mar | 2028→Feb | 2029→Feb | 2030→Jan<br>
                    <strong>Eid ul Adha:</strong> 2025→Jun | 2026→May | 2027→May | 2028→May | 2029→Apr | 2030→Apr<br>
                    <strong>Exam Season (low):</strong> May (Boards) · October (Midterms)<br>
                    <strong>Monsoon Adjustment:</strong> July · August (−8%)<br>
                    <strong>Independence Day Boost:</strong> August 14 (+8%)<br>
                    <strong>Winter Festive:</strong> December (+28%) · January (+13%)
                  </div>
                </div>
                """, unsafe_allow_html=True)

        with tab5:
            st.markdown(f"<div style='font-family:Rajdhani;color:#7a9cc0;margin-bottom:12px;'>{len(df_plot):,} records</div>",
                        unsafe_allow_html=True)
            display_cols = [c for c in df_plot.columns if c not in ['Month_Num','Date_Obj','Fiscal_Year_Label']]
            num_cols = [c for c in display_cols if pd.api.types.is_numeric_dtype(df_plot[c])]
            st.dataframe(
                df_plot[display_cols].style.format({c:'{:,.0f}' for c in num_cols})
                .set_properties(**{'background-color':'#091428','color':'#f0f8ff','border':'1px solid rgba(0,180,255,0.15)'}),
                use_container_width=True, height=500
            )
            csv = df_plot.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ EXPORT CSV", data=csv,
                file_name=f"joyland_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime='text/csv', use_container_width=True
            )

    # ── FOOTER STATUS BAR (matched to HTML preview) ──
    if not df.empty:
        records = len(df)
        projects = df['Project'].nunique() if 'Project' in df.columns else 0
    else:
        records, projects = 0, 0

    st.markdown(f"""
    <div style='text-align:center;padding:20px 0 10px;margin-top:24px;border-top:1px solid rgba(0,180,255,0.1);'>
      <div style='display:flex;justify-content:center;align-items:center;gap:8px;
           font-family:JetBrains Mono,monospace;font-size:10px;color:#00ff9d;letter-spacing:2px;'>
        <span style='width:8px;height:8px;background:#00ff9d;border-radius:50%;display:inline-block;animation:pulsate 1.5s infinite;'></span>
        AI ENGINE ONLINE · ARCHITECT: UMAIR NIZAM · v6.0 ULTRA
      </div>
      <div style='font-family:JetBrains Mono,monospace;font-size:9px;color:#3d6080;margin-top:6px;letter-spacing:2px;'>
        2017 – 2030 · {records:,} RECORDS · {projects} PROJECTS · SEASONAL + TREND + PK EVENTS
      </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
