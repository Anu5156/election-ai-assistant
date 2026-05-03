<div align="center">
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg" width="60" alt="Python" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/GCP-Dark.svg" width="60" alt="GCP" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Firebase-Dark.svg" width="60" alt="Firebase" />
</div>

<h1 align="center">🗳️ CivicGuide AI (Election AI Assistant)</h1>

<p align="center">
  <strong>An Intelligent, Multilingual, and Accessible Election Companion</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-App-red" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Status-Active-green" alt="Status" />
  <img src="https://img.shields.io/badge/GCP-Integration-blue" alt="GCP" />
  <img src="https://img.shields.io/badge/Firebase-Realtime-orange" alt="Firebase" />
</p>

> 🚀 A state-of-the-art, AI-powered election companion designed to democratize access to voting information through geospatial processing, real-time data, and multilingual AI assistance.

---

## ⚡ Overview

**Chosen Vertical:** E-Governance & Civic Tech

**CivicGuide AI** is an intelligent election assistant designed to bridge the gap between voters and the electoral process. By leveraging the Google ecosystem (Gemini, Firebase, and Maps), it provides real-time polling booth recommendations, accessible civic guidance in 12 regional languages, and seamless navigation.

👉 The result: **An inclusive, frictionless, and informed voting experience.**

---

## 🎯 Problem

Citizens face significant hurdles during elections:
- Complex and confusing electoral processes
- Long wait times and crowded polling stations
- Lack of accessible information for non-English speakers and visually impaired voters

---

## 💡 Solution

This system generates **dynamic, personalized voter journeys** using:
- Real-time crowd density syncing
- Smart geospatial recommendation algorithms
- Multilingual LLM conversational agents

👉 Not just a map — a **comprehensive civic guide**

---

## 🧠 Core Innovation

### 🔹 Smart Recommendation Engine

```text
User Location  
   ↓  
Geospatial Processor (identifies viable radius)  
   ↓  
Firebase Sync (real-time crowd density)  
   ↓  
Ranking Algorithm: (Distance * 0.6) + (Crowd * 0.4)  
   ↓  
Optimized Polling Booth Suggestion  
```

### 🔹 Real-Time Synchronization Engine

- **Dynamic Countdown:** Precise T-minus calculation using server-side time vs. fixed election milestones.
- **Session Clock:** Real-time feedback loop providing users with visual confirmation of "Live" session state.
- **Interactive Analytics:** Streaming visualization of mock participation data using high-performance Plotly engines.

### ✨ What Makes It Unique
- **Hybrid Scoring:** Balances proximity with real-time wait times.
- **Context-Aware AI:** Gemini-powered civic guidance with chat history and specialized election instructions.
- **Visual Excellence:** Premium Glassmorphism UI with backdrop-filter blur effects.
- **Graceful Degradation:** Resilient architecture ensures functionality even if external data feeds fail.

---

## 🚀 Features

- ✅ **Real-Time Dashboard** (Dynamic countdowns & live session clock)
- ✅ **Advanced AI Chat** (History-aware, specialized Gemini conversationalist)
- ✅ **Live Data Visualization** (Interactive Plotly analytics for voter trends)
- ✅ **Smart Booth Recommendation** (Distance + Crowd logic)
- ✅ **Real-Time Data Sync** (Firebase integration)
- ✅ **Multilingual AI Chat** (Gemini-powered support for 12 languages: English, Hindi, Kannada, Tamil, Telugu, Bengali, Marathi, Gujarati, Punjabi, Malayalam, Odia, and Urdu)
- ✅ **Text-to-Speech (TTS)** for maximum accessibility
- ✅ **Interactive Maps & Navigation** (Folium & Haversine formula)
- ✅ **Election Reminders** (Google Calendar `.ics` deep linking)
- ✅ **Premium UI/UX** (FAANG-level Glassmorphism design)

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Responsive Dark Mode UI)
- **Backend Orchestration:** Python
- **AI Conversational Layer:** Google Gemini
- **Database & Real-time Sync:** Google Firebase
- **Data Visualization:** Plotly (FAANG-level interactive charts)
- **Mapping & Geospatial:** Folium, Google Maps API
- **Accessibility:** `gTTS` (Google Text-to-Speech)

---

## 🔄 How It Works

1. **Profiling & Validation:** Users input age and location; system validates eligibility.
2. **Geospatial Processing:** Identifies polling stations within a viable radius using coordinates.
3. **Recommendation Engine:** Dynamically ranks booths using the composite score formula.
4. **Actionable Insights:** Provides turn-by-turn navigation, `.ics` calendar reminders, and TTS.
5. **AI Interaction:** Google Gemini handles edge-case civic queries conversationally.

---

## 🏗️ Architecture & Code Quality

- **Modular Design:** Strictly adheres to the Single Responsibility Principle (`app/routes`, `app/models`, `app/utils`, `app/services`).
- **Optimal Resource Usage:** `@st.cache_data` caches heavy API responses (translations, coordinates).
- **Smart Routing Math:** Native Haversine formula calculates distances efficiently without excessive API calls.

---

## 🔐 Security & Privacy

- **Safe Secrets Management:** API Keys handled via `.env` and `python-dotenv`, excluded via `.gitignore`.
- **Data Minimization:** User locations/queries are held ephemerally in Streamlit's `session_state`. **No persistent storage.**

---

## 🧪 Testing & Reliability

- **Validation Framework:** Sanitizes user inputs (`app/utils/validators.py`).
- **Resilience:** API calls wrapped in robust `try...except` blocks. Fails gracefully (e.g., falls back to distance-only calculations if Firebase is down).

---

## ♿ Accessibility (WCAG Aligned)

- **Inclusive Design:** High-contrast colors, clear visual hierarchy, semantic HTML.
- **Multilingual Support:** Fully functional in 12 Indian languages.
- **Voice Output:** `gTTS` integration for visually impaired users.

---

## 🌐 Google Services Integration

- **Google Generative AI (Gemini):** Synthesizes complex electoral rules into localized advice.
- **Google Firebase:** Powers the smart recommendation algorithm with live crowd density.
- **Google Maps Ecosystem:** Geocoding and routing logic for Folium maps.
- **Google Calendar:** Generates instant calendar events and reminders.

---

## ⚙️ Setup

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment Variables
Create a `.env` file and add necessary API keys (Google Gemini, Maps). Ensure `firebase_key.json` is configured if using Firebase.

### 3️⃣ Run the application
```bash
streamlit run app/main.py
```

*(Note: Adjust the launch script if your entry point is different)*

---

## 🤔 Assumptions Made

- Users possess basic internet connectivity.
- Location services (GPS) are permitted, or manual address is provided.
- Live crowd data simulated in MVP mimics actual Election Commission data feeds.
- Default target timezone is IST (Indian Standard Time).

---

## 🌍 Real-World Impact

Helps citizens:
- Overcome language barriers to civic participation.
- Avoid heavily congested polling stations.
- Access reliable, AI-verified voting rules instantly.

---

<div align="center">
  <i>Built with ❤️ for a stronger democracy.</i>
</div>
