import streamlit as st
import requests
import urllib.parse
import time
import os
import base64
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# 1. Environment & Page Setup
# -----------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Nova Image AI | Creative Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Mascot Image as Base64 for fast local rendering
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return None

mascot_path = os.path.join(os.path.dirname(__file__), "assets", "mascot.jpg")
mascot_b64 = get_base64_image(mascot_path)

# -----------------------------------------------------------------------------
# 2. Modern Design System: Navy Blue (#07152E) & Accent Yellow (#FFD43B)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

/* Typography (Preserve Streamlit icons) */
.stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
.stApp button, .stApp input, .stApp textarea, .stApp label {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

span[data-testid="stIconMaterial"], 
[class*="material-symbols"], 
[class*="material-icons"], 
.material-symbols-rounded {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}

/* Base Canvas */
.stApp {
    background-color: #07152E !important;
    background-image: 
        radial-gradient(circle at 50% 12%, rgba(18, 59, 120, 0.45) 0%, transparent 60%),
        radial-gradient(circle at 10% 85%, rgba(18, 59, 120, 0.3) 0%, transparent 50%) !important;
    color: #FFFFFF !important;
}

/* Hide Default Clutter */
header[data-testid="stHeader"], footer, #MainMenu {
    display: none !important;
}

/* Main Container Spacing */
section[data-testid="stMain"] > div.block-container {
    max-width: 880px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 9.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin: 0 auto !important;
}

/* ----------------------------------------------------
   SIDEBAR STYLING
   ---------------------------------------------------- */
section[data-testid="stSidebar"] {
    background-color: #051024 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.4rem 1.2rem !important;
}

.sidebar-logo-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.5rem;
}

.sidebar-robot-badge {
    width: 44px;
    height: 44px;
    background: #0C234B;
    border: 2px solid #FFD43B;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 16px rgba(255, 212, 59, 0.3);
}

.sidebar-logo-text h2 {
    font-size: 1.2rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.01em;
}

.sidebar-logo-text p {
    font-size: 0.74rem;
    color: #8EA0BC;
    margin: 2px 0 0 0;
}

/* Sidebar Yellow Primary Action Button */
.st-key-btn_new_gen button {
    background-color: #FFD43B !important;
    color: #07152E !important;
    font-weight: 800 !important;
    font-size: 0.94rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 11px 16px !important;
    box-shadow: 0 4px 18px rgba(255, 212, 59, 0.35) !important;
    width: 100% !important;
    margin-bottom: 12px !important;
    transition: all 0.2s ease !important;
}

.st-key-btn_new_gen button:hover {
    background-color: #FFE066 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 22px rgba(255, 212, 59, 0.45) !important;
}

/* Sidebar Style Picker */
div[data-testid="stSelectbox"] label {
    color: #CBD5E1 !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
}

div[data-testid="stSelectbox"] > div {
    background-color: #091C3E !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}

/* Sidebar Secondary Button */
.st-key-btn_clear button {
    background-color: transparent !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 9px 14px !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: all 0.2s ease !important;
}

.st-key-btn_clear button:hover {
    background-color: rgba(18, 59, 120, 0.35) !important;
    color: #FFFFFF !important;
    transform: translateX(3px);
}

/* User Profile Badge at Sidebar Bottom */
.sidebar-user-card {
    background: #091C3E;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 12px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 2rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.sidebar-user-avatar {
    width: 36px;
    height: 36px;
    background: #FFD43B;
    color: #07152E;
    font-weight: 900;
    font-size: 0.82rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 10px rgba(255, 212, 59, 0.35);
}

.sidebar-user-info h4 {
    margin: 0;
    font-size: 0.88rem;
    font-weight: 800;
    color: #FFFFFF;
}

.sidebar-user-info p {
    margin: 2px 0 0 0;
    font-size: 0.72rem;
    color: #8EA0BC;
}

/* ----------------------------------------------------
   HERO WELCOME SECTION
   ---------------------------------------------------- */
.hero-center-box {
    text-align: center;
    margin-bottom: 1.8rem;
    padding-top: 0.4rem;
}

.mascot-glow-wrapper {
    width: 88px;
    height: 88px;
    margin: 0 auto 0.9rem auto;
    border-radius: 50%;
    background: #FFD43B;
    padding: 3px;
    box-shadow: 0 0 32px rgba(255, 212, 59, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.mascot-glow-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}

.hero-main-title {
    font-size: 2.15rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
}

.hero-main-title span {
    color: #FFD43B;
}

.hero-subtitle-text {
    font-size: 0.94rem;
    color: #94A3B8;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.45;
}

/* ----------------------------------------------------
   4 INSPIRATION CARDS (2X2 GRID)
   ---------------------------------------------------- */
.st-key-card_img_1 button,
.st-key-card_img_2 button,
.st-key-card_img_3 button,
.st-key-card_img_4 button {
    background: #0B224E !important;
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
    border-radius: 16px !important;
    padding: 14px 18px !important;
    min-height: 80px !important;
    width: 100% !important;
    text-align: left !important;
    color: #8EA0BC !important;
    font-size: 0.78rem !important;
    line-height: 1.4 !important;
    white-space: pre-line !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.22) !important;
    margin-bottom: 8px !important;
}

.st-key-card_img_1 button::first-line,
.st-key-card_img_2 button::first-line,
.st-key-card_img_3 button::first-line,
.st-key-card_img_4 button::first-line {
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    color: #FFFFFF !important;
    line-height: 1.6 !important;
}

.st-key-card_img_1 button:hover,
.st-key-card_img_2 button:hover,
.st-key-card_img_3 button:hover,
.st-key-card_img_4 button:hover {
    background: #123B78 !important;
    border-color: #FFD43B !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(255, 212, 59, 0.22) !important;
}

/* ----------------------------------------------------
   SINGLE SLEEK CHAT INPUT (FIXED NO DOUBLE BORDER)
   ---------------------------------------------------- */
div[data-testid="stBottom"] {
    background: linear-gradient(180deg, transparent 0%, #07152E 40%, #07152E 100%) !important;
    padding-top: 14px !important;
    padding-bottom: 18px !important;
}

div[data-testid="stBottom"] > div {
    background: transparent !important;
    max-width: 880px !important;
    margin: 0 auto !important;
    padding: 0 2rem !important;
}

div[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

div[data-testid="stChatInput"] > div {
    border-radius: 9999px !important;
    background-color: #081B3C !important;
    border: 1.5px solid #1A3E78 !important;
    box-shadow: 0 4px 22px rgba(0, 0, 0, 0.45) !important;
    padding: 3px 8px !important;
    display: flex !important;
    align-items: center !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: #FFD43B !important;
    box-shadow: 0 0 15px rgba(255, 212, 59, 0.25), 0 4px 22px rgba(0, 0, 0, 0.5) !important;
}

div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #FFFFFF !important;
    font-size: 0.94rem !important;
    padding-left: 14px !important;
    line-height: 1.4 !important;
}

div[data-testid="stChatInput"] textarea:focus {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #8EA0BC !important;
}

div[data-testid="stChatInput"] button {
    background-color: #FFD43B !important;
    color: #07152E !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    border: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 10px rgba(255, 212, 59, 0.4) !important;
    transition: transform 0.15s ease !important;
}

div[data-testid="stChatInput"] button:hover {
    transform: scale(1.05);
}

div[data-testid="stChatInput"] button svg {
    fill: #07152E !important;
}

/* ----------------------------------------------------
   IMAGE & CHAT RESULTS
   ---------------------------------------------------- */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 0.7rem 0 !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background-color: #123B78 !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 212, 59, 0.35) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 14px 18px !important;
    max-width: 80% !important;
    margin-left: auto !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageAvatarUser"] {
    display: none !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    background-color: #0B224E !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 16px 20px !important;
    max-width: 85% !important;
}

/* Download Button Yellow Style */
div.stDownloadButton > button {
    background-color: #FFD43B !important;
    color: #07152E !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    margin-top: 8px !important;
    transition: all 0.2s ease !important;
}

div.stDownloadButton > button:hover {
    background-color: #FFE066 !important;
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Environment & Configuration
# -----------------------------------------------------------------------------
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://image-chatbot.services.ai.azure.com/openai/v1/responses")
MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")

# -----------------------------------------------------------------------------
# 4. Sidebar Controls & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo-header">
        <div class="sidebar-robot-badge">🎨</div>
        <div class="sidebar-logo-text">
            <h2>Nova Image AI</h2>
            <p>Creative Studio · By Ahmed</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕  New Canvas", key="btn_new_gen", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_gen_time = 0
        st.rerun()

    style = st.selectbox(
        "Art Style",
        ["Photorealistic", "Cinematic", "Digital Art", "Cyberpunk", "Anime", "3D Render"]
    )

    if st.button("🗑️  Clear History", key="btn_clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_gen_time = 0
        st.rerun()

    st.markdown("""
    <div class="sidebar-user-card">
        <div class="sidebar-user-avatar">MA</div>
        <div class="sidebar-user-info">
            <h4>Muhammad Ahmed</h4>
            <p>Creator & Developer</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. Session State Initialization
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_gen_time" not in st.session_state:
    st.session_state.last_gen_time = 0

# -----------------------------------------------------------------------------
# 6. Prompt Refiner (Azure OpenAI) & Generation Backend
# -----------------------------------------------------------------------------
def get_refined_prompt(user_text, art_style):
    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "input": f"Rewrite this prompt into a vivid, descriptive, high-quality 25-word visual prompt for image generation in {art_style.lower()} style: {user_text}"
    }
    try:
        r = requests.post(ENDPOINT, headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("output", []):
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        text = c.get("text", "").strip('\"\\n ')
                        if text:
                            return text
    except Exception:
        pass
    return f"{user_text}, {art_style.lower()} style, extremely detailed, 8k resolution, award-winning lighting"

# -----------------------------------------------------------------------------
# 7. Main Screen: Inspiration Home vs Generated Gallery
# -----------------------------------------------------------------------------
clicked_prompt = None

if len(st.session_state.messages) == 0:
    mascot_img = f'<img src="data:image/jpeg;base64,{mascot_b64}">' if mascot_b64 else '🎨'

    st.markdown(f"""
    <div class="hero-center-box">
        <div class="mascot-glow-wrapper">
            {mascot_img}
        </div>
        <h1 class="hero-main-title">Welcome to <span>Nova Image AI</span></h1>
        <p class="hero-subtitle-text">Transform your imagination into breathtaking visuals. Type any idea to generate art!</p>
    </div>
    """, unsafe_allow_html=True)

    # 4 Inspiration Cards (2x2 Grid)
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if st.button("🌌  Cyberpunk Cityscape           →\nFuturistic neon-drenched metropolis with flying cars.", key="card_img_1", use_container_width=True):
            clicked_prompt = "Futuristic cyberpunk neon city with flying cars in rainy night reflection"

    with col2:
        if st.button("🦁  Celestial Mythical Beast     →\nMajestic golden lion with glowing ethereal wings.", key="card_img_2", use_container_width=True):
            clicked_prompt = "A majestic celestial golden lion with glowing feathered wings and cosmic dust"

    col3, col4 = st.columns(2, gap="medium")
    with col3:
        if st.button("🏎️  Futuristic Hypercar              →\nSleek aerodynamic electric vehicle on alpine roads.", key="card_img_3", use_container_width=True):
            clicked_prompt = "Concept hypercar futuristic design driving through misty winding mountain pass"

    with col4:
        if st.button("🪐  Bioluminescent Planet         →\nAlien flora, twin moons, and radiant glowing forest.", key="card_img_4", use_container_width=True):
            clicked_prompt = "Alien planetary landscape with bioluminescent flora, crystal trees, and twin moons"

else:
    # Gallery Conversation Stream
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px;">
        <h3 style="margin:0; font-size:1.15rem; color:#FFFFFF;">Art Studio Session with <span style="color:#FFD43B;">Nova Image AI</span></h3>
    </div>
    """, unsafe_allow_html=True)

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image":
                st.markdown(f"**Concept:** *\"{msg.get('prompt')}\"*")
                if msg.get("bytes"):
                    st.image(msg["bytes"], use_container_width=True)
                    st.download_button(
                        label="📥 Download Artwork (PNG)",
                        data=msg["bytes"],
                        file_name=f"nova_ai_artwork_{idx + 1}.png",
                        mime="image/png",
                        key=f"dl_btn_{idx}"
                    )
                else:
                    st.image(msg["url"], use_container_width=True)
                
                if msg.get("refined"):
                    with st.expander("✨ Refined Visual Prompt"):
                        st.caption(msg["refined"])
            else:
                st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# 8. Single Unified Chat Input & Image Generation Workflow
# -----------------------------------------------------------------------------
user_input = st.chat_input("Describe the image you want to create with Nova Image AI...")

active_prompt = clicked_prompt if clicked_prompt else user_input

if active_prompt:
    st.session_state.messages.append({"role": "user", "type": "text", "content": active_prompt})
    st.rerun()

# Generation Handler for Latest Prompt
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    current_prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        # Smooth rate limiting
        elapsed = time.time() - st.session_state.last_gen_time
        COOLDOWN = 35
        if elapsed < COOLDOWN:
            wait_time = int(COOLDOWN - elapsed)
            with st.spinner(f"Nova Image AI is queueing render slot ({wait_time}s)..."):
                time.sleep(wait_time)

        with st.spinner("Nova Image AI is rendering your masterpiece..."):
            refined_prompt = get_refined_prompt(current_prompt, style)
            encoded = urllib.parse.quote(refined_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded}"
            
            headers = {
                "Referer": "https://pollinations.ai/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            img_bytes = None
            try:
                res = requests.get(image_url, headers=headers, timeout=40)
                if res.status_code == 200 and len(res.content) > 1000:
                    img_bytes = res.content
                    st.session_state.last_gen_time = time.time()
            except Exception:
                pass

            if img_bytes:
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": current_prompt,
                    "bytes": img_bytes,
                    "refined": refined_prompt
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": current_prompt,
                    "url": image_url,
                    "refined": refined_prompt
                })
                st.session_state.last_gen_time = time.time()

    st.rerun()
