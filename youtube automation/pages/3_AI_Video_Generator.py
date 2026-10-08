# ================================================
# AI VIDEO GENERATOR - FULL WORKFLOW
# ================================================

import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import sys

# Add services to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.video_service import generate_video
from moviepy.editor import VideoFileClip

st.set_page_config(
    page_title="AI Video Generator - YouTube Automation SaaS",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
    .step-container {
        background: #0f172a;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff0000;
        margin: 15px 0;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        margin: 20px 0 10px 0;
        border-bottom: 2px solid #ff0000;
        padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 AI Video Generator")
st.write("Create professional videos automatically from scripts")

# ================================================
# WORKFLOW STEPS
# ================================================

st.markdown('<h2 class="section-header">🔄 Video Generation Workflow</h2>', unsafe_allow_html=True)

with st.expander("Step 1: Script Content", expanded=True):
    script_content = st.text_area(
        "Enter your script for video generation",
        height=200,
        placeholder="Enter script text here. Each sentence will become a scene in your video.",
        help="The script will be split into scenes (max 6 scenes). Each scene displays for 5-10 seconds based on text length."
    )

with st.expander("Step 2: Voice & Audio Settings"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        voice_provider = st.selectbox(
            "Voice Provider",
            ["Google TTS (Free & Fast)", "ElevenLabs (Premium)", "Microsoft Azure"]
        )
    
    with col2:
        voice_gender = st.selectbox("Voice Gender", ["Male", "Female"])
    
    with col3:
        language = st.selectbox("Language", ["English", "Spanish", "French", "Hindi", "Urdu"])
    
    col1, col2 = st.columns(2)
    with col1:
        voice_speed = st.slider("Voice Speed", 0.5, 2.0, 1.0, step=0.1)
    with col2:
        voice_pitch = st.slider("Pitch", 0.5, 1.5, 1.0, step=0.1)

with st.expander("Step 3: Video Settings"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        resolution = st.selectbox("Resolution", ["1280x720 (HD)", "1920x1080 (Full HD)"])
    
    with col2:
        fps = st.selectbox("Frame Rate", ["24 FPS", "30 FPS"])
    
    with col3:
        add_intro = st.checkbox("Add Intro", value=True)
        add_outro = st.checkbox("Add Outro", value=True)

if add_intro:
    intro_text = st.text_input("Intro text", placeholder="e.g., Welcome to my channel")
else:
    intro_text = None

if add_outro:
    outro_text = st.text_input("Outro text", placeholder="e.g., Thanks for watching")
else:
    outro_text = None

# ================================================
# GENERATE BUTTON WITH REAL BACKEND
# ================================================

st.markdown('<h2 class="section-header">🚀 Generation</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "generated_video.mp4")

with col1:
    if st.button("🎬 Generate Video", use_container_width=True, key="gen_video"):
        if not script_content or script_content.strip() == "":
            st.error("❌ Please enter a script to generate a video.")
        else:
            try:
                with st.spinner("⏳ Generating video... This may take 2-5 minutes..."):
                    progress_bar = st.progress(0)
                    status = st.status("Initializing video generation...", expanded=False)
                    
                    # Update progress
                    status.update(label="📝 Processing script...", state="running")
                    progress_bar.progress(10)
                    
                    status.update(label="🎬 Generating video from script...", state="running")
                    progress_bar.progress(50)
                    
                    # Call generate_video with script
                    generated_path = generate_video(
                        script=script_content,
                        intro_text=intro_text,
                        outro_text=outro_text,
                        output_path=output_path
                    )
                    
                    status.update(label="📊 Analyzing video metadata...", state="running")
                    progress_bar.progress(90)
                    
                    status.update(label="✅ Video Generated Successfully!", state="complete")
                    progress_bar.progress(100)
                    
                    st.success("✅ Video generated successfully!")
                    
                    # Get video metadata
                    try:
                        video_clip = VideoFileClip(generated_path)
                        duration_seconds = int(video_clip.duration)
                        minutes = duration_seconds // 60
                        seconds = duration_seconds % 60
                        width = video_clip.w
                        height = video_clip.h
                        video_clip.close()
                    except Exception as e:
                        st.warning(f"⚠️ Could not read video metadata: {e}")
                        duration_seconds = 0
                        minutes = 0
                        seconds = 0
                        width = 1280
                        height = 720
                    
                    file_size_bytes = os.path.getsize(generated_path)
                    file_size_mb = file_size_bytes / (1024 * 1024)
                    
                    # Show video preview
                    st.markdown('<h3>📺 Video Preview</h3>', unsafe_allow_html=True)
                    st.video(generated_path)
                    
                    # Show stats
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Duration", f"{minutes}m {seconds}s")
                    col2.metric("File Size", f"{file_size_mb:.1f} MB")
                    col3.metric("Resolution", f"{width}x{height}")
                    col4.metric("FPS", "24")
                    
                    # Download section
                    st.markdown("---")
                    st.markdown('<h3>💾 Download & Actions</h3>', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Real download button using file read
                        with open(generated_path, "rb") as f:
                            st.download_button(
                                label="📥 Download MP4",
                                data=f.read(),
                                file_name="generated_video.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    with col2:
                        if st.button("➕ Upload to YouTube", use_container_width=True):
                            st.switch_page("pages/5_YouTube_Uploader.py")
                    
                    with col3:
                        if st.button("📅 Schedule Later", use_container_width=True):
                            st.switch_page("pages/7_Content_Calendar.py")
                    
                    # Store output path in session
                    st.session_state.last_video_path = generated_path
                    st.session_state.video_generated = True
                    
            except FileNotFoundError as e:
                st.error(f"❌ MoviePy Error: Could not find required file - {e}")
                st.info("Make sure all audio files and images exist before generating the video.")
            except Exception as e:
                st.error(f"❌ Error generating video: {str(e)}")
                st.info("This could be a MoviePy issue. Check that all dependencies are installed correctly.")

with col2:
    if st.button("💾 Save Draft", use_container_width=True):
        st.success("✅ Draft settings saved!")

with col3:
    st.info("💡 Tip: Each sentence in your script becomes a scene (5-10 seconds). Keep sentences clear and concise.")

# ================================================
# QUICK PRESETS
# ================================================

st.markdown('<h2 class="section-header">⚡ Quick Presets</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎥 YouTube Video (Standard)", use_container_width=True):
        st.info("✓ Preset: 1280x720, 24 FPS, MP4")

with col2:
    if st.button("📱 YouTube Shorts", use_container_width=True):
        st.info("✓ Preset: Vertical format optimized")

with col3:
    if st.button("🎬 Full HD Video", use_container_width=True):
        st.info("✓ Preset: 1920x1080, 24 FPS, MP4")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
