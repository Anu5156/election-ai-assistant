import time
import streamlit as st
import re
from typing import List
import os

# ────────────── SECURITY CONFIG ──────────────
MAX_INPUT_LENGTH = 500
RATE_LIMIT_SECONDS = 2  # Minimum seconds between AI requests

def validate_age(age: int) -> bool:
    """
    Validates if the user's age is within the legal and biological range.
    """
    return 18 <= age <= 120

def is_rate_limited() -> bool:
    """
    Checks if the current session is exceeding the request rate limit.
    This prevents automated spamming of costly AI/Maps APIs.
    """
    now = time.time()
    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0
    
    if now - st.session_state.last_request_time < RATE_LIMIT_SECONDS:
        return True
    
    st.session_state.last_request_time = now
    return False

def sanitize_input(text: str) -> bool:
    """
    Professional multi-layer sanitization to prevent Prompt Injection, XSS, and SQLi.
    """
    if not text:
        return True
        
    # 📏 Layer 1: Length Validation
    if len(text) > MAX_INPUT_LENGTH:
        return False

    # 🛑 Layer 2: Malicious Pattern Matching (Heuristics)
    blocked_patterns = [
        r"ignore", r"hack", r"bypass", r"forget", r"system prompt",
        r"admin", r"root", r"sudo", r"exec\(", r"eval\(",
        r"javascript:", r"onload=", r"onerror=", r"<script", r"UNION SELECT",
        r"prompt injection", r"dan mode", r"developer mode"
    ]
    
    text_lower = text.lower()
    for pattern in blocked_patterns:
        if re.search(pattern, text_lower):
            return False
            
    # 🧩 Layer 3: Structural Analysis
    # Blocks suspicious HTML tags and unbalanced brackets used for injection
    if "<" in text or ">" in text or "{" in text or "}" in text:
        # Check if it looks like actual HTML or code injection
        if re.search(r"<[^>]+>", text) or re.search(r"\{[^\}]+\}", text):
            return False
        
    return True

def audit_environment() -> List[str]:
    """
    Audits the current application environment for security misconfigurations.
    Returns a list of warnings.
    """
    warnings = []
    # Check for exposed debug flags (simulated check)
    if os.getenv("STREAMLIT_SERVER_RUN_ON_SAVE") == "true":
        warnings.append("Warning: Auto-reload is enabled (Production risk)")
    
    return warnings