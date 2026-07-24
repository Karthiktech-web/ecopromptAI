import streamlit as st
import streamlit.components.v1 as components
from google import genai
import time
from difflib import SequenceMatcher
import pandas as pd
from PIL import Image 

# ==========================================
# UI CONFIGURATION & DESIGN SYSTEM (BOLD GEMINI THEME)
# ==========================================
st.set_page_config(page_title="EcoPrompt AI Gateway", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --surface: #F0F4F9; 
        --surface-hover: #E2E8F0;
        --ink: #0B0B0B; 
        --muted: #1F1F1F; 
        --accent: #0B57D0; 
        --line: #DADCE0;
    }

    html, body, [class*="css"] { 
        font-family: 'Google Sans', 'Inter', sans-serif; 
        color: var(--ink) !important; 
        font-size: 16px;
    }
    
    /* --- The Subtle Gemini Blue Glow Background --- */
    .stApp { 
        background-color: #FFFFFF;
        background-image: radial-gradient(circle at 50% 40%, rgba(232, 240, 254, 0.9) 0%, rgba(255, 255, 255, 0) 55%);
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* --- The Giant Center Greeting --- */
    .gemini-greeting {
        font-family: 'Google Sans', sans-serif;
        font-size: 3.2rem;
        font-weight: 500;
        color: var(--ink);
        text-align: center;
        margin-top: 25vh;
        margin-bottom: 2rem;
        letter-spacing: -0.02em;
    }

    /* Hide old header decorations */
    .page-eyebrow, .page-header-rule, .active-prompt-box { display: none !important; }

    /* ---------- Sidebar Typography & Layout ---------- */
    section[data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: none !important;
        padding-top: 0rem !important; 
    }
    section[data-testid="stSidebar"] * { color: var(--ink) !important; }
    
    section[data-testid="stSidebar"] div.block-container {
        padding-top: 0.5rem !important;
    }
    section[data-testid="stSidebar"] h1 { 
        font-family: 'Google Sans', sans-serif !important;
        font-size: 1.7rem !important; 
        font-weight: 800 !important; 
        color: #000000 !important; 
        margin-top: -1.5rem !important; 
        margin-bottom: 0.2rem !important;
        letter-spacing: -0.03em;
    }
    
    section[data-testid="stSidebar"] h2 {
        font-family: 'Google Sans', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] hr { border-color: var(--line) !important; margin: 0.8rem 0 !important; }

    /* ---------- Prompt Score Gauge Card ---------- */
    .gauge-wrap {
        display: flex;
        align-items: center;
        gap: 16px;
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .gauge-ring {
        width: 64px; height: 64px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .gauge-inner {
        width: 50px; height: 50px;
        border-radius: 50%;
        background: #FFFFFF;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Google Sans', sans-serif;
        font-weight: 800;
        font-size: 1.2rem;
        color: var(--ink);
    }
    .gauge-label {
        font-family: 'Google Sans', sans-serif;
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        color: var(--ink);
        margin-bottom: 2px;
    }
    .gauge-sub { font-size: 0.75rem; font-weight: 600; color: #3C4043; line-height: 1.2; }

    /* ---------- Sidebar Metric Tiles ---------- */
    .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 5px; }
    .metric-tile {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid var(--line);
    }
    .metric-eyebrow {
        font-size: 0.75rem;
        font-weight: 800;
        color: var(--ink) !important;
        margin-bottom: 3px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--ink) !important;
    }

    /* ---------- Sidebar buttons ---------- */
    section[data-testid="stSidebar"] button {
        background: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        border-radius: 20px !important;
        font-family: 'Google Sans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        justify-content: flex-start !important;
        padding: 10px 16px !important;
        transition: background 0.15s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    section[data-testid="stSidebar"] button:hover {
        background: var(--surface-hover) !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] button {
        background: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
        color: var(--accent) !important;
        font-size: 0.95rem !important;
    }

    /* ---------- Gemini-Style Chat Bubbles ---------- */
    div[data-testid="stChatMessage"] {
        border: none !important;
        background: transparent !important;
        padding: 12px 0 !important;
        margin-bottom: 15px !important;
        font-size: 1.05rem !important;
        font-weight: 500;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: transparent !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background-color: var(--surface) !important;
        border-radius: 24px !important;
        padding: 14px 24px !important;
        margin-left: auto !important;
        width: fit-content !important;
        max-width: 85% !important;
        font-weight: 600;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="chatAvatarIcon-user"] {
        display: none !important;
    }

    /* ---------- The Floating Gemini Chat Input Bar ---------- */
    div.st-key-chat_bar {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 40px;
        padding: 8px 12px 8px 16px;
        width: 90%;
        max-width: 820px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    @media (max-width: 900px) {
        div.st-key-chat_bar {
            left: calc(50% + 120px); 
        }
    }
    div.st-key-chat_bar div[data-testid="stHorizontalBlock"] { align-items: center; gap: 0; }
    div.st-key-chat_bar div[data-testid="stPopover"] button {
        border: none !important;
        background: transparent !important;
        font-size: 1.5rem !important;
        padding: 8px !important;
        color: var(--muted) !important;
        box-shadow: none !important;
    }
    div.st-key-chat_bar div[data-testid="stPopover"] button:hover {
        background: var(--surface-hover) !important;
        border-radius: 50% !important;
    }
    div.st-key-chat_bar div[data-testid="stForm"] { border: none !important; background: transparent !important; }
    div.st-key-chat_bar input[type="text"] {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        font-family: 'Google Sans', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding-left: 12px !important;
        color: var(--ink) !important;
    }
    div.st-key-chat_bar input[type="text"]::placeholder { color: var(--muted) !important; }
    
    div.st-key-chat_bar button[kind="formSubmit"] {
        background: transparent !important;
        color: var(--ink) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        font-size: 1.3rem !important;
        box-shadow: none !important;
    }
    div.st-key-chat_bar button[kind="formSubmit"]:hover {
        background: var(--surface-hover) !important;
    }
    div.st-key-chat_bar div[data-testid="stPopover"] button svg { display: none !important; }
    div.st-key-chat_bar div[data-testid="stPopover"] button { min-width: 0 !important; }
    div.st-key-chat_bar div[data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; }
    div[data-testid="InputInstructions"] { display: none !important; }
    
    .attach-chip {
        display: inline-block;
        background: var(--surface);
        color: var(--ink);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 8px 16px;
        font-size: 0.95rem;
        font-weight: 600;
        margin-left: 6px;
        margin-bottom: 20px;
    }

    /* ---------- Inline AI Tools panel ---------- */
    div.st-key-tool_panel {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 20px 22px 10px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .panel-title {
        font-family: 'Google Sans', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# INITIALIZE GEMINI CLIENT WITH API KEY
# =========================================================================
API_KEY = "AIzaSyDgTGXK_TzfVYovtZ02Ped2NauUR9ECbJo"  
client = genai.Client(api_key=API_KEY)

# ==========================================
# INITIALIZE SESSION STATE (Long-Term Memory)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [] 
if "semantic_cache" not in st.session_state:
    st.session_state.semantic_cache = {}
if "session_history" not in st.session_state:
    st.session_state.session_history = []
if "metrics" not in st.session_state:
    st.session_state.metrics = {"tokens": 0, "cost": 0.00, "saved": 0.00, "time": 0.0}
if "active_prompt" not in st.session_state:
    st.session_state.active_prompt = "No prompt submitted yet."
if "prompt_score" not in st.session_state:
    st.session_state.prompt_score = "-"
if "pending_file" not in st.session_state:
    st.session_state.pending_file = None

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ==========================================
# AI TOOLS
# ==========================================
if "active_panel" not in st.session_state:
    st.session_state.active_panel = None
if "panel_cache_key" not in st.session_state:
    st.session_state.panel_cache_key = None
if "panel_result" not in st.session_state:
    st.session_state.panel_result = None
if "panel_error" not in st.session_state:
    st.session_state.panel_error = None

def run_compressor(prompt_text):
    res = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"Rewrite this to be as short and token-efficient as possible. Output ONLY the compressed prompt: '{prompt_text}'"
    )
    return res.text.strip()

def run_tutor(prompt_text):
    meta = f"Analyze this prompt: '{prompt_text}'. List 1. Missing elements 2. Structural advice."
    res = client.models.generate_content(model="gemini-3.6-flash", contents=meta)
    return res.text

# ==========================================
# SIDEBAR: PERSISTENT DASHBOARD
# ==========================================
with st.sidebar:
    st.title("✨ EcoPrompt")

    raw_score = st.session_state.prompt_score
    try:
        score_num = max(0, min(100, int(raw_score)))
    except (ValueError, TypeError):
        score_num = 0
    degrees = int(score_num / 100 * 360)
    display_score = raw_score if raw_score not in ("-", "") else "—"

    st.markdown(f"""
        <div class="gauge-wrap">
            <div class="gauge-ring" style="background: conic-gradient(#0B57D0 {degrees}deg, #E2E8F0 {degrees}deg);">
                <div class="gauge-inner">{display_score}</div>
            </div>
            <div>
                <div class="gauge-label">Prompt Score</div>
                <div class="gauge-sub">Clarity & efficiency<br/>out of 100</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.header("Live Analytics")

    m = st.session_state.metrics
    st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-tile">
                <div class="metric-eyebrow">Tokens</div>
                <div class="metric-value">{m['tokens']:,}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-eyebrow">Time</div>
                <div class="metric-value">{m['time']:.2f}s</div>
            </div>
            <div class="metric-tile">
                <div class="metric-eyebrow">Cost</div>
                <div class="metric-value">₹{m['cost']:.5f}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-eyebrow">Saved</div>
                <div class="metric-value">₹{m['saved']:.5f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.header("AI Tools")
    if st.button("✂️  Prompt Compressor", use_container_width=True):
        st.session_state.active_panel = "compressor"

    if st.button("🎓  Prompt Tutor", use_container_width=True):
        st.session_state.active_panel = "tutor"

    st.markdown("---")
    st.header("Admin Export")
    
    admin_toggle = st.toggle("🔒 Administrator Mode")
    
    if admin_toggle:
        admin_password = st.text_input("Enter Admin PIN", type="password", placeholder="PIN: admin123")
        if admin_password == "admin123":
            st.success("Access Granted")
            if st.session_state.session_history:
                df = pd.DataFrame(st.session_state.session_history)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Audit CSV", 
                    data=csv, 
                    file_name="ecoprompt_enterprise_audit.csv", 
                    mime="text/csv", 
                    use_container_width=True
                )
            else:
                st.info("No logs recorded yet.")
        elif admin_password != "":
            st.error("Invalid PIN")
    else:
        st.caption("🔒 Restricted to Admins.")

# ==========================================
# MAIN CHAT INTERFACE & FILE UPLOAD
# ==========================================

if not st.session_state.messages:
    st.markdown('<div class="gemini-greeting">What\'s next, Karthik?</div>', unsafe_allow_html=True)

if st.session_state.active_panel in ("compressor", "tutor"):
    panel_meta = {
        "compressor": ("✂️", "Prompt Compressor", "Token-efficient rewrite of your active prompt"),
        "tutor": ("🎓", "Prompt Tutor", "Structure and clarity feedback on your active prompt"),
    }
    icon, panel_title, panel_sub = panel_meta[st.session_state.active_panel]

    with st.container(key="tool_panel"):
        head_col, close_col = st.columns([12, 1])
        with head_col:
            st.markdown(f'<div class="panel-title">{icon} {panel_title}</div>', unsafe_allow_html=True)
        with close_col:
            if st.button("✕", key="close_panel", help="Close"):
                st.session_state.active_panel = None
                st.rerun()

        active_prompt_text = st.session_state.active_prompt
        if active_prompt_text == "No prompt submitted yet.":
            st.warning("Send a message in the chat first, then reopen this tool.")
        else:
            cache_key = f"{st.session_state.active_panel}::{active_prompt_text}"
            if st.session_state.panel_cache_key != cache_key:
                with st.spinner("Working on it..."):
                    try:
                        if st.session_state.active_panel == "compressor":
                            st.session_state.panel_result = run_compressor(active_prompt_text)
                        else:
                            st.session_state.panel_result = run_tutor(active_prompt_text)
                        st.session_state.panel_error = None
                    except Exception as e:
                        st.session_state.panel_result = None
                        st.session_state.panel_error = str(e)
                    st.session_state.panel_cache_key = cache_key

            if st.session_state.panel_error:
                st.error(f"Error: {st.session_state.panel_error}")
            elif st.session_state.active_panel == "compressor":
                st.code(st.session_state.panel_result, language="markdown")
            else:
                st.markdown(st.session_state.panel_result)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.pending_file:
    st.markdown(
        f'<span class="attach-chip">📎 {st.session_state.pending_file.name} — ready to send</span>',
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)

prompt = None
with st.container(key="chat_bar"):
    plus_col, field_col = st.columns([1, 14])
    with plus_col:
        with st.popover("➕", help="Attach a file"):
            uploaded_file = st.file_uploader("Attach Image or Text", type=["png", "jpg", "jpeg", "txt"])
            if uploaded_file:
                st.session_state.pending_file = uploaded_file
                st.success(f"Attached: {uploaded_file.name}")

    with field_col:
        with st.form("chat_form", clear_on_submit=True, border=False):
            text_col, send_col = st.columns([14, 1])
            with text_col:
                user_text = st.text_input(
                    "prompt", label_visibility="collapsed",
                    placeholder="Ask Gemini"
                )
            with send_col:
                submitted = st.form_submit_button("➤")
            if submitted and user_text.strip():
                prompt = user_text.strip()

components.html("""
<script>
function disableSpellcheck() {
    const doc = window.parent.document;
    doc.querySelectorAll('div.st-key-chat_bar input[type="text"]').forEach(el => {
        el.setAttribute('spellcheck', 'false');
        el.setAttribute('autocorrect', 'off');
        el.setAttribute('autocapitalize', 'off');
    });
}
disableSpellcheck();
new MutationObserver(disableSpellcheck).observe(window.parent.document.body, {childList: true, subtree: true});
</script>
""", height=0)

if prompt:
    st.session_state.active_prompt = prompt
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start_time = time.time()
            prompt_key = prompt.lower().strip()
            
            try:
                score_res = client.models.generate_content(
                    model="gemini-3.6-flash", 
                    contents=f"Score this prompt from 1 to 100 based on token efficiency, directness, and technical clarity. You MUST heavily penalize conversational filler (e.g., 'Hello', 'Please', 'Hope you are well') and unnecessary rambling. A score of 90+ should only be given to perfectly concise, direct prompts. Respond with ONLY the number. Prompt: '{prompt}'"
                )
                extracted_score = "".join(filter(str.isdigit, score_res.text))
                st.session_state.prompt_score = extracted_score if extracted_score else "N/A"
            except:
                st.session_state.prompt_score = "Err"
            
            cache_hit = False
            for stored_prompt, stored_data in st.session_state.semantic_cache.items():
                if get_similarity(prompt_key, stored_prompt) > 0.85:
                    cache_hit = True
                    cached_response = stored_data['text']
                    break
            
            if cache_hit:
                end_time = time.time()
                st.markdown(f"**⚡ Cache Hit (0 Tokens Used)**\n\n{cached_response}")
                st.session_state.messages.append({"role": "assistant", "content": cached_response})
                
                st.session_state.metrics["time"] = end_time - start_time
                st.session_state.metrics["tokens"] = 0
                st.session_state.metrics["saved"] += 0.50 
                
            else:
                if any(keyword in prompt_key for keyword in ["code", "analyze", "evaluate", "debug"]):
                    model_id = "gemini-3.1-pro-preview"
                    cost_per_token = (1.25 / 1000000) * 83 
                    savings = 0.0 
                else:
                    model_id = "gemini-3.6-flash"
                    cost_per_token = (0.075 / 1000000) * 83 
                    savings = ((1.25 - 0.075) / 1000000) * 83 * 1000 
                
                try:
                    contents = [prompt]
                    if st.session_state.pending_file is not None:
                        file = st.session_state.pending_file
                        if file.type in ["image/png", "image/jpeg", "image/jpg"]:
                            image = Image.open(file)
                            contents.append(image)
                        elif file.type == "text/plain":
                            text_data = file.getvalue().decode("utf-8")
                            contents.append(f"\n\n--- Attached File Content ---\n{text_data}")
                        st.session_state.pending_file = None
                    
                    response = client.models.generate_content(
                        model=model_id,
                        contents=contents
                    )
                    
                    end_time = time.time()
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    try:
                        actual_tokens = response.usage_metadata.total_token_count
                    except AttributeError:
                        actual_tokens = len(response.text.split()) * 1.5 
                        
                    actual_cost = actual_tokens * cost_per_token
                    
                    st.session_state.metrics["tokens"] = actual_tokens
                    st.session_state.metrics["cost"] = actual_cost
                    st.session_state.metrics["time"] = end_time - start_time
                    st.session_state.metrics["saved"] += savings
                    
                    st.session_state.session_history.append({
                        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "Score": st.session_state.prompt_score,
                        "Tokens": actual_tokens,
                        "Cost (INR)": round(actual_cost, 5),
                        "Time (s)": round(end_time - start_time, 2)
                    })
                    
                    st.session_state.semantic_cache[prompt_key] = {"text": response.text}
                    
                except Exception as e:
                    st.error(f"API Error: {e}")
    
    st.rerun()