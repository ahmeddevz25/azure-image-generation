import streamlit as st
import requests
import urllib.parse
import time
import os
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Clean, ChatGPT/Claude style layout
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Centered Canvas */
.block-container {
    max-width: 740px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 6rem !important;
    margin: 0 auto !important;
}

/* Header */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-logo {
    width: 36px;
    height: 36px;
    background: #6366F1;
    color: #FFFFFF;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 700;
}

.brand-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
}

.brand-subtitle {
    font-size: 0.78rem;
    color: #94A3B8;
    margin: 0;
}

.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 999px;
    color: #34D399;
    font-size: 0.75rem;
    font-weight: 500;
}

.status-dot {
    width: 6px;
    height: 6px;
    background: #10B981;
    border-radius: 50%;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    padding: 0.75rem 0 !important;
}

/* User Message Bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 10px 16px !important;
    max-width: 80% !important;
    margin-left: auto !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] * {
    color: #FFFFFF !important;
}

/* Hide default user icon for clean floating bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageAvatarUser"] {
    display: none !important;
}

/* Image Container */
.image-result-box {
    margin-top: 8px;
    margin-bottom: 8px;
    border-radius: 12px;
    overflow: hidden;
}

/* Chat input */
div[data-testid="stChatInput"] {
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

# Azure OpenAI configuration
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://image-chatbot.services.ai.azure.com/openai/v1/responses")
MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")

# Clean Header
st.markdown("""
<div class="app-header">
    <div class="brand-wrapper">
        <div class="brand-logo">✦</div>
        <div>
            <h1 class="brand-title">AI Image Generator</h1>
            <p class="brand-subtitle">Powered by Azure OpenAI (gpt-4o)</p>
        </div>
    </div>
    <div class="model-badge">
        <span class="status-dot"></span>
        gpt-4o Ready
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.subheader("Settings")
    style = st.selectbox(
        "Style",
        ["Photorealistic", "Cinematic", "Digital Art", "Anime", "Cyberpunk"]
    )
    
    st.markdown("---")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_gen_time = 0
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "type": "text",
            "content": "Hello! What image would you like me to generate for you today?"
        }
    ]

if "last_gen_time" not in st.session_state:
    st.session_state.last_gen_time = 0

# Display conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.markdown(f"**Prompt:** *\"{msg.get('prompt')}\"*")
            
            if msg.get("bytes"):
                st.image(msg["bytes"], use_container_width=True)
                st.download_button(
                    label="📥 Download Image",
                    data=msg["bytes"],
                    file_name="generated_image.png",
                    mime="image/png"
                )
            else:
                st.image(msg["url"], use_container_width=True)
                
            if "refined" in msg and msg["refined"]:
                with st.expander("Refined Prompt"):
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
    return f"{user_text}, {art_style.lower()} style, high quality"

prompt = st.chat_input("Describe the image you want to generate...")

if prompt:
    # 1. User message
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Assistant response
    with st.chat_message("assistant"):
        # Auto cooldown to ensure smooth generations
        elapsed = time.time() - st.session_state.last_gen_time
        COOLDOWN = 40
        if elapsed < COOLDOWN:
            wait_time = int(COOLDOWN - elapsed)
            with st.spinner(f"Waiting {wait_time}s for generation slot..."):
                time.sleep(wait_time)

        with st.spinner("Generating image..."):
            refined_prompt = get_refined_prompt(prompt, style)
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

            st.markdown(f"**Result for:** *\"{prompt}\"*")
            
            if img_bytes:
                st.image(img_bytes, use_container_width=True)
                st.download_button(
                    label="📥 Download Image",
                    data=img_bytes,
                    file_name="generated_image.png",
                    mime="image/png"
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": prompt,
                    "bytes": img_bytes,
                    "refined": refined_prompt
                })
            else:
                st.image(image_url, use_container_width=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": prompt,
                    "url": image_url,
                    "refined": refined_prompt
                })
                st.session_state.last_gen_time = time.time()

            with st.expander("Refined Prompt"):
                st.caption(refined_prompt)
