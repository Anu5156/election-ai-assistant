"""
Maps Service - CivicGuide AI
V2.2.1 - Enhanced Reliability & Legacy Compatibility
"""
import requests
from app.config import GOOGLE_MAPS_API_KEY
import streamlit as st
from typing import Tuple, List, Dict, Optional, Any
from math import radians, sin, cos, sqrt, atan2

# ---------------- GEOCODING ----------------
def geocode_location(location: str) -> Tuple[Optional[float], Optional[float]]:
    """Converts location string to (lat, lng)."""
    try:
        if "," in location:
            parts = location.split(",")
            if len(parts) == 2:
                try:
                    return float(parts[0].strip()), float(parts[1].strip())
                except ValueError: pass
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": location, "key": GOOGLE_MAPS_API_KEY}
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except Exception as e:
        print(f"GEOCODE ERROR: {e}")
    return None, None

# ---------------- SEARCH POLLING STATIONS ----------------
@st.cache_data(show_spinner=False)
def get_polling_stations(location: str, bias_lat: Optional[float] = None, bias_lng: Optional[float] = None) -> List[Dict[str, Any]]:
    """Searches for polling stations using Google Places (New) API with fallback logic."""
    try:
        url = "https://places.googleapis.com/v1/places:searchText"
        lat, lng = geocode_location(location)
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating"
        }
        
        queries = [
            f"polling station near {location}, India",
            f"government school near {location}, India",
            f"voting center near {location}, India"
        ]
        
        all_stations = []
        seen_names = set()
        for q in queries:
            payload = {"textQuery": q}
            if lat and lng:
                payload["locationBias"] = {"circle": {"center": {"latitude": lat, "longitude": lng}, "radius": 10000.0}}
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            data = res.json()
            for p in data.get("places", []):
                name = p["displayName"]["text"]
                if name not in seen_names:
                    all_stations.append({
                        "name": name,
                        "address": p.get("formattedAddress", ""),
                        "lat": p["location"]["latitude"],
                        "lng": p["location"]["longitude"],
                        "rating": p.get("rating", 0.0)
                    })
                    seen_names.add(name)
        return all_stations
    except Exception as e:
        print(f"PLACES API ERROR: {e}")
        return []

# ---------------- ROUTE DETAILS ----------------
def get_route_details(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Tuple[str, str, str]:
    """Calculates walking route."""
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "mode": "walking", "key": GOOGLE_MAPS_API_KEY
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if data["status"] == "OK":
            route = data["routes"][0]["legs"][0]
            return route["duration"]["text"], route["distance"]["text"], data["routes"][0]["overview_polyline"]["points"]
    except Exception as e:
        print(f"DIRECTIONS API ERROR: {e}")
    return "N/A", "N/A", None

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance."""
    R = 6371.0
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1-a)), 2)

# ── Export Aliases (Legacy Support & New Standard) ──
fetch_polling_stations = get_polling_stations
load_stations = get_polling_stations # Restored for legacy compatibility