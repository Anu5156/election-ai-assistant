"""
Dashboard Route - CivicGuide AI
Handles the primary user overview, profile management, and live analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from app.utils.ui_components import topbar, render_metrics_row
from app.services.gemini_service import get_ai_strategy
from app.utils.validators import validate_age
from app.services.maps_service import geocode_location
from app.services.calendar_service import generate_calendar_link, generate_ics
from app.models.user import User
from streamlit_js_eval import get_geolocation

def render_dashboard(t, days_left, election_date, countdown_display):
    """
    Renders the complete Dashboard view with Sequential Flow (Profile -> Calendar -> Journey).
    """
    topbar(
        "📊 " + t("Dashboard"),
        [(f"{t('Election in')} {days_left} {t('days')}", "cg-chip-amber"), ("India (Lok Sabha)", "")],
    )

    render_metrics_row(t, countdown_display, election_date)
    
    # ── State Initialization ──
    if "calendar_added" not in st.session_state: st.session_state.calendar_added = False
    
    # ── GPS Logic ──
    current_geo = None
    if st.session_state.get("detecting_gps", False):
        current_geo = get_geolocation()
        if current_geo:
            st.session_state.geo = current_geo
            st.session_state.detecting_gps = False
    
    # ── AI Strategy ──
    if st.session_state.user_data:
        user = st.session_state.user_data
        st.markdown(f"### ✨ {t('Your Personalized Strategy')}")
        with st.container():
            strategy = get_ai_strategy(user.age, user.location, user.voting_location, user.is_registered)
            st.markdown(f'<div class="cg-card blue" style="border-left: 4px solid #3b82f6;"><div style="display: flex; align-items: flex-start; gap: 15px;"><div style="font-size: 24px;">🤖</div><div style="font-style: italic; color: #e2eaf5;">{strategy}</div></div></div>', unsafe_allow_html=True)
    
    # ── Live Analytics ──
    st.markdown(f"### 📈 {t('Live Participation Trends')}")
    df = pd.DataFrame({
        "Hour": ["7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM"],
        "Voters": [120, 250, 450, 580, 420, 310, 280, 400, 520, 610, 490, 200]
    })
    fig = px.area(df, x="Hour", y="Voters", title=t("Real-time Voter Turnout Estimate"), color_discrete_sequence=["#22c55e"], template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="DM Sans", margin=dict(l=0, r=0, t=40, b=0), height=250)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── STEP 1: Voter Profile ──
    st.markdown(f"### 🧑 {t('Step 1: Your Voter Profile')}")
    st.markdown('<div class="cg-card">', unsafe_allow_html=True)

    age = st.number_input(t("Your Age"), min_value=0, max_value=120, step=1, key="profile_age")
    if age < 18 and age > 0: st.warning(t("You must be at least 18 years old to vote."))

    st.markdown(f"### 📍 {t('Location')}")
    col_gps1, col_gps2 = st.columns([1, 2])
    with col_gps1:
        if st.button("🛰️ " + t("Detect GPS")):
            st.session_state.detecting_gps = True
            st.rerun()
    with col_gps2:
        if st.session_state.get("geo"): st.success(f"📡 {t('Live GPS Locked')}")
        elif st.session_state.get("detecting_gps"): st.info(f"⏳ {t('Fetching location...')}")
        else: st.warning(f"📡 {t('GPS Not Used (Manual Mode)')}")

    geo = st.session_state.get("geo")
    if geo:
        lat, lng = geo["coords"]["latitude"], geo["coords"]["longitude"]
        location = f"{lat},{lng}"
        st.markdown(f'<div class="cg-card blue" style="border-left: 4px solid #3b82f6; margin-bottom: 20px;"><div style="font-size: 10px; font-weight:700; color: #3b82f6;">{t("LIVE LOCATION LOCKED")}</div><div style="font-size: 14px; margin-top: 5px;">{round(lat,6)}, {round(lng,6)}</div></div>', unsafe_allow_html=True)
    else:
        location = st.text_input(t("Enter current physical location"), placeholder="e.g. Ramanagara, Bengaluru", key="profile_location")
    
    voting_loc = st.text_input(t("Voting Constituency / Area (Optional)"), placeholder=t("Enter registered area if different"), key="profile_voting_loc")
    registered = st.checkbox(t("I am registered to vote"), key="profile_registered")

    if st.button(t("💾 Save Profile"), disabled=(age<18)):
        if not location.strip():
            st.error(t("Please enter your location."))
        else:
            with st.spinner(t("Saving profile...")):
                lat_val, lng_val = (geo["coords"]["latitude"], geo["coords"]["longitude"]) if geo else geocode_location(location)
                st.session_state.user_data = User(
                    age=age, location=location, 
                    voting_location=voting_loc if voting_loc.strip() else location,
                    is_registered=registered, latitude=lat_val, longitude=lng_val
                )
                st.success(t("Profile saved! Now set your election reminder below."))

    st.markdown('</div>', unsafe_allow_html=True)

    # ── STEP 2: Reminders ──
    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"### 🔔 {t('Step 2: Set Election Reminder')}")
    st.markdown('<div class="cg-card blue">', unsafe_allow_html=True)
    st.info(t("Important: You must add the election to your calendar to proceed to the Journey."))
    
    col1, col2 = st.columns(2)
    with col1: reminder_date = st.date_input(t("Election Date"), value=election_date)
    with col2: reminder_time = st.time_input(t("Reminder Time"), value=datetime.strptime("09:00:00", "%H:%M:%S").time())

    default_loc = st.session_state.user_data.location if st.session_state.user_data else ""
    loc_rem = st.text_input(t("Location for reminder"), value=default_loc)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📅 " + t("Add to Google Calendar")):
            st.session_state.calendar_added = True
            link = generate_calendar_link(loc_rem, reminder_date.strftime("%Y%m%d"), t("Vote in Election"))
            if link: st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none; color:#3b82f6;">🔗 {t("Click to Open Google Calendar")}</a>', unsafe_allow_html=True)
    with col_btn2:
        ics = generate_ics(loc_rem, reminder_date.isoformat(), reminder_time.strftime("%H:%M:%S"))
        if ics: 
            if st.download_button(label="📥 " + t("Download ICS"), data=ics, file_name="election_reminder.ics", mime="text/calendar"):
                st.session_state.calendar_added = True

    st.markdown('</div>', unsafe_allow_html=True)

    # ── STEP 3: Start Journey ──
    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"### 🚀 {t('Step 3: Begin Your Journey')}")
    
    can_proceed = st.session_state.user_data is not None and st.session_state.calendar_added
    
    if not can_proceed:
        st.warning(t("Complete your profile (Step 1) and add to calendar (Step 2) to unlock the journey."))
    
    if st.button(t("🛰️ Start My Journey"), disabled=not can_proceed):
        st.session_state.target_menu = "Journey"
        st.rerun()
