def get_next_step(user):
    # 🔒 Safety check
    if user is None:
        return ["User information not available."]

    # 🚫 Not eligible
    if user.age < 18:
        return [
            "❌ You are not eligible to vote yet.",
            "ℹ️ You must be at least 18 years old.",
            "📅 Come back once you turn 18 to register."
        ]

    # 📝 Not registered
    if not user.is_registered:
        return [
            "📝 Step 1: Fill voter registration form (NVSP portal)",
            "📄 Step 2: Submit valid ID proof (Aadhaar, Passport, etc.)",
            "⏳ Step 3: Wait for verification",
            "✅ Step 4: Get your Voter ID"
        ]

    # ✅ Fully ready
    return [
        f"📍 Step 1: Check your polling booth near {user.location}",
        "🪪 Step 2: Carry your Voter ID or valid ID proof",
        "🗳️ Step 3: Visit polling station",
        "✔️ Step 4: Cast your vote using EVM"
    ]