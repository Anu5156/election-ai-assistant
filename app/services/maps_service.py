import requests
from app.config import GOOGLE_MAPS_API_KEY
import streamlit as st
from typing import Tuple, List, Dict, Optional, Any


# ---------------- GEOCODING ----------------
def geocode_location(location: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Converts a human-readable address or coordinate string into (latitude, longitude).
    
    Args:
        location: Address string (e.g., 'Bengaluru') or coordinate pair (e.g., '12.9,77.5').
        
    Returns:
        A tuple of (lat, lng). Returns (None, None) if geocoding fails.
    """
    try:
        # 📍 Check if input is already raw coordinates
        if "," in location:
            parts = location.split(",")
            if len(parts) == 2:
                try:
                    return float(parts[0].strip()), float(parts[1].strip())
                except ValueError:
                    pass

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": location,
            "key": GOOGLE_MAPS_API_KEY
        }

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
    """
    Searches for polling stations near a location using the Google Places (New) API.
    Uses strict Indian regional biasing to prevent international drift.
    
    Args:
        location: The user's search area.
        bias_lat: Optional latitude for regional weighting.
        bias_lng: Optional longitude for regional weighting.
        
    Returns:
        A list of dictionaries containing station name, address, coordinates, and rating.
    """
    try:
        print(f"DEBUG: Fetching stations for: {location}")

        url = "https://places.googleapis.com/v1/places:searchText"
        lat, lng = geocode_location(location)

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating"
        }

        # 🇮🇳 Strategy: Search for "polling station" and fallback to "government school"
        queries = [
            f"polling station near {location}, India",
            f"government school near {location}, India"
        ]

        stations = []
        station_names = set()

        for q in queries:
            print(f"DEBUG: QUERY: {q}")
            payload = {"textQuery": q}
            
            # Add bias if coordinates are available
            if lat and lng:
                payload["locationBias"] = {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lng},
                        "radius": 5000.0
                    }
                }

            res = requests.post(url, json=payload, headers=headers, timeout=10)
            data = res.json()

            results = data.get("places", [])
            print(f"DEBUG: RESULT COUNT: {len(results)}")

            for p in results:
                name = p["displayName"]["text"]
                if name not in station_names:
                    stations.append({
                        "name": name,
                        "address": p.get("formattedAddress", ""),
                        "lat": p["location"]["latitude"],
                        "lng": p["location"]["longitude"],
                        "rating": p.get("rating", 0.0)
                    })
                    station_names.add(name)

        return stations

    except Exception as e:
        print(f"PLACES API ERROR: {e}")
        return []


# ---------------- ROUTE DETAILS ----------------
def get_route_details(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict[str, Any]:
    """
    Calculates walking/driving route between two points using Google Directions API.
    
    Args:
        origin_lat, origin_lng: Starting coordinates.
        dest_lat, dest_lng: Destination coordinates.
        
    Returns:
        A dictionary containing distance text, duration text, and raw polyline.
    """
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "mode": "walking",
            "key": GOOGLE_MAPS_API_KEY
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data["status"] == "OK":
            route = data["routes"][0]["legs"][0]
            return {
                "distance": route["distance"]["text"],
                "duration": route["duration"]["text"],
                "polyline": data["routes"][0]["overview_polyline"]["points"]
            }
    except Exception as e:
        print(f"DIRECTIONS API ERROR: {e}")

    return {"distance": "N/A", "duration": "N/A", "polyline": None}