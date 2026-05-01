from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("AIzaSyB-g8wAfZNaH3hQ_NGmMSFH3h3iO_S-ylo"))

def get_gemini_response(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",   # ✅ FIXED MODEL
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"⚠️ Error: {e}"