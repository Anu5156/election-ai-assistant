"""
Journey Route - CivicGuide AI
Handles the personalized voting journey, booth scoring, and progress tracking.
"""

import streamlit as st
from app.utils.ui_components import topbar, render_journey_steps
from app.services.maps_service import load_stations, calculate_distance, get_route_details
from app.services.firebase_service import get_booth_crowd

def score_booth(s, base_lat, base_lng, crowd_data):
    """
    Calculates a composite score for a polling booth.
    Priority = (Distance * 0.7) + (Crowd * 0.3)
    """
    d = calculate_distance(base_lat, base_lng, s["lat"], s["lng"])
    c = crowd_data.get(s["name"], 0)
    return (d * 0.7) + (c * 0.3)

def journey_ui(user, target_lang, t, base_lat, base_lng, crowd_data):
    """
    Renders the Journey page UI.
    """
    topbar("🗺️ " + t("My Voting Journey"), [("Personalized Path", "badge-blue")])

    if not user:
        st.warning(t("Please complete your profile on the Dashboard first."))
        st.stop()

    # ── Progress Steps ──
    st.markdown(f"### 🎯 {t('Your Progress')}")
    render_journey_steps(t, user.is_registered)

    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)

    # ── Booth Recommendations ──
    search_loc = user.voting_location if user.voting_location else user.location
    stations = load_stations(search_loc)
    
    if not stations:
        st.error(t("No polling stations found in your area."))
        return

    # Use actual coordinates if available
    b_lat, b_lng = (user.latitude, user.longitude) if user.latitude else (base_lat, base_lng)
    
    crowd_data = get_booth_crowd() or {}
    
    # Rank stations by smart score
    stations.sort(key=lambda s: score_booth(s, b_lat, b_lng, crowd_data))
    best_booth = stations[0]

    st.markdown(f"### 🏆 {t('Top Recommendation')}")
    dist = calculate_distance(b_lat, b_lng, best_booth["lat"], best_booth["lng"])
    
    st.markdown(f"""
    <div class="cg-card blue" style="border-left: 4px solid #3b82f6;">
        <h4 style="margin:0">🏫 {best_booth['name']}</h4>
        <p style="color:#8ba3c4; font-size:14px; margin:5px 0;">{best_booth['address']}</p>
        <div style="display:flex; gap:20px; margin-top:15px;">
            <div>📏 <b>{t('Distance')}:</b> {dist:.2f} km</div>
            <div>👥 <b>{t('Live Crowd')}:</b> {crowd_data.get(best_booth['name'], 0)} {t('people')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info(t("Pro Tip: This booth is selected based on a hybrid score of proximity and current crowd density."))