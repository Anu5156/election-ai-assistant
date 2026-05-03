"""
CivicGuide AI - Main Orchestration Module
FAANG-Standard Architecture v3.0
"""

import streamlit as st
import sys
import os
from datetime import datetime

# ── Ensure app directory is in path ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Import Routes ──
from app.routes.dashboard import render_dashboard
from app.routes.journey import journey_ui
from app.routes.map import render_map_page
from app.routes.timeline import render_timeline
from app.routes.guide import render_voting_guide
from app.routes.quiz import render_quiz
from app.routes.help import render_help_center
from app.routes.chat import render_chat_page

# ── Import Services & Utils ──
from app.services.translate_service import translate_text
from app.utils.validators import validate_age, sanitize_input, is_rate_limited
from app.utils.ui_components import topbar
from app.utils.styles import get_global_styles

# ── Page Config ──
st.set_page_config(
    page_title="CivicGuide AI",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ──
ELECTION_DATE = datetime(2026, 5, 20)
LANG_OPTIONS = {
    "English": "en", "हिंदी": "hi", "ಕನ್ನಡ": "kn", "తెలుగు": "te", "தமிழ்": "ta",
    "മലയാളം": "ml", "বাংলা": "bn", "मराठी": "mr", "ગુજરાતી": "gu", "ਪੰਜਾਬੀ": "pa",
    "ଓଡ଼ିଆ": "or", "اردو": "ur"
}

# ── State Management ──
if "user_data" not in st.session_state: st.session_state.user_data = None
if "geo" not in st.session_state: st.session_state.geo = None
if "detecting_gps" not in st.session_state: st.session_state.detecting_gps = False
if "navigation_menu" not in st.session_state: st.session_state.navigation_menu = "Dashboard"

# ── Programmatic Redirect Handler ──
# If a route wants to switch pages, it sets 'target_menu' and reruns.
# We must update the widget state BEFORE it is instantiated in the sidebar.
if "target_menu" in st.session_state:
    st.session_state.navigation_menu = st.session_state.target_menu
    del st.session_state.target_menu

# ── Accessibility Layer ──
st.markdown('<div id="sr-announcer" role="status" aria-live="polite" style="position:absolute; left:-10000px; width:1px; height:1px; overflow:hidden;">Application Loaded.</div>', unsafe_allow_html=True)

# ── GLOBAL CSS ──
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)
st.markdown(get_global_styles(), unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    now = datetime.now()
    st.markdown(f"### 🗳️ CivicGuide AI\nLive Session • {now.strftime('%H:%M:%S')}")
    
    selected_lang = st.selectbox("Language", list(LANG_OPTIONS.keys()))
    target_lang = LANG_OPTIONS[selected_lang]
    def t(text: str) -> str: return translate_text(text, target_lang)

    # Sync radio button with session state for programmatic switching
    menu = st.radio(
        "Navigation", 
        ["Dashboard", "Journey", "Map", "AI Assistant", "Timeline", "Voting Guide", "Quiz", "Help Center"],
        key="navigation_menu"
    )
    
    st.markdown("---")
    high_contrast = st.toggle("High Contrast Mode")
    st.markdown(f"<script>document.documentElement.setAttribute('data-high-contrast', '{str(high_contrast).lower()}');</script>", unsafe_allow_html=True)
    
    if st.button("⚖️ Privacy Policy"):
        st.info("CivicGuide AI processes all geospatial data in-memory and does not store permanent GPS logs.")

# ── MAIN CONTENT ──
days_left = (ELECTION_DATE - datetime.now()).days
countdown_display = f"{days_left}d"

if menu == "Dashboard":
    render_dashboard(t, days_left, ELECTION_DATE, countdown_display)
elif menu == "Journey":
    journey_ui(st.session_state.user_data, target_lang, t, 12.9716, 77.5946, {}) # Defaults to Bengaluru if no geo
elif menu == "Map":
    render_map_page(t, target_lang)
elif menu == "AI Assistant":
    render_chat_page(t)
elif menu == "Timeline":
    render_timeline(t)
elif menu == "Voting Guide":
    render_voting_guide(t)
elif menu == "Quiz":
    render_quiz(t)
elif menu == "Help Center":
    render_help_center(t)