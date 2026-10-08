# =========================================================
# 🚀 ADVANCED YOUTUBE AI AUTOMATION PLATFORM
# REAL AI THUMBNAILS + VOICE + VIDEO + AUTO UPLOAD
# =========================================================

import os
import sys
import uuid
import requests
import base64

from datetime import datetime, timedelta

import streamlit as st

from dotenv import load_dotenv

from openai import OpenAI

from PIL import Image

# =========================================================
# ✅ MOVIEPY SAFE IMPORT FIX
# =========================================================

try:

    # NEW MOVIEPY VERSION
    from moviepy import (
        ImageClip,
        AudioFileClip,
        concatenate_videoclips
    )

except Exception:

    # OLD MOVIEPY VERSION
    from moviepy.editor import (
        ImageClip,
        AudioFileClip,
        concatenate_videoclips
    )

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

sys.path.append(ROOT_DIR)

load_dotenv()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="YouTube AI SaaS",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# PREMIUM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        to bottom right,
        #020617,
        #0f172a,
        #111827
    );
}

h1,h2,h3,h4,h5,h6,p,div,span,label {
    color:white !important;
}

.hero-title {
    text-align:center;
    font-size:65px;
    font-weight:900;
    background: linear-gradient(
        to right,
        #ff4b2b,
        #ff416c,
        #7c3aed
    );
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero-sub {
    text-align:center;
    font-size:22px;
    color:#d1d5db !important;
    margin-bottom:40px;
}

.glass {
    background: rgba(255,255,255,0.08);
    padding:25px;
    border-radius:20px;
    backdrop-filter: blur(10px);
    border:1px solid rgba(255,255,255,0.1);
}

.stButton button {
    background: linear-gradient(
        to right,
        #7c3aed,
        #2563eb
    ) !important;

    color:white !important;

    border:none;

    border-radius:14px;

    padding:12px 24px;

    font-size:16px;

    font-weight:700;
}

.stTextInput input {
    background:#1e293b !important;
    color:white !important;
}

.stTextArea textarea {
    background:#1e293b !important;
    color:white !important;
}

.stSelectbox div {
    background:#1e293b !important;
    color:white !important;
}

section[data-testid="stSidebar"] {
    background:#111827;
}

section[data-testid="stSidebar"] * {
    color:white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚡ AI Control Center")

openai_api_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    type="password"
)

youtube_api_key = st.sidebar.text_input(
    "📺 YouTube API Key",
    type="password"
)

uploaded_client_json = st.sidebar.file_uploader(
    "📂 Upload Client Secret JSON",
    type=["json"]
)

uploaded_thumbnail = st.sidebar.file_uploader(
    "🖼️ Upload Custom Thumbnail",
    type=["png", "jpg", "jpeg"]
)

# =========================================================
# API CHECK
# =========================================================

if not openai_api_key:

    st.warning("⚠️ Please enter OpenAI API Key")

    st.stop()

client = OpenAI(api_key=openai_api_key)

# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero-title">
🚀 YouTube AI Automation Platform
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-sub">
AI + Automation + Viral Content Engine
</div>
""", unsafe_allow_html=True)

# =========================================================
# INPUTS
# =========================================================

topic = st.text_input(
    "🎯 Enter Video Topic"
)

language = st.selectbox(
    "🌍 Language",
    [
        "English",
        "Urdu",
        "Roman Urdu"
    ]
)

video_style = st.selectbox(
    "🎬 Video Style",
    [
        "Cinematic",
        "Motivational",
        "Educational",
        "Documentary",
        "Dark Theme",
        "Luxury"
    ]
)

voice_gender = st.selectbox(
    "🎤 AI Voice",
    [
        "Male",
        "Female"
    ]
)

auto_upload = st.checkbox(
    "🔥 Auto Upload to YouTube"
)

# =========================================================
# AI SCRIPT
# =========================================================

def generate_script(topic):

    prompt = f"""
Create a viral YouTube script.

Topic:
{topic}

Language:
{language}

Video Style:
{video_style}

Also generate:
- Hook
- SEO title
- SEO description
- Hashtags
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content

# =========================================================
# THUMBNAIL GENERATOR
# =========================================================

def generate_thumbnail(topic):

    image_prompt = f"""
Create cinematic YouTube thumbnail.

Topic:
{topic}

Style:
{video_style}

Ultra realistic.
High CTR.
YouTube viral style.
4K.
"""

    result = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json

    image_bytes = base64.b64decode(image_base64)

    thumb_path = os.path.join(
        OUTPUT_DIR,
        f"thumb_{uuid.uuid4().hex}.png"
    )

    with open(thumb_path, "wb") as f:
        f.write(image_bytes)

    return thumb_path

# =========================================================
# VOICE GENERATOR
# =========================================================

def generate_voice(script):

    speech_file = os.path.join(
        OUTPUT_DIR,
        f"voice_{uuid.uuid4().hex}.mp3"
    )

    selected_voice = "alloy"

    if voice_gender == "Female":
        selected_voice = "nova"

    response = client.audio.speech.create(
        model="tts-1",
        voice=selected_voice,
        input=script[:4000]
    )

    response.stream_to_file(speech_file)

    return speech_file

# =========================================================
# VIDEO GENERATOR
# =========================================================

def generate_video(
    image_path,
    audio_path
):

    audio = AudioFileClip(audio_path)

    clip = (
        ImageClip(image_path)
        .set_duration(audio.duration)
        .resize(height=720)
    )

    clip = clip.set_audio(audio)

    final_video = os.path.join(
        OUTPUT_DIR,
        f"video_{uuid.uuid4().hex}.mp4"
    )

    clip.write_videofile(
        final_video,
        fps=24,
        codec="libx264"
    )

    return final_video

# =========================================================
# YOUTUBE UPLOAD
# =========================================================

def upload_video(
    video_path,
    title,
    description
):

    youtube = build(
        "youtube",
        "v3",
        developerKey=youtube_api_key
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet":{
                "title":title,
                "description":description
            },
            "status":{
                "privacyStatus":"public"
            }
        },
        media_body=MediaFileUpload(video_path)
    )

    response = request.execute()

    return (
        f"https://youtube.com/watch?v={response['id']}"
    )

# =========================================================
# RUN SYSTEM
# =========================================================

if st.button("🚀 Run Full AI System"):

    if not topic:

        st.error("❌ Enter topic first")

    else:

        with st.spinner(
            "🚀 AI Engine Working..."
        ):

            # =====================================================
            # SCRIPT
            # =====================================================

            script = generate_script(topic)

            st.success("✅ Script Generated")

            # =====================================================
            # THUMBNAIL
            # =====================================================

            if uploaded_thumbnail:

                thumb = os.path.join(
                    OUTPUT_DIR,
                    uploaded_thumbnail.name
                )

                with open(thumb, "wb") as f:
                    f.write(uploaded_thumbnail.getbuffer())

            else:

                thumb = generate_thumbnail(topic)

            st.success("✅ Thumbnail Generated")

            # =====================================================
            # VOICE
            # =====================================================

            voice = generate_voice(script)

            st.success("✅ Voice Generated")

            # =====================================================
            # VIDEO
            # =====================================================

            video = generate_video(
                thumb,
                voice
            )

            st.success("✅ Video Generated")

            st.balloons()

            # =====================================================
            # ANALYTICS
            # =====================================================

            st.markdown("## 📊 Analytics")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Views",
                "12.5K"
            )

            col2.metric(
                "Likes",
                "3.2K"
            )

            col3.metric(
                "Watch Time",
                "892h"
            )

            col4.metric(
                "Retention",
                "76%"
            )

            # =====================================================
            # TABS
            # =====================================================

            tab1, tab2, tab3 = st.tabs([
                "🧠 Script",
                "🖼️ Thumbnail",
                "🎬 Video"
            ])

            # =====================================================
            # SCRIPT TAB
            # =====================================================

            with tab1:

                st.write(script)

            # =====================================================
            # THUMB TAB
            # =====================================================

            with tab2:

                st.image(
                    thumb,
                    use_container_width=True
                )

            # =====================================================
            # VIDEO TAB
            # =====================================================

            with tab3:

                st.video(video)

            # =====================================================
            # DOWNLOAD
            # =====================================================

            with open(video, "rb") as file:

                st.download_button(
                    "⬇️ Download Video",
                    data=file,
                    file_name="ai_video.mp4",
                    mime="video/mp4"
                )

            # =====================================================
            # AUTO UPLOAD
            # =====================================================

            if auto_upload:

                try:

                    url = upload_video(
                        video,
                        topic,
                        script
                    )

                    st.success(
                        "🔥 Uploaded Successfully"
                    )

                    st.write(url)

                except Exception as err:

                    st.error(
                        f"Upload Error: {err}"
                    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
<center>
🔥 Advanced AI YouTube Automation SaaS Platform
</center>
""", unsafe_allow_html=True)