import pytest
from app.models.user import User

def test_user_creation():
    user = User(age=25, location="Udupi", is_registered=True)
    assert user.age == 25
    assert user.location == "Udupi"
    assert user.is_registered is True

def test_user_eligible():
    user = User(age=18, location="Udupi", is_registered=True)
    assert user.is_eligible() is True

def test_user_not_eligible():
    user = User(age=17, location="Udupi", is_registered=False)
    assert user.is_eligible() is False

def test_user_needs_registration():
    user = User(age=20, location="Udupi", is_registered=False)
    assert user.needs_registration() is True

def test_user_ready_to_vote():
    user = User(age=20, location="Udupi", is_registered=True)
    assert user.get_status() == "Ready to Vote"

def test_user_status_not_eligible():
    user = User(age=16, location="Udupi", is_registered=False)
    assert user.get_status() == "Not Eligible"

def test_user_status_needs_registration():
    user = User(age=20, location="Udupi", is_registered=False)
    assert user.get_status() == "Needs Registration"

def test_user_defaults():
    user = User(age=20, location="Udupi", is_registered=True)
    assert user.preferred_language == "en"
    assert user.stage == "start"
    assert user.latitude is None
