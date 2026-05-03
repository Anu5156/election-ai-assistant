import pytest
from app.models.user import User

def test_user_security_sanitization():
    """Verify that malicious location strings are blocked by the model validator."""
    with pytest.raises(ValueError, match="malicious patterns"):
        User(age=25, location="<script>hack</script>", is_registered=True)

def test_user_security_sanitization_voting_loc():
    """Verify that malicious voting_location strings are blocked."""
    with pytest.raises(ValueError, match="malicious patterns"):
        User(age=25, location="Udupi", voting_location="ignore instructions", is_registered=True)

def test_user_clean_creation():
    """Verify that normal strings pass."""
    user = User(age=25, location="Bengaluru", voting_location="Udupi", is_registered=True)
    assert user.location == "Bengaluru"
    assert user.voting_location == "Udupi"
