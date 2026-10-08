# ================================================
# YOUTUBE UPLOADER - VIDEO UPLOAD & MANAGEMENT
# ================================================

from streamlit import page_link
import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="YouTube Uploader - YouTube Automation SaaS",
    page_icon="📤",
    layout="wide"
)

st.markdown("""
<style>
    .upload-box {
        background: #0f172a;
        padding: 20px;
        border: 2px dashed #ff0000;
        border-radius: 10px;
        text-align: center;
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

st.title("📤 YouTube Uploader")
st.write("Upload and manage your videos on YouTube")

# ================================================
# TABS
# ================================================

tab1, tab2, tab3 = st.tabs(["Upload Video", "Scheduled Uploads", "Upload History"])

# ================================================
# TAB 1: UPLOAD VIDEO
# ================================================

with tab1:
    st.markdown('<h2 class="section-header">🎬 Upload New Video</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Step 1: Video File")
        
        video_file = st.file_uploader(
            "Choose video file (MP4, WebM, MOV)",
            type=["mp4", "webm", "mov"],
            help="Upload your generated or existing video"
        )
        
        if video_file:
            st.success(f"✅ File selected: {video_file.name}")
            st.write(f"File size: {video_file.size / (1024*1024):.2f} MB")
    
    with col2:
        st.subheader("Step 2: Thumbnail")
        
        thumbnail_file = st.file_uploader(
            "Choose thumbnail (JPG, PNG)",
            type=["jpg", "jpeg", "png"],
            help="Custom thumbnail (1280x720 recommended)"
        )
        
        if thumbnail_file:
            st.success(f"✅ Thumbnail selected: {thumbnail_file.name}")
    
    st.markdown('<h2 class="section-header">📝 Video Information</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input(
            "Video Title *",
            placeholder="e.g., 10 AI Tools That Will Change Your Life",
            max_chars=100,
            help="Max 100 characters"
        )
        
        description = st.text_area(
            "Description *",
            placeholder="Enter video description with timestamps and links...",
            height=150,
            max_chars=5000,
            help="Max 5000 characters"
        )
    
    with col2:
        tags_input = st.text_area(
            "Tags (comma-separated)",
            placeholder="AI, tools, productivity, automation...",
            height=100,
            help="Max 30 tags"
        )
        
        category = st.selectbox(
            "Category *",
            [
                "Film & Animation",
                "Autos & Vehicles",
                "Music",
                "Pets & Animals",
                "Sports",
                "Shortfilms",
                "Travel & Events",
                "Gaming",
                "Videoblogging",
                "People & Blogs",
                "Comedy",
                "Entertainment",
                "News & Politics",
                "Howto & Style",
                "Education",
                "Science & Technology",
                "Nonprofits & Activism"
            ],
            index=15  # Science & Technology
        )
    
    st.markdown('<h2 class="section-header">⚙️ Publishing Settings</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        privacy = st.selectbox(
            "Privacy Status *",
            ["Public", "Unlisted", "Private"],
            help="Who can see this video?"
        )
        
        upload_channel = st.selectbox(
            "Upload to Channel",
            ["My Main Channel", "Secondary Channel"],
            help="Which channel to upload to?"
        )
    
    with col2:
        st.subheader("Publishing Options")
        
        publish_now = st.radio(
            "When to publish?",
            ["Publish Immediately", "Schedule for Later"]
        )
        
        if publish_now == "Schedule for Later":
            publish_date = st.date_input("Publish Date")
            publish_time = st.time_input("Publish Time")
    
    st.markdown("---")
    
    st.subheader("Additional Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        enable_comments = st.checkbox("Enable Comments", value=True)
        enable_ratings = st.checkbox("Enable Ratings", value=True)
    
    with col2:
        allow_embedding = st.checkbox("Allow Embedding", value=True)
        record_stats = st.checkbox("Record Statistics", value=True)
    
    with col3:
        st.checkbox("Notify Subscribers", value=True)
        st.checkbox("Add to Playlist", value=False)
    
    # Upload button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📤 Upload to YouTube", use_container_width=True):
            if not video_file or not title:
                st.error("❌ Please select a video file and enter a title")
            else:
                with st.spinner("📤 Uploading to YouTube... This may take several minutes..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(100):
                        import time
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    st.success("✅ Video uploaded successfully!")
                    
                    st.markdown("---")
                    st.markdown('<h3>🎉 Upload Complete</h3>', unsafe_allow_html=True)
                    
                    video_id = "dQw4w9WgXcQ"  # Example
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"""
                        **Video ID:** `{video_id}`
                        
                        **URL:** https://youtube.com/watch?v={video_id}
                        """)
                    
                    with col2:
                        st.success(f"""
                        **Status:** Published
                        
                        **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        """)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button(
                            "👁️ View on YouTube",
                            f"https://youtube.com/watch?v={video_id}",
                            use_container_width=True
                        )
                    with col2:
                        if st.button("➕ Create Another Video", use_container_width=True):
                            st.rerun()
    
    with col2:
        if st.button("💾 Save as Draft", use_container_width=True):
            st.success("✅ Saved as draft")

# ================================================
# TAB 2: SCHEDULED UPLOADS
# ================================================

with tab2:
    st.markdown('<h2 class="section-header">📅 Scheduled Uploads</h2>', unsafe_have_html=True)
    
    scheduled_data = {
        "Video": ["AI Tools Guide", "Python Tutorial Pt. 2", "Crypto News"],
        "Scheduled Date": ["2024-02-15 3:00 PM", "2024-02-18 10:00 AM", "2024-02-20 5:00 PM"],
        "Status": ["⏳ Queued", "⏳ Queued", "📅 Scheduled"],
        "Privacy": ["Public", "Public", "Unlisted"]
    }
    
    df_scheduled = pd.DataFrame(scheduled_data)
    st.dataframe(df_scheduled, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✏️ Edit Scheduled Upload"):
            st.info("Select a scheduled upload to edit")
    
    with col2:
        if st.button("❌ Cancel Upload"):
            st.warning("Upload cancelled")

# ================================================
# TAB 3: UPLOAD HISTORY
# ================================================

with tab3:
    st.markdown('<h2 class="section-header">📋 Upload History</h2>', unsafe_allow_html=True)
    
    history_data = {
        "Video Title": ["10 AI Tools", "Python Tutorial", "Web Dev Tips", "Blockchain 101", "AI Explained"],
        "Upload Date": ["2024-02-10", "2024-02-08", "2024-02-05", "2024-02-01", "2024-01-28"],
        "Views": [2457, 1823, 892, 3421, 1203],
        "Likes": [123, 95, 42, 178, 67],
        "Status": ["✅ Published", "✅ Published", "✅ Published", "✅ Published", "✅ Published"]
    }
    
    df_history = pd.DataFrame(history_data)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Uploads", 247, "+12 this month")
    
    with col2:
        st.metric("Average Views", "1,959", "+234")
    
    with col3:
        st.metric("Average Engagement", "4.2%", "+0.3%")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
