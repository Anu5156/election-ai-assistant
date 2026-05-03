"""
Map Route - CivicGuide AI
Handles the interactive polling booth map, routing, and crowd density visualization.
"""

import streamlit as st
import folium
import random
from folium.plugins import MiniMap, Fullscreen, HeatMap
from streamlit_folium import st_folium
import polyline
from app.utils.ui_components import topbar
from app.services.maps_service import fetch_polling_stations, geocode_location, get_route_details, calculate_distance
from app.services.firebase_service import get_booth_crowd

def score_booth_map(s, base_lat, base_lng, crowd_data):
    """Calculates a priority score for a booth based on distance and crowd."""
    d = calculate_distance(base_lat, base_lng, s["lat"], s["lng"])
    c = crowd_data.get(s["name"], 0)
    return (d * 0.7) + (c * 0.3)

def render_map_page(t, target_lang):
    """
    Renders the interactive Map page.
    """
    topbar("🗺️ " + t("Polling Map"), [("Live Crowd Sync", "badge-green")])

    if "user_data" not in st.session_state or not st.session_state.user_data:
        st.warning(t("Please complete your profile on the Dashboard first."))
        st.stop()

    user = st.session_state.user_data
    search_loc = user.voting_location if user.voting_location else user.location
    stations = fetch_polling_stations(search_loc)

    if not stations:
        st.error(t("No polling stations found in your area. Please check your location settings."))
        return

    base_lat, base_lng = user.latitude, user.longitude
    if base_lat is None:
        base_lat, base_lng = geocode_location(user.location)
        if base_lat is None:
            # Fallback to the first station if geocoding fails
            base_lat, base_lng = stations[0]["lat"], stations[0]["lng"]

    crowd_data = get_booth_crowd() or {}
    nearest = min(stations, key=lambda s: score_booth_map(s, base_lat, base_lng, crowd_data))

    # ── Map Construction ──
    m = folium.Map(location=[base_lat, base_lng], zoom_start=13, tiles="CartoDB positron")
    MiniMap().add_to(m)
    Fullscreen().add_to(m)

    folium.Marker([base_lat, base_lng], popup=t("You are here"), icon=folium.Icon(color="blue")).add_to(m)

    for s in stations:
        crowd = crowd_data.get(s["name"], 0)
        color = "blue" if s == nearest else ("red" if crowd > 50 else "green")
        folium.Marker(
            [s["lat"], s["lng"]],
            popup=f"<b>{s['name']}</b><br>{t('Crowd')}: {crowd}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    # ── Route & Heatmap ──
    duration = "N/A"
    try:
        dur, _, poly_str = get_route_details(base_lat, base_lng, nearest["lat"], nearest["lng"])
        if poly_str:
            folium.PolyLine(polyline.decode(poly_str), color="#2563eb", weight=6).add_to(m)
            duration = dur
    except:
        pass

    heat_data = [[s["lat"], s["lng"]] for s in stations for _ in range(random.randint(3, 8))]
    HeatMap(heat_data).add_to(m)

    st_folium(m, width=800, height=500, returned_objects=[])

    # ── Metrics ──
    st.markdown(f"### 🏫 {t('Recommended Booth')}: {nearest['name']}")
    col1, col2 = st.columns(2)
    with col1: st.metric(t("Distance"), f"{calculate_distance(base_lat, base_lng, nearest['lat'], nearest['lng']):.2f} km")
    with col2: st.metric(t("Estimated Travel"), duration)

    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={nearest['lat']},{nearest['lng']}"
    st.markdown(f'<a href="{maps_url}" target="_blank"><button style="background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;">🧭 {t("Open in Google Maps")}</button></a>', unsafe_allow_html=True)
