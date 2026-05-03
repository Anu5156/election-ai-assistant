import pytest
from app.services import firebase_service

def test_db_none_safety_guards():
    """Verify that service functions don't crash when Firebase db is None (default on Cloud)"""
    # Ensure db is None
    firebase_service.db = None
    
    # These should return empty values/None instead of crashing
    assert firebase_service.get_vote_counts() == {}
    assert firebase_service.get_crowd_data() == {}
    assert firebase_service.get_booth_crowd() == {}
    assert firebase_service.get_detailed_votes() == []
    
    # These should just return (void) without crashing
    assert firebase_service.submit_vote("Candidate A", "Udupi") is None
    assert firebase_service.submit_verification("QR123", True) is None
