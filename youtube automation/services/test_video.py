import streamlit as st
import os

from config.settings import PEXELS_API_KEY, HF_TOKEN
from voice_service import generate_voice
from video_service import generate_video, generate_visual_keywords

st.sidebar.markdown("### 🔧 Environment Debug")
st.sidebar.write(f"PEXELS_API_KEY loaded: {bool(PEXELS_API_KEY)}")
st.sidebar.write(f"HF_TOKEN loaded: {bool(HF_TOKEN)}")
if not PEXELS_API_KEY:
    st.sidebar.error("PEXELS_API_KEY not found in .env")
if not HF_TOKEN:
    st.sidebar.warning("HF_TOKEN not found in .env (AI video generation disabled)")


st.set_page_config(
    page_title="Video Generator Test",
    layout="wide"
)

st.title("🎬 YouTube Video Generator Test")

script = st.text_area(
    "Enter Script",
    height=250,
    value="""
Tesla changed the electric vehicle industry.
Elon Musk invested heavily in innovation.
Tesla factories expanded worldwide.
The company became one of the most valuable car manufacturers.
"""
)

language = st.selectbox(
    "Voice Language",
    ["English", "Urdu", "Hindi"]
)

if st.button("🚀 Generate Test Video"):

    try:

        with st.spinner("Generating Voice..."):

            voice_path = generate_voice(
                script=script,
                language=language
            )

        st.success("✅ Voice Generated")

        st.write(voice_path)

        visual_keywords = generate_visual_keywords(script)
        st.markdown("**Visual search keywords:**")
        st.write(visual_keywords)

        with st.spinner("Generating Video..."):

            video_path = generate_video(
                script=script,
                narration_path=voice_path
            )

        st.success("✅ Video Generated")

        st.write(video_path)

        if os.path.exists(video_path):

            st.video(video_path)

    except Exception as e:

        st.error(str(e))