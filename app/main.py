"""
CivicGuide AI - The Ultimate AI-Powered Election Assistant
Main Orchestration Module

This application provides citizens with localized, real-time election information including:
- Polling booth discovery and routing (Google Maps API)
- Real-time crowd density tracking (Firebase Firestore)
- Personalized voting strategies (Google Gemini AI)
- Multi-language support (12 Indian languages)
- Digital Voting Pass and calendar reminders

Author: CivicGuide AI Team
License: MIT
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

# ── CONFIGURATION ──
st.set_page_config(
    page_title="CivicGuide AI",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CONSTANTS ──
ELECTION_DATE = datetime(2026, 5, 20)
LANG_OPTIONS = {
    "English": "en", "Hindi (हिंदी)": "hi", "Kannada (ಕನ್ನಡ)": "kn",
    "Tamil (தமிழ்)": "ta", "Telugu (తెలుగు)": "te", "Bengali (বাংলা)": "bn",
    "Marathi (मराठी)": "mr", "Gujarati (ગુજરાતી)": "gu", "Punjabi (ಪੰਜਾਬಿ)": "pa",
    "Malayalam (മലയാളം)": "ml", "Odia (ଓಡ଼ಿಶ)": "or", "Urdu (اردو)": "ur"
}

# ── SESSION STATE INIT ──
_defaults = {
    "user_data": None, "messages": [], "timeline_step": 0, "guide_step": 0,
    "quiz_scores": [], "geo": None, "last_location": None, "stations": []
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── ACCESSIBILITY & SECURITY METADATA ──
st.markdown("""
    <script>
        document.documentElement.lang = 'en';
        const isHighContrast = window.localStorage.getItem('highContrast') === 'true';
        document.documentElement.setAttribute('data-high-contrast', isHighContrast);
    </script>
    <head>
        <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="DENY">
    </head>
    <div id="sr-announcer" role="status" aria-live="polite" style="position:absolute; left:-10000px; width:1px; height:1px; overflow:hidden;">
        Application Loaded.
    </div>
""", unsafe_allow_html=True)

# ── GLOBAL CSS ──
st.markdown(get_global_styles(), unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    now = datetime.now()
    st.markdown(f"### 🗳️ CivicGuide AI\nLive Session • {now.strftime('%H:%M:%S')}")
    
    selected_lang = st.selectbox("Language", list(LANG_OPTIONS.keys()))
    target_lang = LANG_OPTIONS[selected_lang]
    def t(text: str) -> str: return translate_text(text, target_lang)

    menu = st.radio("Navigation", ["Dashboard", "Journey", "Map", "AI Assistant", "Timeline", "Voting Guide", "Quiz", "Help Center"])
    
    st.markdown("---")
    high_contrast = st.toggle("High Contrast Mode")
    st.markdown(f"<script>document.documentElement.setAttribute('data-high-contrast', '{str(high_contrast).lower()}');</script>", unsafe_allow_html=True)
    
    if st.button("⚖️ Privacy Policy"):
        st.info("CivicGuide AI processes all geospatial data in-memory and does not store permanent GPS logs.")

# ── MAIN CONTENT ──
st.markdown("<main id='main-content'>", unsafe_allow_html=True)

# Calculate global variables for routes
days_left = (ELECTION_DATE - datetime.now()).days
countdown_display = f"{days_left}d"

if menu == "Dashboard":
    render_dashboard(t, days_left, ELECTION_DATE, countdown_display)
elif menu == "Journey":
    journey_ui(st.session_state.user_data, target_lang, t, 0, 0, {})
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

st.markdown("</main>", unsafe_allow_html=True)