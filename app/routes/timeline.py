"""
Timeline Route - CivicGuide AI
Interactive election journey tracker with AI explanations and TTS support.
"""

import streamlit as st
from app.utils.ui_components import topbar
from app.services.gemini_service import get_gemini_response

def render_timeline(t):
    """
    Renders the interactive Election Timeline page.
    """
    topbar("📅 " + t("Election Timeline"))

    steps = [
        (t("Registration"), t("You register as a voter to be eligible for elections.")),
        (t("Verification"), t("Authorities verify your identity and details.")),
        (t("Voter Slip"), t("You receive polling booth and voter details.")),
        (t("Poll Day"), t("You visit the booth and cast your vote.")),
        (t("Counting"), t("Votes are counted securely.")),
        (t("Results"), t("Final winners are announced."))
    ]

    if "timeline_step" not in st.session_state:
        st.session_state.timeline_step = 0

    current = st.session_state.timeline_step
    st.progress((current + 1) / len(steps))

    title, desc = steps[current]
    st.markdown(f"""
    <div class="cg-card" style="animation: fadeIn 0.6s ease-in-out;">
        <h3>{title}</h3>
        <p style="color:#8ba3c4">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(t("🧠 Detailed Explanation")):
        with st.spinner(t("Generating explanation...")):
            full_explanation = get_gemini_response(f"Explain '{title}' step of election process in detail for a beginner")
            st.info(full_explanation)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ " + t("Previous"), disabled=current == 0):
            st.session_state.timeline_step -= 1
            st.rerun()
    with col2:
        if st.button(t("Next") + " ➡️", disabled=current == len(steps) - 1):
            st.session_state.timeline_step += 1
            st.rerun()
