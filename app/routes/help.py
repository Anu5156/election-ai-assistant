"""
Help Center Route - CivicGuide AI
Q&A interface for general election queries.
"""

import streamlit as st
from app.utils.ui_components import topbar
from app.services.gemini_service import get_gemini_response

def render_help_center(t):
    """
    Renders the Help Center page.
    """
    topbar("💬 " + t("Help Center"))

    st.markdown(f"## 🧠 {t('Ask Questions')}")
    st.markdown(t("Try asking things like:"))
    st.write("• " + t("What is EVM?"))
    st.write("• " + t("How to vote?"))
    st.write("• " + t("What is NOTA?"))

    user_q = st.text_input(t("Your question"))
    if st.button(t("Get Help")):
        if user_q:
            with st.spinner(t("Thinking...")):
                answer = get_gemini_response(user_q)
                if answer: st.success(answer)
                else: st.warning(t("No response from AI"))
