import streamlit as st
import requests
import urllib.parse
import time
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

st.set_page_config(page_title="AI Image Chatbot", page_icon="🖼️")

st.title("AI Image Chatbot")
st.caption("Generate images from text prompts using Azure OpenAI gpt-4o")

# Azure OpenAI credentials
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://image-chatbot.services.ai.azure.com/openai/v1/responses")
MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")

# Sidebar
with st.sidebar:
    st.subheader("Settings")
    style = st.selectbox("Style", ["Photorealistic", "Digital Art", "Cinematic", "Anime"])
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_gen_time = 0
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "type": "text", "content": "Hello! Describe an image you want to generate."}
    ]

if "last_gen_time" not in st.session_state:
    st.session_state.last_gen_time = 0

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.write(f"**Prompt:** {msg.get('prompt')}")
            st.image(msg["content"], use_container_width=True)
            if "refined" in msg:
                st.caption(f"Refined prompt: {msg['refined']}")
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
                        t = c.get("text", "").strip('\"\\n ')
                        if t:
                            return t
    except Exception:
        pass
    return f"{user_text}, {art_style.lower()} style, high quality"

prompt = st.chat_input("Type your image prompt here...")

if prompt:
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # Auto cooldown to prevent free rate limit banner
        elapsed = time.time() - st.session_state.last_gen_time
        COOLDOWN = 42
        
        if elapsed < COOLDOWN:
            wait_time = int(COOLDOWN - elapsed)
            with st.spinner(f"Please wait {wait_time}s for next generation slot..."):
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
                if res.status_code == 200:
                    img_bytes = res.content
                    st.session_state.last_gen_time = time.time()
            except Exception:
                pass

            st.write(f"**Result for:** *{prompt}*")
            if img_bytes:
                st.image(img_bytes, use_container_width=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": prompt,
                    "content": img_bytes,
                    "refined": refined_prompt
                })
            else:
                st.image(image_url, use_container_width=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "prompt": prompt,
                    "content": image_url,
                    "refined": refined_prompt
                })
                st.session_state.last_gen_time = time.time()
                
            st.caption(f"Refined prompt: {refined_prompt}")
