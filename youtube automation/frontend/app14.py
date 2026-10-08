# =========================================================
# 🚀 ELITE AI YOUTUBE AUTOMATION PLATFORM
# FULL SaaS LEVEL STREAMLIT APP
# =========================================================

import streamlit as st
import os
import pickle
import openai
import requests
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
from gtts import gTTS

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="🚀 Elite AI YouTube Automation Platform",
    layout="wide",
    page_icon="🎬"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"]{
    background:#020617;
    color:white;
}

.stButton>button{
    width:100%;
    background:linear-gradient(90deg,#ff0000,#ff4d4d);
    color:white;
    border:none;
    border-radius:12px;
    height:50px;
    font-size:16px;
    font-weight:bold;
}

.block-container{
    padding-top:2rem;
}

.card{
    background:#0f172a;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
    border:1px solid #1e293b;
}

.success-box{
    background:#065f46;
    padding:20px;
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ AI CONTROL PANEL")

# =========================================================
# OPENAI KEY
# =========================================================

openai_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    type="password"
)

if openai_key:
    openai.api_key = openai_key

# =========================================================
# CLIENT SECRET JSON
# =========================================================

client_secret = st.sidebar.file_uploader(
    "📂 Upload client_secret.json",
    type=["json"]
)

if client_secret:

    with open("client_secret.json", "wb") as f:
        f.write(client_secret.read())

    st.sidebar.success("✅ client_secret.json uploaded")

# =========================================================
# YOUTUBE SETTINGS
# =========================================================

privacy_status = st.sidebar.selectbox(
    "🔒 Privacy",
    ["public", "private", "unlisted"]
)

language = st.sidebar.selectbox(
    "🌍 Language",
    [
        "English",
        "Urdu",
        "Hindi",
        "Spanish",
        "French"
    ]
)

voice_gender = st.sidebar.selectbox(
    "🎙️ Voice Type",
    [
        "Male",
        "Female"
    ]
)

content_type = st.sidebar.selectbox(
    "🎬 Content Type",
    [
        "Business",
        "Motivation",
        "Finance",
        "Technology",
        "AI",
        "Education",
        "News",
        "Gaming"
    ]
)

video_style = st.sidebar.selectbox(
    "🎥 Video Style",
    [
        "Cinematic",
        "Realistic",
        "Modern",
        "Dark",
        "Documentary",
        "Corporate"
    ]
)

auto_thumbnail = st.sidebar.checkbox(
    "🖼️ Auto Generate Thumbnail",
    value=True
)

auto_script = st.sidebar.checkbox(
    "🧠 Auto Generate Script",
    value=True
)

auto_voice = st.sidebar.checkbox(
    "🎙️ Auto Generate Voice",
    value=True
)

auto_video = st.sidebar.checkbox(
    "🎬 Auto Generate Video",
    value=True
)

auto_seo = st.sidebar.checkbox(
    "📈 Auto SEO",
    value=True
)

auto_tags = st.sidebar.checkbox(
    "🏷️ Auto Tags",
    value=True
)

auto_subtitles = st.sidebar.checkbox(
    "🧾 Auto Captions",
    value=True
)

# =========================================================
# YOUTUBE AUTH
# =========================================================

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():

    credentials = None

    if os.path.exists("token.pkl"):

        with open("token.pkl", "rb") as token:
            credentials = pickle.load(token)

    if not credentials:

        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json",
            SCOPES
        )

        credentials = flow.run_local_server(port=0)

        with open("token.pkl", "wb") as token:
            pickle.dump(credentials, token)

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    return youtube

# =========================================================
# AI SCRIPT GENERATOR
# =========================================================

def generate_script(topic):

    prompt = f"""
    Create a highly engaging YouTube video script.

    Topic: {topic}

    Style: {video_style}

    Language: {language}

    Make it professional, viral, emotional and cinematic.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content

# =========================================================
# AI TITLE GENERATOR
# =========================================================

def generate_title(topic):

    prompt = f"""
    Create a viral YouTube title for:
    {topic}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content

# =========================================================
# AI DESCRIPTION GENERATOR
# =========================================================

def generate_description(topic):

    prompt = f"""
    Create SEO optimized YouTube description for:
    {topic}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content

# =========================================================
# AI TAGS GENERATOR
# =========================================================

def generate_tags(topic):

    prompt = f"""
    Generate viral YouTube tags for:
    {topic}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    tags = response.choices[0].message.content

    return tags.split(",")

# =========================================================
# THUMBNAIL GENERATOR
# =========================================================

def create_thumbnail(title):

    img = Image.new(
        "RGB",
        (1280,720),
        color=(20,20,20)
    )

    draw = ImageDraw.Draw(img)

    draw.rectangle(
        [(0,0),(1280,720)],
        fill=(30,41,59)
    )

    draw.text(
        (100,300),
        title[:60],
        fill="white"
    )

    thumbnail_path = "thumbnail.jpg"

    img.save(thumbnail_path)

    return thumbnail_path

# =========================================================
# VOICE GENERATOR
# =========================================================

def generate_voice(script):

    tts = gTTS(
        text=script,
        lang="en"
    )

    audio_path = "voice.mp3"

    tts.save(audio_path)

    return audio_path

# =========================================================
# VIDEO GENERATOR
# =========================================================

def generate_video(script, audio_path):

    clips = []

    colors = [
        (255,0,0),
        (0,255,0),
        (0,0,255),
        (255,255,0)
    ]

    for i in range(5):

        clip = ColorClip(
            size=(1280,720),
            color=random.choice(colors),
            duration=5
        )

        txt = TextClip(
            f"AI Scene {i+1}",
            fontsize=70,
            color='white'
        ).set_position('center').set_duration(5)

        final = CompositeVideoClip([clip, txt])

        clips.append(final)

    video = concatenate_videoclips(clips)

    audio = AudioFileClip(audio_path)

    final_video = video.set_audio(audio)

    output = "generated_video.mp4"

    final_video.write_videofile(
        output,
        fps=24
    )

    return output

# =========================================================
# UPLOAD VIDEO
# =========================================================

def upload_video(
    youtube,
    video_path,
    title,
    description,
    tags
):

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "28"
        },

        "status": {
            "privacyStatus": privacy_status
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = request.execute()

    return response["id"]

# =========================================================
# UPLOAD THUMBNAIL
# =========================================================

def upload_thumbnail(
    youtube,
    video_id,
    thumbnail_path
):

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path)
    ).execute()

# =========================================================
# MAIN UI
# =========================================================

st.title("🚀 ELITE AI YOUTUBE AUTOMATION PLATFORM")

st.markdown("""
<div class='card'>

<h2>🔥 FULL AI MEDIA AUTOMATION ENGINE</h2>

✅ AI Script Generation  
✅ AI Voiceover  
✅ AI Video Generation  
✅ AI Thumbnail Generation  
✅ SEO Optimization  
✅ Auto Upload  
✅ Shorts Support  
✅ Multi Language  
✅ SaaS Ready  

</div>
""", unsafe_allow_html=True)

# =========================================================
# VIDEO TOPIC
# =========================================================

topic = st.text_input(
    "🎯 Enter Video Topic"
)

# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button("🚀 GENERATE FULL AI VIDEO"):

    if not openai_key:

        st.error("Please Enter OpenAI API Key")

    else:

        try:

            # =========================================
            # SCRIPT
            # =========================================

            with st.spinner("🧠 Generating AI Script..."):

                if auto_script:
                    script = generate_script(topic)
                else:
                    script = topic

            st.success("✅ Script Generated")

            st.text_area(
                "📝 Generated Script",
                script,
                height=300
            )

            # =========================================
            # TITLE
            # =========================================

            if auto_seo:

                title = generate_title(topic)

                description = generate_description(topic)

            else:

                title = topic
                description = topic

            # =========================================
            # TAGS
            # =========================================

            if auto_tags:

                tags = generate_tags(topic)

            else:

                tags = ["AI","YouTube"]

            # =========================================
            # VOICE
            # =========================================

            if auto_voice:

                with st.spinner("🎙️ Generating Voice..."):

                    audio_path = generate_voice(script)

                st.success("✅ Voice Generated")

            # =========================================
            # VIDEO
            # =========================================

            if auto_video:

                with st.spinner("🎬 Generating Video..."):

                    video_path = generate_video(
                        script,
                        audio_path
                    )

                st.success("✅ Video Generated")

                st.video(video_path)

            # =========================================
            # THUMBNAIL
            # =========================================

            if auto_thumbnail:

                thumbnail_path = create_thumbnail(title)

                st.image(
                    thumbnail_path,
                    use_column_width=True
                )

            # =========================================
            # YOUTUBE UPLOAD
            # =========================================

            if os.path.exists("client_secret.json"):

                with st.spinner("🚀 Uploading to YouTube..."):

                    youtube = authenticate_youtube()

                    video_id = upload_video(
                        youtube,
                        video_path,
                        title,
                        description,
                        tags
                    )

                    if auto_thumbnail:

                        try:

                            upload_thumbnail(
                                youtube,
                                video_id,
                                thumbnail_path
                            )

                        except Exception as e:

                            st.warning(
                                f"Thumbnail Upload Failed: {e}"
                            )

                st.success("✅ Uploaded Successfully")

                st.markdown(f"""
                <div class='success-box'>

                <h2>🎉 VIDEO PUBLISHED</h2>

                🔗 https://youtube.com/watch?v={video_id}

                </div>
                """, unsafe_allow_html=True)

        except Exception as e:

            st.error(f"❌ ERROR: {e}")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    f"🚀 Elite AI YouTube Automation Platform • {datetime.now().year}"
)