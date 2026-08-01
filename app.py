import random
import time
from difflib import SequenceMatcher
from google import genai
import pandas as pd
from PIL import Image
import streamlit as st

# ==========================================
# UI CONFIGURATION & DESIGN SYSTEM
# ==========================================
st.set_page_config(page_title="EcoPrompt AI Gateway", layout="wide", initial_sidebar_state="expanded")

first_name = "Karthik"
quotes = [f"What's next, {first_name}?", f"Ready to optimize your prompts, {first_name}?"]
if "current_quote" not in st.session_state:
    st.session_state.current_quote = random.choice(quotes)

# --- NATIVE THEME CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], * { font-family: 'Google Sans', 'Inter', sans-serif; }
    .stApp > header { background-color: transparent !important; }
    .gemini-greeting { font-family: 'Google Sans', sans-serif; font-size: 3.2rem; font-weight: 500; text-align: center; margin-top: 25vh; margin-bottom: 2rem; }
    div[data-testid="stChatMessage"] { padding: 12px 0 !important; font-size: 1.05rem !important; }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) { background-color: var(--secondary-background-color) !important; border-radius: 24px !important; padding: 14px 24px !important; margin-left: auto !important; width: fit-content !important; max-width: 85% !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INITIALIZE CLIENT
# ==========================================
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    client = None

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "messages" not in st.session_state: st.session_state.messages = []
if "semantic_cache" not in st.session_state: st.session_state.semantic_cache = {}
if "session_history" not in st.session_state: st.session_state.session_history = []

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ==========================================
# MAIN CHAT INTERFACE
# ==========================================
if not st.session_state.messages:
    st.markdown(f'<div class="gemini-greeting">{st.session_state.current_quote}</div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask Gemini...")

# ==========================================
# LIVE BACKEND PROCESSING & REAL ERRORS
# ==========================================
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.status("⚙️ Running Backend Protocols...", expanded=True) as status:
            start_time = time.time()
            prompt_key = prompt.lower().strip()

            if not client:
                status.update(label="❌ API Key Missing", state="error", expanded=True)
                st.error("**Missing or Invalid API Key.** Please check Streamlit Secrets.")
                st.stop()

            st.write("🗄️ Querying semantic cache...")
            cache_hit = False
            for stored_prompt, stored_data in st.session_state.semantic_cache.items():
                if get_similarity(prompt_key, stored_prompt) > 0.85:
                    cache_hit = True
                    cached_response = stored_data["text"]
                    break

            if cache_hit:
                st.write("⚡ Cache Hit! Bypassing API...")
                status.update(label="Response retrieved from Cache", state="complete")
                final_output = f"**⚡ Cache Hit**\n\n{cached_response}"
            else:
                st.write("🌐 Routing to Gemini API...")
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash", contents=[prompt]
                    )
                    st.session_state.semantic_cache[prompt_key] = {"text": response.text}
                    status.update(label="Request completed", state="complete")
                    final_output = response.text
                except Exception as e:
                    status.update(label="❌ Gateway Error - Connection Failed", state="error", expanded=True)
                    final_output = f"**Google API Error:** `{str(e)}`\n\n*Check your API key in Streamlit Secrets!*"

        st.markdown(final_output)
        st.session_state.messages.append({"role": "assistant", "content": final_output})
    st.rerun()
