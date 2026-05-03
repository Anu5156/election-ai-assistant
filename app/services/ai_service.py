"""
AI Guidance Service - CivicGuide AI
A hybrid decision-engine combining rule-based heuristics and Large Language Models.

This service prioritizes fast, deterministic rule-based responses for common 
queries (eligibility, documentation, voting hours) and falls back to 
GPT-4o-mini for complex, natural language questions.
"""

import logging
from typing import Any, Optional
from openai import OpenAI
from app.config import OPENAI_API_KEY

# ────────────── CONFIGURATION ──────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_guidance(user: Any, query: str) -> str:
    """
    Orchestrates the response logic for user queries.
    Execution Flow: Heuristics -> Input Validation -> LLM Inference.
    
    Args:
        user: The User model instance containing profile data.
        query: The raw question string from the user.
        
    Returns:
        A finalized response string.
    """
    if not query:
        return "Please ask a question related to the election process."

    query_lower = query.lower().strip()

    # ────────────── 1. RULE-BASED DETERMINISTIC ENGINE ──────────────
    # High-priority rules to ensure policy compliance and speed.

    if "who to vote" in query_lower or "whom to vote" in query_lower:
        return (
            "As an impartial assistant, I cannot suggest a candidate or party. "
            "Please review the official manifestos and choose responsibly."
        )

    if "eligible" in query_lower:
        if user.age < 18:
            return "You are not eligible to vote yet. The legal voting age in India is 18."
        return "You are eligible to vote if your name is present in the electoral roll."

    if any(k in query_lower for k in ["where", "polling station", "polling booth"]):
        return f"Your nearest polling station for {user.location} is displayed in the 'Map' and 'Journey' sections."

    if any(k in query_lower for k in ["documents", "id proof", "voter id"]):
        return (
            "You must carry your Voter ID (EPIC). If not available, you can use "
            "Aadhaar, Passport, Driving License, or other ECI-approved photo IDs."
        )

    if any(k in query_lower for k in ["time", "when", "hours"]):
        return (
            "Voting typically happens from 7:00 AM to 6:00 PM. \n\n"
            "🟢 7 AM – 9 AM: Recommended (Low crowd)\n"
            "🔴 12 PM – 3 PM: Peak hours (High crowd)\n"
            "🟢 4 PM – 6 PM: Recommended (Moderate crowd)"
        )

    if any(k in query_lower for k in ["register", "voter card", "apply"]):
        return (
            "Registration is done via the NVSP portal (voters.eci.gov.in). "
            "You can use the 'Journey' tab in this app for a step-by-step guide."
        )

    if "help" in query_lower:
        return (
            f"I can help you navigate the 2026 elections in {user.location}. "
            "Ask me about registration, finding booths, or required documents."
        )

    # ────────────── 2. VALIDATION & FALLBACK ──────────────

    if len(query_lower) < 3:
        return "Please ask a more specific question related to the election."

    # ────────────── 3. GENERATIVE AI INFERENCE (LLM) ──────────────
    # Used for complex reasoning and natural language understanding.

    try:
        system_prompt = (
            "You are an intelligent, non-partisan election assistant for CivicGuide AI. "
            "Provide clear, concise, and helpful guidance based on the user's profile."
        )
        
        user_context = (
            f"Voter Profile:\n- Age: {user.age}\n- Location: {user.location}\n"
            f"- Registration Status: {'Registered' if user.is_registered else 'Unregistered'}\n\n"
            f"Question: {query}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_context}
            ],
            max_tokens=250,
            temperature=0.7
        )

        return response.choices[0].message.content or "I'm sorry, I couldn't generate a response."

    except Exception as e:
        logger.error(f"AI Service Inference Error: {e}")
        return (
            "Our AI reasoning engine is currently at capacity. "
            "Please refer to the 'Journey' tab for standard election procedures."
        )