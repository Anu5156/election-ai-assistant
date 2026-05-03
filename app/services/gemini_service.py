from google import genai
import os
import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv(override=True)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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
def get_gemini_response(prompt, history=None):
    # Model hierarchy for resilience (FAANG-level fallback)
    models = ["gemini-2.0-flash", "gemini-1.5-flash"]
    
    full_prompt = f"{SYSTEM_INSTRUCTION}\n\nUser: {prompt}\nAI:"
    if history:
        # Pass only recent history to save tokens and stay within limits
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{history_text}\nUser: {prompt}\nAI:"

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
                print(f"DEBUG: Gemini Error ({model_name}): {err_str}")
                
                # Handling 429 Resource Exhausted gracefully
                if "429" in err_str or "resource_exhausted" in err_str:
                    if attempt == 0:
                        time.sleep(2) # slightly longer wait
                        continue
                    else:
                        # Fallback to next model in list
                        break 
                
                # For other unexpected errors, try the next model instead of giving up
                break 

    return "🤖 We're experiencing high demand or intermittent connectivity. Please try your question again in a few seconds."

@st.cache_data(show_spinner=False)
def get_ai_strategy(age, location, voting_area, is_registered):
    prompt = f"""
    Based on this voter profile, provide a 2-sentence "FAANG-level" personalized voting strategy:
    - Age: {age}
    - Current Location: {location}
    - Voting Area: {voting_area}
    - Registration Status: {"Registered" if is_registered else "Not Registered"}
    
    Context: The election is on May 5, 2026.
    If not registered, emphasize that as step 1. 
    If far away (e.g. Ramanagara to Udupi), suggest planning travel.
    Keep it concise, professional, and high-impact.
    """
    
    return get_gemini_response(prompt)