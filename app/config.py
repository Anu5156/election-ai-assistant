from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

def _get_key(name):
    """Try .env first (local), then st.secrets (Streamlit Cloud)."""
    val = os.getenv(name)
    if val:
        return val
    try:
        return st.secrets[name]
    except Exception:
        return None

OPENAI_API_KEY = _get_key("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = _get_key("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY = _get_key("GEMINI_API_KEY")