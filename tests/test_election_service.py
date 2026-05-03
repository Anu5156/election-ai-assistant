import pytest
from app.services.election_service import get_next_step

class MockUser:
    def __init__(self, age, location, is_registered):
        self.age = age
        self.location = location
        self.is_registered = is_registered

def test_underage_user():
    user = MockUser(17, "Delhi", False)
    steps = get_next_step(user)
    assert any("not eligible" in s.lower() for s in steps)

def test_unregistered_user():
    user = MockUser(20, "Mumbai", False)
    steps = get_next_step(user)
    # Match "registration" (from Form 6)
    assert any("registration" in s.lower() for s in steps)

def test_registered_user():
    user = MockUser(25, "Bengaluru", True)
    steps = get_next_step(user)
    # Match "polling station" or "booth"
    assert any("polling station" in s.lower() or "booth" in s.lower() for s in steps)
    assert "Bengaluru" in steps[0]

def test_none_user():
    steps = get_next_step(None)
    assert "not available" in steps[0].lower()

def test_boundary_age_18():
    user = MockUser(18, "Chennai", False)
    steps = get_next_step(user)
    assert any("registration" in s.lower() for s in steps)
