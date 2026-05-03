import pytest
from unittest.mock import MagicMock, patch
from app.services.gemini_service import get_gemini_response

def test_gemini_fallback_logic():
    """
    Test that Gemini service correctly falls back to the secondary model 
    when the primary one fails with a 429 error.
    """
    mock_client = MagicMock()
    
    # Simulate 429 error for the first model, then success for the second
    mock_client.models.generate_content.side_effect = [
        Exception("Resource exhausted (429)"),
        MagicMock(text="Fallback success")
    ]
    
    with patch("app.services.gemini_service.client", mock_client):
        # We need to bypass the cache for this test
        from app.services.gemini_service import get_gemini_response
        response = get_gemini_response("Hello", history=[])
        assert response == "Fallback success"
        assert mock_client.models.generate_content.call_count == 2

def test_gemini_exhaustion_message():
    """Test that it returns a graceful message if all models fail."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("General Error")
    
    with patch("app.services.gemini_service.client", mock_client):
        response = get_gemini_response("Hello")
        assert "intermittent connectivity" in response
