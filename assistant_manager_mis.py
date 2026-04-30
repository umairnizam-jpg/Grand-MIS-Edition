# app.py
# Joyland MIS AI Assistant - Single File Expert Edition
# Streamlit app with:
# - Preserved login credentials exactly as requested
# - Smart Excel ingestion
# - Dark UI redesign
# - KPI dashboard
# - Advanced charts
# - Forecasting with Pakistani / Islamic / weather / trend heuristics
# - PDF / Excel / Word upload with immediate AI processing
# - Export to PDF / Excel / Word
# - Optional OpenAI integration for global search & comparison
# - Retains AI insights, download buttons, project analysis, forecasting, raw data, etc.

import os
import re
import io
import math
import json
import time
import base64
import textwrap
import traceback
from io import BytesIO
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Optional / graceful imports
try:
    import requests
except Exception:
    requests = None

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

try:
    from pypdf import PdfReader
    PDF_READER_AVAILABLE = True
except Exception:
    PDF_READER_AVAILABLE = False

try:
    from docx import Document as WordDocument
    from docx.shared import Inches
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table as RLTable,
        TableStyle, Image as RLImage
    )
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


# -----------------------------------------------------------------------------
# STREAMLIT CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Joyland MIS AI Assistant",
    page_icon="🎡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
APP_TITLE = "Joyland MIS AI Assistant"
APP_VERSION = "Expert Edition 5.0"
LOGIN_USERNAME = "admin"          # preserve exactly
LOGIN_PASSWORD = "MIS2024@secure" # preserve exactly

DEFAULT_DATA_PATHS = [
    "RAW DATA.xlsx",
    "./RAW DATA.xlsx",
    os.path.join(os.getcwd(), "RAW DATA.xlsx"),
    "/mnt/data/RAW DATA.xlsx",
    "/workspace/RAW DATA.xlsx",
]

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}
MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
QUARTER_MAP = {
    "q1": [1, 2, 3],
    "q2": [4, 5, 6],
    "q3": [7, 8, 9],
    "q4": [10, 11, 12],
}
MONTH_PATTERN = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b",
    re.IGNORECASE,
)

# Example project aliases; dynamic matching from actual data is also applied
PROJECT_ALIASES = {
    "fortress": "Joyland Fortress",
    "joyland fortress": "Joyland Fortress",
    "super space": "Super Space",
    "joyland": "Joyland",
    "lahore": "Joyland Lahore",
    "karachi": "Joyland Karachi",
    "rawalpindi": "Joyland Rawalpindi",
    "gujranwala": "Joyland Gujranwala",
    "multan": "Joyland Multan",
}

# Islamic / Pakistan event effects (heuristic calendar months)
# You can refine these yearly if needed.
EID_CALENDAR = {
    2025: {3: "Ramadan / Eid-ul-Fitr", 6: "Eid-ul-Adha"},
    2026: {3: "Ramadan / Eid-ul-Fitr", 5: "Eid-ul-Adha"},
    2027: {2: "Ramadan / Eid-ul-Fitr", 5: "Eid-ul-Adha"},
    2028: {2: "Ramadan / Eid-ul-Fitr", 4: "Eid-ul-Adha"},
    2029: {1: "Ramadan / Eid-ul-Fitr", 4: "Eid-ul-Adha"},
    2030: {1: "Ramadan / Eid-ul-Fitr", 3: "Eid-ul-Adha", 12: "Ramadan lead-in"},
}

PAKISTAN_CITY_CONTEXT = {
    "Lahore": {"lat": 31.5204, "lon": 74.3587},
    "Karachi": {"lat": 24.8607, "lon": 67.0011},
    "Islamabad": {"lat": 33.6844, "lon": 73.0479},
    "Rawalpindi": {"lat": 33.5651, "lon": 73.0169},
}

# Dark theme colors
COLORS = {
    "bg": "#07111f",
    "panel": "#0c1729",
    "panel2": "#0f1f36",
    "border": "#1d3357",
    "text": "#e8eefc",
    "muted": "#9fb4d9",
    "accent": "#5eead4",
    "accent2": "#8b5cf6",
    "accent3": "#38bdf8",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "pink": "#ec4899",
    "gold": "#fbbf24",
}

# Small retained knowledge base / fallback context
KNOWLEDGE_BASE = {
    "best_month": "July",
    "worst_month": "May",
    "peak_year": 2025,
    "covid_note": "COVID-19 caused a clear performance dip during the pandemic period.",
    "growth_note_2022": "2022 marked a strong post-COVID recovery phase.",
}


# -----------------------------------------------------------------------------
# CSS / THEME
# -----------------------------------------------------------------------------
def inject_dark_css():
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {COLORS["bg"]};
            --panel: {COLORS["panel"]};
            --panel2: {COLORS["panel2"]};
            --border: {COLORS["border"]};
            --text: {COLORS["text"]};
            --muted: {COLORS["muted"]};
            --accent: {COLORS["accent"]};
            --accent2: {COLORS["accent2"]};
            --accent3: {COLORS["accent3"]};
            --success: {COLORS["success"]};
            --warning: {COLORS["warning"]};
            --danger: {COLORS["danger"]};
            --gold: {COLORS["gold"]};
        }}

        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(56,189,248,0.08), transparent 22%),
                radial-gradient(circle at top left, rgba(139,92,246,0.08), transparent 25%),
                linear-gradient(180deg, #06101c 0%, #07111f 100%);
            color: var(--text);
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #08111d 0%, #0c1729 100%);
            border-right: 1px solid var(--border);
        }}

        .block-container {{
            padding-top: 1.3rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}

        h1, h2, h3, h4, h5, h6, p, div, span, label {{
            color: var(--text) !important;
        }}

        .hero-card {{
            background: linear-gradient(135deg, rgba(14,27,48,0.96), rgba(9,19,34,0.96));
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 22px 24px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.28);
            margin-bottom: 1rem;
        }}

        .mini-card {{
            background: linear-gradient(180deg, rgba(12,23,41,0.96), rgba(8,17,31,0.96));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 10px 26px rgba(0,0,0,0.18);
        }}

        .metric-card {{
            background: linear-gradient(180deg, rgba(15,31,54,0.95), rgba(10,20,36,0.95));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px 18px;
            min-height: 124px;
            box-shadow: 0 14px 28px rgba(0,0,0,0.22);
        }}

        .metric-label {{
            color: var(--muted) !important;
            font-size: 0.92rem;
            letter-spacing: 0.02em;
            margin-bottom: 10px;
        }}

        .metric-value {{
            font-size: 1.75rem;
            font-weight: 800;
            line-height: 1.15;
            color: var(--text) !important;
        }}

        .metric-sub {{
            margin-top: 8px;
            color: var(--muted) !important;
            font-size: 0.88rem;
        }}

        .insight-box {{
            background: rgba(15,31,54,0.72);
            border: 1px solid var(--border);
            border-left: 5px solid var(--accent);
            border-radius: 16px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background: transparent;
            padding-bottom: 10px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: #0b1525;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 10px 16px;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(180deg, #11213a, #0d1c31) !important;
            border-color: #31558d !important;
        }}

        div[data-testid="stMetric"] {{
            background: linear-gradient(180deg, rgba(15,31,54,0.9), rgba(10,20,36,0.9));
            border: 1px solid var(--border);
            padding: 12px;
            border-radius: 16px;
        }}

        .stTextInput > div > div,
        .stNumberInput > div > div,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextArea textarea {{
            background: #0d1a2e !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
        }}

        .stButton button,
        .stDownloadButton button {{
            background: linear-gradient(180deg, #13233d, #0e1c30) !important;
            color: white !important;
            border: 1px solid #2a4677 !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 0.55rem 0.9rem !important;
        }}

        .stButton button:hover,
        .stDownloadButton button:hover {{
            border-color: var(--accent) !important;
            transform: translateY(-1px);
        }}

        .stDataFrame, .stTable {{
            background: transparent !important;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
        }}

        .chat-bubble {{
            background: rgba(15,31,54,0.78);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 12px 14px;
        }}

        .small-muted {{
            color: var(--muted) !important;
            font-size: 0.88rem;
        }}

        hr {{
            border-color: var(--border);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "authenticated": False,
        "chat_history": [],
        "pending_prompt": "",
        "uploaded_docs": [],
        "uploaded_excel_frames": [],
        "openai_key": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def clean_text(s) -> str:
    return str(s).strip() if s is not None else ""

def normalize_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).strip().lower()).strip()

def fmt_int(x) -> str:
    try:
        return f"{int(round(float(x))):,}"
    except Exception:
        return "0"

def fmt_num(x) -> str:
    try:
        return f"{float(x):,.2f}"
    except Exception:
        return "0.00"

def fmt_currency(x) -> str:
    try:
        return f"Rs. {float(x):,.0f}"
    except Exception:
        return "Rs. 0"

def fmt_pct(x) -> str:
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return "0.0%"

def safe_div(a, b):
    try:
        if b in [0, None] or pd.isna(b):
            return 0.0
        return float(a) / float(b)
    except Exception:
        return 0.0

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def month_to_num(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)) and 1 <= int(value) <= 12:
        return int(value)
    text = normalize_key(value)
    for k, v in MONTH_MAP.items():
        if text == k:
            return v
    for k, v in MONTH_MAP.items():
        if k in text:
            return v
    return np.nan

def month_to_name(value):
    try:
        return MONTH_NAMES.get(int(value), str(value))
    except Exception:
        return str(value)

def current_year():
    return datetime.now().year

def current_month():
    return datetime.now().month


# -----------------------------------------------------------------------------
# OPENAI / WEB SEARCH INTEGRATION
# -----------------------------------------------------------------------------
def get_secret_value(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def get_openai_api_key(manual_key: str = "") -> str:
    if manual_key:
        return manual_key.strip()
    env_key = os.getenv("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    secret_key = get_secret_value("OPENAI_API_KEY", "").strip()
    return secret_key

def extract_response_text(resp_json: dict) -> str:
    if not resp_json:
        return ""
    if isinstance(resp_json, dict) and resp_json.get("output_text"):
        return resp_json["output_text"]

    parts = []
    try:
        for item in resp_json.get("output", []):
            for c in item.get("content", []):
                if c.get("type") in ("output_text", "text"):
                    t = c.get("text", "")
                    if t:
                        parts.append(t)
        return "\n".join(parts).strip()
    except Exception:
        return ""

def call_openai_analysis(
    user_query: str,
    data_context: str = "",
    doc_context: str = "",
    use_web_search: bool = False,
    manual_key: str = "",
) -> Optional[str]:
    api_key = get_openai_api_key(manual_key)
    if not api_key or requests is None:
        return None

    system_prompt = (
        "You are an expert Pakistani business intelligence analyst. "
        "Use the provided data context first. If web search is enabled, use it only for fresh market/global comparison "
        "and clearly separate external insight from internal MIS data. "
        "Be precise, concise, and business-focused."
    )

    payload = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": (
                    f"User query:\n{user_query}\n\n"
                    f"Internal data context:\n{data_context[:18000]}\n\n"
                    f"Uploaded files context:\n{doc_context[:14000]}\n\n"
                    "Return a direct answer with numbers where available."
                )
            }
        ]
    }

    if use_web_search:
        payload["tools"] = [{"type": "web_search_preview"}]

    try:
        resp = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=90,
        )
        if resp.status_code >= 400:
            return None
        data = resp.json()
        text = extract_response_text(data)
        return text.strip() if text else None
    except Exception:
        return None


# -----------------------------------------------------------------------------
# DATA INGESTION
# -----------------------------------------------------------------------------
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    original_cols = list(df.columns)

    rename_map = {}
    used_targets = set()

    def assign(col, target):
        if target not in used_targets:
            rename_map[col] = target
            used_targets.add(target)

    for col in original_cols:
        ck = normalize_key(col)

        if any(k in ck for k in ["project", "park", "site", "branch", "location", "property", "venue"]):
            assign(col, "Project")
        elif ck in ["year", "yr"] or ("year" in ck and "fiscal" not in ck):
            assign(col, "Year")
        elif "month" in ck or ck in ["mnth", "period"]:
            assign(col, "Month")
        elif "date" == ck or ck.startswith("date "):
            assign(col, "Date")
        elif "fiscal year" in ck or ck == "fy":
            assign(col, "Fiscal Year")
        elif ("actual" in ck and "revenue" in ck) or ck in ["revenue", "sales", "actual revenue"]:
            assign(col, "Actual Revenue")
        elif "target" in ck and "revenue" in ck:
            assign(col, "Target Revenue")
        elif (
            ("actual" in ck and ("footfall" in ck or "visitor" in ck or "pax" in ck))
            or ck in ["footfall", "visitors", "visitor", "pax", "actual footfall"]
        ):
            assign(col, "Actual Footfall")
        elif "target" in ck and ("footfall" in ck or "visitor" in ck or "pax" in ck):
            assign(col, "Target Footfall")

    df = df.rename(columns=rename_map)

    # Ensure core columns exist
    for col in [
        "Project", "Year", "Month", "Date",
        "Actual Revenue", "Target Revenue",
        "Actual Footfall", "Target Footfall"
    ]:
        if col not in df.columns:
            df[col] = np.nan

    return df

def normalize_dataframe(df: pd.DataFrame, source_name: str = "") -> pd.DataFrame:
    df = standardize_columns(df)

    # remove completely empty rows
    df = df.dropna(how="all").copy()

    # Parse date if available
    if "Date" in df.columns:
        try:
            parsed_date = pd.to_datetime(df["Date"], errors="coerce")
            if parsed_date.notna().sum() > 0:
                missing_year = df["Year"].isna()
                df.loc[missing_year, "Year"] = parsed_date.dt.year[missing_year]
                missing_month = df["Month"].isna()
                df.loc[missing_month, "Month"] = parsed_date.dt.month[missing_month]
        except Exception:
            pass

    # Month normalize
    if "Month" in df.columns:
        df["Month_Num"] = df["Month"].apply(month_to_num)
    else:
        df["Month_Num"] = np.nan

    # Year normalize
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # If Month missing but Date exists
    if df["Month_Num"].isna().all() and "Date" in df.columns:
        try:
            parsed_date = pd.to_datetime(df["Date"], errors="coerce")
            df["Month_Num"] = parsed_date.dt.month
            df["Year"] = df["Year"].fillna(parsed_date.dt.year)
        except Exception:
            pass

    # Month name
    df["Month_Name"] = df["Month_Num"].apply(
        lambda x: MONTH_NAMES.get(int(x), "") if pd.notna(x) else ""
    )

    # Numeric conversions
    for col in ["Actual Revenue", "Target Revenue", "Actual Footfall", "Target Footfall"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("Rs.", "", regex=False)
                .str.replace("PKR", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Project normalize
    if "Project" in df.columns:
        df["Project"] = df["Project"].astype(str).str.strip().replace({"nan": "Unknown"})
    else:
        df["Project"] = "Unknown"

    # Build Date_Obj
    try:
        tmp_year = df["Year"].fillna(current_year()).astype(int)
        tmp_month = df["Month_Num"].fillna(1).astype(int)
        df["Date_Obj"] = pd.to_datetime(
            {
                "year": tmp_year,
                "month": tmp_month,
                "day": 1
            },
            errors="coerce"
        )
    except Exception:
        df["Date_Obj"] = pd.NaT

    # Fiscal year label (Jul-Jun)
    def fy_label(row):
        try:
            y = int(row["Year"])
            m = int(row["Month_Num"])
            start_y = y if m >= 7 else y - 1
            end_y = start_y + 1
            return f"FY {start_y}-{str(end_y)[-2:]}"
        except Exception:
            return ""

    df["Fiscal_Year_Label"] = df.apply(fy_label, axis=1)
    df["__source__"] = source_name or df.get("__source__", "Primary")
    df = df.sort_values(["Date_Obj", "Project"], na_position="last").reset_index(drop=True)
    return df

def read_excel_any(excel_source, source_name="Primary") -> Optional[pd.DataFrame]:
    try:
        xls = pd.ExcelFile(excel_source)
        frames = []
        for sheet in xls.sheet_names:
            tmp = pd.read_excel(xls, sheet_name=sheet)
            if tmp is None or tmp.empty:
                continue
            norm = normalize_dataframe(tmp, source_name=f"{source_name} | {sheet}")
            if norm.shape[1] >= 4:
                frames.append(norm)
        if frames:
            out = pd.concat(frames, ignore_index=True)
            return out
    except Exception:
        try:
            tmp = pd.read_excel(excel_source)
            return normalize_dataframe(tmp, source_name=source_name)
        except Exception:
            return None
    return None

def load_primary_data() -> pd.DataFrame:
    for path in DEFAULT_DATA_PATHS:
        if os.path.exists(path):
            df = read_excel_any(path, source_name="Primary Local File")
            if df is not None and not df.empty:
                return df
    return pd.DataFrame()

def combine_dataframes(frames: List[pd.DataFrame]) -> pd.DataFrame:
    valid = [f for f in frames if f is not None and not f.empty]
    if not valid:
        return pd.DataFrame()
    df = pd.concat(valid, ignore_index=True)
    # de-duplicate softly
    dedupe_cols = [c for c in ["Project", "Year", "Month_Num", "Actual Revenue", "Actual Footfall", "Target Revenue", "Target Footfall"] if c in df.columns]
    if dedupe_cols:
        df = df.drop_duplicates(subset=dedupe_cols, keep="last")
    return df.sort_values(["Date_Obj", "Project"], na_position="last").reset_index(drop=True)


# -----------------------------------------------------------------------------
# DOCUMENT PARSING
# -----------------------------------------------------------------------------
def extract_pdf_text(file_bytes: bytes) -> str:
    if not PDF_READER_AVAILABLE:
        return "PDF parser not installed. Please install pypdf."
    try:
        reader = PdfReader(BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts).strip()
    except Exception as e:
        return f"Unable to parse PDF: {e}"

def extract_docx_text(file_bytes: bytes) -> str:
    if not DOCX_AVAILABLE:
        return "Word parser not installed. Please install python-docx."
    try:
        doc = WordDocument(BytesIO(file_bytes))
        texts = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(texts).strip()
    except Exception as e:
        # weak fallback for .doc files
        try:
            return file_bytes.decode("utf-8", errors="ignore")[:15000]
        except Exception:
            return f"Unable to parse Word file: {e}"

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())

def local_text_summary(text: str, max_sentences: int = 5) -> str:
    if not text:
        return "No readable text found."
    clean = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    if not sentences:
        return clean[:600]
    return " ".join(sentences[:max_sentences])[:1200]

def retrieve_relevant_sentences(query: str, docs: List[dict], top_k: int = 6) -> List[str]:
    q_terms = set(tokenize(query))
    results = []

    for doc in docs:
        text = doc.get("text", "")
        name = doc.get("name", "Document")
        if not text:
            continue
        chunks = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text))
        for chunk in chunks:
            c = chunk.strip()
            if len(c) < 35:
                continue
            c_terms = set(tokenize(c))
            score = len(q_terms & c_terms)
            if score > 0:
                results.append((score, f"[{name}] {c}"))

    results = sorted(results, key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:top_k]]

def process_uploaded_files(uploaded_files, manual_openai_key="") -> Tuple[List[pd.DataFrame], List[dict]]:
    excel_frames = []
    docs = []

    if not uploaded_files:
        return excel_frames, docs

    for up in uploaded_files:
        try:
            name = up.name
            ext = os.path.splitext(name.lower())[1]
            file_bytes = up.getvalue()

            if ext in [".xlsx", ".xlsm", ".xls"]:
                df = read_excel_any(BytesIO(file_bytes), source_name=f"Uploaded Excel: {name}")
                if df is not None and not df.empty:
                    excel_frames.append(df)
                    docs.append({
                        "name": name,
                        "type": "excel",
                        "summary": f"Excel file processed successfully. Rows: {len(df):,}, Projects: {df['Project'].nunique() if 'Project' in df.columns else 0}",
                        "text": df.head(25).to_string(index=False),
                    })

            elif ext == ".pdf":
                text = extract_pdf_text(file_bytes)
                ai_summary = call_openai_analysis(
                    user_query=f"Summarize this uploaded PDF in 6 bullet points for a business analyst.\n\n{text[:12000]}",
                    data_context="",
                    doc_context="",
                    use_web_search=False,
                    manual_key=manual_openai_key,
                )
                docs.append({
                    "name": name,
                    "type": "pdf",
                    "summary": ai_summary or local_text_summary(text),
                    "text": text[:25000],
                })

            elif ext in [".docx", ".doc"]:
                text = extract_docx_text(file_bytes)
                ai_summary = call_openai_analysis(
                    user_query=f"Summarize this uploaded Word document in 6 bullet points for a business analyst.\n\n{text[:12000]}",
                    data_context="",
                    doc_context="",
                    use_web_search=False,
                    manual_key=manual_openai_key,
                )
                docs.append({
                    "name": name,
                    "type": "word",
                    "summary": ai_summary or local_text_summary(text),
                    "text": text[:25000],
                })

        except Exception as e:
            docs.append({
                "name": getattr(up, "name", "Unknown File"),
                "type": "unknown",
                "summary": f"Could not process file: {e}",
                "text": "",
            })

    return excel_frames, docs


# -----------------------------------------------------------------------------
# ANALYSIS / SUMMARIES
# -----------------------------------------------------------------------------
def ensure_core_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ["Actual Revenue", "Target Revenue", "Actual Footfall", "Target Footfall"]:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

def yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = ensure_core_metrics(df)
    grp = (
        df.groupby("Year", dropna=True)[["Actual Revenue", "Target Revenue", "Actual Footfall", "Target Footfall"]]
        .sum()
        .reset_index()
        .sort_values("Year")
    )
    grp["Revenue Achievement %"] = np.where(grp["Target Revenue"] > 0, grp["Actual Revenue"] / grp["Target Revenue"] * 100, 0)
    grp["Footfall Achievement %"] = np.where(grp["Target Footfall"] > 0, grp["Actual Footfall"] / grp["Target Footfall"] * 100, 0)
    grp["Rev/Pax"] = np.where(grp["Actual Footfall"] > 0, grp["Actual Revenue"] / grp["Actual Footfall"], 0)
    grp["Revenue YoY %"] = grp["Actual Revenue"].pct_change() * 100
    grp["Footfall YoY %"] = grp["Actual Footfall"].pct_change() * 100
    return grp

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = ensure_core_metrics(df)
    grp = (
        df.groupby(["Month_Num", "Month_Name"], dropna=True)[["Actual Revenue", "Actual Footfall", "Target Revenue", "Target Footfall"]]
        .sum()
        .reset_index()
        .sort_values("Month_Num")
    )
    grp["Rev/Pax"] = np.where(grp["Actual Footfall"] > 0, grp["Actual Revenue"] / grp["Actual Footfall"], 0)
    grp["Revenue Achievement %"] = np.where(grp["Target Revenue"] > 0, grp["Actual Revenue"] / grp["Target Revenue"] * 100, 0)
    return grp

def project_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Project" not in df.columns:
        return pd.DataFrame()
    df = ensure_core_metrics(df)
    grp = (
        df.groupby("Project", dropna=True)[["Actual Revenue", "Target Revenue", "Actual Footfall", "Target Footfall"]]
        .sum()
        .reset_index()
        .sort_values("Actual Revenue", ascending=False)
    )
    grp["Achievement %"] = np.where(grp["Target Revenue"] > 0, grp["Actual Revenue"] / grp["Target Revenue"] * 100, 0)
    grp["Rev/Pax"] = np.where(grp["Actual Footfall"] > 0, grp["Actual Revenue"] / grp["Actual Footfall"], 0)
    return grp

def kpi_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "revenue": 0, "footfall": 0, "avg_achievement": 0,
            "rev_pax": 0, "yoy_growth": 0,
        }
    ys = yearly_summary(df)
    total_rev = df["Actual Revenue"].sum() if "Actual Revenue" in df.columns else 0
    total_ff = df["Actual Footfall"].sum() if "Actual Footfall" in df.columns else 0
    avg_ach = 0
    if "Target Revenue" in df.columns and df["Target Revenue"].sum() > 0:
        avg_ach = safe_div(total_rev, df["Target Revenue"].sum()) * 100
    rev_pax = safe_div(total_rev, total_ff)
    yoy = 0
    if not ys.empty and len(ys) >= 2:
        yoy = ys["Revenue YoY %"].iloc[-1] if pd.notna(ys["Revenue YoY %"].iloc[-1]) else 0
    return {
        "revenue": total_rev,
        "footfall": total_ff,
        "avg_achievement": avg_ach,
        "rev_pax": rev_pax,
        "yoy_growth": yoy,
    }

def build_ai_insights(df: pd.DataFrame) -> List[str]:
    if df.empty:
        return ["No data available yet. Upload Excel/PDF/Word files or place RAW DATA.xlsx next to this app."]
    ys = yearly_summary(df)
    ms = monthly_summary(df)
    ps = project_summary(df)

    insights = []

    if not ys.empty:
        peak_year_row = ys.loc[ys["Actual Revenue"].idxmax()]
        insights.append(
            f"Peak revenue year: {int(peak_year_row['Year'])} with {fmt_currency(peak_year_row['Actual Revenue'])}."
        )
        if len(ys) >= 2:
            last = ys.iloc[-1]
            insights.append(
                f"Latest year revenue growth: {fmt_pct(last['Revenue YoY %'] if pd.notna(last['Revenue YoY %']) else 0)}."
            )

    if not ms.empty:
        best_month_row
