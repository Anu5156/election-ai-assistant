import streamlit as st
from app.models.user import User
from app.services.ai_service import generate_guidance
from app.services.translate_service import translate_text
from app.utils.validators import sanitize_input
from app.services.recommendation import recommend_info

def chat_ui(age, location, registered, target_lang, t):

    st.markdown("## 💬 " + t("Ask About Elections"))

    # -------- SESSION CHAT HISTORY --------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # -------- SUGGESTIONS --------
    st.markdown("### 💡 " + t("Try asking:"))

    suggestions = [
        "How do I vote?",
        "Where is my polling station?",
        "What documents are required?",
        "Am I eligible to vote?",
        "What is the best time to vote?"
    ]
    user = User(age=age, location=location, is_registered=registered)
    if st.button("🧠 Get Voting Guidance"):
        st.info(translate_text(recommend_info(user), target_lang))

    cols = st.columns(2)

    for i, s in enumerate(suggestions):
        if cols[i % 2].button(t(s)):
            st.session_state["quick_query"] = s

    # -------- INPUT --------
    query = st.text_input(
        t("Ask your question"),
        value=st.session_state.get("quick_query", "")
    )

    # clear quick query after use
    if "quick_query" in st.session_state:
        del st.session_state["quick_query"]

    # -------- SEND BUTTON --------
    if st.button(t("Ask AI")):

        if query.strip() == "":
            st.error(t("Please enter a question"))

        elif not sanitize_input(query):
            st.error(t("Unsafe input detected"))

        else:
            try:
                user = User(
                    age=age,
                    location=location,
                    is_registered=registered
                )

                with st.spinner(t("Thinking...")):
                    response = generate_guidance(user, query)

                translated = translate_text(response, target_lang)

                # -------- SAVE HISTORY --------
                st.session_state.chat_history.append({
                    "q": query,
                    "a": translated
                })

            except Exception as e:
                st.error(t("AI service unavailable"))

                fallback = "Please visit the official election website or nearest polling office."
                translated = translate_text(fallback, target_lang)

                st.session_state.chat_history.append({
                    "q": query,
                    "a": translated
                })

    # -------- DISPLAY CHAT HISTORY --------
    for chat in reversed(st.session_state.chat_history):

        # USER MESSAGE
        st.markdown(f"""
        <div style="
            background:#1f2937;
            padding:12px;
            border-radius:12px;
            margin-bottom:8px;
        ">
        🧑 {chat['q']}
        </div>
        """, unsafe_allow_html=True)

        # AI RESPONSE
        st.markdown(f"""
        <div class="card">
        🤖 <b>{t("AI Assistant")}</b><br><br>
        {chat['a']}
        </div>
        """, unsafe_allow_html=True)