import os
from openai import OpenAI
from app.config import OPENAI_API_KEY

# 🔥 keep your original client
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_guidance(user, query):
    query_lower = query.lower().strip()

    # =========================================================
    # 🔥 1. RULE-BASED INTELLIGENCE (IMPROVED)
    # =========================================================

    if "who to vote" in query_lower or "whom to vote" in query_lower:
        return "I cannot suggest a candidate. Please review policies and choose responsibly."

    elif "eligible" in query_lower:
        if user.age < 18:
            return "You are not eligible to vote yet. You must be at least 18 years old."
        else:
            return "You are eligible to vote if you are registered in the voter list."

    elif "where" in query_lower or "polling station" in query_lower:
        return f"You can find your nearest polling station in the map section for {user.location}."

    elif "polling booth" in query_lower:
        return f"Your polling booth will be displayed on the map for {user.location}."

    elif "documents" in query_lower or "id" in query_lower:
        return "Carry your Voter ID or any valid government ID proof like Aadhaar, Passport, etc."

    elif "time" in query_lower or "when" in query_lower:
        return """
Best time to vote:

🟢 7 AM – Low crowd  
🟡 11 AM – Moderate  
🔴 2–4 PM – High crowd  
🟢 After 5 PM – Low again
"""

    elif "register" in query_lower or "not registered" in query_lower:
        return "You can register through the NVSP portal or visit your nearest election office."

    elif "help" in query_lower:
        return f"""
Here’s how I can help:

📍 Find polling station near {user.location}
🚗 Get navigation directions
📅 Set voting reminders
🗣️ Answer election questions
"""

    elif "how" in query_lower and "vote" in query_lower:
        return f"""
Here’s how you can vote:

1. Go to your polling station near {user.location}
2. Carry valid ID proof
3. Verify your name in voter list
4. Cast your vote using EVM
"""

    # =========================================================
    # 🔁 2. SMART FALLBACK (BEFORE OPENAI)
    # =========================================================

    if len(query_lower) < 3:
        return "Please ask a clear question related to voting."

    # =========================================================
    # 🔥 3. OPENAI (ORIGINAL LOGIC RETAINED)
    # =========================================================

    try:
        prompt = f"""
You are an intelligent election assistant.

User:
- Age: {user.age}
- Location: {user.location}
- Registered: {user.is_registered}

Instructions:
- Give simple explanations
- Provide step-by-step guidance
- Be clear and helpful
- Avoid political bias

User Question: {query}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    # =========================================================
    # 🔥 4. FAIL-SAFE (VERY IMPORTANT)
    # =========================================================

    except Exception as e:
        print("AI ERROR:", e)

        return (
            "AI service is temporarily unavailable. "
            "Please visit the official election website or your nearest polling office."
        )