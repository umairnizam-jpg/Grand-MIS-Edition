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
#  JOYLAND MIS ASSISTANT  ·  v7.0 APEX
#  Architect: Umair Nizam  |  Scope: 2017 – 2030
#  AI Engine: Advanced Seasonal Decomposition + Pakistan Events
#  Design: Ultra-Premium Financial Terminal Aesthetic
# ═══════════════════════════════════════════════════════════════

PAGE_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── ROOT VARIABLES ─────────────────────────────────────────── */
:root {
  /* Primary Backgrounds */
  --bg-void: #080c14;
  --bg-base: #0d1321;
  --bg-raised: #111827;
  --bg-surface: #162032;
  --bg-overlay: #1c2a3f;
  --bg-hover: #1f3050;

  /* Accent System */
  --accent-primary: #3b82f6;
  --accent-glow: rgba(59,130,246,0.35);
  --accent-subtle: rgba(59,130,246,0.08);
  --accent-border: rgba(59,130,246,0.20);
  --accent-border-strong: rgba(59,130,246,0.45);

  /* Gold System */
  --gold: #f59e0b;
  --gold-glow: rgba(245,158,11,0.30);
  --gold-subtle: rgba(245,158,11,0.07);
  --gold-border: rgba(245,158,11,0.22);

  /* Emerald System */
  --emerald: #10b981;
  --emerald-glow: rgba(16,185,129,0.30);
  --emerald-subtle: rgba(16,185,129,0.07);
  --emerald-border: rgba(16,185,129,0.22);

  /* Rose System */
  --rose: #f43f5e;
  --rose-glow: rgba(244,63,94,0.30);
  --rose-subtle: rgba(244,63,94,0.07);

  /* Violet System */
  --violet: #8b5cf6;
  --violet-glow: rgba(139,92,246,0.30);
  --violet-subtle: rgba(139,92,246,0.07);

  /* Amber */
  --amber: #f97316;

  /* Text */
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #475569;
  --text-faint: #2d3f55;

  /* Typography */
  --font-display: 'Syne', sans-serif;
  --font-body: 'Space Grotesk', sans-serif;
  --font-mono: 'DM Mono', monospace;

  /* Borders */
  --border-subtle: rgba(148,163,184,0.06);
  --border-default: rgba(148,163,184,0.10);
  --border-strong: rgba(148,163,184,0.18);

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
  --shadow-md: 0 4px 20px rgba(0,0,0,0.5);
  --shadow-lg: 0 8px 40px rgba(0,0,0,0.6);
  --shadow-xl: 0 20px 60px rgba(0,0,0,0.7);

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

/* ── GLOBAL RESET / BASE ────────────────────────────────────── */
html, body,
.stApp, .main,
[class*="css"],
section.main > div,
.block-container {
  background: var(--bg-void) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-body) !important;
}

[style*="background: white"],[style*="background-color: white"],
[style*="background: rgb(255, 255, 255)"],[style*="background-color: rgb(255, 255, 255)"],
[style*="background: #fff"],[style*="background-color: #fff"],
[style*="background: #ffffff"],[style*="background-color: #ffffff"],
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
  background: var(--bg-void) !important;
  background-color: var(--bg-void) !important;
}

/* Subtle noise grain overlay */
.main::before {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  opacity: 0.4;
}

/* Subtle grid */
.main::after {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    linear-gradient(rgba(59,130,246,0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.015) 1px, transparent 1px);
  background-size: 64px 64px;
}

/* ── TEXT ───────────────────────────────────────────────────── */
p, span, div, label, li, td, th, a { color: var(--text-primary) !important; }
.stMarkdown p, .stMarkdown span, .stMarkdown li {
  color: var(--text-secondary) !important; font-size: 14px !important;
  font-weight: 400 !important; line-height: 1.75 !important;
  font-family: var(--font-body) !important;
}
h1, h2, h3 { color: var(--text-primary) !important; font-family: var(--font-display) !important; }

/* ── SIDEBAR ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--bg-base) !important;
  border-right: 1px solid var(--border-default) !important;
}
section[data-testid="stSidebar"] * { background-color: transparent !important; }
section[data-testid="stSidebar"]::after {
  content: '';
  position: absolute; top: 0; left: 0; width: 1px; height: 100%;
  background: linear-gradient(180deg, transparent 0%, var(--accent-primary) 30%, var(--gold) 70%, transparent 100%);
  opacity: 0.3;
}

/* ── METRIC CARDS ───────────────────────────────────────────── */
div[data-testid="stMetric"] {
  background: var(--bg-raised) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-lg) !important;
  padding: 20px 18px !important;
  position: relative; overflow: hidden;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 12px 40px rgba(59,130,246,0.15), var(--shadow-md) !important;
  border-color: var(--accent-border-strong) !important;
  background: var(--bg-surface) !important;
}
div[data-testid="stMetric"]::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--accent-primary) 50%, transparent 100%);
  opacity: 0.6;
}
div[data-testid="stMetricLabel"] > div {
  color: var(--text-muted) !important; font-family: var(--font-mono) !important;
  font-size: 10px !important; letter-spacing: 1.5px !important;
  text-transform: uppercase !important; font-weight: 500 !important;
}
div[data-testid="stMetricValue"] > div {
  color: var(--text-primary) !important; font-family: var(--font-display) !important;
  font-size: 26px !important; font-weight: 800 !important;
  letter-spacing: -0.5px !important;
}
div[data-testid="stMetricDelta"] > div {
  color: var(--emerald) !important; font-family: var(--font-mono) !important;
  font-size: 11px !important; font-weight: 500 !important;
  background: var(--emerald-subtle) !important; padding: 2px 8px !important;
  border-radius: 20px !important; border: 1px solid var(--emerald-border) !important;
}

/* ── BUTTONS ────────────────────────────────────────────────── */
.stButton > button {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text-secondary) !important; font-family: var(--font-body) !important;
  font-weight: 600 !important; letter-spacing: 0.5px !important;
  border-radius: var(--radius-md) !important;
  font-size: 12px !important; transition: all 0.2s ease !important;
  padding: 8px 16px !important;
}
.stButton > button:hover {
  background: var(--bg-hover) !important;
  border-color: var(--accent-border-strong) !important;
  color: var(--text-primary) !important;
  box-shadow: 0 0 20px var(--accent-glow) !important;
  transform: translateY(-1px) !important;
}

/* Primary action button */
.stButton > button[kind="primary"], .stButton > button:first-child {
  background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
  border-color: transparent !important;
  color: white !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
  box-shadow: 0 4px 20px rgba(59,130,246,0.4) !important;
}

/* ── TABS ───────────────────────────────────────────────────── */
div[data-baseweb="tab-list"] {
  background: var(--bg-raised) !important; border-radius: var(--radius-md) !important;
  padding: 4px !important; border: 1px solid var(--border-default) !important; gap: 2px !important;
}
div[data-baseweb="tab"] {
  font-family: var(--font-body) !important; font-weight: 600 !important;
  font-size: 11px !important; letter-spacing: 0.5px !important;
  border-radius: var(--radius-sm) !important; color: var(--text-muted) !important;
  transition: all 0.15s !important; background: transparent !important;
  text-transform: uppercase !important; padding: 8px 16px !important;
}
div[aria-selected="true"] {
  background: var(--bg-surface) !important; color: var(--text-primary) !important;
  box-shadow: var(--shadow-sm) !important; border: 1px solid var(--border-strong) !important;
}
div[role="tabpanel"], div[role="tabpanel"] > div, div[data-baseweb="tab-panel"] {
  background: var(--bg-void) !important; padding-top: 16px !important;
}

/* ── SELECTBOX / DROPDOWN ───────────────────────────────────── */
div[data-baseweb="select"] > div, div[data-baseweb="select"] > div > div {
  background: var(--bg-raised) !important; border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important; color: var(--text-primary) !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div[class*="singleValue"],
div[data-baseweb="select"] div[class*="placeholder"],
div[data-baseweb="select"] svg {
  color: var(--text-primary) !important; fill: var(--text-muted) !important;
  font-family: var(--font-body) !important; font-weight: 500 !important;
}
div[data-baseweb="popover"], div[data-baseweb="popover"] > div,
ul[role="listbox"], div[role="listbox"], [data-baseweb="menu"],
[data-baseweb="menu"] ul, [data-baseweb="menu"] > div {
  background: var(--bg-raised) !important; border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius-lg) !important; box-shadow: var(--shadow-xl) !important;
}
li[role="option"], div[role="option"], [data-baseweb="menu"] li {
  background: var(--bg-raised) !important; color: var(--text-secondary) !important;
  font-family: var(--font-body) !important; font-size: 13px !important; font-weight: 500 !important;
}
li[role="option"]:hover, div[role="option"]:hover, li[aria-selected="true"] {
  background: var(--accent-subtle) !important; color: var(--text-primary) !important;
}

/* ── CHAT INPUT ─────────────────────────────────────────────── */
div[data-testid="stChatInput"] {
  background: var(--bg-raised) !important; border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius-lg) !important;
}
div[data-testid="stChatInput"] textarea {
  background: transparent !important; border: none !important;
  color: var(--text-primary) !important; font-family: var(--font-body) !important;
  font-size: 14px !important; caret-color: var(--accent-primary) !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
  color: var(--text-muted) !important; font-style: italic !important;
}
div[data-testid="stChatInput"]:focus-within {
  border-color: var(--accent-border-strong) !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.10), 0 0 30px rgba(59,130,246,0.06) !important;
}
div[data-testid="stChatInput"] button {
  background: var(--accent-primary) !important;
  border-radius: var(--radius-sm) !important; border: none !important;
}
div[data-testid="stBottom"], div[data-testid="stBottom"] > div,
.stChatFloatingInputContainer {
  background: var(--bg-void) !important; border-top: 1px solid var(--border-subtle) !important;
}
footer, footer * { background: var(--bg-void) !important; color: var(--text-faint) !important; }

/* ── CHAT MESSAGES ──────────────────────────────────────────── */
div[data-testid="stChatMessage"] { background: transparent !important; border: none !important; }
div[data-testid="stChatMessage"] > div {
  background: var(--bg-raised) !important; border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-lg) !important;
}
div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] li, div[data-testid="stChatMessage"] td {
  color: var(--text-secondary) !important; font-size: 13.5px !important;
  font-weight: 400 !important; line-height: 1.75 !important;
}
div[data-testid="stChatMessage"] strong { color: var(--text-primary) !important; font-weight: 700 !important; }
div[data-testid="stChatMessage"] code {
  color: var(--emerald) !important; background: var(--emerald-subtle) !important;
  padding: 2px 6px !important; border-radius: 4px !important;
  font-family: var(--font-mono) !important; font-size: 12px !important;
  border: 1px solid var(--emerald-border) !important;
}

/* ── PLOTLY CHARTS ──────────────────────────────────────────── */
div[data-testid="stPlotlyChart"], div[data-testid="stPlotlyChart"] > div,
.js-plotly-plot, .js-plotly-plot .plotly, .js-plotly-plot .plotly .main-svg,
.plot-container, .plot-container > svg, .svg-container, .svg-container svg {
  background: transparent !important; background-color: transparent !important;
}
.modebar, .modebar-container, .modebar-group {
  background: var(--bg-raised) !important; border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border-default) !important;
}
.modebar-btn svg path { fill: var(--text-muted) !important; }
.modebar-btn:hover svg path { fill: var(--text-primary) !important; }

/* ── DATAFRAME / TABLES ─────────────────────────────────────── */
div[data-testid="stDataFrame"], div[data-testid="stDataFrame"] > div,
.stDataFrame, .stDataFrame > div {
  background: var(--bg-raised) !important; border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-lg) !important; overflow: hidden !important;
}
[data-testid="stDataFrame"] canvas { filter: invert(1) hue-rotate(180deg); }
[data-testid="stDataFrame"] > div > div { background: var(--bg-raised) !important; border-radius: var(--radius-lg) !important; }
[data-testid="stDataFrame"] [role="columnheader"] {
  background: var(--bg-surface) !important; color: var(--text-muted) !important;
  font-family: var(--font-mono) !important; font-size: 10px !important;
  letter-spacing: 1px !important; text-transform: uppercase !important;
}
[data-testid="stDataFrame"] [role="gridcell"] {
  background: var(--bg-raised) !important; color: var(--text-secondary) !important;
  border-color: var(--border-subtle) !important;
}
table { background: var(--bg-raised) !important; border-radius: var(--radius-lg) !important; width: 100% !important; }
thead, thead tr { background: var(--bg-surface) !important; }
th {
  background: var(--bg-surface) !important; color: var(--text-muted) !important;
  font-family: var(--font-mono) !important; font-size: 10px !important;
  letter-spacing: 1.5px !important; text-transform: uppercase !important;
  padding: 12px 16px !important; border-bottom: 1px solid var(--border-default) !important;
  font-weight: 500 !important;
}
td {
  color: var(--text-secondary) !important; background: transparent !important;
  font-size: 13px !important; padding: 10px 16px !important;
  border-bottom: 1px solid var(--border-subtle) !important;
  font-family: var(--font-body) !important;
}
tr:hover td { background: rgba(59,130,246,0.03) !important; }
tr:last-child td { border-bottom: none !important; }

/* ── EXPANDER ───────────────────────────────────────────────── */
div[data-testid="stExpander"], details[data-testid="stExpander"] {
  background: var(--bg-raised) !important; border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
}
details[data-testid="stExpander"] summary {
  color: var(--text-secondary) !important; font-family: var(--font-body) !important; font-weight: 600 !important;
}

/* ── ALERTS ─────────────────────────────────────────────────── */
div[data-testid="stAlert"] {
  background: var(--accent-subtle) !important; border: 1px solid var(--accent-border) !important;
  border-radius: var(--radius-md) !important; color: var(--text-secondary) !important;
}
div[data-testid="stSuccess"] { background: var(--emerald-subtle) !important; border-color: var(--emerald-border) !important; }
div[data-testid="stWarning"] { background: var(--gold-subtle) !important; border-color: var(--gold-border) !important; }
div[data-testid="stError"] { background: var(--rose-subtle) !important; border-color: rgba(244,63,94,0.25) !important; }

/* ── DOWNLOAD BUTTON ────────────────────────────────────────── */
div[data-testid="stDownloadButton"] button {
  background: var(--emerald-subtle) !important;
  border: 1px solid var(--emerald-border) !important; color: var(--emerald) !important;
  font-family: var(--font-body) !important; font-weight: 600 !important;
  letter-spacing: 0.5px !important; border-radius: var(--radius-md) !important;
  text-transform: uppercase !important; font-size: 11px !important;
}
div[data-testid="stDownloadButton"] button:hover {
  background: rgba(16,185,129,0.14) !important;
  box-shadow: 0 4px 16px var(--emerald-glow) !important;
}

/* ── SCROLLBAR ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── DIVIDER ────────────────────────────────────────────────── */
hr { border-color: var(--border-subtle) !important; }

/* ── INPUT WIDGETS ──────────────────────────────────────────── */
div[data-baseweb="input"] > div, input[type="text"], input[type="number"], textarea {
  background: var(--bg-raised) !important; border-color: var(--border-default) !important;
  color: var(--text-primary) !important; border-radius: var(--radius-md) !important;
  font-family: var(--font-body) !important;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM PREMIUM COMPONENTS
   ═══════════════════════════════════════════════════════════════ */

/* Hero Banner */
.hero-banner {
  position: relative;
  background: var(--bg-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: 40px 48px;
  margin-bottom: 28px;
  overflow: hidden;
}
.hero-banner::before {
  content: '';
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at -10% 0%, rgba(59,130,246,0.10) 0%, transparent 60%),
    radial-gradient(ellipse 50% 80% at 110% 100%, rgba(245,158,11,0.07) 0%, transparent 60%);
}
.hero-banner-inner {
  position: relative; z-index: 1;
  display: flex; align-items: center; justify-content: space-between; gap: 24px;
}
.hero-left {}
.hero-eyebrow {
  font-family: var(--font-mono);
  font-size: 10px; letter-spacing: 3px; color: var(--accent-primary);
  text-transform: uppercase; font-weight: 500; margin-bottom: 10px;
  display: flex; align-items: center; gap: 8px;
}
.hero-eyebrow::before {
  content: '';
  display: inline-block; width: 20px; height: 1px;
  background: var(--accent-primary); opacity: 0.7;
}
.hero-title {
  font-family: var(--font-display) !important;
  font-size: 38px !important; font-weight: 800 !important;
  letter-spacing: -1px !important;
  color: var(--text-primary) !important;
  line-height: 1 !important; margin: 0 0 10px !important;
}
.hero-title span {
  background: linear-gradient(135deg, #60a5fa 0%, #f59e0b 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-family: var(--font-body); font-size: 14px;
  color: var(--text-muted); font-weight: 400; letter-spacing: 0.2px;
  line-height: 1.5;
}
.hero-right {
  display: flex; flex-direction: column; align-items: flex-end; gap: 10px; flex-shrink: 0;
}
.hero-stat {
  text-align: right;
}
.hero-stat-val {
  font-family: var(--font-display); font-size: 22px; font-weight: 800;
  color: var(--text-primary); line-height: 1;
}
.hero-stat-label {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 2px;
  color: var(--text-muted); text-transform: uppercase; margin-top: 2px;
}
.status-chip {
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--emerald-subtle); border: 1px solid var(--emerald-border);
  border-radius: 100px; padding: 5px 14px;
  font-family: var(--font-mono); font-size: 9px;
  color: var(--emerald); letter-spacing: 2px; text-transform: uppercase;
}
.pulse {
  width: 6px; height: 6px; background: var(--emerald);
  border-radius: 50%; animation: pulse-anim 2s ease-in-out infinite;
}
@keyframes pulse-anim {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }
  50% { opacity: 0.8; transform: scale(1.1); box-shadow: 0 0 0 5px rgba(16,185,129,0); }
}

/* KPI Cards */
.kpi-row {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 28px;
}
.kpi-card {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg); padding: 20px 18px;
  position: relative; overflow: hidden;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
}
.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}
.kpi-card::after {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
}
.kpi-card.blue { border-top: 2px solid var(--accent-primary); }
.kpi-card.blue:hover { border-color: var(--accent-primary); box-shadow: 0 8px 30px rgba(59,130,246,0.15); }
.kpi-card.gold { border-top: 2px solid var(--gold); }
.kpi-card.gold:hover { box-shadow: 0 8px 30px rgba(245,158,11,0.12); }
.kpi-card.green { border-top: 2px solid var(--emerald); }
.kpi-card.green:hover { box-shadow: 0 8px 30px rgba(16,185,129,0.12); }
.kpi-card.violet { border-top: 2px solid var(--violet); }
.kpi-card.violet:hover { box-shadow: 0 8px 30px rgba(139,92,246,0.12); }
.kpi-card.amber { border-top: 2px solid var(--amber); }
.kpi-card.amber:hover { box-shadow: 0 8px 30px rgba(249,115,22,0.12); }

.kpi-icon {
  font-size: 18px; margin-bottom: 12px; display: block;
  opacity: 0.8;
}
.kpi-label {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 1.5px;
  color: var(--text-muted); text-transform: uppercase; font-weight: 500;
  margin-bottom: 6px;
}
.kpi-value {
  font-family: var(--font-display); font-size: 22px; font-weight: 800;
  line-height: 1; margin-bottom: 8px; letter-spacing: -0.5px;
}
.kpi-card.blue .kpi-value { color: var(--accent-primary); }
.kpi-card.gold .kpi-value { color: var(--gold); }
.kpi-card.green .kpi-value { color: var(--emerald); }
.kpi-card.violet .kpi-value { color: var(--violet); }
.kpi-card.amber .kpi-value { color: var(--amber); }
.kpi-delta {
  font-family: var(--font-mono); font-size: 10px; font-weight: 500;
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 8px; border-radius: 100px;
}
.kpi-delta.up {
  background: var(--emerald-subtle); color: var(--emerald);
  border: 1px solid var(--emerald-border);
}
.kpi-delta.down {
  background: var(--rose-subtle); color: var(--rose);
  border: 1px solid rgba(244,63,94,0.2);
}
.kpi-delta.neutral {
  background: var(--accent-subtle); color: var(--accent-primary);
  border: 1px solid var(--accent-border);
}

/* Section Header */
.section-hdr {
  display: flex; align-items: center; gap: 12px;
  margin: 28px 0 16px;
}
.section-hdr-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--border-default), transparent);
}
.section-hdr-text {
  font-family: var(--font-mono) !important;
  font-size: 10px !important; font-weight: 500 !important;
  letter-spacing: 2.5px !important; color: var(--text-muted) !important;
  text-transform: uppercase !important; white-space: nowrap;
}

/* AI Insight Card */
.insight-card {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-left: 3px solid var(--accent-primary);
  border-radius: var(--radius-lg); padding: 18px 20px; margin-bottom: 24px;
  position: relative;
}
.insight-label {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 2px;
  color: var(--accent-primary); text-transform: uppercase;
  margin-bottom: 8px; font-weight: 500; display: block;
}
.insight-text {
  font-size: 13px; color: var(--text-secondary); line-height: 1.65;
  font-weight: 400;
}
.insight-text strong { color: var(--text-primary) !important; font-weight: 600; }

/* Chart Container */
.chart-wrap {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg); padding: 20px;
  margin-bottom: 16px;
}
.chart-title {
  font-family: var(--font-display); font-size: 13px; font-weight: 700;
  color: var(--text-primary); margin-bottom: 4px; letter-spacing: -0.2px;
}
.chart-sub {
  font-family: var(--font-mono); font-size: 10px; color: var(--text-muted);
  letter-spacing: 1px; margin-bottom: 16px;
}

/* Data Table Pro */
.pro-table { width: 100%; border-collapse: collapse; font-family: var(--font-body); }
.pro-table thead tr { background: var(--bg-surface) !important; }
.pro-table th {
  font-family: var(--font-mono) !important; font-size: 9px !important;
  letter-spacing: 1.5px !important; color: var(--text-muted) !important;
  text-transform: uppercase !important; padding: 12px 16px !important;
  border-bottom: 1px solid var(--border-default) !important;
  font-weight: 500 !important; text-align: left !important;
}
.pro-table td {
  padding: 11px 16px !important; font-size: 13px !important;
  color: var(--text-secondary) !important;
  border-bottom: 1px solid var(--border-subtle) !important;
  font-family: var(--font-body) !important;
}
.pro-table tr:hover td { background: rgba(59,130,246,0.025) !important; }
.pro-table tr:last-child td { border-bottom: none !important; }
.badge {
  display: inline-flex; align-items: center; padding: 3px 10px;
  border-radius: 100px; font-family: var(--font-mono);
  font-size: 10px; font-weight: 500;
}
.badge.good { background: var(--emerald-subtle); color: var(--emerald); border: 1px solid var(--emerald-border); }
.badge.warn { background: var(--gold-subtle); color: var(--gold); border: 1px solid var(--gold-border); }
.badge.bad  { background: var(--rose-subtle); color: var(--rose); border: 1px solid rgba(244,63,94,0.22); }

/* Forecast Box */
.forecast-panel {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-top: 2px solid var(--gold);
  border-radius: var(--radius-lg); padding: 24px;
  margin-bottom: 16px;
}
.forecast-label {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 2px;
  color: var(--gold); text-transform: uppercase; margin-bottom: 16px;
  display: block; font-weight: 500;
}
.forecast-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.fm-card {
  background: var(--bg-surface); border-radius: var(--radius-md);
  padding: 16px; border: 1px solid var(--border-subtle);
}
.fm-label {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 1.5px;
  color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px; font-weight: 500;
}
.fm-value {
  font-family: var(--font-display); font-size: 24px; font-weight: 800;
  letter-spacing: -0.5px; margin-bottom: 4px; line-height: 1;
}
.fm-range {
  font-family: var(--font-mono); font-size: 10px; color: var(--text-muted);
}
.fm-rev .fm-value { color: var(--accent-primary); }
.fm-ff .fm-value { color: var(--gold); }
.fm-modifiers {
  margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border-subtle);
  font-family: var(--font-body); font-size: 12px; color: var(--text-muted);
  line-height: 1.6;
}

/* Event Calendar */
.event-calendar {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg); padding: 20px;
  margin-top: 16px;
}
.ec-title {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 2px;
  color: var(--gold); text-transform: uppercase; margin-bottom: 14px; font-weight: 500;
}
.ec-row {
  display: flex; gap: 12px; align-items: baseline;
  padding: 7px 0; border-bottom: 1px solid var(--border-subtle);
  font-size: 12px;
}
.ec-row:last-child { border-bottom: none; }
.ec-key {
  font-family: var(--font-mono); font-size: 10px; color: var(--text-muted);
  font-weight: 500; min-width: 160px; flex-shrink: 0;
}
.ec-val { color: var(--text-secondary); font-size: 11px; font-family: var(--font-mono); }

/* Footer */
.footer-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 0 8px; margin-top: 32px;
  border-top: 1px solid var(--border-subtle);
}
.footer-brand {
  font-family: var(--font-display); font-size: 13px; font-weight: 700;
  color: var(--text-muted);
}
.footer-brand span { color: var(--accent-primary); }
.footer-meta {
  font-family: var(--font-mono); font-size: 10px; color: var(--text-faint);
  letter-spacing: 1px;
}
</style>
"""

DATAFRAME_FIX = """
<style>
[data-testid="stDataFrame"] canvas { filter: invert(1) hue-rotate(180deg); }
[data-testid="stDataFrame"] > div > div { background: var(--bg-raised, #111827) !important; border-radius: 12px !important; }
[data-testid="stDataFrame"] [role="columnheader"] {
  background: rgba(17,24,39,0.9) !important; color: #64748b !important;
  font-family: 'DM Mono', monospace !important; font-size: 10px !important;
  letter-spacing: 1px !important; text-transform: uppercase !important;
}
[data-testid="stDataFrame"] [role="gridcell"] {
  background: #111827 !important; color: #94a3b8 !important;
  border-color: rgba(148,163,184,0.06) !important;
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
        mult *= 1.45; notes.append("🌙 Eid ul Fitr +45%")
    if year in EID_ADHA_MONTHS and month_num in EID_ADHA_MONTHS[year]:
        mult *= 1.38; notes.append("🐑 Eid ul Adha +38%")
    if month_num in [5,10]: mult *= 0.88; notes.append("📚 Exam Season -12%")
    if month_num in [7,8]:  mult *= 0.92; notes.append("🌧️ Monsoon -8%")
    if month_num == 8:  mult *= 1.08; notes.append("🇵🇰 Independence Day +8%")
    if month_num == 12: mult *= 1.10; notes.append("🎆 Year-End Holidays +10%")
    if month_num == 1:  mult *= 1.05; notes.append("🎊 New Year +5%")
    return mult, " · ".join(notes) if notes else "Standard Season"


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
#  PLOTLY CONFIG — Ultra Premium
# ═══════════════════════════════════════════════════════════════

# Premium color palette
C = {
    'blue':   '#3b82f6',
    'gold':   '#f59e0b',
    'emerald':'#10b981',
    'rose':   '#f43f5e',
    'violet': '#8b5cf6',
    'amber':  '#f97316',
    'sky':    '#38bdf8',
    'lime':   '#84cc16',
}
COLORS = list(C.values())

PROJECT_COLORS = {
    'Joyland Fortress': C['blue'],
    'JAP-OD':           C['gold'],
    'SS-PKG':           C['emerald'],
    'SS-FSM':           C['rose'],
    'SS-JAP':           C['violet'],
    'B-PKG':            C['amber'],
    'B-EMP':            C['sky'],
}

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(17,24,39,0.5)',
    font=dict(family='Space Grotesk, sans-serif', color='#94a3b8', size=12),
    title_font=dict(family='Syne, sans-serif', size=14, color='#f1f5f9'),
    legend=dict(
        bgcolor='rgba(17,24,39,0.9)',
        bordercolor='rgba(148,163,184,0.12)',
        borderwidth=1,
        font=dict(size=12, color='#94a3b8', family='Space Grotesk'),
        itemsizing='constant',
    ),
    xaxis=dict(
        gridcolor='rgba(148,163,184,0.05)',
        linecolor='rgba(148,163,184,0.10)',
        zerolinecolor='rgba(148,163,184,0.08)',
        tickfont=dict(family='DM Mono', size=10, color='#64748b'),
        title_font=dict(family='Space Grotesk', size=12, color='#64748b'),
        showspikes=True,
        spikecolor='rgba(59,130,246,0.3)',
        spikethickness=1,
        spikedash='dot',
    ),
    yaxis=dict(
        gridcolor='rgba(148,163,184,0.05)',
        linecolor='rgba(148,163,184,0.10)',
        zerolinecolor='rgba(148,163,184,0.08)',
        tickfont=dict(family='DM Mono', size=10, color='#64748b'),
        title_font=dict(family='Space Grotesk', size=12, color='#64748b'),
    ),
    margin=dict(l=56, r=32, t=60, b=56),
    hoverlabel=dict(
        bgcolor='rgba(17,24,39,0.97)',
        bordercolor='rgba(59,130,246,0.35)',
        font=dict(family='DM Mono', size=11, color='#f1f5f9'),
        namelength=-1,
    ),
    hovermode='x unified',
)

def fmt_rev(v):
    if v >= 1e9: return f"Rs. {v/1e9:.2f}B"
    if v >= 1e6: return f"Rs. {v/1e6:.1f}M"
    return f"Rs. {v:,.0f}"


# ═══════════════════════════════════════════════════════════════
#  CHARTS — Ultra Premium
# ═══════════════════════════════════════════════════════════════

def chart_gauge(actual, target, title="Revenue Achievement"):
    pct = min((actual/target*100) if target > 0 else 0, 150)
    if pct >= 100: color, bg = C['emerald'], 'rgba(16,185,129,0.08)'
    elif pct >= 75: color, bg = C['gold'], 'rgba(245,158,11,0.08)'
    else: color, bg = C['rose'], 'rgba(244,63,94,0.08)'

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=pct,
        delta={'reference':100,'suffix':'%','font':{'size':14,'family':'DM Mono'}},
        number={'suffix':'%','font':{'size':40,'family':'Syne','color':color}},
        title={'text':title,'font':{'size':13,'family':'Space Grotesk','color':'#64748b'}},
        gauge={
            'axis':{
                'range':[0,150],'tickcolor':'#475569','tickwidth':1,
                'tickvals':[0,50,75,100,125,150],
                'ticktext':['0%','50%','75%','100%','125%','150%'],
                'tickfont':{'family':'DM Mono','size':10,'color':'#475569'},
            },
            'bar':{'color':color,'thickness':0.22},
            'bgcolor':bg,'borderwidth':0,
            'threshold':{'line':{'color':'rgba(148,163,184,0.4)','width':2},'thickness':0.75,'value':100},
            'steps':[
                {'range':[0,75],'color':'rgba(244,63,94,0.04)'},
                {'range':[75,100],'color':'rgba(245,158,11,0.04)'},
                {'range':[100,150],'color':'rgba(16,185,129,0.06)'}
            ]
        }
    ))
    fig.add_annotation(
        text=f"<b>Actual:</b> {fmt_rev(actual)}<br><b>Target:</b> {fmt_rev(target)}",
        x=0.5, y=0.10, xref='paper', yref='paper', showarrow=False,
        font=dict(family='DM Mono', size=11, color='#64748b'), align='center'
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=360,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


def chart_trend_advanced(df, col, color, title, show_annotations=True):
    df = df.sort_values('Date_Obj')
    df_valid = df[df[col] > 0].dropna(subset=[col])
    fig = go.Figure()

    # Gradient area fill
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    fig.add_trace(go.Scatter(
        x=df_valid['Date_Obj'], y=df_valid[col],
        fill='tozeroy',
        fillcolor=f'rgba({r},{g},{b},0.06)',
        line=dict(color=color, width=2.5, shape='spline', smoothing=0.8),
        name=col, mode='lines+markers',
        marker=dict(size=5, color=color, line=dict(color='white', width=1.5), symbol='circle'),
        hovertemplate='<b>%{x|%B %Y}</b><br>' + col + ': <b>%{y:,.0f}</b><extra></extra>'
    ))

    # 3-month moving average
    if len(df_valid) >= 6:
        ma = df_valid[col].rolling(3, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df_valid['Date_Obj'], y=ma,
            line=dict(color='rgba(245,158,11,0.6)', width=1.5, dash='dot'),
            name='3M Moving Avg',
            hovertemplate='3M Avg: <b>%{y:,.0f}</b><extra></extra>'
        ))

    if show_annotations and len(df_valid) > 0:
        max_idx = df_valid[col].idxmax()
        min_idx = df_valid[col].idxmin()
        max_row = df_valid.loc[max_idx]
        min_row = df_valid.loc[min_idx]
        fig.add_annotation(
            x=max_row['Date_Obj'], y=max_row[col],
            text=f"Peak<br>{fmt_rev(max_row[col])}<br>{max_row['Date_Obj'].strftime('%b %Y')}",
            showarrow=True, arrowhead=2, arrowcolor=C['emerald'], arrowwidth=1.5,
            bgcolor='rgba(16,185,129,0.10)', bordercolor=C['emerald'],
            font=dict(family='DM Mono', size=10, color=C['emerald']), ax=0, ay=-48,
            borderwidth=1, borderpad=6, opacity=0.9
        )
        fig.add_annotation(
            x=min_row['Date_Obj'], y=min_row[col],
            text=f"Low<br>{fmt_rev(min_row[col])}<br>{min_row['Date_Obj'].strftime('%b %Y')}",
            showarrow=True, arrowhead=2, arrowcolor=C['rose'], arrowwidth=1.5,
            bgcolor='rgba(244,63,94,0.10)', bordercolor=C['rose'],
            font=dict(family='DM Mono', size=10, color=C['rose']), ax=0, ay=48,
            borderwidth=1, borderpad=6, opacity=0.9
        )

    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=440,
                      xaxis_title="", yaxis_title=col)
    return fig


def chart_bar_labeled(df, x_col, y_cols, title, x_label="", y_label=""):
    fig = go.Figure()
    color_list = [C['blue'], C['gold'], C['emerald'], C['violet']]
    for i, c in enumerate(y_cols):
        if c not in df.columns: continue
        color = color_list[i % len(color_list)]
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fig.add_trace(go.Bar(
            x=df[x_col], y=df[c], name=c,
            marker=dict(
                color=f'rgba({r},{g},{b},0.80)',
                line=dict(color=color, width=1.5),
                cornerradius=4,
            ),
            text=[fmt_rev(v) if v > 0 else '' for v in df[c]],
            textposition='outside',
            textfont=dict(family='DM Mono', size=10, color='#64748b'),
            hovertemplate=f'<b>%{{x}}</b><br>{c}: <b>%{{y:,.0f}}</b><extra></extra>'
        ))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', title=title, height=440,
                      xaxis_title=x_label, yaxis_title=y_label,
                      bargap=0.3, bargroupgap=0.08)
    return fig


def chart_yearly_bar(df):
    yearly = df.groupby('Year').agg({'Actual Revenue':'sum','Target revenue':'sum'}).reset_index()
    yearly = yearly[yearly['Year'] > 2015]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=yearly['Year'].astype(str), y=yearly['Actual Revenue'],
        name='Actual Revenue',
        marker=dict(
            color=[f'rgba(59,130,246,{0.5 + 0.5*(v/yearly["Actual Revenue"].max()):.2f})' for v in yearly['Actual Revenue']],
            line=dict(color=C['blue'], width=1.5),
            cornerradius=4,
        ),
        text=[fmt_rev(v) for v in yearly['Actual Revenue']],
        textposition='outside',
        textfont=dict(family='DM Mono', size=10, color='#64748b'),
        hovertemplate='<b>%{x}</b><br>Actual: <b>%{y:,.0f}</b><extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=yearly['Year'].astype(str), y=yearly['Target revenue'],
        name='Target Revenue',
        marker=dict(
            color='rgba(245,158,11,0.15)',
            line=dict(color=C['gold'], width=1.5),
            cornerradius=4,
        ),
        hovertemplate='<b>%{x}</b><br>Target: <b>%{y:,.0f}</b><extra></extra>'
    ))
    yearly['ach'] = np.where(yearly['Target revenue'] > 0,
                              yearly['Actual Revenue']/yearly['Target revenue']*100, 0)
    fig.add_trace(go.Scatter(
        x=yearly['Year'].astype(str), y=yearly['ach'],
        name='Achievement %', yaxis='y2',
        line=dict(color=C['emerald'], width=2, shape='spline', smoothing=0.8),
        mode='lines+markers+text',
        marker=dict(size=7, color=C['emerald'], line=dict(color='white', width=1.5)),
        text=[f"{v:.0f}%" for v in yearly['ach']], textposition='top center',
        textfont=dict(family='DM Mono', size=10, color=C['emerald']),
        hovertemplate='Achievement: <b>%{y:.1f}%</b><extra></extra>'
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, barmode='group',
        title="Annual Revenue: Actual vs Target",
        height=460, xaxis_title="", yaxis_title="Revenue (PKR)",
        bargap=0.35, bargroupgap=0.1,
        yaxis2=dict(
            overlaying='y', side='right',
            title='Achievement %',
            gridcolor='transparent',
            tickformat='.0f', ticksuffix='%',
            tickfont=dict(family='DM Mono', size=10, color=C['emerald']),
            title_font=dict(family='Space Grotesk', size=12, color=C['emerald'])
        )
    )
    return fig


def chart_monthly_heatmap(df):
    pivot = df.pivot_table(values='Actual Revenue', index='Year',
                           columns='Months', aggfunc='sum', observed=True)
    text_vals = [[fmt_rev(v) if pd.notna(v) and v > 0 else '' for v in row] for row in pivot.values]
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        text=text_vals, texttemplate='%{text}',
        textfont=dict(family='DM Mono', size=9, color='rgba(241,245,249,0.85)'),
        colorscale=[
            [0.0, '#0d1321'],
            [0.2, '#1e3a5f'],
            [0.5, '#1d4ed8'],
            [0.75,'#3b82f6'],
            [1.0, '#93c5fd'],
        ],
        hovertemplate='<b>%{y} — %{x}</b><br>Revenue: <b>Rs. %{z:,.0f}</b><extra></extra>',
        showscale=True,
        colorbar=dict(
            title=dict(text='Revenue', font=dict(family='Space Grotesk', color='#64748b', size=11)),
            tickfont=dict(family='DM Mono', size=9, color='#64748b'),
            thickness=12, len=0.8,
        )
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Revenue Heatmap — Year × Month",
                      height=420, xaxis_title="", yaxis_title="")
    return fig


def chart_project_advanced(df):
    d = df.groupby('Project').agg({'Actual Revenue':'sum','Actual Footfall':'sum'}).reset_index()
    d = d[d['Actual Revenue'] > 0]
    d['Rev_Per'] = d['Actual Revenue'] / d['Actual Footfall'].replace(0, np.nan)
    d = d.sort_values('Actual Revenue', ascending=False)
    colors = [PROJECT_COLORS.get(p, C['blue']) for p in d['Project']]
    fig = go.Figure()

    # Revenue bars
    for i, (_, row) in enumerate(d.iterrows()):
        color = colors[i]
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fig.add_trace(go.Bar(
            name=row['Project'], x=[row['Project']], y=[row['Actual Revenue']],
            marker=dict(
                color=f'rgba({r},{g},{b},0.75)',
                line=dict(color=color, width=1.5),
                cornerradius=4,
            ),
            text=[fmt_rev(row['Actual Revenue'])],
            textposition='outside',
            textfont=dict(family='DM Mono', size=10, color='#94a3b8'),
            showlegend=False,
            hovertemplate=f'<b>{row["Project"]}</b><br>Revenue: <b>%{{y:,.0f}}</b><br>Footfall: <b>{row["Actual Footfall"]:,.0f}</b><br>Rev/Visitor: <b>Rs. {row["Rev_Per"]:,.0f}</b><extra></extra>'
        ))

    # Rev/Visitor line
    fig.add_trace(go.Scatter(
        x=d['Project'], y=d['Rev_Per'], name='Rev / Visitor', yaxis='y2',
        mode='lines+markers+text',
        line=dict(color=C['violet'], width=2, shape='spline', smoothing=0.7),
        marker=dict(size=9, color=C['violet'], line=dict(color='white', width=1.5), symbol='diamond'),
        text=[f"Rs.{v:,.0f}" for v in d['Rev_Per'].fillna(0)],
        textposition='top center',
        textfont=dict(family='DM Mono', size=9, color=C['violet']),
        hovertemplate='Rev/Visitor: <b>Rs. %{y:,.0f}</b><extra></extra>'
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT, barmode='group',
        title="Project Performance: Revenue & Revenue per Visitor",
        height=460, xaxis_title="", yaxis_title="Revenue (PKR)",
        bargap=0.25,
        yaxis2=dict(
            overlaying='y', side='right', showgrid=False,
            tickfont=dict(family='DM Mono', size=10, color=C['violet']),
            title='Rev / Visitor (Rs.)',
            title_font=dict(family='Space Grotesk', size=12, color=C['violet'])
        )
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
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        is_latest = (yr == years[-1])
        fig.add_trace(go.Scatter(
            x=monthly['Months'].astype(str), y=monthly['Actual Revenue'],
            name=str(int(yr)),
            line=dict(color=color, width=2.5 if is_latest else 1.5,
                      shape='spline', smoothing=0.7),
            mode='lines+markers',
            marker=dict(size=6 if is_latest else 4, color=color,
                        line=dict(color='white', width=1 if is_latest else 0.5)),
            opacity=1.0 if is_latest else 0.65,
            hovertemplate=f'<b>{int(yr)} — %{{x}}</b><br>Revenue: <b>Rs. %{{y:,.0f}}</b><extra></extra>'
        ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Year-over-Year Monthly Revenue",
                      height=460, xaxis_title="Month (Fiscal: Jul → Jun)",
                      yaxis_title="Revenue (PKR)")
    return fig


def chart_forecast_trajectory_advanced(df):
    hist = df[df['Actual Revenue']>0].dropna(subset=['Actual Revenue']).sort_values('Date_Obj')
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist['Date_Obj'], y=hist['Actual Revenue'],
        name='Historical Revenue',
        fill='tozeroy', fillcolor='rgba(59,130,246,0.05)',
        line=dict(color=C['blue'], width=2.5, shape='spline', smoothing=0.6),
        mode='lines',
        hovertemplate='<b>%{x|%B %Y}</b><br>Actual: <b>Rs. %{y:,.0f}</b><extra></extra>'
    ))

    tgt = df[df['Target revenue']>0].groupby('Date_Obj')['Target revenue'].sum().reset_index()
    if not tgt.empty:
        fig.add_trace(go.Scatter(
            x=tgt['Date_Obj'], y=tgt['Target revenue'],
            name='Target',
            line=dict(color='rgba(245,158,11,0.45)', width=1.5, dash='dot'),
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
            x=future_dates, y=forecast_vals,
            name='AI Forecast',
            line=dict(color=C['gold'], width=2, dash='dot', shape='spline', smoothing=0.7),
            mode='lines+markers',
            marker=dict(size=5, symbol='diamond', color=C['gold'],
                        line=dict(color='rgba(0,0,0,0.3)', width=1)),
            hovertemplate='<b>%{x|%B %Y}</b><br>Forecast: <b>Rs. %{y:,.0f}</b><extra></extra>'
        ))

        ci_u = [v*1.15 for v in forecast_vals]
        ci_l = [max(0,v*0.85) for v in forecast_vals]
        fig.add_trace(go.Scatter(
            x=future_dates+future_dates[::-1], y=ci_u+ci_l[::-1],
            fill='toself', fillcolor='rgba(245,158,11,0.04)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Confidence Band ±15%',
            hoverinfo='skip'
        ))

    # COVID shading
    fig.add_vrect(
        x0="2020-03-01", x1="2021-07-01",
        fillcolor="rgba(244,63,94,0.04)",
        annotation_text="COVID-19 Impact",
        annotation_position="top left",
        annotation_font=dict(color='rgba(244,63,94,0.7)', size=11, family='DM Mono'),
        line_width=0,
        annotation_borderpad=4,
    )

    fig.update_layout(**PLOTLY_LAYOUT,
                      title="Revenue Trajectory 2017–2028 · Historical + AI Forecast",
                      height=500, xaxis_title="", yaxis_title="Revenue (PKR)")
    return fig


def chart_waterfall_advanced(df, metric='Actual Revenue'):
    d = df.groupby('Months',observed=True)[metric].sum().reset_index()
    d = d[d[metric] > 0]
    if d.empty: return None
    fig = go.Figure(go.Waterfall(
        x=d['Months'].astype(str).tolist(), y=d[metric].tolist(),
        measure=['relative']*len(d),
        text=[fmt_rev(v) for v in d[metric]], textposition='outside',
        textfont=dict(family='DM Mono', size=10, color='#64748b'),
        connector=dict(line=dict(color='rgba(148,163,184,0.15)', width=1, dash='dot')),
        increasing=dict(marker=dict(color='rgba(16,185,129,0.65)', line=dict(color=C['emerald'], width=1.5))),
        decreasing=dict(marker=dict(color='rgba(244,63,94,0.65)', line=dict(color=C['rose'], width=1.5))),
        hovertemplate='<b>%{x}</b><br>' + metric + ': <b>Rs. %{y:,.0f}</b><extra></extra>'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=f"{metric} — Monthly Waterfall Analysis",
                      height=440, xaxis_title="", yaxis_title=metric)
    return fig


def chart_regression_advanced(df):
    d = df[(df['Actual Revenue']>0)&(df['Actual Footfall']>0)].dropna()
    if len(d) < 5: return None
    fig = go.Figure()
    for proj in d['Project'].unique():
        pd_proj = d[d['Project']==proj]
        color = PROJECT_COLORS.get(proj, C['blue'])
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fig.add_trace(go.Scatter(
            x=pd_proj['Actual Footfall'], y=pd_proj['Actual Revenue'],
            mode='markers', name=proj,
            marker=dict(
                color=f'rgba({r},{g},{b},0.65)', size=9, symbol='circle',
                line=dict(color=color, width=1)
            ),
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
        line=dict(color='rgba(245,158,11,0.6)', width=1.5, dash='dash'),
        name=f'Regression (R²={r2:.3f})',
        hovertemplate='Trend: Rs. %{y:,.0f}<extra></extra>'
    ))
    fig.add_annotation(
        text=f"R² = {r2:.3f}   ·   Slope = Rs. {m.coef_[0]:,.0f} / visitor",
        x=0.02, y=0.98, xref='paper', yref='paper', showarrow=False,
        bgcolor='rgba(17,24,39,0.9)', bordercolor='rgba(148,163,184,0.15)',
        font=dict(family='DM Mono', size=11, color='#64748b'), align='left',
        borderwidth=1, borderpad=8, opacity=0.95
    )
    fig.update_layout(**PLOTLY_LAYOUT,
                      title="Revenue vs Footfall — Regression Analysis",
                      height=460, xaxis_title="Footfall (Visitors)",
                      yaxis_title="Revenue (PKR)", hovermode='closest')
    return fig


def chart_pie_advanced(df, val_col, name_col, title):
    d = df.groupby(name_col)[val_col].sum().reset_index()
    d = d[d[val_col] > 0].sort_values(val_col, ascending=False)
    colors = [PROJECT_COLORS.get(n, COLORS[i%len(COLORS)]) for i, n in enumerate(d[name_col])]
    fig = go.Figure(go.Pie(
        values=d[val_col], labels=d[name_col], hole=0.55,
        marker=dict(
            colors=colors,
            line=dict(color='rgba(8,12,20,0.8)', width=2)
        ),
        textinfo='label+percent',
        texttemplate='%{label}<br><b>%{percent}</b>',
        textfont=dict(family='Space Grotesk', size=11, color='white'),
        hovertemplate='<b>%{label}</b><br>Revenue: Rs. %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        insidetextorientation='radial',
    ))
    # Center label
    total = d[val_col].sum()
    fig.add_annotation(
        text=f"<b>{fmt_rev(total)}</b><br>Total",
        x=0.5, y=0.5, xref='paper', yref='paper',
        showarrow=False,
        font=dict(family='Syne', size=14, color='#f1f5f9'),
        align='center'
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=460,
                      hovermode='closest', showlegend=True)
    return fig


# ═══════════════════════════════════════════════════════════════
#  AI QUERY ENGINE
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
                f"### 🔮 AI Forecast — {month_name} {y_val}{proj_str}\n\n"
                f"| Metric | Projection | Lower Bound | Upper Bound |\n"
                f"|--------|------------|-------------|-------------|\n"
                f"| Revenue | **{fmt_rev(p_rev)}** | {fmt_rev(lr)} | {fmt_rev(ur)} |\n"
                f"| Footfall | **{p_ff:,.0f}** | {lf:,.0f} | {uf:,.0f} |\n\n"
                f"**Event Modifiers:** {note_rev}\n"
                f"{eid_note}\n\n"
                f"> *Model: Same-Month Trend (60%) + Polynomial Extrapolation (40%)*"
            )
            return msg, None, None
        else:
            return (
                "🔮 **Forecast requires a Month + Year (2025–2030)**\n\n"
                "*Examples:* `Forecast March 2027` · `Predict July 2026 Joyland Fortress`"
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
            margin = abs(r_chg)
            msg = (
                f"### Comparison: **{l1}** vs **{l2}**\n\n"
                f"| Metric | {l1} | {l2} | Δ Change |\n"
                f"|--------|------|------|----------|\n"
                f"| Revenue | {fmt_rev(r1)} | {fmt_rev(r2)} | `{r_chg:+.1f}%` |\n"
                f"| Footfall | {f1:,.0f} | {f2:,.0f} | `{f_chg:+.1f}%` |\n"
                f"| Rev/Visitor | Rs. {rpp1:,.0f} | Rs. {rpp2:,.0f} | `{rpp_chg:+.1f}%` |\n\n"
                f"{'✅' if r_chg > 0 else '⚠️'} **{winner}** showed `{margin:.1f}%` {'higher' if r_chg > 0 else 'lower'} revenue.\n"
            )
            comp_data = {"labels":[l1,l2],"revenue":[r1,r2],"footfall":[f1,f2]}
            return msg, None, comp_data
        else:
            return "⚠️ No data found for one or both periods.", None, None

    if 'covid' in q or ('2020' in q and any(k in q for k in ['lockdown','impact','why','closed'])):
        msg = (
            "### COVID-19 Impact Analysis — 2020\n\n"
            "| Period | Revenue | vs 2019 | Status |\n"
            "|--------|---------|----------|--------|\n"
            "| Jan–Feb 2020 | Rs. 276M | Normal | Open |\n"
            "| March 2020 | Rs. 92.8M | −40% | Partial Closure |\n"
            "| Apr–Jul 2020 | **Rs. 0** | **−100%** | Complete Closure |\n"
            "| Aug–Dec 2020 | Rs. 97M | −65% | Partial Reopening |\n\n"
            "- Full year 2020 achievement: **49.2%** of target\n"
            "- 2019 → 2020: Rs. 779.9M → Rs. 467.2M (**−40% YoY**)\n"
            "- Full recovery achieved in **2022** (Rs. 1.65B, new record)\n"
        )
        return msg, df[df['Year'].isin([2019,2020,2021])], None

    if any(k in q for k in ['eid','ramadan','ramazan','eid ul fitr','eid ul adha','islamic']):
        msg = (
            "### Islamic Events & Revenue Impact\n\n"
            "**Eid ul Fitr** — largest revenue spike:\n"
            "| Year | Month | Boost |\n|------|-------|-------|\n"
            "| 2023 | April | +48% |\n| 2024 | April | +52% |\n| 2025 | March | +45% est. |\n\n"
            "**Eid ul Adha** — second major boost (~38% above avg):\n"
            "2024 → June · 2025 → June · 2026 → May\n\n"
            "**Ramadan Effect:**\n"
            "- Early Ramadan: −15–20% footfall\n"
            "- Last 10 days: near-zero footfall\n"
            "- Chand Raat → Eid days: massive spike\n"
        )
        return msg, None, None

    if any(k in q for k in ['monsoon','rain','weather','summer']):
        msg = (
            "### Weather & Seasonal Impact\n\n"
            "| Season | Months | Factor |\n|--------|--------|--------|\n"
            "| Summer Peak | Jun, Jul, Aug | +25–35% |\n"
            "| Winter Festive | Dec, Jan | +20–28% |\n"
            "| Monsoon Drag | Jul, Aug | −8% overlay |\n"
            "| Exam Season | May, Oct | −12% |\n\n"
            "**July** = historically highest revenue month (summer + school holidays).\n"
            "**May** = typically slowest (board exam season).\n"
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
            "### Revenue Trend 2017–2026\n\n"
            "| Year | Revenue | Footfall | Achievement | YoY |\n"
            "|------|---------|----------|-------------|-----|\n"
            + "\n".join(rows) + "\n\n"
            "**Highlights:** 🦠 2020 COVID impact · 🚀 2022 Rs. 1.6B milestone · "
            "🏆 2024 Rs. 2.5B record · ⭐ CAGR 2017–2025: ~33%/year\n"
        )
        return msg, df, None

    if any(k in q for k in ['best','worst','highest','lowest','top','bottom','peak']):
        if any(k in q for k in ['month']):
            monthly = df.groupby('Months',observed=True)['Actual Revenue'].sum().reset_index()
            monthly = monthly.sort_values('Actual Revenue', ascending=False)
            best = monthly.iloc[0]
            worst = monthly[monthly['Actual Revenue']>0].iloc[-1]
            msg = (
                f"### Best & Worst Months (All-Time)\n\n"
                f"**Best:** {best['Months']} — {fmt_rev(best['Actual Revenue'])}\n"
                f"**Worst:** {worst['Months']} — {fmt_rev(worst['Actual Revenue'])}\n\n"
                "**Top 3:** " + " · ".join([f"{r['Months']} ({fmt_rev(r['Actual Revenue'])})" for _, r in monthly.head(3).iterrows()])
            )
            return msg, None, None

    proj_kw = ['project','projects','all projects','which project','best project','top project']
    if any(k in q for k in proj_kw):
        d = df.groupby('Project').agg({'Actual Revenue':'sum','Actual Footfall':'sum','Target revenue':'sum'}).reset_index()
        d = d[d['Actual Revenue']>0].sort_values('Actual Revenue', ascending=False)
        d['Ach'] = np.where(d['Target revenue']>0, d['Actual Revenue']/d['Target revenue']*100, 0).round(1)
        d['RPP'] = (d['Actual Revenue']/d['Actual Footfall'].replace(0,np.nan)).round(0)
        rows = []
        for _, r in d.iterrows():
            rows.append(f"| {r['Project']} | {fmt_rev(r['Actual Revenue'])} | {r['Actual Footfall']/1e3:.0f}K | {r['Ach']:.1f}% | Rs. {r['RPP']:,.0f} |")
        msg = (
            "### All Projects — Summary (2017–2026)\n\n"
            "| Project | Revenue | Footfall | Achievement | Rev/Visitor |\n"
            "|---------|---------|----------|-------------|-------------|\n"
            + "\n".join(rows) + "\n\n"
            "🥇 **Joyland Fortress** — flagship, highest revenue · "
            "💡 **B-EMP** — highest revenue per visitor\n"
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
            "### Monthly Revenue Breakdown — All-Time\n\n"
            "| Month | Revenue | Footfall | Rev/Visitor |\n"
            "|-------|---------|----------|-------------|\n"
            + "\n".join(rows) + "\n\n"
            "**July** = peak · **December** = #2 · **May** = slowest (exams)\n"
        )
        return msg, None, None

    ach_kw = ['achievement','achieve','target','vs target','reached','met','goal','performance']
    if any(k in q for k in ach_kw):
        filtered, months, years, project = filter_df(q, df)
        if not filtered.empty:
            act_rev = filtered['Actual Revenue'].sum()
            tgt_rev = filtered['Target revenue'].sum()
            act_ff = filtered['Actual Footfall'].sum()
            tgt_ff = filtered['Target Footfall'].sum()
            rev_ach = act_rev/tgt_rev*100 if tgt_rev > 0 else 0
            ff_ach = act_ff/tgt_ff*100 if tgt_ff > 0 else 0
            s_rev = "✅ TARGET MET" if rev_ach>=100 else "⚠️ NEAR" if rev_ach>=75 else "❌ MISSED"
            s_ff = "✅ TARGET MET" if ff_ach>=100 else "⚠️ NEAR" if ff_ach>=75 else "❌ MISSED"
            proj_str = f" — {project}" if project else ""
            period_str = ", ".join(months + [str(y) for y in years]) if (months or years) else "All Data"
            diff = act_rev - tgt_rev
            surplus = f"\n\n{'Surplus' if diff >= 0 else 'Shortfall'}: **{fmt_rev(abs(diff))}** {'above' if diff >= 0 else 'below'} target." if tgt_rev > 0 else ""
            msg = (
                f"### Target Achievement — {period_str}{proj_str}\n\n"
                f"| Metric | Actual | Target | Achievement | Status |\n"
                f"|--------|--------|--------|-------------|--------|\n"
                f"| Revenue | {fmt_rev(act_rev)} | {fmt_rev(tgt_rev)} | **{rev_ach:.1f}%** | {s_rev} |\n"
                f"| Footfall | {act_ff:,.0f} | {tgt_ff:,.0f} | **{ff_ach:.1f}%** | {s_ff} |\n"
                f"{surplus}"
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
                f"### {q_name}{yr_str}{proj_str} — {', '.join(q_months)}\n\n"
                f"| Metric | Value |\n|--------|-------|\n"
                f"| Revenue | **{fmt_rev(act_rev)}** |\n"
                f"| Footfall | **{act_ff:,.0f}** |\n"
                f"| Target | {fmt_rev(tgt_rev)} |\n"
                f"| Achievement | **{ach:.1f}%** |\n"
            )
            if act_ff > 0:
                msg += f"| Rev/Visitor | **Rs. {act_rev/act_ff:,.0f}** |"
            return msg, filtered, None

    rpp_kw = ['revenue per','per visitor','spend per','rev per','rpp','spending','average spend']
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
            f"### Revenue Per Visitor — {period}{proj_str}\n\n"
            f"| Metric | Value |\n|--------|-------|\n"
            f"| Revenue | {fmt_rev(rev)} |\n"
            f"| Footfall | {ff:,.0f} |\n"
            f"| Rev/Visitor | **Rs. {rpp:,.0f}** |\n"
            f"| All-Time Avg | Rs. {all_rpp:,.0f} |\n"
            f"| vs Avg | `{(rpp-all_rpp)/all_rpp*100:+.1f}%` |"
        )
        return msg, filtered if not filtered.empty else None, None

    filtered, months, years, project = filter_df(q, df)

    want_rev = any(k in q for k in ['revenue','rev','income','earning','sales'])
    want_ff = any(k in q for k in ['footfall','foot fall','visitors','attendance','customers','guest'])
    want_both = not want_rev and not want_ff

    if filtered.empty:
        return (
            "⚠️ **No data matched.** Try:\n\n"
            "- `Revenue July 2023`\n- `Footfall 2024 Fortress`\n"
            "- `August 2023 vs August 2024`\n- `Forecast March 2027`\n"
            "- `Q1 2024 achievement`\n- `Revenue trend`\n\n"
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
        rows.append(f"| Revenue | **{fmt_rev(act_rev)}** |")
        if tgt_rev > 0:
            rows.append(f"| Target Revenue | {fmt_rev(tgt_rev)} |")
            rows.append(f"| Achievement | **{rev_ach:.1f}%** |")
    if want_ff or want_both:
        rows.append(f"| Footfall | **{act_ff:,.0f}** |")
        if tgt_ff > 0:
            rows.append(f"| Target Footfall | {tgt_ff:,.0f} |")
            if ff_ach: rows.append(f"| FF Achievement | **{ff_ach:.1f}%** |")
    if want_both and act_ff > 0:
        rows.append(f"| Rev/Visitor | **Rs. {rpp:,.0f}** |")
    if n_months > 1 and (want_rev or want_both):
        rows.append(f"| Avg Monthly Rev | {fmt_rev(act_rev/n_months)} |")

    msg = f"### Analysis — {period_desc}\n\n| Metric | Value |\n|--------|-------|\n"
    msg += "\n".join(rows)

    if rev_ach:
        if rev_ach >= 100:
            msg += f"\n\n✅ Target exceeded — **{rev_ach:.1f}%** achieved. Surplus: {fmt_rev(act_rev-tgt_rev)}"
        elif rev_ach >= 85:
            msg += f"\n\n⚠️ Near target — **{rev_ach:.1f}%** achieved, {fmt_rev(tgt_rev-act_rev)} short"
        else:
            msg += f"\n\n❌ Below target — **{rev_ach:.1f}%** achieved"

    return msg, filtered, None


# ═══════════════════════════════════════════════════════════════
#  INTRO / HELP MESSAGES
# ═══════════════════════════════════════════════════════════════
def _intro_message():
    return (
        "### Welcome to Joyland MIS v7.0\n\n"
        "I'm the **Joyland MIS AI Assistant** — trained on 2017–2026 data across 8 projects, "
        "built by **MIS Assistant Manager Umair Nizam**.\n\n"
        "| Query Type | Example |\n|---|---|\n"
        "| Revenue | `Revenue July 2023` |\n"
        "| Footfall | `Footfall 2024 Joyland Fortress` |\n"
        "| Comparison | `August 2023 vs August 2024` |\n"
        "| AI Forecast | `Forecast March 2027` |\n"
        "| Achievement | `Target achievement 2025` |\n"
        "| Trends | `Revenue trend all years` |\n"
        "| Events | `Eid impact` · `COVID 2020` · `Monsoon effect` |\n\n"
        "**Ask me anything.**"
    )

def _help_message():
    return (
        "### Query Guide\n\n"
        "**Revenue:** `Revenue July 2023` · `Total revenue 2024` · `Revenue Q1 2023`\n\n"
        "**Footfall:** `Footfall August 2024` · `Total visitors 2023`\n\n"
        "**Compare:** `July 2023 vs July 2024` · `2023 vs 2024` · `Fortress 2024 vs JAP-OD 2024`\n\n"
        "**Forecast (2025–2030):** `Forecast March 2027` · `Predict December 2028 Fortress`\n\n"
        "**Pakistan Events:** `Eid impact` · `Monsoon effect` · `PSL cricket impact` · `COVID 2020`\n\n"
        "**Analysis:** `Revenue trend` · `Best month` · `Monthly breakdown` · `Achievement 2024` · `Rev per visitor 2025`"
    )


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
def render_sidebar(df, auth_obj=None):
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style='padding: 20px 4px 12px;'>
          <div style='font-family: var(--font-mono, DM Mono), monospace; font-size: 9px;
               letter-spacing: 3px; color: #475569; text-transform: uppercase; margin-bottom: 6px;'>
            Management Information System
          </div>
          <div style='font-family: var(--font-display, Syne), sans-serif; font-size: 20px;
               font-weight: 800; color: #f1f5f9; letter-spacing: -0.5px; line-height: 1;'>
            Joyland
            <span style='color: #3b82f6;'>MIS</span>
          </div>
          <div style='font-family: DM Mono, monospace; font-size: 9px; color: #475569;
               letter-spacing: 1.5px; margin-top: 4px;'>v7.0 APEX · 2017–2030</div>
        </div>
        <div style='height: 1px; background: linear-gradient(90deg, rgba(59,130,246,0.3), transparent); margin: 4px 0 16px;'></div>
        """, unsafe_allow_html=True)

        # Status
        analyst_name = st.session_state.get('name', 'Analyst')
        st.markdown(f"""
        <div style='background: rgba(17,24,39,0.8); border: 1px solid rgba(148,163,184,0.08);
             border-radius: 12px; padding: 14px; margin-bottom: 14px;'>
          <div style='font-family: DM Mono, monospace; font-size: 9px; letter-spacing: 1.5px;
               color: #475569; text-transform: uppercase; margin-bottom: 4px;'>Active User</div>
          <div style='font-family: Syne, sans-serif; font-size: 14px; font-weight: 700;
               color: #f1f5f9;'>{analyst_name}</div>
          <div style='display: flex; align-items: center; gap: 6px; margin-top: 10px;
               font-family: DM Mono, monospace; font-size: 9px; color: #10b981; letter-spacing: 2px;'>
            <span style='width: 6px; height: 6px; background: #10b981; border-radius: 50%;
                  display: inline-block; animation: pulse-anim 2s infinite;'></span>
            AI ENGINE ACTIVE
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_filtered_df = None
            st.session_state.comparison_data = None
            st.rerun()

        if auth_obj:
            auth_obj.logout('Sign Out', 'sidebar')

        st.markdown("<div style='height:1px;background:rgba(148,163,184,0.06);margin:12px 0;'></div>", unsafe_allow_html=True)

        # Data scope
        if not df.empty:
            projects = df['Project'].nunique() if 'Project' in df.columns else 0
            records = len(df)
            min_yr = int(df['Year'].min()) if 'Year' in df.columns else 2017
            max_yr = int(df['Year'].max()) if 'Year' in df.columns else 2026
            st.markdown(f"""
            <div style='background: rgba(17,24,39,0.6); border: 1px solid rgba(148,163,184,0.07);
                 border-radius: 12px; padding: 14px; margin-bottom: 14px;'>
              <div style='font-family: DM Mono, monospace; font-size: 9px; letter-spacing: 1.5px;
                   color: #475569; text-transform: uppercase; margin-bottom: 10px;'>Data Scope</div>
              <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px;'>
                <div style='background: rgba(59,130,246,0.05); border-radius: 8px; padding: 10px; border: 1px solid rgba(59,130,246,0.1);'>
                  <div style='font-family: DM Mono; font-size: 9px; color: #475569; margin-bottom: 3px;'>PERIOD</div>
                  <div style='font-family: Syne; font-size: 13px; font-weight: 700; color: #f1f5f9;'>{min_yr}–{max_yr}</div>
                </div>
                <div style='background: rgba(245,158,11,0.04); border-radius: 8px; padding: 10px; border: 1px solid rgba(245,158,11,0.1);'>
                  <div style='font-family: DM Mono; font-size: 9px; color: #475569; margin-bottom: 3px;'>RECORDS</div>
                  <div style='font-family: Syne; font-size: 13px; font-weight: 700; color: #f1f5f9;'>{records:,}</div>
                </div>
                <div style='background: rgba(16,185,129,0.04); border-radius: 8px; padding: 10px; border: 1px solid rgba(16,185,129,0.1);'>
                  <div style='font-family: DM Mono; font-size: 9px; color: #475569; margin-bottom: 3px;'>PROJECTS</div>
                  <div style='font-family: Syne; font-size: 13px; font-weight: 700; color: #f1f5f9;'>{projects}</div>
                </div>
                <div style='background: rgba(139,92,246,0.04); border-radius: 8px; padding: 10px; border: 1px solid rgba(139,92,246,0.1);'>
                  <div style='font-family: DM Mono; font-size: 9px; color: #475569; margin-bottom: 3px;'>MODEL</div>
                  <div style='font-family: Syne; font-size: 10px; font-weight: 700; color: #f1f5f9;'>AI+Events</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Quick queries
        quick_queries = [
            ("Revenue July 2024", "rev"),
            ("Footfall 2025", "ff"),
            ("Aug 2023 vs Aug 2024", "cmp"),
            ("Forecast March 2027", "fcast"),
            ("Revenue trend", "trend"),
            ("Q1 2024 Fortress", "q"),
            ("Achievement 2025", "ach"),
            ("All projects comparison", "proj"),
            ("COVID impact 2020", "event"),
            ("Eid impact on revenue", "event"),
        ]
        st.markdown("""
        <div style='background: rgba(17,24,39,0.5); border: 1px solid rgba(148,163,184,0.07);
             border-radius: 12px; padding: 14px;'>
          <div style='font-family: DM Mono, monospace; font-size: 9px; letter-spacing: 1.5px;
               color: #475569; text-transform: uppercase; margin-bottom: 10px;'>Quick Queries</div>
        """, unsafe_allow_html=True)
        for qk, _ in quick_queries:
            st.markdown(f"""
            <div style='font-family: DM Mono, monospace; font-size: 10px; color: #64748b;
                 padding: 5px 0; border-bottom: 1px solid rgba(148,163,184,0.04);
                 cursor: default; transition: color 0.15s;'>
              <span style='color: #3b82f6; margin-right: 6px;'>›</span>{qk}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='padding: 14px 0 4px; text-align: center;'>
          <div style='font-family: DM Mono, monospace; font-size: 9px; color: #2d3f55; letter-spacing: 1px;'>
            Architect: <span style='color: #3b82f6;'>Umair Nizam</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Joyland MIS · v7.0 Apex",
        layout="wide", page_icon="📊",
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
        auth = Authenticate(credentials, "joyland_mis", "auth_key_v7", cookie_expiry_days=30)
        auth.login(location='main')
        is_auth = st.session_state.get("authentication_status")
    except ImportError:
        st.warning("⚠️ streamlit-authenticator not installed. Running in demo mode.")
        is_auth = True
        auth = None

    if not is_auth:
        st.markdown("""
        <div style='max-width:420px;margin:80px auto;text-align:center;'>
          <div style='font-family:Syne,sans-serif;font-size:32px;font-weight:800;color:#f1f5f9;
               letter-spacing:-1px;margin-bottom:8px;'>
            Joyland <span style='color:#3b82f6;'>MIS</span>
          </div>
          <div style='font-family:DM Mono,monospace;font-size:11px;letter-spacing:2px;color:#475569;
               margin-bottom:32px;text-transform:uppercase;'>
            Intelligence Platform · v7.0 Apex
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    render_sidebar(df, auth)

    # ── HERO BANNER ──
    if not df.empty:
        total_rev = df['Actual Revenue'].sum()
        total_ff = df['Actual Footfall'].sum()
        max_yr = df['Year'].max()
    else:
        total_rev = total_ff = 0
        max_yr = 2026

    st.markdown(f"""
    <div class='hero-banner'>
      <div class='hero-banner-inner'>
        <div class='hero-left'>
          <div class='hero-eyebrow'>Management Information System · v7.0 Apex</div>
          <div class='hero-title'>Joyland <span>Analytics</span></div>
          <div class='hero-sub'>Advanced Business Intelligence Platform · Pakistan Events AI Engine · 2017–2030 Forecast</div>
        </div>
        <div class='hero-right'>
          <div>
            <div style='display:flex;align-items:center;gap:16px;'>
              <div class='hero-stat'>
                <div class='hero-stat-val'>{fmt_rev(total_rev)}</div>
                <div class='hero-stat-label'>Lifetime Revenue</div>
              </div>
              <div class='hero-stat'>
                <div class='hero-stat-val'>{total_ff/1e6:.1f}M</div>
                <div class='hero-stat-label'>Total Visitors</div>
              </div>
            </div>
          </div>
          <div class='status-chip'><span class='pulse'></span>AI Engine Active</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI CARDS ──
    if not df.empty:
        try:
            total_tgt = df['Target revenue'].sum()
            ach = total_rev/total_tgt*100 if total_tgt > 0 else 0
            rpp = total_rev/total_ff if total_ff > 0 else 0
            last_yr = df[df['Year']==max_yr]['Actual Revenue'].sum()
            prev_yr = df[df['Year']==max_yr-1]['Actual Revenue'].sum()
            yoy_g = (last_yr-prev_yr)/prev_yr*100 if prev_yr > 0 else 0
            delta_cls = "up" if yoy_g >= 0 else "down"
            delta_sym = "↑" if yoy_g >= 0 else "↓"

            st.markdown(f"""
            <div class='kpi-row'>
              <div class='kpi-card blue'>
                <span class='kpi-icon'>💰</span>
                <div class='kpi-label'>Lifetime Revenue</div>
                <div class='kpi-value'>{fmt_rev(total_rev)}</div>
                <div class='kpi-delta neutral'>2017 – {max_yr}</div>
              </div>
              <div class='kpi-card gold'>
                <span class='kpi-icon'>👥</span>
                <div class='kpi-label'>Total Visitors</div>
                <div class='kpi-value'>{total_ff/1e6:.2f}M</div>
                <div class='kpi-delta neutral'>Cumulative</div>
              </div>
              <div class='kpi-card green'>
                <span class='kpi-icon'>🎯</span>
                <div class='kpi-label'>Avg Achievement</div>
                <div class='kpi-value'>{ach:.1f}%</div>
                <div class='kpi-delta up'>vs All Targets</div>
              </div>
              <div class='kpi-card violet'>
                <span class='kpi-icon'>💡</span>
                <div class='kpi-label'>Rev / Visitor</div>
                <div class='kpi-value'>Rs.{rpp:,.0f}</div>
                <div class='kpi-delta neutral'>Lifetime Avg</div>
              </div>
              <div class='kpi-card amber'>
                <span class='kpi-icon'>📈</span>
                <div class='kpi-label'>YoY Growth</div>
                <div class='kpi-value'>{yoy_g:+.1f}%</div>
                <div class='kpi-delta {delta_cls}'>{delta_sym} {int(max_yr-1)}→{int(max_yr)}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass

    # ── AI INSIGHT ──
    if not df.empty:
        try:
            best_proj = df.groupby('Project')['Actual Revenue'].sum().idxmax()
            peak_month = df.groupby('Months',observed=True)['Actual Revenue'].sum().idxmax()
            best_year_row = df.groupby('Year')['Actual Revenue'].sum()
            best_year = best_year_row.idxmax()
            all_rpp = df['Actual Revenue'].sum()/df['Actual Footfall'].sum()
            st.markdown(f"""
            <div class='insight-card'>
              <span class='insight-label'>◈ AI System Intelligence</span>
              <div class='insight-text'>
                Peak revenue month: <strong>{peak_month}</strong> &nbsp;·&nbsp;
                Top project: <strong>{best_proj}</strong> &nbsp;·&nbsp;
                Best year: <strong>{best_year}</strong> ({fmt_rev(best_year_row[best_year])}) &nbsp;·&nbsp;
                Lifetime Rev/Visitor: <strong>Rs. {all_rpp:,.0f}</strong> &nbsp;·&nbsp;
                CAGR 2017–2025: <strong>~33%/year</strong>
              </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass

    # ── SECTION: AI CHAT ──
    st.markdown("""
    <div class='section-hdr'>
      <span class='section-hdr-text'>AI Analytics Assistant</span>
      <div class='section-hdr-line'></div>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["is_user"] else "assistant"):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything — Revenue · Footfall · Comparison · Forecast · Eid · Monsoon · Trends…")

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

        st.markdown("""
        <div class='section-hdr'>
          <span class='section-hdr-text'>Visual Intelligence Panel</span>
          <div class='section-hdr-line'></div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Deep Analysis", "Projects",
            "Forecast", "Data Export"
        ])

        with tab1:
            # Comparison chart
            if st.session_state.comparison_data:
                cd = st.session_state.comparison_data
                fig_comp = go.Figure()
                for i, (lbl, rev, ff) in enumerate(zip(cd['labels'], cd['revenue'], cd['footfall'])):
                    color = [C['blue'], C['gold']][i]
                    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
                    fig_comp.add_trace(go.Bar(
                        name=f'{lbl}', x=[lbl], y=[rev],
                        marker=dict(
                            color=f'rgba({r},{g},{b},0.75)',
                            line=dict(color=color, width=1.5),
                            cornerradius=4,
                        ),
                        text=[fmt_rev(rev)], textposition='outside',
                        textfont=dict(family='DM Mono', size=11, color='#64748b'),
                        hovertemplate=f'<b>{lbl}</b><br>Revenue: <b>Rs. %{{y:,.0f}}</b><extra></extra>'
                    ))
                fig_comp.update_layout(**PLOTLY_LAYOUT, barmode='group',
                    title="Period Comparison — Revenue", height=420,
                    xaxis_title="", yaxis_title="Revenue (PKR)", bargap=0.5)
                st.plotly_chart(fig_comp, use_container_width=True)
                st.divider()

            chart_opt = st.selectbox("Select Visualization", [
                "Revenue Achievement Gauge",
                "Footfall Achievement Gauge",
                "Revenue: Actual vs Target",
                "Revenue Trend (Area + Peaks)",
                "Footfall Trend (Area + Peaks)",
                "Monthly Waterfall",
                "Revenue Share by Month",
                "Revenue Share by Project",
                "Footfall vs Revenue Regression",
                "Year-over-Year Comparison",
            ])

            res = df_plot[[c for c in ['Actual Revenue','Actual Footfall','Target revenue','Target Footfall'] if c in df_plot.columns]].sum()

            if chart_opt == "Revenue Achievement Gauge":
                st.plotly_chart(chart_gauge(res.get('Actual Revenue',0), res.get('Target revenue',0), "Revenue Achievement"), use_container_width=True)
            elif chart_opt == "Footfall Achievement Gauge":
                st.plotly_chart(chart_gauge(res.get('Actual Footfall',0), res.get('Target Footfall',0), "Footfall Achievement"), use_container_width=True)
            elif chart_opt == "Revenue: Actual vs Target":
                cols = [c for c in ['Actual Revenue','Target revenue'] if c in df_plot.columns]
                agg = df_plot.groupby('Months',observed=True)[cols].sum().reset_index()
                st.plotly_chart(chart_bar_labeled(agg,'Months',cols,"Revenue: Actual vs Target","","Revenue (PKR)"), use_container_width=True)
            elif chart_opt == "Revenue Trend (Area + Peaks)":
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(chart_trend_advanced(df_plot.sort_values('Date_Obj'),'Actual Revenue',C['blue'],'Revenue Trend'), use_container_width=True)
            elif chart_opt == "Footfall Trend (Area + Peaks)":
                if 'Actual Footfall' in df_plot.columns:
                    st.plotly_chart(chart_trend_advanced(df_plot.sort_values('Date_Obj'),'Actual Footfall',C['gold'],'Footfall Trend'), use_container_width=True)
            elif chart_opt == "Monthly Waterfall":
                fig_wf = chart_waterfall_advanced(df_plot)
                if fig_wf: st.plotly_chart(fig_wf, use_container_width=True)
            elif chart_opt == "Revenue Share by Month":
                if 'Actual Revenue' in df_plot.columns:
                    st.plotly_chart(chart_pie_advanced(df_plot,'Actual Revenue','Months',"Revenue Distribution by Month"), use_container_width=True)
            elif chart_opt == "Revenue Share by Project":
                if 'Project' in df_plot.columns:
                    st.plotly_chart(chart_pie_advanced(df_plot,'Actual Revenue','Project',"Revenue Distribution by Project"), use_container_width=True)
            elif chart_opt == "Footfall vs Revenue Regression":
                fig_r = chart_regression_advanced(df_plot)
                if fig_r: st.plotly_chart(fig_r, use_container_width=True)
            elif chart_opt == "Year-over-Year Comparison":
                st.plotly_chart(chart_yoy_advanced(df_plot), use_container_width=True)

            # Summary row
            disp = [c for c in ['Actual Revenue','Target revenue','Actual Footfall','Target Footfall'] if c in df_plot.columns]
            if disp:
                summary = df_plot[disp].sum().to_frame("Total").T
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                st.dataframe(
                    summary.style.format("{:,.0f}")
                    .set_properties(**{
                        'background-color':'#111827',
                        'color':'#94a3b8',
                        'border':'1px solid rgba(148,163,184,0.08)',
                        'font-family':'DM Mono, monospace',
                        'font-size':'12px'
                    }),
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

                proj_sum = df_plot.groupby('Project').agg({
                    'Actual Revenue':'sum','Actual Footfall':'sum','Target revenue':'sum'
                })
                proj_sum['Achievement'] = (proj_sum['Actual Revenue']/proj_sum['Target revenue']*100).where(proj_sum['Target revenue']>0,0).round(1)
                proj_sum['Rev/Visitor'] = (proj_sum['Actual Revenue']/proj_sum['Actual Footfall'].replace(0,np.nan)).round(0)
                proj_sum = proj_sum.sort_values('Actual Revenue', ascending=False)

                rows_html = ""
                for proj, row in proj_sum.iterrows():
                    ach = row['Achievement']
                    badge_cls = "good" if ach >= 90 else "warn" if ach >= 75 else "bad"
                    rows_html += f"""
                    <tr>
                      <td><strong style='color:#f1f5f9;font-family:Space Grotesk,sans-serif;'>{proj}</strong></td>
                      <td style='font-family:DM Mono,monospace;color:#3b82f6;'>{fmt_rev(row['Actual Revenue'])}</td>
                      <td style='font-family:DM Mono,monospace;'>{row['Actual Footfall']/1e3:.0f}K</td>
                      <td><span class='badge {badge_cls}'>{ach:.1f}%</span></td>
                      <td style='font-family:DM Mono,monospace;'>Rs. {row["Rev/Visitor"]:,.0f}</td>
                    </tr>"""

                st.markdown(f"""
                <div style='background:rgba(17,24,39,0.6);border:1px solid rgba(148,163,184,0.08);border-radius:14px;overflow:hidden;margin-top:16px;'>
                <table class='pro-table'>
                  <thead>
                    <tr><th>Project</th><th>Revenue</th><th>Footfall</th><th>Achievement</th><th>Rev/Visitor</th></tr>
                  </thead>
                  <tbody>{rows_html}</tbody>
                </table>
                </div>
                """, unsafe_allow_html=True)

        with tab4:
            st.markdown("""
            <div class='section-hdr'>
              <span class='section-hdr-text'>Predictive Analytics Engine</span>
              <div class='section-hdr-line'></div>
            </div>
            """, unsafe_allow_html=True)

            if not df.empty:
                st.plotly_chart(chart_forecast_trajectory_advanced(df), use_container_width=True)

                st.markdown("""
                <div style='font-family:Space Grotesk,sans-serif;font-size:14px;font-weight:600;
                     color:#f1f5f9;margin:20px 0 12px;'>Manual Forecast Generator</div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    m_sel = st.selectbox("Month", ['January','February','March','April','May','June',
                                                    'July','August','September','October','November','December'])
                with col2:
                    y_sel = st.selectbox("Year", list(range(2025,2031)))
                with col3:
                    p_sel = st.selectbox("Project", ['All Projects'] + sorted(df['Project'].unique().tolist()))

                if st.button("Generate Forecast", use_container_width=True):
                    m_idx = MONTH_MAP[m_sel.lower()]
                    df_src = df if p_sel == 'All Projects' else df[df['Project']==p_sel]
                    p_rev,(lr,ur),note_rev = generate_advanced_forecast(df_src, m_idx, y_sel, 'Actual Revenue')
                    p_ff,(lf,uf),note_ff = generate_advanced_forecast(df_src, m_idx, y_sel, 'Actual Footfall')

                    eid_alert = ""
                    if y_sel in EID_FITR_MONTHS and m_idx in EID_FITR_MONTHS[y_sel]:
                        eid_alert = "🌙 **Eid ul Fitr** expected — significant footfall spike projected."
                    if y_sel in EID_ADHA_MONTHS and m_idx in EID_ADHA_MONTHS[y_sel]:
                        eid_alert += "\n🐑 **Eid ul Adha** expected — revenue boost projected."

                    st.markdown(f"""
                    <div class='forecast-panel'>
                      <span class='forecast-label'>◈ AI Forecast · {m_sel.upper()} {y_sel} · {p_sel}</span>
                      <div class='forecast-metrics'>
                        <div class='fm-card fm-rev'>
                          <div class='fm-label'>Revenue Projection</div>
                          <div class='fm-value'>{fmt_rev(p_rev)}</div>
                          <div class='fm-range'>Range: {fmt_rev(lr)} — {fmt_rev(ur)}</div>
                        </div>
                        <div class='fm-card fm-ff'>
                          <div class='fm-label'>Footfall Projection</div>
                          <div class='fm-value'>{p_ff:,.0f}</div>
                          <div class='fm-range'>Range: {lf:,.0f} — {uf:,.0f}</div>
                        </div>
                      </div>
                      <div class='fm-modifiers'>
                        <strong style='color:#94a3b8;'>Applied Modifiers:</strong> {note_rev}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if eid_alert:
                        st.info(eid_alert)

                    same_m_hist = df_src[df_src['Month_Num']==m_idx].groupby('Year').agg({'Actual Revenue':'sum'}).reset_index().tail(5)
                    if not same_m_hist.empty:
                        st.markdown(f"<div style='font-family:DM Mono;font-size:11px;color:#475569;margin:14px 0 8px;text-transform:uppercase;letter-spacing:1.5px;'>Historical {m_sel} Revenue</div>", unsafe_allow_html=True)
                        same_m_hist['Actual Revenue'] = same_m_hist['Actual Revenue'].apply(fmt_rev)
                        st.dataframe(same_m_hist.rename(columns={'Actual Revenue':'Revenue'}), use_container_width=True)

                # Event Calendar
                st.markdown("""
                <div class='event-calendar'>
                  <div class='ec-title'>◈ Pakistan Event Calendar — Forecast Basis</div>
                  <div class='ec-row'>
                    <span class='ec-key'>🌙 Eid ul Fitr</span>
                    <span class='ec-val'>2025→Mar · 2026→Mar · 2027→Mar · 2028→Feb · 2029→Feb · 2030→Jan</span>
                  </div>
                  <div class='ec-row'>
                    <span class='ec-key'>🐑 Eid ul Adha</span>
                    <span class='ec-val'>2025→Jun · 2026→May · 2027→May · 2028→May · 2029→Apr · 2030→Apr</span>
                  </div>
                  <div class='ec-row'>
                    <span class='ec-key'>📚 Exam Season (low)</span>
                    <span class='ec-val'>May (Boards) · October (Midterms) — applied −12%</span>
                  </div>
                  <div class='ec-row'>
                    <span class='ec-key'>🌧️ Monsoon Adjustment</span>
                    <span class='ec-val'>July · August — applied −8%</span>
                  </div>
                  <div class='ec-row'>
                    <span class='ec-key'>🇵🇰 Independence Day</span>
                    <span class='ec-val'>August 14 — applied +8%</span>
                  </div>
                  <div class='ec-row'>
                    <span class='ec-key'>🎆 Winter Festive</span>
                    <span class='ec-val'>December +10% · January +5%</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        with tab5:
            st.markdown(f"""
            <div style='font-family:DM Mono,monospace;font-size:10px;color:#475569;
                 letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;'>
              {len(df_plot):,} records in current dataset
            </div>
            """, unsafe_allow_html=True)
            display_cols = [c for c in df_plot.columns if c not in ['Month_Num','Date_Obj','Fiscal_Year_Label']]
            num_cols = [c for c in display_cols if pd.api.types.is_numeric_dtype(df_plot[c])]
            st.dataframe(
                df_plot[display_cols].style.format({c:'{:,.0f}' for c in num_cols})
                .set_properties(**{
                    'background-color':'#111827','color':'#94a3b8',
                    'border':'1px solid rgba(148,163,184,0.06)',
                    'font-family':'DM Mono, monospace','font-size':'12px'
                }),
                use_container_width=True, height=520
            )
            csv = df_plot.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Export as CSV", data=csv,
                file_name=f"joyland_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime='text/csv', use_container_width=True
            )

    # ── FOOTER ──
    if not df.empty:
        records = len(df)
        projects = df['Project'].nunique() if 'Project' in df.columns else 0
    else:
        records, projects = 0, 0

    st.markdown(f"""
    <div class='footer-bar'>
      <div class='footer-brand'>Joyland <span>MIS</span> · v7.0 Apex</div>
      <div class='footer-meta'>
        Architect: Umair Nizam · {records:,} records · {projects} projects · AI + Pakistan Events Model
      </div>
      <div style='display:flex;align-items:center;gap:6px;font-family:DM Mono,monospace;
           font-size:9px;color:#10b981;letter-spacing:2px;text-transform:uppercase;'>
        <span style='width:5px;height:5px;background:#10b981;border-radius:50%;
              display:inline-block;animation:pulse-anim 2s infinite;'></span>
        Online
      </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
