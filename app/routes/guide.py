"""
Voting Guide Route - CivicGuide AI
Step-by-step interactive voting process tutorial.
"""

import streamlit as st
from app.utils.ui_components import topbar
from app.services.gemini_service import get_gemini_response

def render_voting_guide(t):
    """
    Renders the Voting Guide tutorial page.
    """
    topbar("🗳️ " + t("How Voting Works"))

    steps = [
        {"title": t("Step 1: Check Eligibility"), "desc": t("You must be 18+ and registered.")},
        {"title": t("Step 2: Verify Documents"), "desc": t("You need a Voter ID or valid identity proof.")},
        {"title": t("Step 3: Find Polling Booth"), "desc": t("Your assigned booth is based on your location.")},
        {"title": t("Step 4: Cast Your Vote"), "desc": t("Use EVM to vote for your preferred candidate.")}
    ]

    if "guide_step" not in st.session_state:
        st.session_state.guide_step = 0

    step = steps[st.session_state.guide_step]
    st.markdown(f"""
    <div class="cg-card">
        <h3>{step['title']}</h3>
        <p style="color:#8ba3c4">{step['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(t("🧠 Explain this step")):
        with st.spinner(t("Explaining...")):
            st.info(get_gemini_response(f"Explain {step['title']} in simple terms for a first-time voter"))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ " + t("Previous"), disabled=st.session_state.guide_step == 0):
            st.session_state.guide_step -= 1
            st.rerun()
    with col2:
        if st.button(t("Next") + " ➡️", disabled=st.session_state.guide_step == len(steps)-1):
            st.session_state.guide_step += 1
            st.rerun()
