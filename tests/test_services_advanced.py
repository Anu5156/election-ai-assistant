import pytest
from unittest.mock import MagicMock, patch
from app.services.maps_service import geocode_location, get_polling_stations
from app.services.translate_service import translate_text

def test_geocode_raw_coords():
    """Verify that geocode_location handles raw coordinate strings correctly."""
    lat, lng = geocode_location("12.9716, 77.5946")
    assert lat == 12.9716
    assert lng == 77.5946

@patch("requests.get")
def test_geocode_api_failure(mock_get):
    """Verify graceful handling of Geocoding API failures."""
    mock_get.return_value.json.return_value = {"results": []}
    lat, lng = geocode_location("Invalid Location")
    assert lat is None
    assert lng is None

@patch("requests.post")
def test_get_polling_stations_api(mock_post):
    """Verify that Places API data is parsed correctly."""
    mock_post.return_value.json.return_value = {
        "places": [
            {
                "displayName": {"text": "Test Station"},
                "formattedAddress": "123 Street",
                "location": {"latitude": 10.0, "longitude": 20.0},
                "rating": 4.5
            }
        ]
    }
    # Mock geocode_location to avoid network call
    with patch("app.services.maps_service.geocode_location", return_value=(10.0, 20.0)):
        stations = get_polling_stations("Delhi")
        assert len(stations) >= 1
        assert stations[0]["name"] == "Test Station"

@patch("app.services.translate_service._call_translate_api")
def test_translate_caching(mock_call):
    """Verify that translations use the cache to save API costs."""
    mock_call.return_value = [{"translatedText": "नमस्ते"}]
    
    # First call
    res1 = translate_text("Hello", "hi")
    # Second call (should hit cache)
    res2 = translate_text("Hello", "hi")
    
    assert res1 == res2
    assert mock_call.call_count == 1
