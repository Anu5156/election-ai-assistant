"""
Gemini AI Service Module - CivicGuide AI
Powered by Google Gemini 2.0 & 1.5 Flash models.

This module manages the intelligent conversation engine and the personalized 
voting strategy generator. It features a robust multi-model fallback system
and exponential backoff to handle rate limits (429) and connectivity issues.
"""

import os
import time
import logging
from typing import List, Dict, Optional, Any

import streamlit as st
from google import genai
from dotenv import load_dotenv
from app.config import GEMINI_API_KEY

# ────────────── CONFIGURATION ──────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# Initialize the Gemini Client
# Uses GEMINI_API_KEY from config.py or environment fallback
client = genai.Client(api_key=GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """
You are the CivicGuide AI Assistant, a specialized expert in the election process. 
Your goal is to provide accurate, non-partisan information about voting, registration, 
polling stations, and candidate details. 

- If asked about voting dates, mention the upcoming Lok Sabha election on May 5, 2026.
- Always encourage civic participation.
- If you don't know an answer, suggest checking the official ECI (Election Commission of India) portal.
- Keep responses professional, clear, and supportive.
"""


@st.cache_data(show_spinner=False)
def get_gemini_response(prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Generates a response using the Google Gemini model hierarchy.
    Features automated model fallback (2.0 Flash -> 1.5 Flash) for high availability.
    
    Args:
        prompt: The user's query or the task description.
        history: Optional list of previous message dictionaries for context.
        
    Returns:
        The generated text response or a graceful error message.
    """
    
    # Model hierarchy for high-availability resilience
    models = ["gemini-2.0-flash", "gemini-1.5-flash"]
    
    # Context aggregation
    if history:
        # Pass only the 3 most recent turns to maintain high quality and manage token limits
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{history_text}\nUser: {prompt}\nAI:"
    else:
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nUser: {prompt}\nAI:"

    for model_name in models:
        for attempt in range(2): 
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                
                if response and response.text:
                    return response.text
                
            except Exception as e:
                err_str = str(e).lower()
                logger.debug(f"Gemini API attempt ({model_name}) failed: {err_str}")
                
                # 🛑 Handle 429 Resource Exhausted / Rate Limits
                if "429" in err_str or "resource_exhausted" in err_str:
                    if attempt == 0:
                        logger.info(f"Retrying {model_name} after 429 cooldown...")
                        time.sleep(2)
                        continue
                    else:
                        # Fallback to the next model in the hierarchy
                        logger.warning(f"Exhausted {model_name}, falling back...")
                        break 
                
                # For any other fatal error, immediately try the next model
                break 

    return (
        "🤖 We're experiencing high demand or intermittent connectivity. "
        "Please try your question again in a few seconds."
    )


@st.cache_data(show_spinner=False)
def get_ai_strategy(age: int, location: str, voting_area: Optional[str], is_registered: bool) -> str:
    """
    Synthesizes a personalized voting strategy using Gemini's creative reasoning.
    
    Args:
        age: User's age.
        location: User's current location.
        voting_area: User's registered voting constituency.
        is_registered: Boolean status of registration.
        
    Returns:
        A concise, professional 2-sentence strategy.
    """
    
    v_area = voting_area if voting_area else "the current location"
    
    prompt = f"""
    Based on this voter profile, provide a 2-sentence professional personalized voting strategy:
    - Age: {age}
    - Current Location: {location}
    - Registered Voting Area: {v_area}
    - Registration Status: {"Registered" if is_registered else "Not Registered"}
    
    Context: The election is on May 5, 2026.
    Requirement: 
    - If not registered, focus on NVSP registration steps.
    - If current location and voting area are different, include travel planning.
    - Style: Concise, authoritative, and encouraging.
    """
    
    return get_gemini_response(prompt)