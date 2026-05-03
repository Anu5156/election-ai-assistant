"""
Quiz Route - CivicGuide AI
Interactive election quiz with dynamic AI question generation.
"""

import streamlit as st
from app.utils.ui_components import topbar
from app.services.gemini_service import get_gemini_response

def render_quiz(t):
    # ✅ FIX: Initialize session state
    if "quiz_scores" not in st.session_state:
        st.session_state.quiz_scores = []
    """
    Renders the Election Quiz page.
    """
    topbar("🎮 " + t("Election Quiz"))

    difficulty = st.selectbox(t("Select Difficulty"), [t("Easy"), t("Medium"), t("Hard")])
    
    questions = {
        t("Easy"): [{"q": t("Minimum age to vote?"), "options": ["16", "18", "21"], "answer": "18"}],
        t("Medium"): [{"q": t("Who conducts elections?"), "options": ["ECI", "PM", "SC"], "answer": "ECI"}],
        t("Hard"): [{"q": t("Article related to elections?"), "options": ["324", "370", "21"], "answer": "324"}]
    }.get(difficulty, [])

    score = 0
    for i, q in enumerate(questions):
        ans = st.radio(q["q"], q["options"], key=f"quiz_{difficulty}_{i}")
        if ans == q["answer"]: score += 1

    if st.button(t("Submit Quiz")):
        st.session_state.quiz_scores.append(score)
        st.success(f"🎯 {t('Score')}: {score}/{len(questions)}")
        if score == len(questions): st.balloons()

    st.markdown(f"### 🏅 {t('Leaderboard')}")
    for i, s in enumerate(sorted(st.session_state.quiz_scores, reverse=True)[:3]):
        st.write(f"{i+1}. {t('Score')}: {s}")

    st.markdown(f"### 🤖 {t('Ask AI')}")
    user_q = st.text_input(t("Ask about elections"), key="quiz_ai")
    if st.button(t("Get Answer"), key="quiz_ai_btn"):
        if user_q:
            with st.spinner(t("Thinking...")):
                st.success(get_gemini_response(f"Answer this election question simply: {user_q}"))

    if st.button(t("Generate New Question")):
        st.write(get_gemini_response(t("Generate a MCQ question about elections with answer")))
