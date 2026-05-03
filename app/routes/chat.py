"""
Chat Route - CivicGuide AI
Handles the AI conversational interface for election queries.
"""

import streamlit as st
from app.utils.ui_components import topbar
from app.services.gemini_service import get_gemini_response
from app.utils.validators import sanitize_input, is_rate_limited

def render_chat_page(t):
    """
    Renders the AI Assistant chat page.
    """
    topbar("🤖 " + t("AI Election Assistant"), [("Live AI", "badge-green")])

    st.markdown(f"## {t('Ask anything about elections')}")

    # -------- INITIALIZE HISTORY --------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -------- DISPLAY HISTORY --------
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # -------- USER INPUT --------
    if prompt := st.chat_input(t("What would you like to know?")):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            if is_rate_limited():
                st.warning("⚠️ Slow down! Please wait a moment between questions.")
            elif not sanitize_input(prompt):
                st.error("🚨 Suspicious activity detected. Your query has been blocked for safety.")
            else:
                with st.spinner(t("Analyzing and generating response...")):
                    # Pass history for context
                    response = get_gemini_response(prompt, history=st.session_state.messages[-5:])
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button(t("Clear Conversation")):
        st.session_state.messages = []
        st.rerun()