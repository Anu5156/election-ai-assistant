from typing import List, Optional

def get_next_step(user: Optional[object]) -> List[str]:
    """
    Determines the next logical steps for a voter based on their profile.
    
    Args:
        user: A user object containing age, location, and registration status.
        
    Returns:
        A list of actionable strings representing the next steps in the voting process.
    """
    
    # 🔒 Safety check for null user
    if user is None:
        return ["User information not available. Please complete your profile."]

    # 🚫 Not eligible (Age under 18)
    if user.age < 18:
        return [
            "❌ You are not eligible to vote yet.",
            "ℹ️ You must be at least 18 years old to cast a vote in India.",
            "📅 Come back once you turn 18 to start your civic journey."
        ]

    # 📝 Not registered (Eligible but lacks Voter ID)
    if not user.is_registered:
        return [
            "📝 Step 1: Fill voter registration form (Form 6) on the NVSP portal",
            "📄 Step 2: Upload valid ID proof and passport-size photo",
            "⏳ Step 3: Wait for field verification by the Booth Level Officer (BLO)",
            "✅ Step 4: Download your e-EPIC card or receive your Voter ID"
        ]

    # ✅ Fully ready to vote
    return [
        f"📍 Step 1: Locate your assigned polling booth near {user.location}",
        "🪪 Step 2: Carry your physical Voter ID card or a valid alternative photo ID",
        "🗳️ Step 3: Visit the polling station during voting hours",
        "✔️ Step 4: Cast your vote securely on the EVM"
    ]