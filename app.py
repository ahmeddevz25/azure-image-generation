import streamlit as st
import requests
import urllib.parse
import time
import os
from dotenv import load_dotenv

# Load local environment configuration
load_dotenv()

st.set_page_config(
    page_title="Vision Studio | AI Image Generator",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Design System - Human-crafted Modern Studio UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Background canvas */
.stApp {
    background: radial-gradient(circle at 10% 10%, #111827 0%, #080C14 100%) !important;
    color: #F3F4F6;
}

/* Header bar */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    margin-bottom: 24px;
}

.brand-title {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #FFFFFF;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-badge {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 999px;
    color: #A5B4FC;
    letter-spacing: 0.03em;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.75rem;
    font-weight: 500;
    color: #34D399;
}

.status-dot {
    width: 7px;
    height: 7px;
    background: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10B981;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0B0F19 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07);
}

/* Image result container card */
.image-card {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 14px;
    margin-top: 10px;
    margin-bottom: 14px;
}

.prompt-tag {
    font-size: 0.8rem;
    color: #9CA3AF;
    margin-bottom: 8px;
    line-height: 1.4;
}

/* Chat Input Styling */
div[data-testid="stChatInput"] textarea {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    color: #F9FAFB !important;
}

div[data-testid="stChatInput"] textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 1px #6366F1 !important;
}
</style>
""", unsafe_allow_html=True)

# Azure OpenAI configuration
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://image-chatbot.services.ai.azure.com/openai/v1/responses")
MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")

# Top Header Bar
st.markdown("""
<div class="top-header">
    <div style="display: flex; align-items: center; gap: 12px;">
        <h1 class="brand-title">Vision Studio</h1>
        <span class="brand-badge">Azure gpt-4o</span>
    </div>
    <div class="status-indicator">
        <span class="status-dot"></span>
        Ready to generate
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### Studio Controls")
    
    style = st.selectbox(
        "Visual Style",
        [
            "Photorealistic",
            "Cinematic 3D",
            "Digital Concept Art",
            "Anime / Illustration",
            "Cyberpunk Neon",
            "Minimalist Studio"
        ]
    )
    
    st.markdown("---")
    st.markdown("### Suggested Prompts")
    quick_prompt = None
    
    if st.button("🏎️ Classic Vintage Sports Car", use_container_width=True):
        quick_prompt = "Classic 1960s vintage red sports car on a winding mountain road at golden hour"
        
    if st.button("🏙️ Cyberpunk Rain Alley", use_container_width=True):
        quick_prompt = "Futuristic cyberpunk Tokyo street alley at night with neon signs and reflective rain puddles"
        
    if st.button("☕ Cozy Coffee Desk", use_container_width=True):
        quick_prompt = "Steaming ceramic cup of coffee on a rustic wooden desk next to an open notebook and autumn leaves"

    if st.button("🐾 Baby Snow Leopard", use_container_width=True):
        quick_prompt = "Adorable fluffy baby snow leopard sitting in fresh powdery snow, macro detailed fur"

    st.markdown("---")
    if st.button("Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_gen_time = 0
        st.rerun()

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "type": "text",
            "content": "Welcome to Vision Studio! Enter any idea or prompt below, and I'll generate high-resolution artwork for you."
        }
    ]

if "last_gen_time" not in st.session_state:
    st.session_state.last_gen_time = 0

# Display conversation gallery
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.markdown(f"**Prompt:** *\"{msg.get('prompt')}\"*")
            
            # Display image
            if msg.get("bytes"):
                st.image(msg["bytes"], use_container_width=True)
                st.download_button(
                    label="Download Image",
                    data=msg["bytes"],
                    file_name="vision_studio_render.png",
                    mime="image/png"
                )
            else:
                st.image(msg["url"], use_container_width=True)
                
            if "refined" in msg and msg["refined"]:
                with st.expander("Prompt Details"):
                    st.caption(msg["refined"])
        else:
            st.write(msg["content"])

def get_refined_prompt(user_text, art_style):
    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "input": f"Rewrite this prompt into a concise 20-word visual description for image generation in {art_style.lower()} style: {user_text}"
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
    return f"{user_text}, {art_style.lower()} style, high detailed"

# Input handler (from quick prompt button or chat input)
user_input = st.chat_input("Describe the image you want to create...")
active_prompt = quick_prompt if quick_prompt else user_input

if active_prompt:
    st.session_state.messages.append({"role": "user", "type": "text", "content": active_prompt})
    with st.chat_message("user"):
        st.write(active_prompt)

    with st.chat_message("assistant"):
        # Auto-cooldown to ensure smooth generations without rate limit hits
        elapsed = time.time() - st.session_state.last_gen_time
        COOLDOWN = 40
        if elapsed < COOLDOWN:
            wait_time = int(COOLDOWN - elapsed)
            with st.spinner(f"Preparing generation slot (ready in {wait_time}s)..."):
                time.sleep(wait_time)

        with st.spinner("Synthesizing artwork..."):
            refined_prompt = get_refined_prompt(active_prompt, style)
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

            st.markdown(f"**Result for:** *\"{active_prompt}\"*")
            
            if img_bytes:
                st.image(img_bytes, use_container_width=True)
                st.download_button(
                    label="Download Image",
                    data=img_bytes,
                    file_name="vision_studio_render.png",
                    mime="image/png"
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": active_prompt,
                    "bytes": img_bytes,
                    "refined": refined_prompt
                })
            else:
                st.image(image_url, use_container_width=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": active_prompt,
                    "url": image_url,
                    "refined": refined_prompt
                })
                st.session_state.last_gen_time = time.time()

            with st.expander("Prompt Details"):
                st.caption(refined_prompt)
