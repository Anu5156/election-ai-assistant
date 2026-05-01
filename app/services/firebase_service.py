import os
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import timezone



# ================================
# 🔐 FIREBASE INIT
# ================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ================================
# 🗳️ SUBMIT VOTE
# ================================
def submit_vote(candidate, location="unknown"):
    """
    Stores vote in Firestore with extra metadata
    """

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

    records = []

    try:
        docs = db.collection("votes").stream()

        for d in docs:
            records.append(d.to_dict())

    except Exception as e:
        print("Detailed fetch error:", e)

    return records

def submit_verification(voter_qr, is_authentic):
    db.collection("verification_logs").add({
        "voter_qr": voter_qr,
        "is_authentic": is_authentic,
        "timestamp": datetime.utcnow()
    })

def get_live_queue():

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
    docs = db.collection("votes").stream()

    counts = {}
    for d in docs:
        data = d.to_dict()
        candidate = data.get("candidate", "Unknown")
        counts[candidate] = counts.get(candidate, 0) + 1

    return get_vote_counts()

    