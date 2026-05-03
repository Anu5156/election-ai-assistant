import requests
from app.config import GOOGLE_MAPS_API_KEY
import streamlit as st


# ---------------- GEOCODING ----------------
def geocode_location(location):
    try:
        # If it's already a lat,lng string, return it
        if "," in location:
            parts = location.split(",")
            if len(parts) == 2:
                try:
                    return float(parts[0].strip()), float(parts[1].strip())
                except:
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
        print("GEOCODE ERROR:", e)

    return None, None


# ---------------- MAIN FUNCTION ----------------
@st.cache_data(show_spinner=False)
def get_polling_stations(location, bias_lat=None, bias_lng=None):
    try:
        print(f"Fetching stations for: {location}")

        url = "https://places.googleapis.com/v1/places:searchText"

        lat, lng = geocode_location(location)

        session = requests.Session()

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location"
        }

        queries = [
            f"government office near {location}",
            f"municipal office near {location}",
            f"school near {location}",
            f"community center near {location}"
        ]

        for query in queries:

            body = {
                "textQuery": query,
                "rankPreference": "DISTANCE"
            }

            if lat and lng:
                body["locationBias"] = {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lng
                        },
                        "radius": 5000.0
                    }
                }

            for attempt in range(2):
                try:
                    response = session.post(url, json=body, headers=headers, timeout=5)
                    data = response.json()
                    break
                except Exception as e:
                    print(f"Retry {attempt+1} failed:", e)
                    data = {}

            print("QUERY:", query)
            print("RESULT COUNT:", len(data.get("places", [])))

            if "places" not in data:
                continue

            results = data.get("places", [])

            if results:
                stations = []

                for place in results[:5]:
                    name = place.get("displayName", {}).get("text", "Unknown")
                    address = place.get("formattedAddress", "")

                    lat_p = place.get("location", {}).get("latitude")
                    lng_p = place.get("location", {}).get("longitude")

                    if lat_p is None or lng_p is None:
                        continue

                    nav_link = (
                        f"https://www.google.com/maps/dir/?api=1"
                        f"&origin=Current+Location"
                        f"&destination={lat_p},{lng_p}"
                        f"&travelmode=driving"
                    )

                    stations.append({
                        "name": name,
                        "address": address,
                        "lat": lat_p,
                        "lng": lng_p,
                        "nav_link": nav_link
                    })

                if stations:
                    return stations

        print("Using fallback locations")

        return [
            {
                "name": "Nearest Government School",
                "address": location,
                "lat": lat,
                "lng": lng,
                "nav_link": f"https://www.google.com/maps/search/?api=1&query=school+near+{location}"
            },
            {
                "name": "Municipal Office",
                "address": location,
                "lat": lat,
                "lng": lng,
                "nav_link": f"https://www.google.com/maps/search/?api=1&query=government+office+near+{location}"
            }
        ]

    except Exception as e:
        print("MAP ERROR:", e)
        return []


# ---------------- ROUTES API (NEW - ADDED HERE) ----------------
def get_route_details(origin_lat, origin_lng, dest_lat, dest_lng):
    try:
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        }

        body = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin_lat,
                        "longitude": origin_lng
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": dest_lat,
                        "longitude": dest_lng
                    }
                }
            },
            "travelMode": "DRIVE"
        }

        res = requests.post(url, json=body, headers=headers, timeout=5)
        data = res.json()

        if "routes" not in data:
            return None, None, None

        route = data["routes"][0]

        duration = route.get("duration")
        distance = route.get("distanceMeters")
        polyline = route.get("polyline", {}).get("encodedPolyline")

        return duration, distance, polyline

    except Exception as e:
        print("ROUTE ERROR:", e)
        return None, None, None