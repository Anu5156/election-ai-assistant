import streamlit as st
import folium
import polyline
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from app.services.maps_service import get_polling_stations, get_route_details


# -----------------------------------
# 🔹 DISTANCE HELPER
# -----------------------------------
def calculate_distance(lat1, lng1, lat2, lng2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    # Higher precision for near-booth detection
    res = R * c
    return round(res, 3)


# -----------------------------------
# 🔹 CACHE MAP
# -----------------------------------
@st.cache_data(show_spinner=False)
def create_map(stations, base_lat, base_lng, polyline_str):
    m = folium.Map(location=[base_lat, base_lng], zoom_start=14)

    # markers
    for s in stations:
        folium.Marker(
            [s["lat"], s["lng"]],
            popup=f"{s['name']} ({s['distance']} km)",
            tooltip=s["name"],
            icon=folium.Icon(color="red" if s["is_nearest"] else "green")
        ).add_to(m)

    # 🔥 Your Location Marker (Blue)
    folium.Marker(
        [base_lat, base_lng],
        popup="YOU ARE HERE",
        tooltip="Your Location",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    # route
    if polyline_str:
        folium.PolyLine(polyline.decode(polyline_str), color="blue", weight=5, opacity=0.7).add_to(m)

    # stable heatmap
    heat_data = [[s["lat"], s["lng"]] for s in stations for _ in range(5)]
    HeatMap(heat_data).add_to(m)

    return m


# -----------------------------------
# 🔹 MAIN UI
# -----------------------------------
def journey_ui(location, target_lang, t, user_lat=None, user_lng=None):

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

    if not stations:
        st.warning(t("No polling stations found"))
        return

    # -------- BASE LOCATION RESOLUTION --------
    if user_lat is not None and user_lng is not None:
        base_lat, base_lng = user_lat, user_lng
        st.info(f"🛰️ {t('Using precise GPS coordinates for real-time distance.')}")
    else:
        # Try to parse from location string or fallback to first station
        try:
            if "," in location:
                base_lat, base_lng = map(float, location.split(","))
            else:
                base_lat, base_lng = stations[0]["lat"], stations[0]["lng"]
        except:
            base_lat, base_lng = stations[0]["lat"], stations[0]["lng"]
        
        st.warning(f"📍 {t('Using area center for distance. For exact distance, please use Detect Location in Profile.')}")

    # -------- CALC DISTANCES --------
    for s in stations:
        if s.get("lat") and s.get("lng"):
            s["distance"] = calculate_distance(base_lat, base_lng, s["lat"], s["lng"])
            s["is_nearest"] = False
        else:
            s["distance"] = 999
            s["crowd"] = t("Unknown")

    # Mark nearest
    stations.sort(key=lambda x: x["distance"])
    stations[0]["is_nearest"] = True

    # -------- RENDER CARDS --------
    st.markdown(f"## 🏁 {t('Nearest Polling Booths')}")

    for s in stations[:3]:
        is_nearest = s["is_nearest"]
        card_class = "cg-card-nearest" if is_nearest else "cg-card"
        badge = f"<span class='cg-badge-green'>{t('NEAREST')}</span>" if is_nearest else ""
        
        # Real-time indicators
        dist_display = f"{s['distance']} km" if s["distance"] > 0.001 else t("You are here!")
        
        nav_url = f"https://www.google.com/maps/dir/?api=1&destination={s['lat']},{s['lng']}"
        
        st.markdown(f"""
        <div class='{card_class}'>
            <div style='display:flex; justify-content:space-between; align-items:center'>
                <h4 style='margin:0'>📍 {s['name']} {badge}</h4>
            </div>
            <p style='color:#94a3b8; font-size:14px; margin:5px 0'>🏠 {s['address']}</p>
            <div style='display:flex; gap:20px; margin-top:10px'>
                <div>📏 <b>{t('Distance')}:</b> {dist_display}</div>
                <div>👥 <b>{t('Crowd')}:</b> {s.get('crowd', t('Medium'))}</div>
            </div>
            <a href="{nav_url}" target="_blank" style="text-decoration:none;">
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); 
                            color: white; padding: 10px; border-radius: 8px; 
                            text-align: center; margin-top: 15px; font-weight: 600;
                            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);">
                    🚗 {t('Navigate to Booth')}
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)

    # -------- MAP --------
    duration, dist_m, poly_str = None, None, None
    if stations[0]["is_nearest"]:
        duration, dist_m, poly_str = get_route_details(base_lat, base_lng, stations[0]["lat"], stations[0]["lng"])

    st.markdown("<div class='cg-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"### 🗺️ {t('Route to Nearest Booth')}")
    
    m = create_map(stations, base_lat, base_lng, poly_str)
    st_folium(m, width='stretch', height=450, key="stable_map_v2")

    if duration:
        st.success(f"⏱️ {t('Estimated Travel Time')}: {duration}")