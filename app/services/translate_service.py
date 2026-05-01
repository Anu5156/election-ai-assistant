import requests
import streamlit as st
from html import unescape
from app.config import GOOGLE_MAPS_API_KEY
import time


# -----------------------------------
# 🔹 INTERNAL HELPER (STRONGER + BACKOFF)
# -----------------------------------
def _call_translate_api(payload, retries=3, timeout=5):
    url = "https://translation.googleapis.com/language/translate/v2"

    for attempt in range(retries):
        try:
            response = requests.post(url, data=payload, timeout=timeout)

            # 🔥 HTTP safety
            if response.status_code != 200:
                print(f"HTTP ERROR {response.status_code}: {response.text}")
                time.sleep(0.5 * (attempt + 1))
                continue

            data = response.json()

            if "data" in data and "translations" in data["data"]:
                return data["data"]["translations"]

            print("INVALID RESPONSE:", data)

        except requests.exceptions.RequestException as e:
            print(f"TRANSLATE RETRY {attempt+1} ERROR:", e)
            time.sleep(0.5 * (attempt + 1))

    return None


# -----------------------------------
# 🔹 SIMPLE MEMORY CACHE (NEW)
# -----------------------------------
def _cache_key(text, lang):
    return f"{text}_{lang}"


if "translation_cache" not in st.session_state:
    st.session_state.translation_cache = {}


# -----------------------------------
# 🔹 TRANSLATE TEXT (UPGRADED)
# -----------------------------------
@st.cache_data(show_spinner=False)
def translate_text(text, target_lang="en"):
    if not text or target_lang == "en":
        return text

    key = _cache_key(text, target_lang)

    # 🔥 Check session cache
    if key in st.session_state.translation_cache:
        return st.session_state.translation_cache[key]

    try:
        params = {
            "q": text,
            "target": target_lang,
            "format": "text",
            "key": GOOGLE_MAPS_API_KEY
        }

        translations = _call_translate_api(params)

        if translations:
            translated = unescape(translations[0].get("translatedText", text))

            # 🔥 store cache
            st.session_state.translation_cache[key] = translated
            return translated

        return text

    except Exception as e:
        print("TRANSLATE ERROR:", e)
        return text


# -----------------------------------
# 🔹 BATCH TRANSLATION (UPGRADED)
# -----------------------------------
@st.cache_data(show_spinner=False)
def translate_batch(texts, target_lang="en"):
    if not texts or target_lang == "en":
        return texts

    try:
        params = {
            "q": texts,
            "target": target_lang,
            "format": "text",
            "key": GOOGLE_MAPS_API_KEY
        }

        translations = _call_translate_api(params)

        if translations:
            result = [
                unescape(t.get("translatedText", original))
                for t, original in zip(translations, texts)
            ]

            return result

        return texts

    except Exception as e:
        print("BATCH TRANSLATE ERROR:", e)
        return texts


# -----------------------------------
# 🔥 AUTO DETECT (UPGRADED)
# -----------------------------------
@st.cache_data(show_spinner=False)
def translate_auto(text, target_lang="en"):
    if not text or target_lang == "en":
        return text

    try:
        params = {
            "q": text,
            "target": target_lang,
            "key": GOOGLE_MAPS_API_KEY
        }

        translations = _call_translate_api(params)

        if translations:
            return unescape(translations[0].get("translatedText", text))

        return text

    except Exception as e:
        print("AUTO TRANSLATE ERROR:", e)
        return text