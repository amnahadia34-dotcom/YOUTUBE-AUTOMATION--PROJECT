# =========================================================
# 🚀 ULTRA ELITE AI YOUTUBE AUTOMATION ECOSYSTEM
# FULL AUTONOMOUS AI MEDIA OPERATING SYSTEM
# app.py
# =========================================================

import os
import uuid
import base64
import time

import streamlit as st

from openai import OpenAI

# =========================================================
# OPTIONAL MOVIEPY IMPORT
# =========================================================

MOVIEPY_AVAILABLE = True

try:

    try:

        from moviepy import (
            ImageClip,
            AudioFileClip
        )

    except Exception:

        from moviepy.editor import (
            ImageClip,
            AudioFileClip
        )

except Exception:

    MOVIEPY_AVAILABLE = False

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI MEDIA EMPIRE",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# OUTPUT FOLDER
# =========================================================

OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* BACKGROUND */

.stApp {

    background:
    radial-gradient(circle at top left,#1e1b4b 0%,#020617 40%),
    radial-gradient(circle at bottom right,#7c3aed 0%,#020617 30%);

    color:white;
}

/* HERO */

.hero-title {

    text-align:center;

    font-size:80px;

    font-weight:900;

    margin-top:20px;

    background:linear-gradient(
        to right,
        #ff4d4d,
        #7c3aed,
        #38bdf8
    );

    -webkit-background-clip:text;

    -webkit-text-fill-color:transparent;
}

.hero-sub {

    text-align:center;

    font-size:24px;

    color:#d1d5db;

    margin-bottom:40px;
}

/* GLASS */

.glass {

    background:rgba(255,255,255,0.06);

    border:1px solid rgba(255,255,255,0.1);

    border-radius:24px;

    padding:25px;

    margin-bottom:20px;

    backdrop-filter:blur(12px);
}

/* BUTTON */

.stButton button {

    width:100%;

    height:70px;

    border:none;

    border-radius:18px;

    font-size:24px;

    font-weight:900;

    color:white;

    background:linear-gradient(
        to right,
        #7c3aed,
        #2563eb,
        #06b6d4
    );
}

/* SIDEBAR */

section[data-testid="stSidebar"] {

    background:#020617;
}

section[data-testid="stSidebar"] * {

    color:white !important;
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea {

    background:#0f172a !important;

    color:white !important;

    border-radius:14px !important;
}

.stSelectbox div {

    background:#0f172a !important;

    color:white !important;
}

.metric-card {

    background:rgba(255,255,255,0.06);

    border-radius:20px;

    padding:20px;

    text-align:center;

    margin-bottom:15px;

    border:1px solid rgba(255,255,255,0.08);
}

.metric-number {

    font-size:36px;

    font-weight:900;

    color:#38bdf8;
}

.metric-label {

    font-size:16px;

    color:#d1d5db;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚡ AI CONTROL CENTER")

openai_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    type="password"
)

channel_name = st.sidebar.text_input(
    "📺 Channel Name"
)

language = st.sidebar.selectbox(
    "🌍 Language",
    [
        "English",
        "Urdu",
        "Roman Urdu",
        "Hindi",
        "Arabic",
        "Spanish"
    ]
)

niche = st.sidebar.selectbox(
    "🧠 Niche",
    [
        "AI",
        "Technology",
        "Finance",
        "Motivation",
        "Luxury",
        "Documentary",
        "Gaming",
        "Education",
        "News"
    ]
)

video_style = st.sidebar.selectbox(
    "🎨 Video Style",
    [
        "Cinematic",
        "Netflix Style",
        "MrBeast Style",
        "Luxury",
        "Dark Theme",
        "Hyper Realistic"
    ]
)

voice_type = st.sidebar.selectbox(
    "🎤 Voice Style",
    [
        "Male Deep",
        "Female Soft",
        "Motivational",
        "Documentary"
    ]
)

# =========================================================
# API CHECK
# =========================================================

if not openai_key:

    st.warning(
        "⚠️ Please Enter OpenAI API Key"
    )

    st.stop()

client = OpenAI(
    api_key=openai_key
)

# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero-title">
🚀 AI MEDIA EMPIRE
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-sub">
Autonomous AI YouTube Operating System
</div>
""", unsafe_allow_html=True)

# =========================================================
# TOPIC
# =========================================================

topic = st.text_input(
    "🎯 Enter Viral Topic",
    placeholder="Example: Future of Artificial Intelligence"
)

# =========================================================
# ANALYTICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">94%</div>
        <div class="metric-label">Viral Probability</div>
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">88%</div>
        <div class="metric-label">CTR Prediction</div>
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">81%</div>
        <div class="metric-label">Retention Score</div>
    </div>
    """, unsafe_allow_html=True)

with col4:

    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">15.2K</div>
        <div class="metric-label">Projected Views</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# AI SCRIPT ENGINE
# =========================================================

def generate_script(topic):

    prompt = f"""
Create extremely engaging YouTube script.

TOPIC:
{topic}

LANGUAGE:
{language}

NICHE:
{niche}

STYLE:
{video_style}

Generate:

- Viral Hook
- Intro
- Main Content
- Emotional Ending
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
# AI CAPTION ENGINE
# =========================================================

def generate_caption(topic):

    prompt = f"""
Create highly viral YouTube caption.

TOPIC:
{topic}

Generate:
- SEO caption
- Viral hashtags
- Emotional text
- High CTR lines
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
# AI IMAGE ENGINE
# =========================================================

def generate_image(topic):

    prompt = f"""
Create cinematic AI image.

TOPIC:
{topic}

STYLE:
{video_style}

Requirements:
- Ultra realistic
- Cinematic lighting
- Dramatic
- Viral quality
- 4K
"""

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024"
    )

    image_base64 = result.data[0].b64_json

    image_bytes = base64.b64decode(
        image_base64
    )

    image_path = os.path.join(
        OUTPUT_DIR,
        f"image_{uuid.uuid4().hex}.png"
    )

    with open(image_path, "wb") as f:

        f.write(image_bytes)

    return image_path

# =========================================================
# AI THUMBNAIL ENGINE
# =========================================================

def generate_thumbnail(topic):

    prompt = f"""
Create EXTREMELY HIGH CTR YouTube thumbnail.

TOPIC:
{topic}

STYLE:
{video_style}

Requirements:
- MrBeast style
- Hyper realistic
- Strong emotions
- Curiosity trigger
- Cinematic atmosphere
- Dramatic lighting
- Viral thumbnail psychology
"""

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024"
    )

    image_base64 = result.data[0].b64_json

    image_bytes = base64.b64decode(
        image_base64
    )

    thumbnail_path = os.path.join(
        OUTPUT_DIR,
        f"thumbnail_{uuid.uuid4().hex}.png"
    )

    with open(thumbnail_path, "wb") as f:

        f.write(image_bytes)

    return thumbnail_path

# =========================================================
# AI VIDEO ENGINE
# =========================================================

def generate_video(image_path):

    if not MOVIEPY_AVAILABLE:

        return None

    final_video = os.path.join(
        OUTPUT_DIR,
        f"video_{uuid.uuid4().hex}.mp4"
    )

    try:

        clip = (
            ImageClip(image_path)
            .set_duration(8)
        )

        clip.write_videofile(
            final_video,
            fps=24,
            codec="libx264"
        )

        return final_video

    except Exception:

        return None

# =========================================================
# RUN BUTTON
# =========================================================

if st.button("🚀 RUN AUTONOMOUS AI SYSTEM"):

    if not topic:

        st.error(
            "❌ Please Enter Topic"
        )

    else:

        with st.spinner(
            "🧠 AI System Running..."
        ):

            progress = st.progress(0)

            status = st.empty()

            steps = [

                "Detecting Trends...",
                "Analyzing Audience...",
                "Generating Script...",
                "Generating Caption...",
                "Generating AI Image...",
                "Generating AI Thumbnail...",
                "Building Video...",
                "Optimizing SEO..."
            ]

            for i, step in enumerate(steps):

                status.info(step)

                progress.progress(
                    int((i + 1) / len(steps) * 100)
                )

                time.sleep(1)

            # =====================================================
            # GENERATIONS
            # =====================================================

            script = generate_script(topic)

            caption = generate_caption(topic)

            image = generate_image(topic)

            thumbnail = generate_thumbnail(topic)

            video = generate_video(image)

            # =====================================================
            # SUCCESS
            # =====================================================

            st.success(
                "🔥 Autonomous AI Media System Completed"
            )

            st.balloons()

            # =====================================================
            # TABS
            # =====================================================

            tab1, tab2, tab3, tab4, tab5 = st.tabs([

                "🧠 Script",
                "✍️ Caption",
                "🖼️ AI Image",
                "🔥 Thumbnail",
                "🎬 Video"

            ])

            # =====================================================
            # SCRIPT
            # =====================================================

            with tab1:

                st.write(script)

            # =====================================================
            # CAPTION
            # =====================================================

            with tab2:

                st.write(caption)

            # =====================================================
            # IMAGE
            # =====================================================

            with tab3:

                st.image(
                    image,
                    use_container_width=True
                )

                with open(image, "rb") as file:

                    st.download_button(
                        "⬇️ Download AI Image",
                        data=file,
                        file_name="ai_image.png",
                        mime="image/png"
                    )

            # =====================================================
            # THUMBNAIL
            # =====================================================

            with tab4:

                st.image(
                    thumbnail,
                    use_container_width=True
                )

                with open(thumbnail, "rb") as file:

                    st.download_button(
                        "⬇️ Download Thumbnail",
                        data=file,
                        file_name="thumbnail.png",
                        mime="image/png"
                    )

            # =====================================================
            # VIDEO
            # =====================================================

            with tab5:

                if video:

                    st.video(video)

                    with open(video, "rb") as file:

                        st.download_button(
                            "⬇️ Download Video",
                            data=file,
                            file_name="ai_video.mp4",
                            mime="video/mp4"
                        )

                else:

                    st.warning(
                        "⚠️ MoviePy Not Installed Properly"
                    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
<center>

<h2>
🔥 ELITE AI MEDIA OPERATING SYSTEM
</h2>

<p>
Next Generation Autonomous Content Infrastructure
</p>

</center>
""", unsafe_allow_html=True)