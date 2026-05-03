"""
Configuration Module - CivicGuide AI
Manages API keys and environment settings with dual-mode support (Local vs Cloud).

Priority Order:
1. Environment Variables (.env / OS)
2. Streamlit Secrets (for Cloud deployment)
"""

import os
from typing import Optional
import streamlit as st
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

def _get_key(name: str) -> Optional[str]:
    """
    Retrieves a configuration key by name.
    Prioritizes local environment variables, falling back to Streamlit Secrets for cloud deployment.
    
    Args:
        name: The name of the API key or configuration variable.
        
    Returns:
        The configuration value or None if not found.
    """
    # 🏠 Check .env or OS environment first (Local Development)
    val = os.getenv(name)
    if val:
        return val
        
    # ☁️ Check st.secrets (Streamlit Cloud Production)
    try:
        return st.secrets.get(name)
    except Exception:
        return None

# 🔑 Global API Credentials
OPENAI_API_KEY: Optional[str] = _get_key("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY: Optional[str] = _get_key("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY: Optional[str] = _get_key("GEMINI_API_KEY")