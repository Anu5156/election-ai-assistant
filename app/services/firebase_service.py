import os
import json
from datetime import datetime

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import timezone


# ================================
# 🔐 FIREBASE INIT (LOCAL + CLOUD)
# ================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

db = None  # Default to None

try:
    if not firebase_admin._apps:
        if os.path.exists(KEY_PATH):
            cred = credentials.Certificate(KEY_PATH)
        elif "firebase" in st.secrets:
            import tempfile
            key_dict = dict(st.secrets["firebase"])
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
            json.dump(key_dict, tmp)
            tmp.close()
            cred = credentials.Certificate(tmp.name)
        else:
            raise FileNotFoundError("No Firebase credentials found")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected successfully")
except Exception as e:
    print(f"⚠️ Firebase unavailable ({e}). Using mock data.")
    db = None


# ================================
# 🗳️ SUBMIT VOTE
# ================================
def submit_vote(candidate, location="unknown"):
    """
    Stores vote in Firestore with extra metadata
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
        print("Vote submit error:", e)


# ================================
# 📊 GET VOTE COUNTS
# ================================
def get_vote_counts():
    """
    Returns total votes per candidate
    """
    if db is None:
        return {}
    counts = {}

    try:
        docs = db.collection("votes").stream()

        for d in docs:
            data = d.to_dict()
            candidate = data.get("candidate", "Unknown")

            counts[candidate] = counts.get(candidate, 0) + 1

    except Exception as e:
        print("Firestore error:", e)

    return counts


# ================================
# 📡 CROWD DATA (LOCATION BASED)
# ================================
def get_crowd_data():
    """
    Returns number of voters per location
    """
    if db is None:
        return {}
    crowd = {}

    try:
        docs = db.collection("votes").stream()

        for d in docs:
            data = d.to_dict()
            loc = data.get("location", "unknown")

            crowd[loc] = crowd.get(loc, 0) + 1

    except Exception as e:
        print("Crowd fetch error:", e)

    return crowd


# ================================
# 📈 ADVANCED ANALYTICS (OPTIONAL)
# ================================
def get_detailed_votes():
    """
    Returns full vote records (for dashboards / ML)
    """
    if db is None:
        return []
    records = []

    try:
        docs = db.collection("votes").stream()

        for d in docs:
            records.append(d.to_dict())

    except Exception as e:
        print("Detailed fetch error:", e)

    return records

def submit_verification(voter_qr, is_authentic):
    if db is None:
        return
    db.collection("verification_logs").add({
        "voter_qr": voter_qr,
        "is_authentic": is_authentic,
        "timestamp": datetime.utcnow()
    })

def get_live_queue():
    if db is None:
        return {}
    docs = db.collection("votes").stream()
    now = datetime.utcnow()

    queue = {}

    for d in docs:
        data = d.to_dict()
        loc = data.get("location", "unknown")
        ts = data.get("timestamp")

        if ts and (now - ts).seconds < 1800:
            queue[loc] = queue.get(loc, 0) + 1

    return queue

def get_booth_crowd():
    if db is None:
        return {}
    from datetime import datetime, timezone
    docs = db.collection("votes").stream()
    now = datetime.now(timezone.utc)

    crowd = {}

    for d in docs:
        data = d.to_dict()
        loc = data.get("location", "unknown")
        ts = data.get("timestamp")

        if ts:
            # 🔥 Ensure ts is timezone-aware
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            if (now - ts).total_seconds() < 1800:
                crowd[loc] = crowd.get(loc, 0) + 1

    return crowd

def get_live_analytics():
    if db is None:
        return {}
    docs = db.collection("votes").stream()

    counts = {}
    for d in docs:
        data = d.to_dict()
        candidate = data.get("candidate", "Unknown")
        counts[candidate] = counts.get(candidate, 0) + 1

    return get_vote_counts()

    