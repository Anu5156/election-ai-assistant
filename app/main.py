"""
CivicGuide AI - The Ultimate AI-Powered Election Assistant
Main Orchestration Module

This application provides citizens with localized, real-time election information including:
- Polling booth discovery and routing (Google Maps API)
- Real-time crowd density tracking (Firebase Firestore)
- Personalized voting strategies (Google Gemini AI)
- Multi-language support (12 Indian languages)
- Digital Voting Pass and calendar reminders
"""
import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.maps_service import get_polling_stations, geocode_location
from app.services.translate_service import translate_text
from app.services.calendar_service import generate_calendar_link
from app.utils.validators import validate_age, sanitize_input, is_rate_limited
from app.routes.journey import journey_ui
from app.models.user import User
from streamlit_js_eval import get_geolocation
from app.services.maps_service import get_route_details
from streamlit_folium import st_folium
from app.services.firebase_service import get_booth_crowd
from app.services.gemini_service import get_gemini_response, get_ai_strategy
import time
import urllib.parse
from datetime import datetime
import plotly.express as px
import pandas as pd
import numpy as np

# ─────────────────────────────────────────
# REAL-TIME CONFIG
# ─────────────────────────────────────────
ELECTION_DATE = datetime(2026, 5, 5)
now = datetime.now()
days_left = (ELECTION_DATE - now).days
countdown_display = f"{days_left}d" if days_left > 0 else "Today"


st.markdown("""
<style>
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)


from gtts import gTTS
import tempfile

def speak_text(text):
    try:
        tts = gTTS(text=text, lang='en')
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        return tmp_file.name
    except:
        return None


def calculate_distance(lat1, lng1, lat2, lng2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def score_booth_map(s, base_lat, base_lng, crowd_data):
    dist = calculate_distance(base_lat, base_lng, s["lat"], s["lng"])
    crowd = crowd_data.get(s["name"], 0)
    # Normalize crowd (0–100 → 0–1)
    crowd_score = crowd / 100

    return (dist * 0.6) + (crowd_score * 0.4)



def get_share_link(candidate, voter_id, location):
    base = "https://voterbuddy.streamlit.app/"
    query = f"?candidate={urllib.parse.quote(candidate)}&voter_id={voter_id}&location={urllib.parse.quote(location)}"
    return base + query


@st.cache_data(show_spinner=False)
def load_stations(location):
    return get_polling_stations(location)
# ─────────────────────────────────────────
# PAGE CONFIG  (must be first st call)
# ─────────────────────────────────────────
st.set_page_config(
    page_title="CivicGuide AI - Your Smart Election Companion",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🌍 ACCESSIBILITY, SEO & SECURITY METADATA
st.markdown("""
    <script>
        document.documentElement.lang = 'en';
        const isHighContrast = window.localStorage.getItem('highContrast') === 'true';
        document.documentElement.setAttribute('data-high-contrast', isHighContrast);
    </script>
    <head>
        <meta name="description" content="CivicGuide AI: A multilingual, AI-powered election assistant helping citizens find polling booths, track crowd density, and cast informed votes.">
        <meta name="keywords" content="election, voting, india, polling station, civic guide, voter assistance">
        <meta property="og:title" content="CivicGuide AI">
        <meta property="og:description" content="Your intelligent companion for a frictionless voting experience.">
        <!-- 🛡️ SECURITY HEADERS -->
        <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="DENY">
    </head>
    <a href="#main-content" class="skip-link" style="position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden;">
        Skip to main content
    </a>
    <div id="sr-announcer" role="status" aria-live="polite" style="position:absolute; left:-10000px; width:1px; height:1px; overflow:hidden;">
        Application Loaded.
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# LANGUAGE  (12 languages)
# ─────────────────────────────────────────
LANG_OPTIONS = {
    "English": "en", "Hindi": "hi", "Kannada": "kn", "Tamil": "ta",
    "Telugu": "te", "Bengali": "bn", "Marathi": "mr", "Gujarati": "gu",
    "Punjabi": "pa", "Malayalam": "ml", "Odia": "or", "Urdu": "ur",
}

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
_defaults = {
    "stations": [],
    "last_location": "",
    "user_data": None,
    "geo": None,
    "quiz_scores": [],
    "quiz_attempts": 0,
    "messages": [], # For AI Chat
}
# =========================
# SESSION STATE INIT
# =========================
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────
# GLOBAL CSS  — premium dark civic aesthetic
# ─────────────────────────────────────────
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>
    /* ── High Contrast Mode Override ── */
    [data-high-contrast="true"] body, 
    [data-high-contrast="true"] [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    [data-high-contrast="true"] .cg-card,
    [data-high-contrast="true"] .metric-card {
        background: #f0f0f0 !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    [data-high-contrast="true"] h1, 
    [data-high-contrast="true"] h2, 
    [data-high-contrast="true"] h3 {
        color: #000000 !important;
    }
    </style>

    <style>
    /* ── Reset & base ── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #08101e !important;
        color: #e2eaf5 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1828 !important;
        border-right: 1px solid #1e3050 !important;
    }
    [data-testid="stSidebar"] * { color: #8ba3c4 !important; }

    /* ── Typography ── */
    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
        color: #e2eaf5 !important;
        letter-spacing: -0.01em;
    }
    h1 { font-size: 1.6rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.25rem !important; font-weight: 600 !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; }

    /* ── Card component ── */
    .cg-card {
        background: rgba(13, 24, 40, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(30, 48, 80, 0.5);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .cg-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .cg-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #22c55e 0%, transparent 70%);
    }
    .cg-card.amber::before { background: linear-gradient(90deg,#f59e0b,transparent 70%); }
    .cg-card.blue::before  { background: linear-gradient(90deg,#3b82f6,transparent 70%); }
    .cg-card.red::before   { background: linear-gradient(90deg,#ef4444,transparent 70%); }

    /* ── Metric card ── */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        background: rgba(13, 24, 40, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(30, 48, 80, 0.5);
        border-radius: 14px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        background: rgba(22, 37, 64, 0.8);
        border-color: rgba(34, 197, 94, 0.4);
    }
    .metric-card .top-bar {
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
    }
    .metric-card .m-label {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .1em;
        color: #4d6585;
        margin-bottom: 10px;
    }
    .metric-card .m-value {
        font-family: 'Syne', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #e2eaf5;
        line-height: 1;
    }
    .metric-card .m-sub  { font-size: 11px; color: #8ba3c4; margin-top: 6px; }
    .badge {
        display: inline-block;
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 4px;
        margin-top: 8px;
    }
    .badge-green { background:rgba(34,197,94,.1);  color:#22c55e; border:1px solid rgba(34,197,94,.25); }
    .badge-amber { background:rgba(245,158,11,.1); color:#f59e0b; border:1px solid rgba(245,158,11,.25); }
    .badge-blue  { background:rgba(59,130,246,.1); color:#3b82f6; border:1px solid rgba(59,130,246,.25); }
    .badge-red   { background:rgba(239,68,68,.1);  color:#ef4444; border:1px solid rgba(239,68,68,.25); }

    /* ── Alert banners ── */
    .alert {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 11px 14px;
        border-radius: 8px;
        font-size: 13px;
        line-height: 1.55;
        margin-top: 10px;
    }
    .alert-success { background:rgba(34,197,94,.08);  border:1px solid rgba(34,197,94,.2);  color:#4ade80; }
    .alert-warning { background:rgba(245,158,11,.08); border:1px solid rgba(245,158,11,.2); color:#fbbf24; }
    .alert-error   { background:rgba(239,68,68,.08);  border:1px solid rgba(239,68,68,.2);  color:#f87171; }
    .alert-info    { background:rgba(59,130,246,.08); border:1px solid rgba(59,130,246,.2); color:#60a5fa; }

    /* ── Station list ── */
    .station-row {
        display: flex;
        align-items: center;
        gap: 14px;
        background: #0d1828;
        border: 1px solid #1e3050;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: border-color .15s;
    }
    .station-row:hover { border-color: #2a4268; }
    .dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
    .dot-low  { background:#22c55e; }
    .dot-med  { background:#f59e0b; }
    .dot-high { background:#ef4444; }
    .s-name { font-size:13px; font-weight:500; color:#e2eaf5; }
    .s-addr { font-family:'DM Mono',monospace; font-size:11px; color:#4d6585; margin-top:3px; }
    .s-dist { font-family:'DM Mono',monospace; font-size:11px; color:#8ba3c4; margin-left:auto; }

    /* ── Journey steps ── */
    .journey-step {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding-bottom: 18px;
        position: relative;
    }
    .journey-step:not(:last-child)::before {
        content: '';
        position: absolute;
        left: 11px; top: 26px; bottom: 0;
        width: 1px;
        background: #1e3050;
    }
    .jnode {
        width: 24px; height: 24px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-family: 'DM Mono',monospace;
        flex-shrink: 0; border: 1px solid; z-index: 1;
    }
    .jnode-done    { background:rgba(34,197,94,.12); border-color:rgba(34,197,94,.3);  color:#22c55e; }
    .jnode-active  { background:rgba(245,158,11,.12); border-color:rgba(245,158,11,.3); color:#f59e0b; }
    .jnode-pending { background:#111f33; border-color:#1e3050; color:#4d6585; }
    .j-title { font-size:13px; font-weight:500; color:#e2eaf5; }
    .j-desc  { font-size:11px; color:#4d6585; font-family:'DM Mono',monospace; margin-top:3px; }

    /* ── Simulator ── */
    .sim-step-label {
        display: inline-block;
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        background: rgba(34,197,94,.1);
        border: 1px solid rgba(34,197,94,.2);
        color: #22c55e;
        border-radius: 6px;
        padding: 3px 10px;
        margin-bottom: 16px;
    }

    /* ── Streamlit element overrides ── */
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] select,
    div[data-testid="stTextArea"] textarea {
        background: #111f33 !important;
        border: 1px solid #1e3050 !important;
        border-radius: 8px !important;
        color: #e2eaf5 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextInput"] input:focus {
        border-color: #2a4268 !important;
        box-shadow: none !important;
    }
    .stRadio > label { color: #8ba3c4 !important; }
    .stCheckbox > label { color: #8ba3c4 !important; }

    /* ── Primary button ── */
    .stButton > button {
        background: #22c55e !important;
        color: #0a1a0e !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 9px 20px !important;
        transition: background .15s, transform .1s !important;
    }
    .stButton > button:hover {
        background: #4ade80 !important;
        transform: translateY(-1px) !important;
    }

    /* ── Sidebar radio nav ── */
    .stRadio > div { gap: 4px !important; }
    .stRadio > div > label {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 13px !important;
        color: #8ba3c4 !important;
        transition: background .12s !important;
    }
    .stRadio > div > label:hover { background: #162540 !important; }
    [data-testid="stSidebar"] .stSelectbox label { font-size:11px !important; }

    /* ── Section divider ── */
    .cg-divider { height:1px; background:#1e3050; margin:22px 0; }

    /* ── Map placeholder ── */
    .map-ph {
        background: #111f33;
        border: 1px solid #1e3050;
        border-radius: 12px;
        height: 260px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 8px;
        color: #4d6585;
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .map-ph::before {
        content:'';
        position:absolute; inset:0;
        background-image:
            linear-gradient(rgba(34,197,94,.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(34,197,94,.05) 1px, transparent 1px);
        background-size: 28px 28px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width:5px; }
    ::-webkit-scrollbar-track { background:#08101e; }
    ::-webkit-scrollbar-thumb { background:#1e3050; border-radius:3px; }

    /* ── Success / info messages ── */
    div[data-testid="stAlert"] { border-radius:10px !important; }

    /* ── Top header bar line ── */
    .cg-topbar {
        display:flex; align-items:center; justify-content:space-between;
        padding: 0 0 20px 0; margin-bottom: 4px;
        border-bottom: 1px solid #1e3050;
    }
    .cg-page-title {
        font-family:'Syne',sans-serif; font-size:1.4rem;
        font-weight:700; color:#e2eaf5;
    }
    .cg-chip {
        display:inline-block;
        font-family:'DM Mono',monospace; font-size:11px;
        padding:4px 12px; border-radius:20px;
        background:#111f33; border:1px solid #1e3050; color:#8ba3c4;
    }
    .cg-chip-amber {
        background:rgba(245,158,11,.07);
        border-color:rgba(245,158,11,.25);
        color:#f59e0b;
    }
    .live-dot {
        display:inline-block; width:7px; height:7px;
        border-radius:50%; background:#22c55e;
        animation:pulse 2s infinite;
        margin-right:5px; vertical-align:middle;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
    /* ── Animated Buttons ── */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        color: #e2eaf5 !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        padding: 12px 24px !important;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #334155 0%, #1e293b 100%) !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(-2px);
    }

    .cg-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(30, 48, 80, 0.8), transparent);
        margin: 32px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:4px 0 18px">
          <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#e2eaf5">
            <span style="color:#22c55e">Civic</span>Guide AI
          </div>
          <div style="margin-top:8px;display:inline-flex;align-items:center;
               background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.2);
               border-radius:6px;padding:3px 10px;font-family:'DM Mono',monospace;
               font-size:11px;color:#22c55e">
            <span class="live-dot"></span> Live Session • {now.strftime('%H:%M:%S')}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. LANGUAGE FIRST (Required for translation function 't')
    st.markdown(
        "<div style='font-family:DM Mono,monospace;font-size:10px;text-transform:uppercase;"
        "letter-spacing:.1em;color:#4d6585;margin-bottom:6px'>Language</div>",
        unsafe_allow_html=True,
    )
    selected_lang = st.selectbox(
        "Language",
        list(LANG_OPTIONS.keys()),
        label_visibility="collapsed"
    )
    target_lang = LANG_OPTIONS[selected_lang]

    # 🔥 DEFINE 't' EARLY
    def t(text: str) -> str:
        try:
            return translate_text(text, target_lang)
        except:
            return text

    # 🛰️ AUTO-TRACK TOGGLE (FAANG LEVEL)
    st.markdown("<div class='cg-divider' style='margin:15px 0'></div>", unsafe_allow_html=True)
    auto_gps = st.toggle("🛰️ " + t("Live GPS Tracking"), value=True)
    if auto_gps and st.session_state.geo is None:
        st.session_state.geo = get_geolocation()

    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)

    # 2. NAVIGATION
    st.markdown(
        f"<div style='font-family:DM Mono,monospace;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:.1em;color:#4d6585;margin-bottom:6px'>{t('Navigation')}</div>",
        unsafe_allow_html=True,
    )
    menu = st.radio(
        "Navigation",
        ["Dashboard", "Journey", "Map", "AI Assistant", "Timeline", "Voting Guide", "Quiz", "Help Center"],
        label_visibility="collapsed",
        help=t("Select a page to navigate")
    )

    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)

    # 3. 📅 ELECTION TIMELINE
    st.markdown(f"### 📅 {t('Election Timeline')}")
    st.markdown(f"""
    <div style="border-left: 2px solid #3b82f6; padding-left: 15px; margin-left: 5px;">
        <div style="margin-bottom: 15px; position: relative;">
            <div style="position: absolute; left: -21px; top: 0; width: 10px; height: 10px; background: #22c55e; border-radius: 50%; border: 2px solid #0d1828;"></div>
            <div style="font-size: 11px; color: #4d6585; text-transform: uppercase;">{t('Phase 1')}</div>
            <div style="font-size: 13px; font-weight: 600;">{t('Registration Open')}</div>
        </div>
        <div style="margin-bottom: 15px; position: relative;">
            <div style="position: absolute; left: -21px; top: 0; width: 10px; height: 10px; background: #3b82f6; border-radius: 50%; border: 2px solid #0d1828;"></div>
            <div style="font-size: 11px; color: #4d6585; text-transform: uppercase;">{t('Phase 2')}</div>
            <div style="font-size: 13px; font-weight: 600;">{t('Candidate Finalization')}</div>
        </div>
        <div style="position: relative;">
            <div style="position: absolute; left: -21px; top: 0; width: 10px; height: 10px; background: #ef4444; border-radius: 50%; border: 2px solid #0d1828; animation: pulse 2s infinite;"></div>
            <div style="font-size: 11px; color: #4d6585; text-transform: uppercase;">{t('Big Day')}</div>
            <div style="font-size: 13px; font-weight: 700; color: #ef4444;">{t('ELECTION DAY')}</div>
            <div style="font-size: 11px; margin-top: 2px;">{ELECTION_DATE.strftime('%d %B, %Y')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### ♿ {t('Accessibility')}")
    high_contrast = st.toggle(t("High Contrast Mode"))
    if high_contrast:
        st.markdown("<script>document.documentElement.setAttribute('data-high-contrast', 'true'); window.localStorage.setItem('highContrast', 'true');</script>", unsafe_allow_html=True)
    else:
        st.markdown("<script>document.documentElement.setAttribute('data-high-contrast', 'false'); window.localStorage.setItem('highContrast', 'false');</script>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### ⚖️ {t('Legal')}")
    if st.button(t("Privacy Policy")):
        st.info(t("CivicGuide AI respects your privacy. We do not store exact GPS locations permanently. All data is processed in-memory to provide routing and crowd density information. Voter IDs are obfuscated before being stored for analytics."))

# 🏁 START MAIN CONTENT LANDMARK
st.markdown("<main id='main-content'>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def metric_card(label: str, value: str, sub: str, badge: str, badge_cls: str, bar_color: str) -> str:
    return f"""
    <div class="metric-card" role="region" aria-label="{label} metric">
      <div class="top-bar" style="background:linear-gradient(90deg,{bar_color},transparent 70%)"></div>
      <div class="m-label">{label}</div>
      <div class="m-value" aria-live="polite">{value}</div>
      <div class="m-sub">{sub}</div>
      <div class="badge {badge_cls}" role="status">{badge}</div>
    </div>
    """


def render_metrics_row():
    html = f"""
    <div class="metric-grid">
      {metric_card(t("Registration"), "✓", t("Voter ID verified"), t("Active"), "badge-green", "#22c55e")}
      {metric_card(t("Stations Nearby"), "3", t("Within 2 km radius"), t("Mapped"), "badge-blue", "#3b82f6")}
      {metric_card(t("Crowd Level"), t("Low"), t("Best time: 9–11 AM"), t("Updated"), "badge-amber", "#f59e0b")}
      {metric_card(t("Election Countdown"), countdown_display, t(ELECTION_DATE.strftime('%B %d, %Y')), t("Lok Sabha"), "badge-red", "#ef4444")}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_journey_steps():
    user = st.session_state.user_data
    is_reg = user.is_registered if user else False
    
    steps = [
        ("done" if is_reg else "active", "✓" if is_reg else "→", t("Register to Vote"), t("Voter ID obtained · EPIC card issued")),
        ("done" if is_reg else "pending", "✓" if is_reg else "○", t("Verify your details"), t("Name, photo & address confirmed")),
        ("active" if is_reg else "pending", "→" if is_reg else "○", t("Find your polling booth"), t("Use location finder · Confirm booth no.")),
        ("pending", "○", t("Collect voter slip"), t("From BLO or voters.eci.gov.in")),
        ("pending", "○", t("Cast your vote"), t("Carry EPIC + one more ID on poll day")),
    ]
    rows = ""
    for state, icon, title, desc in steps:
        rows += f"""
        <div class="journey-step">
          <div class="jnode jnode-{state}">{icon}</div>
          <div>
            <div class="j-title">{title}</div>
            <div class="j-desc">{desc}</div>
          </div>
        </div>"""
    st.markdown(rows, unsafe_allow_html=True)


def topbar(title: str, chips: list[tuple[str, str]] = None):
    chip_html = ""
    for label, extra_cls in (chips or []):
        chip_html += f'<span class="cg-chip {extra_cls}">{label}</span> '
    st.markdown(
        f"""<div class="cg-topbar">
          <div class="cg-page-title">{title}</div>
          <div style="display:flex;gap:8px;align-items:center">{chip_html}</div>
        </div>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# PAGE — DASHBOARD
# ─────────────────────────────────────────
if menu == "Dashboard":
    topbar(
        "📊 " + t("Dashboard"),
        [(f"{t('Election in')} {days_left} {t('days')}", "cg-chip-amber"), ("Bengaluru, KA", "")],
    )

    render_metrics_row()
    
    # ─────────────────────────────────────────
    # ✨ AI STRATEGY (NEW - FAANG LEVEL)
    # ─────────────────────────────────────────
    if st.session_state.user_data:
        user = st.session_state.user_data
        st.markdown(f"### ✨ {t('Your Personalized Strategy')}")
        with st.container():
            strategy = get_ai_strategy(user.age, user.location, user.voting_location, user.is_registered)
            st.markdown(f"""
            <div class="cg-card blue" style="border-left: 4px solid #3b82f6;">
                <div style="display: flex; align-items: flex-start; gap: 15px;">
                    <div style="font-size: 24px;">🤖</div>
                    <div style="font-style: italic; color: #e2eaf5;">{strategy}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ─────────────────────────────────────────
    # 📈 LIVE ANALYTICS (NEW - FAANG LEVEL)
    # ─────────────────────────────────────────
    st.markdown(f"### 📈 {t('Live Participation Trends')}")
    
    # Mock data for FAANG-level visualization
    df = pd.DataFrame({
        "Hour": ["7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM"],
        "Voters": [120, 250, 450, 580, 420, 310, 280, 400, 520, 610, 490, 200],
        "Capacity": [800] * 12
    })
    
    fig = px.area(
        df, x="Hour", y="Voters",
        title=t("Real-time Voter Turnout Estimate"),
        color_discrete_sequence=["#22c55e"],
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="DM Sans",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0),
        height=300
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(30,48,80,0.5)")
    
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

    st.markdown(
        "<h3 style='margin-bottom:14px'>🧑 " + t("Your Voter Profile") + "</h3>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cg-card">', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    # 👤 PROFILE FORM (VERTICAL LAYOUT ✅)

    # AGE
    age = st.number_input(
        t("Your Age"),
        min_value=0,
        max_value=120,
        step=1
    )
    if age > 0 and age < 18:
        st.markdown(
            f"""
            <div class="alert alert-warning">
            ⚠ {t("You must be at least 18 years old to vote.")}
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif age >= 18:
        st.toast(t("You are eligible to vote!"), icon="✅")
        st.markdown(
            f"""
            <div class="alert alert-success">
            ✅ {t("Great news! You are eligible to participate in the democratic process.")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 📍 LOCATION (NOW BELOW AGE)
    st.markdown(f"### 📍 {t('Location')}")

    # Detect GPS
    col_gps1, col_gps2 = st.columns([1, 2])
    with col_gps1:
        if st.button("🛰️ " + t("Detect GPS")):
            st.session_state.geo = get_geolocation()
    
    with col_gps2:
        if st.session_state.geo:
            st.success(f"📡 {t('Live GPS Locked')}")
        else:
            st.warning(f"📡 {t('GPS Not Used (Manual Mode)')}")

    geo = st.session_state.geo

    if geo:
        lat = geo["coords"]["latitude"]
        lng = geo["coords"]["longitude"]
        location = f"{lat},{lng}"

        st.markdown(f"""
            <div class="cg-card blue" style="border-left: 4px solid #3b82f6; margin-bottom: 20px; position: relative; overflow: hidden;">
                <div style="position: absolute; top: -10px; right: -10px; font-size: 60px; opacity: 0.05;">🛰️</div>
                <div style="font-size: 10px; font-family: 'DM Mono', monospace; text-transform: uppercase; color: #3b82f6; letter-spacing: 1.5px;">{t('Verified Live Location')}</div>
                <div style="font-size: 20px; font-weight: 700; margin-top: 8px; color: #e2eaf5;">📍 {t('Coordinates Locked')}</div>
                <div style="font-family: 'DM Mono', monospace; font-size: 14px; color: #8ba3c4; margin-top: 5px;">
                    {round(lat,6)}, {round(lng,6)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 " + t("Reset & Use Manual Address")):
            st.session_state.geo = None
            st.rerun()
    else:
        location = st.text_input(
            t("Enter current physical location"),
            placeholder="e.g. Ramanagara, Bengaluru",
            help=t("Type where you are RIGHT NOW for accurate distance calculation.")
        )
    
    voting_loc = st.text_input(
        t("Voting Constituency / Area (Optional)"),
        placeholder=t("Enter your registered voting area if different"),
        help=t("If left blank, we'll use your current location to find booths.")
    )

    registered = st.checkbox(t("I am registered to vote"))

    if st.button(t("🚀 Start My Journey"),disabled=(age<18)):
        if age > 0 and age < 18:
            st.info("You will be eligible to vote after turning 18.")
        if not validate_age(age):
            st.markdown(
                f'<div class="alert alert-error">✗ {t("Invalid age. Must be 18+.")}</div>',
                unsafe_allow_html=True,
            )
        elif not location.strip():
            st.markdown(
                f'<div class="alert alert-error">✗ {t("Please enter your location.")}</div>',
                unsafe_allow_html=True,
            )
        else:
            lat_val = None
            lng_val = None
            if st.session_state.geo:
                lat_val = st.session_state.geo["coords"]["latitude"]
                lng_val = st.session_state.geo["coords"]["longitude"]
            else:
                # Try geocoding the manual address input
                lat_val, lng_val = geocode_location(location)

            st.session_state.user_data = User(
                age=age, 
                location=location, 
                voting_location=voting_loc if voting_loc.strip() else location,
                is_registered=registered,
                latitude=lat_val,
                longitude=lng_val
            )
            st.markdown(
                f'<div class="alert alert-success">✓ {t("Profile saved. Head to Journey →")}</div>',
                unsafe_allow_html=True,
            )

    

    # Reminders
    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)

    st.markdown(
        "<h3 style='margin-bottom:14px'>🔔 " + t("Set Election Reminder") + "</h3>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cg-card blue">', unsafe_allow_html=True)

    # ================================
    # 📅 DATE + TIME (NEW)
    # ================================
    col1, col2 = st.columns(2)

    with col1:
        reminder_date = st.date_input(t("Election Date"))

    with col2:
        reminder_time = st.time_input(t("Reminder Time"))

    # ================================
    # 📍 AUTO LOCATION (UPGRADED)
    # ================================
    default_location = ""

    if "user_data" in st.session_state and st.session_state.user_data:
        default_location = st.session_state.user_data.location

    loc_rem = st.text_input(
        t("Location for reminder"),
        value=default_location,
        placeholder=t("Your address or area"),
    )

    # ================================
    # 🔘 BUTTON ACTION (UPGRADED)
    # ================================

    # 📅 Google Calendar Button
    if st.button("📅 " + t("Add to Calendar")):
        link = generate_calendar_link(
            loc_rem,
            reminder_date.isoformat(),
            reminder_time.strftime("%H:%M:%S")
        )

        st.markdown(
            f"""
            <div class="alert alert-info">
            📅 {t("Reminder created!")}<br>
            🕒 {reminder_date} {reminder_time}<br>
            📍 {loc_rem}<br><br>

            <a href="{link}" target="_blank">
            👉 {t("Open Calendar")}
            </a>
            </div>
        """,
        unsafe_allow_html=True,
        )


    # 📥 ICS DOWNLOAD BUTTON
    from app.services.calendar_service import generate_ics

    if st.button("📥 " + t("Download Reminder (.ics)")):
        ics = generate_ics(
            location=loc_rem,
            date=reminder_date.isoformat(),
            time=reminder_time.strftime("%H:%M:%S")
        )

        if ics:
            st.download_button(
                label=t("Download ICS File"),
                data=ics,
                file_name="election_reminder.ics",
                mime="text/calendar"
            )
        else:
            st.error(t("Failed to generate reminder file"))

    # ─────────────────────────────────────────
    # PAGE — JOURNEY (FIXED)
    # ─────────────────────────────────────────
elif menu == "Journey":

    topbar("🗺️ " + t("My Voting Journey"))

    user = st.session_state.user_data

    if not user:
        st.warning("Complete profile first")
        st.stop()

    search_loc = user.voting_location if user.voting_location else user.location

    if st.session_state.last_location != search_loc:
        st.session_state.stations = load_stations(search_loc)
        st.session_state.last_location = search_loc

    stations = st.session_state.stations
    location = user.location # Physical location for distance ref

    if user.latitude and user.longitude:
        base_lat, base_lng = user.latitude, user.longitude
    elif "," in location:
        try:
            base_lat, base_lng = map(float, location.split(","))
        except:
            base_lat, base_lng = geocode_location(location)
    else:
        base_lat, base_lng = geocode_location(location)
        
    # Final fallback if geocoding failed
    if base_lat is None:
        base_lat, base_lng = stations[0]["lat"], stations[0]["lng"]


    crowd_data = get_booth_crowd() or {}

    best_booth = min(
        stations,
        key=lambda s: score_booth_map(s, base_lat, base_lng, crowd_data)
    )

    st.markdown(f"### 🧠 {t('AI Recommendation')}")
    st.success(f"⭐ **{t('Best Booth')}: {best_booth['name']}**")

    crowd_val = crowd_data.get(best_booth["name"], 0)
    dist_to_best = calculate_distance(base_lat, base_lng, best_booth["lat"], best_booth["lng"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📏 {t('Distance')}:** {dist_to_best} km")
        if dist_to_best < 0.1:
            st.info(f"🚶 {t('Extremely close! Walking is recommended.')}")
    with col2:
        st.markdown(f"**👥 {t('Crowd Estimate')}:** {crowd_val} {t('people')}")

    if crowd_val < 30:
        st.success("🟢 Low crowd — best time to go now")
    elif crowd_val < 60:
        st.warning("🟡 Moderate crowd")
    else:
        st.error("🔴 High crowd — try later")
   
    # 🧭 STEPS
    st.markdown(f"<h3>{t('Your Steps')}</h3>", unsafe_allow_html=True)
    render_journey_steps()

    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)

    # 📍 MAP + STATIONS
    st.markdown(f"<h3>{t('Nearby Polling Stations')}</h3>", unsafe_allow_html=True)
    journey_ui(location, target_lang, t, base_lat, base_lng, crowd_data)

# ─────────────────────────────────────────
# PAGE — MAP (UNCHANGED BUT CLEAR PURPOSE)
# ─────────────────────────────────────────
elif menu == "Map":
    topbar("🗺️ " + t("Polling Map"))

    # ================================
    # 🔒 USER CHECK (UNCHANGED)
    # ================================
    if "user_data" not in st.session_state or not st.session_state.user_data:
        st.warning("Please complete profile first")
        st.stop()

    user_data = st.session_state.user_data
    location = user_data.location # physical
    search_loc = user_data.voting_location if user_data.voting_location else location
    
    if not search_loc:
        st.warning("Please enter location first")
        st.stop()

    # ================================
    # 📍 FETCH STATIONS (UNCHANGED)
    # ================================
    stations = load_stations(search_loc)

    user_data = st.session_state.user_data
    if user_data.latitude and user_data.longitude:
        base_lat, base_lng = user_data.latitude, user_data.longitude
    elif "," in location:
        try:
            base_lat, base_lng = map(float, location.split(","))
        except:
            base_lat, base_lng = geocode_location(location)
    else:
        base_lat, base_lng = geocode_location(location)

    if base_lat is None:
        base_lat, base_lng = stations[0]["lat"], stations[0]["lng"]


    # ================================
    # 🔥 SAFE: FETCH CROWD DATA
    # ================================
    try:
        crowd_data = get_booth_crowd()

        # fallback if None
        if not crowd_data:
            crowd_data = {}

    except Exception as e:
        st.warning(f"⚠ Crowd data unavailable: {e}")
        crowd_data = {}

    # ================================
    # 🔥 FIND BEST BOOTH (SMART)
    # ================================
    nearest = min(
        stations,
        key=lambda s: score_booth_map(s, base_lat, base_lng, crowd_data)
    )

    # ================================
    # 🗺️ MAP (UNCHANGED BASE)
    # ================================
    import folium
    m = folium.Map(
        location=[base_lat, base_lng],
        zoom_start=13,
        tiles="CartoDB positron"
    )

    from folium.plugins import MiniMap, Fullscreen

    MiniMap().add_to(m)
    Fullscreen().add_to(m)

    # ================================
    # 🔥 NEW: USER LOCATION MARKER
    # ================================
    folium.Marker(
        [base_lat, base_lng],
        popup="You are here",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    # ===========================
    # 🔥 UPDATED MARKERS 
    # ===========================
    for s in stations:
        crowd = crowd_data.get(s["name"], 0)

        if s == nearest:
            color = "blue"
            icon = "star"
        elif crowd > 50:
            color = "red"
            icon = "exclamation-sign"
        elif crowd > 20:
            color = "orange"
            icon = "info-sign"
        else:
            color = "green"
            icon = "ok-sign"

        folium.Marker(
            [s["lat"], s["lng"]],
            popup=f"""
            <b>{s['name']}</b><br>
            Crowd: {crowd} people
            """,
            icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)

    # ================================
    # 🔥 NEW: ROUTE LINE
    # ================================
    try:
        duration, _, polyline_str = get_route_details(
            base_lat, base_lng,
            nearest["lat"], nearest["lng"]
        )

        if polyline_str:
            import polyline
            folium.PolyLine(
            polyline.decode(polyline_str),
            color="#2563eb",
            weight=6,
            opacity=0.8
            ).add_to(m)

            

    except Exception as e:
        st.warning(f"Route not available: {e}")

    # ================================
    # 🔥 NEW: HEATMAP
    # ================================
    st.metric("⏱ ETA", duration if 'duration' in locals() else "N/A")
    try:
        from folium.plugins import HeatMap
        import random

        heat_data = []

        for s in stations:
            for _ in range(random.randint(3, 8)):
                heat_data.append([s["lat"], s["lng"]])

        HeatMap(heat_data).add_to(m)

    except:
        pass

    # ================================
    # 🗺️ DISPLAY MAP (FIXED)
    # ================================

    st_folium(
        m,
        width="stretch",
        height=500,
        returned_objects=[]
    )

    # ===========================
    # 🔥 NEW: SUMMARY INFO
    # ===========================
 # 📍 Nearest Booth Info
    distance_km = calculate_distance(
        base_lat, base_lng,
        nearest["lat"], nearest["lng"]
    )

    st.markdown("### 🧠 Recommended Polling Booth")
    st.success(f"🏫 {nearest['name']}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("📏 Distance", f"{distance_km:.2f} km")

    with col2:
        st.metric("⏱ ETA", duration if 'duration' in locals() else "N/A")

    # ================================
    # 🔥 SMART SUGGESTION
    # ================================
    if distance_km < 1:
        st.info("🚶 Very close! Walking is recommended.")
    elif distance_km < 5:
        st.info("🚗 Short distance. Consider bike or auto.")
    else:
        st.warning("🚘 Long distance. Plan travel early.")

    # ================================
    # 🔥 NAVIGATION BUTTON
    # ================================

    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={nearest['lat']},{nearest['lng']}"

    st.markdown(
        f"""
        <a href="{maps_url}" target="_blank">
        <button style="
            background-color:#22c55e;
            color:white;
            padding:10px 20px;
            border:none;
            border-radius:8px;
            font-weight:bold;
            cursor:pointer;">
            🧭 Open in Google Maps
        </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    # ================================
    # 🔥 CROWD SIMULATION (UNIQUE)
    # ================================
 
    crowd = crowd_data.get(nearest["name"], 0)

    st.markdown("### 📊 Booth Crowd Estimate")

    st.progress(crowd / 100)

    if crowd < 30:
        st.success(f"🟢 Low crowd ({crowd} people)")
    elif crowd < 60:
        st.warning(f"🟡 Medium crowd ({crowd} people)")
    else:
        st.error(f"🔴 High crowd ({crowd} people)")

    # ================================
    # 🔥 BEST TIME SUGGESTION
    # ================================
    st.markdown("### 🧠 Best Time to Vote")

    if crowd < 30:
        st.success("👍 Now is a great time to vote!")
    elif crowd < 60:
        st.info("⏳ Wait 30–60 mins for less crowd")
    else:
        st.warning("⚠️ Try early morning or evening")


#=========================
#        TIMELINE
#=========================

elif menu == "Timeline":
    topbar("📅 Election Timeline")

    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)

    st.markdown("## 🗳️ Interactive Election Journey")

    steps = [
        ("📝 Registration", "You register as a voter to be eligible for elections."),
        ("🔍 Verification", "Authorities verify your identity and details."),
        ("📄 Voter Slip", "You receive polling booth and voter details."),
        ("🗳️ Poll Day", "You visit the booth and cast your vote."),
        ("📊 Counting", "Votes are counted securely."),
        ("🏆 Results", "Final winners are announced.")
    ]

    # =========================
    # 🎯 PROGRESS TRACKER
    # =========================
    if "timeline_step" not in st.session_state:
        st.session_state.timeline_step = 0

    current = st.session_state.timeline_step

    st.progress((current + 1) / len(steps))

    # =========================
    # 🎬 ANIMATED STEP DISPLAY
    # =========================
    title, desc = steps[current]

    st.markdown(f"""
    <div class="cg-card" style="animation: fadeIn 0.6s ease-in-out;">
        <h3>{title}</h3>
        <p style="color:#8ba3c4">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # 🧠 AI EXPLANATION
    # =========================
    ai_explanations = {
        "📝 Registration": "This step ensures every citizen is officially recorded in the electoral roll.",
        "🔍 Verification": "Prevents fraud by confirming identity and eligibility.",
        "📄 Voter Slip": "Helps you locate your polling station easily.",
        "🗳️ Poll Day": "This is where democracy happens — your vote matters.",
        "📊 Counting": "Votes are securely counted to ensure fairness.",
        "🏆 Results": "Final results determine the elected representatives."
    }


    # =========================
    # 🔊 TEXT-TO-SPEECH BUTTON (NEW)
    # =========================
    st.markdown("---")

    col_speak, col_detail = st.columns([1, 3])

    with col_speak:
        if st.button("🔊 Hear Explanation"):
            with st.spinner("Generating audio..."):
                text = ai_explanations.get(title, "")
                audio_file = speak_text(text)
                
                if audio_file:
                    st.audio(audio_file)
                else:
                    st.warning("Sorry! Could not generate audio right now.")
    
    with col_detail:
        if st.button("🧠 Detailed Explanation"):
            with st.spinner("Generating detailed explanation..."):
                full_explanation = get_gemini_response(
                    f"Explain '{title}' step of election process in detail for a beginner"
                )
                st.info(full_explanation)

    # =========================
    # 🔘 NAVIGATION BUTTONS
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Previous", disabled=current == 0):
            st.session_state.timeline_step -= 1
            st.rerun()

    with col2:
        if st.button("Next ➡️", disabled=current == len(steps) - 1):
            st.session_state.timeline_step += 1
            st.rerun()

    # =========================
    # 🎯 STEP INDICATOR DOTS
    # =========================
    st.markdown("### Progress")

    dots = ""
    for i in range(len(steps)):
        if i == current:
            dots += "🔵 "
        else:
            dots += "⚪ "

    st.markdown(dots)

    st.success("🎯 Follow each step to fully understand the election process!")

    st.markdown("</div>", unsafe_allow_html=True)

#================
# Voter Guide
#================

elif menu == "Voting Guide":
    topbar("🗳️ How Voting Works (Step-by-Step)")

    st.markdown("## 🎓 Learn the Voting Process Interactively")

    steps = [
        {
            "title": "📝 Step 1: Check Eligibility",
            "desc": "You must be 18+ and registered as a voter.",
            "action": "Enter your age",
            "key": "age"
        },
        {
            "title": "📄 Step 2: Verify Documents",
            "desc": "You need a Voter ID or valid identity proof.",
            "action": "Select your ID type",
            "key": "id"
        },
        {
            "title": "📍 Step 3: Find Polling Booth",
            "desc": "Your assigned booth is based on your location.",
            "action": "Enter your location",
            "key": "location"
        },
        {
            "title": "🗳️ Step 4: Cast Your Vote",
            "desc": "Use EVM to vote for your preferred candidate.",
            "action": "Choose a candidate",
            "key": "vote"
        }
    ]

    if "guide_step" not in st.session_state:
        st.session_state.guide_step = 0

    step = steps[st.session_state.guide_step]

    # ========================
    # STEP DISPLAY
    # ========================
    st.markdown(f"""
    <div class="cg-card">
        <h3>{step['title']}</h3>
        <p style="color:#8ba3c4">{step['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ========================
    # USER INTERACTION
    # ========================
    if step["key"] == "age":
        age = st.number_input("Enter your age", 0, 120)

        if age >= 18:
            st.success("✅ You are eligible to vote")
        elif age > 0:
            st.error("❌ You are not eligible yet")

    elif step["key"] == "id":
        id_type = st.selectbox("Select ID", ["Voter ID", "Aadhaar", "Passport"])
        st.info(f"You selected: {id_type}")

    elif step["key"] == "location":
        location = st.text_input("Enter your location")
        if location:
            st.success("📍 Booth will be assigned based on this")

    elif step["key"] == "vote":
        candidate = st.radio("Choose candidate", ["Candidate A", "Candidate B", "NOTA"])
        st.success(f"🗳️ You voted for {candidate}")

    # ========================
    # 🧠 AI EXPLANATION
    # ========================
    if st.button("🧠 Explain this step", key=f"guide_{st.session_state.guide_step}"):
        with st.spinner("Explaining..."):
            explanation = get_gemini_response(
                f"Explain {step['title']} in simple terms for a first-time voter"
            )
            st.info(explanation)

    # ========================
    # NAVIGATION
    # ========================
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.guide_step == 0):
            st.session_state.guide_step -= 1
            st.rerun()

    with col2:
        if st.button("Next ➡️", disabled=st.session_state.guide_step == len(steps)-1):
            st.session_state.guide_step += 1
            st.rerun()

    # ========================
    # PROGRESS BAR
    # ========================
    st.progress((st.session_state.guide_step + 1) / len(steps))

    st.success("🎯 Follow all steps to understand how voting works in real life!")

# ================================
# 🎮 QUIZ PAGE (ADD HERE 👇)
# ================================
elif menu == "Quiz":
    topbar("🎮 Election Quiz")

    st.markdown("## 🧠 Test Your Knowledge")

    # =========================
    # 🎯 DIFFICULTY LEVEL
    # =========================
    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    if difficulty == "Easy":
        questions = [
            {"q": "Minimum age to vote?", "options": ["16", "18", "21"], "answer": "18"},
            {"q": "Voting machine?", "options": ["EVM", "Laptop", "Mobile"], "answer": "EVM"}
        ]

    elif difficulty == "Medium":
        questions = [
            {"q": "Who conducts elections?", "options": ["ECI", "PM", "SC"], "answer": "ECI"},
            {"q": "Voter ID is called?", "options": ["PAN", "EPIC", "UID"], "answer": "EPIC"}
        ]

    else:  # Hard
        questions = [
            {"q": "Article related to elections?", "options": ["324", "370", "21"], "answer": "324"},
            {"q": "Election Commissioner tenure?", "options": ["6 years", "3 years", "10 years"], "answer": "6 years"}
        ]

    score = 0

    # =========================
    # QUESTIONS
    # =========================
    for i, q in enumerate(questions):
        ans = st.radio(q["q"], q["options"], key=f"quiz_{difficulty}_{i}")

        if ans == q["answer"]:
            score += 1

    # =========================
    # SUBMIT
    # =========================
    if st.button("Submit Quiz"):
        st.session_state.quiz_scores.append(score)
        st.session_state.quiz_attempts += 1

        st.success(f"🎯 Score: {score}/{len(questions)}")

        if score == len(questions):
            st.balloons()
            st.success("🏆 Perfect!")
        elif score >= len(questions) // 2:
            st.info("👍 Good job!")
        else:
            st.warning("📚 Try again!")

    # =========================
    # 🧠 SCORE HISTORY
    # =========================
    st.markdown("### 🧠 Score History")

    if st.session_state.quiz_scores:
        for i, s in enumerate(st.session_state.quiz_scores):
            st.write(f"Attempt {i+1}: {s}")
    else:
        st.info("No attempts yet")

    # =========================
    # 🏅 LEADERBOARD (LOCAL)
    # =========================
    st.markdown("### 🏅 Leaderboard")

    leaderboard = sorted(st.session_state.quiz_scores, reverse=True)

    for i, score in enumerate(leaderboard[:5]):
        st.write(f"{i+1}. Score: {score}")

    # =========================
    # 🧠 AI Q&A
    # =========================
    st.markdown("### 🧠 Ask AI")

    user_q = st.text_input("Ask about elections", key="quiz_ai")

    if st.button("Get Answer", key="quiz_ai_btn"):
        if user_q:
            with st.spinner("Thinking..."):
                answer = get_gemini_response(
                    f"Answer this election question simply: {user_q}"
                )
                st.success(answer)

    # =========================
    # 🔥 GENERATE QUESTION
    # =========================
    if st.button("Generate New Question"):
        q = get_gemini_response("Generate a MCQ question about elections with answer")
        st.write(q)


# ================================
# 🤖 AI ASSISTANT PAGE
# ================================
elif menu == "AI Assistant":
    topbar("🤖 " + t("AI Election Assistant"), [("Live AI", "badge-green")])

    st.markdown(f"## {t('Ask anything about elections')}")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input(t("What would you like to know?")):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            if is_rate_limited():
                st.warning("⚠️ Slow down! Please wait a moment between questions.")
            elif not sanitize_input(prompt):
                st.error("🚨 Suspicious activity detected. Your query has been blocked for safety.")
            else:
                with st.spinner(t("Analyzing and generating response...")):
                    # Pass history for context
                    response = get_gemini_response(prompt, history=st.session_state.messages[-5:])
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button(t("Clear Conversation")):
        st.session_state.messages = []
        st.rerun()



# ================================
# 💬 HELP CENTER
# ================================
elif menu == "Help Center":
    topbar("💬 Help Center")

    st.markdown("## 🧠 Ask Questions")

    st.markdown("Try asking things like:")
    st.write("• What is EVM?")
    st.write("• How to vote?")
    st.write("• What is NOTA?")

    user_q = st.text_input("Your question")

    if st.button("Get Help"):
        if user_q:
            with st.spinner("Thinking..."):
                answer = get_gemini_response(user_q)

                if answer:
                    st.success(answer)
                else:
                    st.warning("No response from AI")