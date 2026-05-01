import streamlit as st
import folium
import polyline
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from app.services.maps_service import get_polling_stations, get_route_details


# -----------------------------------
# 🔹 DISTANCE HELPER (UNCHANGED)
# -----------------------------------
def calculate_distance(lat1, lng1, lat2, lng2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return round(R * c, 2)


# -----------------------------------
# 🔹 CACHE MAP (🔥 MAIN FIX)
# -----------------------------------
@st.cache_data(show_spinner=False)
def create_map(stations, base_lat, base_lng, polyline_str):
    m = folium.Map(location=[base_lat, base_lng], zoom_start=13)

    # markers
    for s in stations:
        folium.Marker(
            [s["lat"], s["lng"]],
            popup=f"{s['name']} ({s['distance']} km)",
            tooltip=s["name"],
            icon=folium.Icon(color="red" if s["is_nearest"] else "green")
        ).add_to(m)

    # route
    if polyline_str:
        folium.PolyLine(polyline.decode(polyline_str), color="blue", weight=5).add_to(m)

    # 🔥 stable heatmap (NO RANDOM)
    heat_data = []
    for s in stations:
        for _ in range(5):   # fixed value instead of random
            heat_data.append([s["lat"], s["lng"]])

    HeatMap(heat_data).add_to(m)

    return m


# -----------------------------------
# 🔹 MAIN UI
# -----------------------------------
def journey_ui(location, target_lang, t):

    # -------- SESSION --------
    if "stations" not in st.session_state:
        st.session_state.stations = []

    if "last_location" not in st.session_state:
        st.session_state.last_location = ""

    # -------- FETCH --------
    if st.session_state.last_location != location:
        st.session_state.stations = get_polling_stations(location)
        st.session_state.last_location = location

    stations = st.session_state.stations

    st.markdown("## 📍 " + t("Nearby Polling Stations"))

    if not stations:
        st.warning(t("No polling stations found"))
        return

    # -------- BASE LOCATION --------
    base_lat = stations[0]["lat"]
    base_lng = stations[0]["lng"]

    # -------- DISTANCE + CROWD --------
    for s in stations:
        if s.get("lat") and s.get("lng"):
            s["distance"] = calculate_distance(base_lat, base_lng, s["lat"], s["lng"])

            # 🔥 stable crowd (based on distance, not random)
            if s["distance"] < 1:
                s["crowd"] = "High"
            elif s["distance"] < 3:
                s["crowd"] = "Medium"
            else:
                s["crowd"] = "Low"

        else:
            s["distance"] = 999
            s["crowd"] = "Unknown"

    # -------- NEAREST --------
    nearest = min(stations, key=lambda x: x["distance"])

    # mark nearest (for caching stability)
    for s in stations:
        s["is_nearest"] = (s == nearest)

    # -------- ROUTE --------
    duration, distance_meters, polyline_str = get_route_details(
        base_lat, base_lng,
        nearest["lat"], nearest["lng"]
    )

    # -------- MAP (CACHED) --------
    m = create_map(stations, base_lat, base_lng, polyline_str)

    st.markdown("### 🗺️ " + t("Live Map"))

    # 🔥 IMPORTANT: fixed key
    st_folium(
        m,
        use_container_width=True,
        height=450,
        key="stable_map"
    )

    # -------- SUMMARY --------
    if duration:
        st.success(f"⏱️ ETA to nearest: {duration}")

    st.info(f"⭐ {t('Nearest Booth')}: {nearest['name']} ({nearest['distance']} km)")

    # -------- CARDS --------
    for s in stations:
        highlight = "⭐ NEAREST" if s == nearest else ""

        st.markdown(f"""
        <div class="card">
        <b>📍 {s['name']}</b> {highlight}<br>
        🏠 {s['address']}<br>
        📏 {t("Distance")}: {s['distance']} km<br>
        👥 {t("Crowd")}: {s['crowd']}<br><br>

        <a href="{s['nav_link']}" target="_blank">
        🚗 {t("Navigate")}
        </a>
        </div>
        """, unsafe_allow_html=True)