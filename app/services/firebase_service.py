"""
Firebase Service Module - CivicGuide AI
Handles real-time data persistence, crowd tracking, and election analytics.

This module provides a secure, fail-safe connection to Google Cloud Firestore.
It automatically handles authentication for both local development (via service account JSON)
and Streamlit Cloud production (via st.secrets).
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ────────────── CONFIGURATION ──────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

db: Optional[firestore.client] = None

# ────────────── INITIALIZATION ──────────────
try:
    if not firebase_admin._apps:
        if os.path.exists(KEY_PATH):
            # 🏠 Local initialization
            cred = credentials.Certificate(KEY_PATH)
        elif "firebase" in st.secrets:
            # ☁️ Cloud initialization (Streamlit Secrets)
            import tempfile
            key_dict = dict(st.secrets["firebase"])
            # Firebase SDK expects a file path or a dict with specific formatting
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
                json.dump(key_dict, tmp)
                tmp_path = tmp.name
            cred = credentials.Certificate(tmp_path)
        else:
            raise FileNotFoundError("Missing Firebase configuration (JSON or Secrets)")
            
        firebase_admin.initialize_app(cred)
        
    db = firestore.client()
    logger.info("✅ Firebase connection established successfully")
except Exception as e:
    logger.warning(f"⚠️ Firebase initialization failed: {e}. Falling back to mock/local mode.")
    db = None


# ────────────── CORE SERVICES ──────────────

def submit_vote(candidate: str, location: str = "unknown") -> None:
    """
    Records a vote event with geospatial and temporal metadata.
    
    Args:
        candidate: Name of the candidate or party.
        location: The user's area or polling booth name.
    """
    if db is None:
        return

    try:
        db.collection("votes").add({
            "candidate": candidate,
            "location": location,
            "timestamp": datetime.now(timezone.utc)
        })
    except Exception as e:
        logger.error(f"Error submitting vote: {e}")


def get_vote_counts() -> Dict[str, int]:
    """
    Aggregates total votes per candidate from Firestore.
    
    Returns:
        A dictionary mapping candidate names to vote tallies.
    """
    if db is None:
        return {}

    counts: Dict[str, int] = {}
    try:
        docs = db.collection("votes").stream()
        for d in docs:
            data = d.to_dict()
            candidate = data.get("candidate", "Unknown")
            counts[candidate] = counts.get(candidate, 0) + 1
    except Exception as e:
        logger.error(f"Error fetching vote counts: {e}")

    return counts


def get_crowd_data() -> Dict[str, int]:
    """
    Calculates the distribution of voters across various locations.
    
    Returns:
        A dictionary mapping locations to the number of active voters.
    """
    if db is None:
        return {}

    crowd: Dict[str, int] = {}
    try:
        docs = db.collection("votes").stream()
        for d in docs:
            data = d.to_dict()
            loc = data.get("location", "unknown")
            crowd[loc] = crowd.get(loc, 0) + 1
    except Exception as e:
        logger.error(f"Error fetching crowd data: {e}")

    return crowd


def get_booth_crowd() -> Dict[str, int]:
    """
    Returns live crowd density (votes within the last 30 minutes) per booth.
    This is used for real-time traffic estimation.
    
    Returns:
        A dictionary of booth names and their recent voter count.
    """
    if db is None:
        return {}

    now = datetime.now(timezone.utc)
    crowd: Dict[str, int] = {}
    
    try:
        # Optimization: In production, use a Firestore Query to filter by timestamp
        docs = db.collection("votes").stream()
        for d in docs:
            data = d.to_dict()
            loc = data.get("location", "unknown")
            ts = data.get("timestamp")

            if ts:
                # Ensure timezone awareness for comparison
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)

                # Count only if within last 30 minutes (1800 seconds)
                if (now - ts).total_seconds() < 1800:
                    crowd[loc] = crowd.get(loc, 0) + 1
    except Exception as e:
        logger.error(f"Error calculating booth crowd: {e}")

    return crowd


def submit_verification(voter_qr: str, is_authentic: bool) -> None:
    """
    Logs ID verification attempts for security auditing.
    
    Args:
        voter_qr: The scanned QR code data (obfuscated in production).
        is_authentic: Result of the AI-powered authenticity check.
    """
    if db is None:
        return

    try:
        db.collection("verification_logs").add({
            "voter_qr": voter_qr,
            "is_authentic": is_authentic,
            "timestamp": datetime.now(timezone.utc)
        })
    except Exception as e:
        logger.error(f"Error logging verification: {e}")


def get_detailed_votes() -> List[Dict[str, Any]]:
    """
    Retrieves the full dataset of votes for analytical visualization.
    
    Returns:
        A list of raw dictionary records from the 'votes' collection.
    """
    if db is None:
        return []

    try:
        docs = db.collection("votes").stream()
        return [d.to_dict() for d in docs]
    except Exception as e:
        logger.error(f"Error fetching detailed votes: {e}")
        return []


def get_live_analytics() -> Dict[str, int]:
    """
    Interface for live polling analytics.
    
    Returns:
        Current global vote distribution.
    """
    return get_vote_counts()
