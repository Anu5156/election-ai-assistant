from app.services.election_service import get_next_step

def test_unregistered_user():
    class User:
        age = 20
        is_registered = False

    steps = get_next_step(User())
    assert "Step 1" in steps[0]