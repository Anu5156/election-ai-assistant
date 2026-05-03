from typing import Any

def recommend_info(user: Any) -> str:
    """
    Generates a personalized recommendation summary based on the user's location.
    
    Args:
        user: The user profile object.
        
    Returns:
        A formatted string with civic participation advice.
    """
    return f"""
📍 Based on your profile in {user.location}:

👉 Important Suggestions:
- Compare the manifestos of all candidates in your constituency.
- Check past performance records on the 'Know Your Candidate' portal.
- Verify candidate credibility and criminal records if any.

⚠️ Reminder: This AI tool provides guidance, but you must make your own informed decision at the booth.
"""