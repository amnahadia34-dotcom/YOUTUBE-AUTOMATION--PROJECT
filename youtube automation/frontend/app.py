import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import edge_tts
import asyncio
import tempfile
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="YouTube Automation", page_icon="🎬", layout="wide")

# ==========================================================
# LOAD ENV
# ==========================================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# ==========================================================
# OPENAI CLIENT
# ==========================================================
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"OpenAI init error: {e}")

# ==========================================================
# SESSION STATE
# ==========================================================
defaults = {
    "script": "", "title": "", "caption": "", "description": "", "hashtags": "",
    "thumbnail_text": "", "suggestions": "", "video_keywords": "",
    "pexels_videos": [], "audio_file": None, "final_video": None,
    "thumbnail_image": None, "existing_thumbnail": None, "existing_video": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def ask_openai(prompt):
    if not client:
        return "OpenAI API key missing"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a YouTube expert."},
                      {"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def search_pexels_videos(query):
    if not PEXELS_API_KEY:
        return []
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=8"
    try:
        r = requests.get(url, headers=headers, timeout=30)
        return r.json().get("videos", [])
    except:
        return []

def generate_hf_thumbnail(prompt):
    if not HF_API_KEY:
        return None
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    try:
        r = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except:
        return None

def download_video(url):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    with open(temp.name, "wb") as f:
        f.write(requests.get(url, stream=True).content)
    return temp.name

def create_final_video(duration_sec, quality):
    # quality not directly used here (moviepy default is decent)
    clips = []
    for vid in st.session_state.pexels_videos[:max(1, duration_sec//5)]:
        try:
            url = vid["video_files"][0]["link"]
            path = download_video(url)
            clip = VideoFileClip(path).subclip(0, min(5, VideoFileClip(path).duration))
            clips.append(clip)
        except:
            pass
    if not clips:
        return None
    final = concatenate_videoclips(clips)
    # Trim to desired duration
    if final.duration > duration_sec:
        final = final.subclip(0, duration_sec)
    if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
        audio = AudioFileClip(st.session_state.audio_file)
        if audio.duration > final.duration:
            audio = audio.subclip(0, final.duration)
        final = final.set_audio(audio)
    out_path = "final_video.mp4"
    final.write_videofile(out_path, codec="libx264", audio_codec="aac", threads=4)
    for c in clips:
        c.close()
    final.close()
    return out_path

async def generate_voice(text, voice_name, out_file):
    await edge_tts.Communicate(text, voice_name).save(out_file)

def get_voice_name(gender):
    return "en-US-GuyNeural" if gender == "Male" else "en-US-JennyNeural"

# ==========================================================
# SIDEBAR - SETTINGS
# ==========================================================
st.sidebar.title("⚙️ Settings")
voice_gender = st.sidebar.selectbox("Voice", ["Male", "Female"], key="side_voice")
duration_min = st.sidebar.selectbox("Video Duration (minutes)", [0.5, 1, 2, 3, 5], key="side_dur")
duration_sec = int(duration_min * 60)
quality_opt = st.sidebar.selectbox("Quality", ["720p", "1080p"], key="side_qual")

# ==========================================================
# MAIN UI
# ==========================================================
st.title("🎬 YouTube Automation (AI Script + Thumbnail + Video)")
st.caption("Generate everything with OpenAI, Pexels, Hugging Face & edge-tts")

# --- Topic input ---
topic = st.text_input("Video Topic", placeholder="e.g., How to grow on YouTube", key="topic_input")
col_gen1, col_gen2, col_gen3 = st.columns(3)

with col_gen1:
    if st.button("📝 Generate Script", key="gen_script"):
        if topic:
            prompt = f"Write a {duration_min} min YouTube script about '{topic}'. Include hook, intro, body, CTA."
            st.session_state.script = ask_openai(prompt)
        else:
            st.warning("Enter a topic first")

with col_gen2:
    if st.button("🏷️ Generate Title", key="gen_title"):
        prompt = f"Give 5 catchy YouTube titles for: {topic}\nScript: {st.session_state.script}"
        st.session_state.title = ask_openai(prompt)

with col_gen3:
    if st.button("📢 Generate Caption", key="gen_caption"):
        prompt = f"Write an engaging YouTube caption for: {topic}\nScript: {st.session_state.script}"
        st.session_state.caption = ask_openai(prompt)

col_gen4, col_gen5, col_gen6 = st.columns(3)
with col_gen4:
    if st.button("📄 Generate Description", key="gen_desc"):
        prompt = f"SEO YouTube description for: {topic}\nScript: {st.session_state.script}"
        st.session_state.description = ask_openai(prompt)
with col_gen5:
    if st.button("#️⃣ Generate Hashtags", key="gen_hashtags"):
        prompt = f"Generate 20 trending hashtags for: {topic}"
        st.session_state.hashtags = ask_openai(prompt)
with col_gen6:
    if st.button("🖼️ Generate Thumbnail Text", key="gen_thumbtext"):
        prompt = f"Short viral thumbnail text (max 5 words) for: {topic}"
        st.session_state.thumbnail_text = ask_openai(prompt)

# --- Editable fields (manual override) ---
st.subheader("✏️ Edit Your Content (manual entry also works)")
st.session_state.script = st.text_area("Script", st.session_state.script, height=200, key="edit_script")
st.session_state.title = st.text_input("Title", st.session_state.title, key="edit_title")
st.session_state.caption = st.text_area("Caption", st.session_state.caption, height=80, key="edit_caption")
st.session_state.description = st.text_area("Description", st.session_state.description, height=150, key="edit_desc")
st.session_state.hashtags = st.text_input("Hashtags (space separated)", st.session_state.hashtags, key="edit_hashtags")
st.session_state.thumbnail_text = st.text_input("Thumbnail Text", st.session_state.thumbnail_text, key="edit_thumbtext")

# --- AI Suggestions ---
st.subheader("📈 AI Video Strategy Suggestions")
if st.button("Get Suggestions", key="suggest_btn"):
    prompt = f"""Analyze this YouTube video:
    Topic: {topic}
    Script: {st.session_state.script}
    Give: best upload time, CTR tips, thumbnail ideas, SEO tips, retention tricks.
    """
    st.session_state.suggestions = ask_openai(prompt)
st.text_area("Suggestions", st.session_state.suggestions, height=200, key="suggest_out")

# --- Thumbnail Section ---
st.subheader("🖼️ Thumbnail")
thumb_col1, thumb_col2 = st.columns(2)
with thumb_col1:
    if st.button("🎨 Generate AI Thumbnail", key="gen_thumb_img"):
        if st.session_state.thumbnail_text:
            prompt = f"YouTube thumbnail, text '{st.session_state.thumbnail_text}', topic '{topic}', bright, clickbait style."
            img = generate_hf_thumbnail(prompt)
            if img:
                st.session_state.thumbnail_image = img
                st.success("Thumbnail generated")
            else:
                st.error("HF_API_KEY missing or error")
        else:
            st.warning("Enter thumbnail text first")
with thumb_col2:
    uploaded_thumb = st.file_uploader("Or upload existing thumbnail", type=["png","jpg","jpeg"], key="upload_thumb")
    if uploaded_thumb:
        st.session_state.existing_thumbnail = uploaded_thumb

if st.session_state.thumbnail_image:
    st.image(st.session_state.thumbnail_image, width=300)
    buf = BytesIO()
    st.session_state.thumbnail_image.save(buf, format="PNG")
    st.download_button("Download AI Thumbnail", buf.getvalue(), "thumb.png", key="dl_thumb")
if st.session_state.existing_thumbnail:
    st.image(st.session_state.existing_thumbnail, width=300)

# --- Video Generation (Pexels + Voice) ---
st.subheader("🎬 Video Creation")
# Generate video keywords from script
if st.button("🔍 Generate Video Keywords from Script", key="gen_vid_keywords"):
    prompt = f"Extract visual keywords from this script:\n{st.session_state.script}"
    st.session_state.video_keywords = ask_openai(prompt)
st.session_state.video_keywords = st.text_input("Video Keywords (for Pexels search)", st.session_state.video_keywords, key="vid_keywords")

if st.button("📹 Search Pexels Clips", key="search_pexels"):
    if st.session_state.video_keywords:
        st.session_state.pexels_videos = search_pexels_videos(st.session_state.video_keywords)
        if st.session_state.pexels_videos:
            st.success(f"Found {len(st.session_state.pexels_videos)} clips")
        else:
            st.warning("No clips found. Check API key or keywords.")
    else:
        st.warning("Generate or enter video keywords first")

# Show found clips
if st.session_state.pexels_videos:
    st.subheader("Preview Pexels Clips (first 3)")
    for i, vid in enumerate(st.session_state.pexels_videos[:3]):
        try:
            st.video(vid["video_files"][0]["link"])
        except:
            pass

# Voice generation
st.subheader("🎙️ Voiceover")
if st.button("🔊 Generate Voice", key="gen_voice"):
    if st.session_state.script:
        voice_name = get_voice_name(voice_gender)
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        asyncio.run(generate_voice(st.session_state.script, voice_name, temp_path))
        st.session_state.audio_file = temp_path
        st.success("Voice generated")
    else:
        st.warning("No script to speak")

if st.session_state.audio_file:
    st.audio(st.session_state.audio_file)
    with open(st.session_state.audio_file, "rb") as f:
        st.download_button("Download Voice MP3", f, "voice.mp3", key="dl_voice")

# Final video render
st.subheader("🎞️ Render Final Video")
if st.button("🚀 Create Final MP4", key="render_vid"):
    if not st.session_state.pexels_videos:
        st.error("Search Pexels clips first")
    elif not st.session_state.audio_file:
        st.error("Generate voice first")
    else:
        with st.spinner("Rendering video... (may take a minute)"):
            out = create_final_video(duration_sec, quality_opt)
            if out:
                st.session_state.final_video = out
                st.success("Video ready!")
            else:
                st.error("Failed to render video")

if st.session_state.final_video:
    st.video(st.session_state.final_video)
    with open(st.session_state.final_video, "rb") as f:
        st.download_button("Download Final MP4", f, "youtube_video.mp4", key="dl_video")

# --- Upload existing video manually ---
st.subheader("📁 Upload Your Own Video (optional)")
uploaded_video = st.file_uploader("Upload MP4", type=["mp4"], key="upload_video")
if uploaded_video:
    st.session_state.existing_video = uploaded_video
    st.video(uploaded_video)
    st.success("Video ready for upload (you can still generate AI video above)")

# --- YouTube upload placeholder (requires OAuth, not full implementation here) ---
st.subheader("📤 Next Steps")
st.info("""
✅ You can now:
- Download the final MP4
- Use the generated title, description, hashtags
- Upload manually to YouTube

To enable auto-upload, you would need `client_secret.json` and `google-api-python-client`.
""")

st.success("🎉 All features ready. Generate script → edit → create video → download.")