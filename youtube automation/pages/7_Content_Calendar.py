# ================================================
# CONTENT CALENDAR - SCHEDULING & PLANNING
# ================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(
    page_title="Content Calendar - YouTube Automation SaaS",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
<style>
    .calendar-event {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #ff0000;
        margin: 5px 0;
        font-size: 12px;
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

st.title("📅 Content Calendar")
st.write("Plan and schedule your YouTube content")

# ================================================
# TABS
# ================================================

tab1, tab2, tab3 = st.tabs(["Calendar View", "Upcoming Schedule", "Create Event"])

# ================================================
# TAB 1: CALENDAR VIEW
# ================================================

with tab1:
    st.markdown('<h2 class="section-header">📅 Month View</h2>', unsafe_have_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Previous"):
            st.info("Showing previous month")
    
    with col2:
        current_month = st.selectbox("Select Month", 
            ["January 2024", "February 2024", "March 2024", "April 2024"],
            index=1)
    
    with col3:
        if st.button("Next →"):
            st.info("Showing next month")
    
    # Calendar grid
    st.markdown("""
    <table style="width:100%; border-collapse: collapse;">
        <tr style="background: #1e1e2e;">
            <th style="padding: 10px; border: 1px solid #333;">Sun</th>
            <th style="padding: 10px; border: 1px solid #333;">Mon</th>
            <th style="padding: 10px; border: 1px solid #333;">Tue</th>
            <th style="padding: 10px; border: 1px solid #333;">Wed</th>
            <th style="padding: 10px; border: 1px solid #333;">Thu</th>
            <th style="padding: 10px; border: 1px solid #333;">Fri</th>
            <th style="padding: 10px; border: 1px solid #333;">Sat</th>
        </tr>
        <tr>
            <td style="padding: 20px; border: 1px solid #333; background: #0f172a; height: 100px; vertical-align: top;">
                <small style="color: #888;">31</small>
            </td>
            <td style="padding: 20px; border: 1px solid #333; background: #0f172a; height: 100px; vertical-align: top;">
                <strong>1</strong><br><span style="font-size: 11px; color: #ff0000;">🎬 AI Tools</span>
            </td>
            <td style="padding: 20px; border: 1px solid #333; background: #0f172a; height: 100px; vertical-align: top;">
                <strong>2</strong>
            </td>
            <td style="padding: 20px; border: 1px solid #333; background: #0f172a; height: 100px; vertical-align: top;">
                <strong>3</strong><br><span style="font-size: 11px; color: #10b981;">📺 Shorts</span>
            </td>
            <td style="padding: 20px; border: 1px solid #333; background: #0f172a; height: 100px; vertical-align: top;">
                <strong>4</strong>
            </td>
            <td style="padding: 20px; border: 1px solid #333; background: #0f172a; height: 100px; vertical-align: top;">
                <strong>5</strong><br><span style="font-size: 11px; color: #ff0000;">🎬 Python Tut</span>
            </td>
            <td style="padding: 20px; border: 1px solid #333; background: #0f172a; height: 100px; vertical-align: top;">
                <strong>6</strong>
            </td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

# ================================================
# TAB 2: UPCOMING SCHEDULE
# ================================================

with tab2:
    st.markdown('<h2 class="section-header">📋 Upcoming Publications</h2>', unsafe_have_html=True)
    
    schedule_data = {
        "Date & Time": [
            "Feb 15, 2024 - 3:00 PM",
            "Feb 18, 2024 - 10:00 AM",
            "Feb 20, 2024 - 5:00 PM",
            "Feb 22, 2024 - 12:00 PM",
            "Feb 25, 2024 - 7:00 PM"
        ],
        "Video Title": [
            "10 AI Tools That Will Change Your Life",
            "Python Tutorial for Beginners",
            "Blockchain Explained (Simplified)",
            "Web Development Roadmap 2024",
            "AI Trends That Matter"
        ],
        "Content Type": ["Long-form", "Long-form", "Long-form", "Shorts", "Long-form"],
        "Status": ["📅 Scheduled", "📅 Scheduled", "⏳ Processing", "📅 Scheduled", "✏️ Draft"],
        "Actions": ["Edit", "Edit", "Edit", "Edit", "Edit"]
    }
    
    df_schedule = pd.DataFrame(schedule_data)
    
    for idx, row in df_schedule.iterrows():
        with st.expander(f"📺 {row['Video Title']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Schedule:** {row['Date & Time']}")
                st.write(f"**Type:** {row['Content Type']}")
                st.write(f"**Status:** {row['Status']}")
            
            with col2:
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✏️ Edit", key=f"edit_{idx}"):
                        st.info("Edit mode for this video")
                with col_b:
                    if st.button("❌ Cancel", key=f"cancel_{idx}"):
                        st.warning(f"Cancelled: {row['Video Title']}")

# ================================================
# TAB 3: CREATE EVENT
# ================================================

with tab3:
    st.markdown('<h2 class="section-header">➕ Schedule New Content</h2>', unsafe_have_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Event Details")
        
        event_title = st.text_input(
            "Video Title",
            placeholder="Enter video title",
            help="The video you want to schedule"
        )
        
        event_type = st.selectbox(
            "Content Type",
            ["Long-form Video", "Shorts", "Premiere", "Live Stream"]
        )
        
        description = st.text_area(
            "Description",
            placeholder="Add description...",
            height=100
        )
    
    with col2:
        st.subheader("Schedule")
        
        schedule_date = st.date_input("Publish Date")
        schedule_time = st.time_input("Publish Time")
        
        video_source = st.selectbox(
            "Video Source",
            ["Select from generated videos", "Upload new video", "Link existing video"]
        )
        
        privacy = st.selectbox(
            "Privacy",
            ["Public", "Unlisted", "Private"]
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Notification Options")
        st.checkbox("Notify Subscribers", value=True)
        st.checkbox("Email Reminder", value=True)
        st.checkbox("Add to Playlist", value=False)
    
    with col2:
        st.subheader("Advanced Options")
        st.checkbox("Add to Featured Content", value=False)
        st.checkbox("Monetization Enabled", value=True)
        st.checkbox("Allow Embedding", value=True)
    
    # Schedule button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📅 Schedule Video", use_container_width=True):
            if not event_title:
                st.error("❌ Please enter a video title")
            else:
                st.success(f"✅ '{event_title}' scheduled for {schedule_date} at {schedule_time}")
    
    with col2:
        if st.button("💾 Save Draft", use_container_width=True):
            st.success("✅ Draft saved")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
