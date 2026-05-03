import requests
import streamlit as st
from html import unescape
from app.config import GOOGLE_MAPS_API_KEY
import time
from typing import List, Optional, Dict, Any


# -----------------------------------
# 🔹 INTERNAL HELPER (STRONGER + BACKOFF)
# -----------------------------------
def _call_translate_api(payload: Dict[str, Any], retries: int = 3, timeout: int = 5) -> Optional[List[Dict[str, str]]]:
    """
    Low-level wrapper for the Google Cloud Translation API with exponential backoff.
    
    Args:
        payload: API parameters including text, target language, and API key.
        retries: Number of retry attempts on failure.
        timeout: Request timeout in seconds.
        
    Returns:
        A list of translation objects or None on failure.
    """
    url = "https://translation.googleapis.com/language/translate/v2"

    for attempt in range(retries):
        try:
            response = requests.post(url, data=payload, timeout=timeout)

            # 🔥 HTTP status safety
            if response.status_code != 200:
                print(f"TRANSLATION API HTTP ERROR {response.status_code}: {response.text}")
                time.sleep(0.5 * (attempt + 1))
                continue

            data = response.json()

            if "data" in data and "translations" in data["data"]:
                return data["data"]["translations"]

            print("INVALID TRANSLATION API RESPONSE STRUCTURE:", data)

        except requests.exceptions.RequestException as e:
            print(f"TRANSLATE RETRY {attempt+1} NETWORK ERROR: {e}")
            time.sleep(0.5 * (attempt + 1))

    return None


# -----------------------------------
# 🔹 SIMPLE MEMORY CACHE
# -----------------------------------
def _cache_key(text: str, lang: str) -> str:
    """Generates a unique cache key for a text-language pair."""
    return f"{text}_{lang}"


if "translation_cache" not in st.session_state:
    st.session_state.translation_cache = {}


# -----------------------------------
# 🔹 TRANSLATE TEXT (UPGRADED)
# -----------------------------------
@st.cache_data(show_spinner=False)
def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translates a single string into the target language with local caching.
    
    Args:
        text: The source text to translate.
        target_lang: The destination ISO language code.
        
    Returns:
        The translated string, or the original text if translation fails.
    """
    if not text or target_lang == "en":
        return text

    key = _cache_key(text, target_lang)

    # 🔥 Check fast session cache (O(1) lookup)
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

            # 🔥 Persistent store for current session
            st.session_state.translation_cache[key] = translated
            return translated

        return text

    except Exception as e:
        print(f"TRANSLATION ERROR: {e}")
        return text


# -----------------------------------
# 🔹 BATCH TRANSLATION (UPGRADED)
# -----------------------------------
@st.cache_data(show_spinner=False)
def translate_batch(texts: List[str], target_lang: str = "en") -> List[str]:
    """
    Translates a list of strings in a single API call for efficiency.
    
    Args:
        texts: A list of strings to translate.
        target_lang: The destination ISO language code.
        
    Returns:
        A list of translated strings in the same order.
    """
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
            return [unescape(t.get("translatedText", texts[i])) for i, t in enumerate(translations)]

        return texts

    except Exception as e:
        print(f"BATCH TRANSLATION ERROR: {e}")
        return texts