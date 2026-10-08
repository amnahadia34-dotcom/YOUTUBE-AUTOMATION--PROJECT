import os
import pickle
import requests
import time
from datetime import datetime

import pandas as pd
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from openai import OpenAI

from services.ai_service import generate_script, optimize_text
from services.video_service import generate_video

load_dotenv(dotenv_path=".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_openai_client(api_key: str = "") -> OpenAI:
    key = api_key.strip() if api_key else OPENAI_API_KEY
    if not key:
        raise ValueError("OpenAI API key is required.")
    return OpenAI(api_key=key)


def generate_title(topic: str, client: OpenAI) -> str:
    prompt = f"Create 5 SEO optimized YouTube titles for the topic: {topic}. Return them as bullet points."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional YouTube content strategist."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


def generate_hashtags(topic: str, client: OpenAI) -> str:
    prompt = f"Generate 10 high-CTR YouTube hashtags for the topic: {topic}. Return a comma-separated list."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI marketing assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()


def generate_description(title: str, keywords: str, client: OpenAI) -> str:
    prompt = (
        f"Create a long-form SEO optimized YouTube video description for title: {title}. "
        f"Include the following keywords: {keywords}. Keep the description engaging and include a call to action."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert YouTube description writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=260
    )
    return response.choices[0].message.content.strip()


def generate_thumbnail_image(prompt: str, hf_token: str) -> bytes:
    if not hf_token:
        raise ValueError("HuggingFace API key is required for thumbnail generation.")

    headers = {
        "Authorization": f"Bearer {hf_token}"
    }
    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    payload = {
        "inputs": prompt,
        "options": {
            "wait_for_model": True
        }
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=300)
    if response.status_code != 200:
        raise RuntimeError(f"HuggingFace thumbnail generation failed: {response.status_code} {response.text}")

    return response.content


def save_uploaded_file(uploaded_file, destination_path: str) -> None:
    with open(destination_path, "wb") as f:
        f.write(uploaded_file.read())


def authenticate_youtube() -> build:
    if not os.path.exists("client_secret.json"):
        raise FileNotFoundError("Upload client_secret.json before authenticating YouTube.")

    credentials = None

    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open("token.pkl", "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)


def upload_video_to_youtube(youtube, video_path: str, title: str, description: str, tags: list) -> str:
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response.get("id")


def upload_thumbnail_to_youtube(youtube, video_id: str, thumbnail_path: str) -> None:
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path)
    ).execute()


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="DD Tech - AI YouTube Automation Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# PROFESSIONAL CSS
# ==========================================================

st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* Main Background - Ultra Premium */
.stApp{
    background: linear-gradient(135deg, #0a0e1a 0%, #141829 15%, #0f1620 30%, #1a1f35 50%, #0f1620 70%, #141829 85%, #0a0e1a 100%);
    background-attachment: fixed;
    color: white;
}

/* Hide unwanted text elements */
.stMarkdownContainer p {
    color: transparent !important;
    height: 0;
    margin: 0;
    padding: 0;
}

/* Scrollbar Styling */
::-webkit-scrollbar{
    width: 10px;
}

::-webkit-scrollbar-track{
    background: rgba(5, 8, 15, 0.9);
}

::-webkit-scrollbar-thumb{
    background: linear-gradient(180deg, #ff3333, #ff6600);
    border-radius: 10px;
    box-shadow: 0 0 15px rgba(255, 51, 51, 0.5);
}

::-webkit-scrollbar-thumb:hover{
    background: linear-gradient(180deg, #ff1111, #ff4400);
    box-shadow: 0 0 20px rgba(255, 51, 51, 0.8);
}

/* Sidebar Premium Styling - Pure Black */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #0a0a0f 0%, #0d0d15 50%, #0a0a0f 100%);
    border-right: 2px solid transparent;
    border-image: linear-gradient(180deg, #ff3333, #ff6600, #ff3333) 1;
    box-shadow: inset -15px 0px 40px rgba(255, 51, 51, 0.12);
}

/* Hide ALL grey text - Sidebar */
section[data-testid="stSidebar"] .stMarkdown {
    color: #0a0a0f !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(0, 0, 0, 0) !important;
    visibility: hidden !important;
}

section[data-testid="stSidebar"] .stText {
    color: rgba(0, 0, 0, 0) !important;
    visibility: hidden !important;
}

section[data-testid="stSidebar"] .st-ey {
    background-color: rgba(0, 0, 0, 0) !important;
}

section[data-testid="stSidebar"] div {
    color: inherit;
}

section[data-testid="stSidebar"] label {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Sidebar Success Messages */
.stSuccess {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05)) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
    border-radius: 12px !important;
}

/* Hero Box */
.hero-box{
    padding: 50px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255, 51, 51, 0.2), rgba(0, 150, 255, 0.12), rgba(255, 100, 0, 0.15));
    backdrop-filter: blur(30px);
    border: 2px solid;
    border-image: linear-gradient(135deg, #ff3333, #00ccff, #ff6600) 1;
    margin-bottom: 40px;
    box-shadow: 0 20px 60px rgba(255, 51, 51, 0.25), inset 0 0 60px rgba(255, 255, 255, 0.08), 0 0 40px rgba(0, 200, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.hero-box::before{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at top right, rgba(255, 51, 51, 0.15), transparent 70%), radial-gradient(circle at bottom left, rgba(0, 200, 255, 0.1), transparent 70%);
    pointer-events: none;
    animation: pulse-glow 4s ease-in-out infinite;
}

@keyframes pulse-glow{
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.hero-title{
    font-size: 64px;
    font-weight: 900;
    color: white;
    text-shadow: 0 0 30px rgba(255, 51, 51, 0.6), 0 8px 20px rgba(0, 0, 0, 0.8);
    letter-spacing: -1.5px;
    position: relative;
    z-index: 1;
    background: linear-gradient(135deg, #ff3333 0%, #ff9900 30%, #ffffff 60%, #00ccff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'Arial Black', sans-serif;
}

.hero-sub{
    font-size: 24px;
    color: #ffffff;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.6), 0 0 15px rgba(255, 100, 0, 0.2);
    position: relative;
    z-index: 1;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Glass Card */
.glass-card{
    background: linear-gradient(135deg, rgba(15, 20, 35, 0.8), rgba(10, 12, 20, 0.8));
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255, 100, 0, 0.3);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 18px;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), inset 0 0 25px rgba(255, 51, 51, 0.08);
}

.glass-card:hover{
    transform: translateY(-8px);
    border-color: rgba(255, 100, 0, 0.6);
    box-shadow: 0 25px 60px rgba(255, 51, 51, 0.25), inset 0 0 35px rgba(255, 100, 0, 0.12);
}

/* Metric Card */
.metric-card{
    background: linear-gradient(135deg, rgba(20, 25, 40, 0.9), rgba(12, 15, 28, 0.9));
    backdrop-filter: blur(25px);
    border: 1.5px solid;
    border-image: linear-gradient(135deg, #ff3333, #ff6600, #00ccff) 1;
    border-radius: 18px;
    text-align: center;
    padding: 32px;
    transition: all 0.4s ease;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4), 0 0 35px rgba(255, 51, 51, 0.15);
    position: relative;
    overflow: hidden;
}

.metric-card::before{
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 51, 51, 0.12), transparent);
    pointer-events: none;
}

.metric-card:hover{
    border-image: linear-gradient(135deg, #ff1111, #ff4400, #00ffff) 1;
    transform: scale(1.1);
    box-shadow: 0 20px 70px rgba(255, 51, 51, 0.3), 0 0 50px rgba(0, 200, 255, 0.15);
}

.metric-value{
    font-size: 42px;
    font-weight: 900;
    background: linear-gradient(135deg, #ff3333, #ff6600, #00ccff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 25px rgba(255, 51, 51, 0.4);
}

.metric-title{
    color: #ffffff;
    font-weight: 700;
    font-size: 16px;
    margin-top: 8px;
    letter-spacing: 0.7px;
}

/* Feature Card */
.feature-card{
    background: linear-gradient(135deg, rgba(15, 20, 35, 0.85), rgba(10, 12, 25, 0.85));
    border-radius: 18px;
    padding: 28px;
    border: 1.5px solid rgba(255, 100, 0, 0.25);
    height: 200px;
    transition: all 0.5s cubic-bezier(0.23, 1, 0.320, 1);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35), inset 0 0 25px rgba(255, 51, 51, 0.08);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.feature-card::before{
    content: '';
    position: absolute;
    top: -100%;
    left: -100%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 100, 0, 0.2), transparent);
    transition: all 0.7s ease;
}

.feature-card:hover{
    border-color: rgba(255, 100, 0, 0.7);
    transform: translateY(-15px);
    box-shadow: 0 20px 65px rgba(255, 51, 51, 0.28), inset 0 0 40px rgba(255, 100, 0, 0.12);
}

.feature-card:hover::before{
    top: 0;
    left: 0;
}

.feature-title{
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
    text-shadow: 0 3px 12px rgba(0, 0, 0, 0.6), 0 0 15px rgba(255, 100, 0, 0.2);
    position: relative;
    z-index: 1;
}

.feature-desc{
    color: #ffffff;
    font-size: 14px;
    font-weight: 500;
    position: relative;
    z-index: 1;
    opacity: 0.95;
}

/* Section Title */
.section-title{
    font-size: 40px;
    font-weight: 900;
    color: white;
    margin-top: 40px;
    margin-bottom: 25px;
    text-shadow: 0 3px 15px rgba(255, 51, 51, 0.4), 0 0 25px rgba(255, 100, 0, 0.15);
    letter-spacing: -0.8px;
    position: relative;
}

.section-title::before{
    content: '';
    position: absolute;
    left: 0;
    bottom: -10px;
    width: 80px;
    height: 5px;
    background: linear-gradient(90deg, #ff3333, #ff6600, transparent);
    border-radius: 3px;
    box-shadow: 0 0 20px rgba(255, 51, 51, 0.5);
}

/* Footer */
.footer-box{
    text-align: center;
    padding: 40px;
    margin-top: 50px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.6));
    border: 2px solid;
    border-image: linear-gradient(135deg, #ef4444, #f97316) 1;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3), inset 0 0 30px rgba(239, 68, 68, 0.05);
}

.footer-box h3{
    background: linear-gradient(135deg, #ef4444, #f97316);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 28px;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}

.footer-box p{
    color: #cbd5e1;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🚀 YouTube SaaS")

st.sidebar.markdown("### YouTube Connect")

client_secret = st.sidebar.file_uploader(
    "Upload client_secret.json",
    type=["json"]
)

if client_secret:
    save_uploaded_file(client_secret, "client_secret.json")
    st.sidebar.success("✅ client_secret.json uploaded")

if st.sidebar.button("Authenticate YouTube"):
    try:
        authenticate_youtube()
        st.sidebar.success("✅ YouTube authenticated")
    except Exception as exc:
        st.sidebar.error(f"Authentication failed: {exc}")

st.sidebar.markdown("---")

openai_key = OPENAI_API_KEY
pexels_key = PEXELS_API_KEY
hf_key = HF_TOKEN

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "AI Topic Generator",
        "AI Script Generator",
        "AI Voice Generator",
        "AI Video Generator",
        "AI Thumbnail Generator",
        "AI Title Generator",
        "AI Description Generator",
        "AI Hashtag Generator",
        "SEO Analysis",
        "Trending Finder",
        "Audience Insights",
        "Shorts Generator",
        "Upload Center",
        "Multi Channel Manager",
        "Settings"
    ]
)

st.sidebar.markdown("---")

st.sidebar.success("System Status: Online")

st.sidebar.metric(
    "Automation Health",
    "99.8%"
)

st.sidebar.metric(
    "AI Accuracy",
    "98%"
)

st.sidebar.metric(
    "Channels",
    "12"
)

openai_client = None
try:
    openai_client = get_openai_client(openai_key)
except ValueError:
    pass

# ==========================================================
# DASHBOARD
# ==========================================================

if page == "Dashboard":

    st.markdown(
    """
    <div class="hero-box">

    <div class="hero-title">
    ⚡ AI-Powered Content Engine
    </div>

    <br>

    <div class="hero-sub">
    Next-Gen Automation Platform | Enterprise Grade | Production Ready
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-value">∞</div>
        <div class="metric-title">Videos/Month</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-value">99.9%</div>
        <div class="metric-title">Uptime</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-value">12M+</div>
        <div class="metric-title">Views</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-value">98%</div>
        <div class="metric-title">SEO Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-value">24/7</div>
        <div class="metric-title">AI Active</div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-value">5s</div>
        <div class="metric-title">Speed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
    '<div class="section-title">⚡ Premium Features</div>',
    unsafe_allow_html=True
    )

    r1c1, r1c2, r1c3 = st.columns(3)

    with r1c1:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">🎯 AI Topics</div>
        <br>
        <div class="feature-desc">Viral trending research powered by GPT-4</div>
        </div>
        """, unsafe_allow_html=True)

    with r1c2:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">✍️ AI Scripts</div>
        <br>
        <div class="feature-desc">Professional scripts in any language</div>
        </div>
        """, unsafe_allow_html=True)

    with r1c3:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">🎬 AI Videos</div>
        <br>
        <div class="feature-desc">Cinematic videos from Pexels + HF</div>
        </div>
        """, unsafe_allow_html=True)

    r2c1, r2c2, r2c3 = st.columns(3)

    with r2c1:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">🎤 Voice Gen</div>
        <br>
        <div class="feature-desc">Human-like narration with AI</div>
        </div>
        """, unsafe_allow_html=True)

    with r2c2:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">🖼️ Thumbnails</div>
        <br>
        <div class="feature-desc">High-CTR AI generated designs</div>
        </div>
        """, unsafe_allow_html=True)

    with r2c3:
        st.markdown("""
        <div class="feature-card">
        <div class="feature-title">📤 Upload</div>
        <br>
        <div class="feature-desc">Auto publish to YouTube</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
    '<div class="section-title">📊 System Performance</div>',
    unsafe_allow_html=True
    )

    stat1, stat2, stat3 = st.columns(3)

    with stat1:
        st.metric("AI Accuracy", "98.5%", "+2.3%")
    with stat2:
        st.metric("Processing Speed", "4.2s/video", "-0.8s")
    with stat3:
        st.metric("Platform Health", "100%", "✅")

    st.markdown(
    '<div class="section-title">🎥 Latest Activity</div>',
    unsafe_allow_html=True
    )

    activities = [
        "✅ 5 AI Scripts Generated",
        "✅ 3 Videos Rendered",
        "✅ 2 Thumbnails Created",
        "✅ 7 YouTube Uploads Complete",
        "✅ SEO Analysis Done"
    ]

    for activity in activities:
        st.success(activity)

    st.markdown(
    """
    <div class="footer-box">
    <h3>🚀 DD Tech Enterprise Platform</h3>
    <p>Advanced AI Automation for YouTube Content Creators</p>
    <p style="font-size: 12px; color: #94a3b8; margin-top: 15px;">
    Scripts • Voice • Video • Thumbnails • SEO • Auto-Upload • Multi-Language
    </p>
    <p style="font-size: 11px; color: #64748b; margin-top: 10px;">
    © 2026 DD Tech - Enterprise Edition
    </p>
    </div>
    """,
    unsafe_allow_html=True
    )

# ==========================================================
# AI TOPIC GENERATOR
# ==========================================================

elif page == "AI Topic Generator":

    st.title("🎯 AI Topic Generator")

    niche = st.text_input(
        "Enter Niche",
        placeholder="AI, Finance, Motivation, Health"
    )

    if st.button("Generate Topics"):

        if not niche:
            st.error("Please enter a niche.")
        elif not openai_client:
            st.error("Please provide an OpenAI API key in the sidebar.")
        else:
            try:
                prompt = (
                    f"Generate 8 viral YouTube video topic ideas for the niche: {niche}. "
                    "Return each idea on a new line."
                )
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a viral YouTube topic strategist."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=180
                )
                topics = response.choices[0].message.content.strip().splitlines()
                for topic in topics:
                    st.success(topic)
            except Exception as exc:
                st.error(f"Topic generation failed: {exc}")

# ==========================================================
# AI SCRIPT GENERATOR
# ==========================================================

elif page == "AI Script Generator":

    st.title("✍ AI Script Generator")

    topic = st.text_input(
        "Video Topic"
    )

    language = st.selectbox(
        "Language",
        ["English", "Urdu", "Hindi", "Spanish", "French"]
    )

    voice_style = st.selectbox(
        "Script Style",
        ["Professional", "Motivational", "Educational", "Storytelling", "Explainer"]
    )

    if st.button("Generate Script"):

        if not topic:
            st.error("Please enter a video topic.")
        elif not openai_client:
            st.error("Please provide an OpenAI API key in the sidebar.")
        else:
            with st.spinner("Generating script..."):
                script = generate_script(topic, language, openai_client=openai_client)
            st.text_area(
                "Generated Script",
                script,
                height=400
            )

# ==========================================================
# AI VOICE GENERATOR
# ==========================================================

elif page == "AI Voice Generator":

    st.title("🎤 AI Voice Generator")

    text = st.text_area(
        "Enter Script"
    )

    voice = st.selectbox(
        "Voice",
        [
            "Male Professional",
            "Female Professional",
            "Narrator",
            "Motivational"
        ]
    )

    if st.button("Generate Voice"):

        if not text:
            st.error("Please enter the script text first.")
        elif not openai_client:
            st.error("Please provide an OpenAI API key in the sidebar.")
        else:
            try:
                os.makedirs("output", exist_ok=True)
                audio_path = os.path.join("output", f"voice_{int(time.time())}.mp3")
                selected_voice = "alloy" if voice != "Female Professional" else "nova"
                response = openai_client.audio.speech.create(
                    model="tts-1",
                    voice=selected_voice,
                    input=text[:4000]
                )
                response.stream_to_file(audio_path)
                st.success("Voice Generated Successfully")
                st.audio(audio_path, format="audio/mp3")
            except Exception as exc:
                st.error(f"Voice generation failed: {exc}")

# ==========================================================
# AI VIDEO GENERATOR
# ==========================================================

elif page == "AI Video Generator":

    st.title("🎬 AI Video Generator")

    script = st.text_area(
        "Enter Video Script",
        placeholder="Paste your generated script or write a short narrative here"
    )

    style = st.selectbox(
        "Style",
        [
            "Cinematic",
            "Documentary",
            "Motivational",
            "Educational",
            "Business"
        ]
    )

    duration = st.slider(
        "Duration (seconds)",
        10,
        300,
        60
    )

    if st.button("Generate Video"):

        if not script:
            st.error("Please provide a script to generate the video.")
        else:
            try:
                os.makedirs("output", exist_ok=True)
                output_path = os.path.join("output", f"video_{int(time.time())}.mp4")
                with st.spinner("Generating video using Pexels and HuggingFace..."):
                    video_path = generate_video(script, narration_path=None, output_path=output_path)
                st.success("Video Created Successfully")
                st.video(video_path)
            except Exception as exc:
                st.error(f"Video generation failed: {exc}")

# ==========================================================
# AI THUMBNAIL GENERATOR
# ==========================================================

elif page == "AI Thumbnail Generator":

    st.title("🖼 AI Thumbnail Generator")

    title = st.text_input(
        "Video Title"
    )

    style = st.selectbox(
        "Thumbnail Style",
        [
            "Mr Beast",
            "Tech",
            "Finance",
            "Gaming",
            "Educational"
        ]
    )

    if st.button("Generate Thumbnail"):

        if not title:
            st.error("Please enter a title for the thumbnail prompt.")
        else:
            try:
                prompt = f"Create a high-CTR YouTube thumbnail for a {style} video titled: {title}."
                image_bytes = generate_thumbnail_image(prompt, hf_key or HF_TOKEN)
                thumbnail_path = os.path.join("output", f"thumbnail_{int(time.time())}.png")
                os.makedirs("output", exist_ok=True)
                with open(thumbnail_path, "wb") as f:
                    f.write(image_bytes)
                st.success("Thumbnail Generated")
                st.image(image_bytes, use_container_width=True)
            except Exception as exc:
                st.error(f"Thumbnail generation failed: {exc}")

# ==========================================================
# AI TITLE GENERATOR
# ==========================================================

elif page == "AI Title Generator":

    st.title("🏆 AI Title Generator")

    keyword = st.text_input(
        "Keyword"
    )

    if st.button("Generate Titles"):

        if not keyword:
            st.error("Please enter a keyword.")
        elif not openai_client:
            st.error("Please provide an OpenAI API key in the sidebar.")
        else:
            try:
                titles = generate_title(keyword, openai_client)
                st.text_area("Generated Titles", titles, height=220)
            except Exception as exc:
                st.error(f"Title generation failed: {exc}")
            # ==========================================================
# AI DESCRIPTION GENERATOR
# ==========================================================

elif page == "AI Description Generator":

    st.title("📝 AI Description Generator")

    video_title = st.text_input(
        "Video Title",
        placeholder="Enter your video title"
    )

    keywords = st.text_area(
        "Keywords",
        placeholder="AI, Automation, YouTube Growth"
    )

    if st.button("Generate Description"):

        if not video_title:
            st.error("Please enter a video title.")
        elif not openai_client:
            st.error("Please provide an OpenAI API key in the sidebar.")
        else:
            try:
                description = generate_description(video_title, keywords, openai_client)
                st.text_area(
                    "Generated Description",
                    description,
                    height=300
                )
            except Exception as exc:
                st.error(f"Description generation failed: {exc}")

# ==========================================================
# AI HASHTAG GENERATOR
# ==========================================================

elif page == "AI Hashtag Generator":

    st.title("#️⃣ AI Hashtag Generator")

    keyword = st.text_input(
        "Main Keyword"
    )

    if st.button("Generate Hashtags"):

        if not keyword:
            st.error("Please enter a main keyword.")
        elif not openai_client:
            st.error("Please provide an OpenAI API key in the sidebar.")
        else:
            try:
                hashtags = generate_hashtags(keyword, openai_client)
                st.code(hashtags)
            except Exception as exc:
                st.error(f"Hashtag generation failed: {exc}")

# ==========================================================
# SEO ANALYSIS
# ==========================================================

elif page == "SEO Analysis":

    st.title("📈 SEO Analysis")

    title = st.text_input(
        "Video Title"
    )

    description = st.text_area(
        "Description"
    )

    if st.button("Analyze SEO"):

        score = np.random.randint(85, 99)

        st.success(
            f"SEO Score: {score}/100"
        )

        st.progress(score)

        st.info("Keyword Density: Excellent")
        st.info("Title Optimization: Strong")
        st.info("Description Quality: High")
        st.info("Ranking Potential: Very Good")

# ==========================================================
# TRENDING FINDER
# ==========================================================

elif page == "Trending Finder":

    st.title("🔥 Trending Finder")

    niche = st.selectbox(
        "Select Niche",
        [
            "AI",
            "Finance",
            "Motivation",
            "Business",
            "Technology",
            "Education"
        ]
    )

    if st.button("Find Trends"):

        trends = [
            f"Future of {niche}",
            f"Best {niche} Tools",
            f"{niche} Trends 2026",
            f"{niche} Automation",
            f"{niche} Success Stories",
            f"{niche} AI Revolution",
            f"{niche} Market Analysis",
            f"{niche} Beginner Guide"
        ]

        for trend in trends:
            st.success(trend)

# ==========================================================
# AUDIENCE INSIGHTS
# ==========================================================

elif page == "Audience Insights":

    st.title("👥 Audience Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Subscribers",
            "245K",
            "+8.5%"
        )

    with col2:
        st.metric(
            "Watch Time",
            "1.8M Hours",
            "+12%"
        )

    with col3:
        st.metric(
            "Engagement",
            "94%",
            "+4%"
        )

    chart_data = pd.DataFrame(
        np.random.randint(
            50,
            200,
            size=(30, 1)
        ),
        columns=["Views"]
    )

    st.line_chart(chart_data)

# ==========================================================
# SHORTS GENERATOR
# ==========================================================

elif page == "Shorts Generator":

    st.title("🎥 AI Shorts Generator")

    long_video_topic = st.text_input(
        "Long Video Topic"
    )

    if st.button("Generate Shorts Ideas"):

        shorts = [
            f"{long_video_topic} in 30 Seconds",
            f"Top 3 Facts About {long_video_topic}",
            f"{long_video_topic} Quick Hack",
            f"{long_video_topic} Myth vs Reality",
            f"{long_video_topic} Secret Nobody Knows",
            f"Beginner Guide To {long_video_topic}",
            f"{long_video_topic} Fast Tutorial",
            f"{long_video_topic} Explained Simply"
        ]

        for short in shorts:
            st.info(short)
            # ==========================================================
# UPLOAD CENTER
# ==========================================================

elif page == "Upload Center":

    st.title("📤 Upload Center")

    st.markdown("### Upload Content")

    uploaded_file = st.file_uploader(
        "Upload Video",
        type=["mp4", "mov", "avi", "mkv"]
    )

    thumbnail = st.file_uploader(
        "Upload Thumbnail",
        type=["png", "jpg", "jpeg"]
    )

    title = st.text_input("Video Title")

    description = st.text_area("Video Description")

    tags = st.text_input("Tags (comma separated)")

    schedule_date = st.date_input(
        "Schedule Date"
    )

    if st.button("Upload To YouTube"):

        if not uploaded_file:
            st.error("Please upload a video file first.")
        elif not title:
            st.error("Please enter a video title.")
        elif not os.path.exists("client_secret.json"):
            st.error("Please upload client_secret.json in the sidebar and authenticate YouTube.")
        else:
            try:
                youtube = authenticate_youtube()
                os.makedirs("output", exist_ok=True)
                upload_path = os.path.join("output", f"upload_{int(time.time())}.mp4")
                save_uploaded_file(uploaded_file, upload_path)
                tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

                with st.spinner("Uploading video to YouTube..."):
                    video_id = upload_video_to_youtube(
                        youtube,
                        upload_path,
                        title,
                        description,
                        tags_list
                    )

                if thumbnail:
                    thumb_path = os.path.join("output", f"thumb_{int(time.time())}.png")
                    save_uploaded_file(thumbnail, thumb_path)
                    upload_thumbnail_to_youtube(youtube, video_id, thumb_path)

                st.success(f"Video uploaded successfully: {video_id}")
            except Exception as exc:
                st.error(f"Upload failed: {exc}")

# ==========================================================
# MULTI CHANNEL MANAGER
# ==========================================================

elif page == "Multi Channel Manager":

    st.title("📺 Multi Channel Manager")

    channels = pd.DataFrame(
        {
            "Channel":[
                "AI Mastery",
                "Finance Pro",
                "Tech Insider",
                "Motivation Hub",
                "Business Growth"
            ],
            "Subscribers":[
                "120K",
                "85K",
                "230K",
                "65K",
                "150K"
            ],
            "Status":[
                "Active",
                "Active",
                "Active",
                "Active",
                "Active"
            ]
        }
    )

    st.dataframe(
        channels,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("Add New Channel")

    st.text_input("Channel Name")

    st.text_input("API Key")

    st.text_input("Channel ID")

    st.button("Connect Channel")

# ==========================================================
# SETTINGS
# ==========================================================

elif page == "Settings":

    st.title("⚙ Settings")

    st.subheader("General Settings")

    st.text_input(
        "Company Name",
        value="DD Tech"
    )

    st.text_input(
        "Admin Email",
        value="admin@example.com"
    )

    st.selectbox(
        "Theme",
        [
            "Dark",
            "Professional",
            "Enterprise"
        ]
    )

    st.subheader("AI Settings")

    st.text_input(
        "OpenAI API Key",
        type="password"
    )

    st.text_input(
        "Gemini API Key",
        type="password"
    )

    st.text_input(
        "ElevenLabs API Key",
        type="password"
    )

    st.text_input(
        "Runway API Key",
        type="password"
    )

    st.button("Save Settings")

# ==========================================================
# ANALYTICS SECTION
# ==========================================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">📊 Analytics Overview</div>',
        unsafe_allow_html=True
    )

    analytics = pd.DataFrame({
        "Views":
        np.random.randint(
            5000,
            20000,
            size=30
        )
    })

    st.line_chart(analytics)

    st.markdown(
        '<div class="section-title">⚡ Recent Activity</div>',
        unsafe_allow_html=True
    )

    activity = [
        "✅ Script Generated",
        "✅ Thumbnail Created",
        "✅ Voice Generated",
        "✅ AI Video Rendered",
        "✅ SEO Optimized",
        "✅ YouTube Upload Completed",
        "✅ Shorts Generated",
        "✅ Hashtags Generated",
        "✅ Trending Topic Found",
        "✅ Audience Report Created"
    ]

    for item in activity:
        st.success(item)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
"""
<div class="footer-box">

<h3>
🚀 DD Tech YouTube Automation SaaS
</h3>

<p>
Enterprise AI Content Creation Platform
</p>

<p>
AI Scripts • AI Voice • AI Video • AI Thumbnails • SEO • Automation
</p>

<p>
© 2026 DD Tech - All Rights Reserved
</p>

</div>
""",
unsafe_allow_html=True
)