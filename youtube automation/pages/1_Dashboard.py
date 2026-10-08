# ================================================
# DASHBOARD - PREMIUM UI/UX REDESIGN (UI ONLY)
# ================================================

import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
from config.settings import OPENAI_API_KEY, YOUTUBE_API_KEY, PEXELS_API_KEY, HF_TOKEN


# ================================================
# PAGE CONFIG
# ================================================

st.set_page_config(
    page_title="Enterprise AI Platform - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ================================================
# HELPERS (unchanged logic)
# ================================================

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SCRIPT_EXTENSIONS = {".txt", ".md"}


def count_files(paths, suffixes):
    total = 0
    for path in paths:
        directory = Path(path)
        if directory.exists():
            total += sum(1 for item in directory.rglob("*") if item.is_file() and item.suffix.lower() in suffixes)
    return total


def find_latest_files(paths, suffixes, limit=5):
    files = []
    for path in paths:
        root = Path(path)
        if root.exists():
            for item in root.rglob("*"):
                if item.is_file() and item.suffix.lower() in suffixes:
                    files.append(item)
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return files[:limit]


def find_latest_scripts(paths, suffixes, limit=5):
    scripts = []
    for path in paths:
        root = Path(path)
        if root.exists():
            for item in root.rglob("*"):
                if item.is_file() and item.suffix.lower() in suffixes and "script" in item.name.lower():
                    scripts.append(item)
    scripts.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return scripts[:limit]


def format_time(file_path):
    return datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def api_status(name, connected):
    status = "Connected" if connected else "Not Connected"
    color = "#10b981" if connected else "#f87171"
    return f"<div class='status-chip'><span class='status-name'>{name}</span><span class='status-value' style='color:{color};'> {status}</span></div>"


# ================================================
# PATHS AND METRICS (unchanged logic)
# ================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIDEO_PATHS = [PROJECT_ROOT / "renders", PROJECT_ROOT / "outputs" / "videos"]
SHORTS_PATHS = [PROJECT_ROOT / "shorts", PROJECT_ROOT / "outputs" / "shorts"]
THUMBNAIL_PATHS = [PROJECT_ROOT / "thumbnails", PROJECT_ROOT / "outputs" / "thumbnails"]
SCRIPT_PATHS = [PROJECT_ROOT / "outputs" / "scripts", PROJECT_ROOT / "scripts"]
UPLOAD_PATHS = [PROJECT_ROOT / "uploads"]

TOTAL_VIDEOS = count_files(VIDEO_PATHS, VIDEO_EXTENSIONS)
TOTAL_SHORTS = count_files(SHORTS_PATHS, VIDEO_EXTENSIONS)
TOTAL_THUMBNAILS = count_files(THUMBNAIL_PATHS, IMAGE_EXTENSIONS)
TOTAL_SCRIPTS = len(find_latest_scripts(SCRIPT_PATHS, SCRIPT_EXTENSIONS, limit=100))
TOTAL_UPLOADS = count_files(UPLOAD_PATHS, VIDEO_EXTENSIONS | IMAGE_EXTENSIONS | SCRIPT_EXTENSIONS)

LATEST_VIDEOS = find_latest_files(VIDEO_PATHS, VIDEO_EXTENSIONS, limit=5)
LATEST_THUMBNAILS = find_latest_files(THUMBNAIL_PATHS, IMAGE_EXTENSIONS, limit=1)
LATEST_SCRIPTS = find_latest_scripts(SCRIPT_PATHS, SCRIPT_EXTENSIONS, limit=5)

AI_STATUS = {
    "OpenAI": bool(OPENAI_API_KEY),
    "Pexels": bool(PEXELS_API_KEY),
    "Hugging Face": bool(HF_TOKEN),
    "YouTube API": bool(YOUTUBE_API_KEY),
}


# ================================================
# PREMIUM CSS / UI
# ================================================

st.markdown(
    """
    <style>
        :root { color-scheme: dark; }

        /* Page background and depth */
        .reportview-container, .main, .block-container {
            background-color: #050405 !important;
            color: #f6f7fb !important;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
        }

        .glass { background: #070608; border:1px solid rgba(255,45,90,0.18); border-radius:18px; }

        /* Sidebar styling */
        .css-1d391kg, .css-18e3th9 { background: transparent !important; }
        .stSidebar { background: #080608 !important; border-right: 1px solid rgba(255,45,90,0.16); }
        .sidebar-brand { padding:24px; border-radius:18px; margin-bottom:20px; background: #0d0a0f; border:1px solid rgba(255,45,90,0.22); }
        .sidebar-brand h2 { color:#fff; font-size:20px; margin:0; }
        .sidebar-brand p { color:#b1b7c4; margin:4px 0 0; font-size:13px; }
        .sidebar-brand .brand-tag { margin-top:14px; display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; background: rgba(255,45,90,0.16); border:1px solid rgba(255,45,90,0.28); color:#ffccd8; font-size:12px; }

        .stSidebar .stButton>button {
            width:100%; text-align:left; padding:14px 16px !important; border-radius:14px !important; border:1px solid rgba(255,255,255,0.06) !important;
            background: #0c0a0f !important; color:#f8f9fc !important; font-weight:700 !important; margin-bottom:10px !important;
        }
        .stSidebar .stButton>button:hover {
            background: rgba(255,45,90,0.12) !important; border-color: rgba(255,45,90,0.28) !important;
        }

        .hero { display:flex; gap:20px; align-items:center; padding:30px; border-radius:20px; background: #0c090f; border:1px solid rgba(255,45,90,0.18); }
        .hero-left { flex:1; }
        .hero-badge { font-size:12px; margin-bottom:12px; }
        .accent-pill { display:inline-flex; align-items:center; gap:6px; padding:9px 14px; border-radius:999px; background: rgba(255,45,90,0.16); color:#ffcad6; font-size:12px; font-weight:700; text-transform:uppercase; border:1px solid rgba(255,45,90,0.28); }
        .sidebar-item { padding:14px 16px; border-radius:14px; margin-bottom:10px; color:#f5f8ff; background: #0c090f; border:1px solid rgba(255,255,255,0.05); font-weight:700; }
        .sidebar-item.active { background: rgba(255,45,90,0.18); border-color: rgba(255,45,90,0.3); color:#fff; }
        .hero-title { font-size:40px; font-weight:900; margin:0; color:#ffffff; }
        .hero-sub { color:#c4c8d6; margin-top:12px; font-size:15px; line-height:1.6; }
        .hero-meta { display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-top:14px; }
        .hero-pill { padding:10px 16px; border-radius:999px; border:1px solid rgba(255,45,90,0.18); background: rgba(255,45,90,0.08); color:#e2e7f0; font-size:12px; }

        .hero-accent { width:220px; min-width:220px; border-radius:20px; padding:20px; background: #100b11; border:1px solid rgba(255,45,90,0.18); }
        .hero-accent-inner { width:100%; height:100%; display:flex; align-items:center; justify-content:center; }
        .hero-mic { width:72px; height:94px; background: #160b14; border-radius:42px; position:relative; box-shadow: inset 0 0 18px rgba(255,45,90,0.12); }
        .hero-mic::before { content:''; position:absolute; left:50%; top:8px; transform:translateX(-50%); width:44px; height:58px; border-radius:24px; background: #0b070c; }
        .hero-mic::after { content:''; position:absolute; left:50%; bottom:-14px; transform:translateX(-50%); width:20px; height:28px; border-radius:14px; background: #0d0810; }
        .hero-mic-strip { position:absolute; left:50%; top:32px; transform:translateX(-50%); width:24px; height:34px; border-radius:12px; background: linear-gradient(180deg, rgba(255,45,90,0.16), rgba(255,45,90,0.06)); }

        .kpi { flex:1; padding:24px; border-radius:18px; background: rgba(255,255,255,0.02); border:1px solid rgba(255,0,40,0.08); box-shadow: 0 18px 40px rgba(0,0,0,0.35); }
        .kpi:hover { transform:translateY(-4px); }
        .kpi .label { color:#9ba6bf; font-size:12px; text-transform:uppercase; letter-spacing:1px; }
        .kpi .value { font-size:40px; font-weight:900; color:#fff; margin-top:12px; }
        .kpi .meta { color:#a5b0c6; margin-top:12px; font-size:13px; }

        .project-card { padding:20px; border-radius:18px; background: rgba(255,255,255,0.02); border:1px solid rgba(255,0,40,0.08); box-shadow: 0 20px 60px rgba(0,0,0,0.35); }
        .project-heading { color:#ffffff; font-weight:800; margin-bottom:8px; }
        .project-meta { color:#9fa8bc; font-size:13px; }

        .preview-card { padding:20px; border-radius:18px; background: rgba(255,255,255,0.02); border:1px solid rgba(255,0,40,0.08); box-shadow: 0 20px 60px rgba(0,0,0,0.28); }

        .status-chip { display:flex; justify-content:space-between; align-items:center; padding:16px 14px; border-radius:16px; background: rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.03); }
        .status-chip div { display:flex; align-items:center; gap:10px; }
        .status-value { font-weight:800; }

        .footer { padding:18px; border-radius:16px; color:#9fb0c8; font-size:13px; display:flex; justify-content:space-between; align-items:center; background: rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); }

        @media (max-width: 1024px) { .hero { flex-direction:column; align-items:start; } .hero-accent { width:100%; min-width:auto; } }
        @media (max-width: 820px) { .stSidebar .stButton>button { text-align:left; padding:12px 14px !important; } }
    </style>
    <div class="app-noise"></div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(f"""
        <div class='glass sidebar-brand'>
            <div style='display:flex;flex-direction:column;'>
                <div style='display:flex;align-items:center;gap:10px;'>
                    <div style='width:46px;height:46px;border-radius:10px;background:linear-gradient(135deg,#ff2d55,#e11d48);display:flex;align-items:center;justify-content:center;font-weight:900;color:white;'>AI</div>
                    <div>
                        <div class='brand-title'>TubeAI Enterprise</div>
                        <div class='brand-sub'>YouTube Automation Operating System</div>
                    </div>
                </div>
                <div style='margin-top:10px;'><span class='accent-pill'>🚀 ENTERPRISE</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-item active'>📊 Dashboard</div>", unsafe_allow_html=True)
    if st.button("🖼️ Thumbnail Studio", key="nav_thumbnail"):
        st.switch_page("4_Thumbnail_Studio")
    if st.button("🔥 Topic Intelligence", key="nav_trending"):
        st.switch_page("pages/8_Trending_Research.py")
    if st.button("🎞️ Shorts Generator", key="nav_shorts"):
        st.switch_page("3_AI_Video_Generator")
    if st.button("📤 YouTube Uploader", key="nav_upload"):
        st.switch_page("5_YouTube_Uploader")
    if st.button("📅 Content Calendar", key="nav_calendar"):
        st.switch_page("pages/7_Content_Calendar.py")

    st.markdown("---")
    st.markdown("### AI Connectivity")
    for name, connected in AI_STATUS.items():
        st.markdown(api_status(name, connected), unsafe_allow_html=True)


# ================================================
# HERO / HEADER (replaces simple title)
# ================================================

st.markdown(
    """
    <div class='glass hero'>
        <div class='hero-left'>
            <div class='hero-badge'>
                <span class='accent-pill'>🚀 ENTERPRISE AI PLATFORM</span>
            </div>
            <h1 class='hero-title'>YouTube Automation Operating System</h1>
            <div class='hero-sub'>Black and cherry red theme with clean website-style dashboard experience, optimized for creators and teams.</div>
            <div class='hero-meta'>
                <div class='hero-pill'>Cherry red accents</div>
                <div class='hero-pill'>Minimal dark layout</div>
            </div>
        </div>
        <div class='hero-accent'>
            <div class='hero-accent-inner'>
                <div class='hero-mic'><div class='hero-mic-strip'></div></div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Top action buttons for dashboard flow
top_actions = st.columns([1,1,1,1], gap='large')
with top_actions[0]:
    if st.button("Generate Video", key="top_generate_video"):
        st.switch_page("3_AI_Video_Generator")
with top_actions[1]:
    if st.button("Create Thumbnail", key="top_create_thumbnail"):
        st.switch_page("4_Thumbnail_Studio")
with top_actions[2]:
    if st.button("Upload to YouTube", key="top_upload"):
        st.switch_page("5_YouTube_Uploader")
with top_actions[3]:
    if st.button("View Trends", key="top_trends"):
        st.switch_page("pages/8_Trending_Research.py")


# ================================================
# KPI CARDS (same metrics, redesigned)
# ================================================

kpis = [
    ("Total Videos", TOTAL_VIDEOS, "renders, outputs/videos"),
    ("Total Shorts", TOTAL_SHORTS, "shorts, outputs/shorts"),
    ("Total Thumbnails", TOTAL_THUMBNAILS, "thumbnails, outputs/thumbnails"),
    ("Total Scripts", TOTAL_SCRIPTS, "outputs/scripts"),
    ("Total Uploads", TOTAL_UPLOADS, "uploads"),
]

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
cols = st.columns(len(kpis), gap="large")
for column, (label, value, subtitle) in zip(cols, kpis):
    with column:
        st.markdown(
            f"""
            <div class='kpi glass' style='border-left:4px solid rgba(255,0,40,0.12)'>
                <div class='label'>{label}</div>
                <div class='value'>{value}</div>
                <div class='meta'>Source: {subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ================================================
# MAIN PANELS (preserve all functionality)
# ================================================

main_left, main_right = st.columns([3, 2], gap="large")

with main_left:
    st.markdown("<div style='margin-top:8px; margin-bottom:10px;'><h2 style='margin:0;color:#fff'>Recent Projects</h2></div>", unsafe_allow_html=True)
    if LATEST_VIDEOS:
        recent_data = [
            {
                "Project": video.name,
                "Category": "Video",
                "Updated": format_time(video),
                "Location": str(video.parent.name),
            }
            for video in LATEST_VIDEOS
        ]
        st.markdown("<div class='project-card glass'>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(recent_data), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='project-card'><div class='project-heading'>No recent generated videos found.</div><div class='project-meta'>Generate a new video or add files to renders/outputs/videos to populate this section.</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:18px;'><h3 style='margin:0;color:#fff'>AI Status Panel</h3></div>", unsafe_allow_html=True)
    status_cols = st.columns(2)
    idx = 0
    for name, connected in AI_STATUS.items():
        with status_cols[idx % 2]:
            st.markdown(f"<div class='status-chip glass'><div style='display:flex;align-items:center;gap:12px;'><div style='width:12px;height:12px;border-radius:50%;background:{'#10b981' if connected else '#ff6b6b'}'></div><div style='font-weight:700;color:#e6eef8'>{name}</div></div><div style='font-weight:800;color:{'#10b981' if connected else '#f87171'}'>{'Connected' if connected else 'Not Connected'}</div></div>", unsafe_allow_html=True)
        idx += 1

    st.markdown("<div style='margin-top:18px;'><h3 style='margin:0;color:#fff'>Quick Actions</h3></div>", unsafe_allow_html=True)
    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("Generate Video", key="qa_video"):
            st.switch_page("3_AI_Video_Generator")
    with action_cols[1]:
        if st.button("Generate Shorts", key="qa_shorts"):
            st.switch_page("3_AI_Video_Generator")
    with action_cols[0]:
        if st.button("Create Thumbnail", key="qa_thumbnail"):
            st.switch_page("4_Thumbnail_Studio")
    with action_cols[1]:
        if st.button("Upload Video", key="qa_upload"):
            st.switch_page("5_YouTube_Uploader")

with main_right:
    st.markdown("<div style='margin-bottom:8px;'><h3 style='margin:0;color:#fff'>Latest Thumbnail Preview</h3></div>", unsafe_allow_html=True)
    if LATEST_THUMBNAILS:
        st.markdown("<div class='preview-card glass'>", unsafe_allow_html=True)
        st.image(str(LATEST_THUMBNAILS[0]), caption="Latest generated thumbnail preview", use_column_width=True)
        st.markdown(
            f"<div style='margin-top:10px; font-weight:800; color:#fff'>{LATEST_THUMBNAILS[0].stem}</div><div style='color:#9aa7b8; font-size:13px'>Updated {format_time(LATEST_THUMBNAILS[0])}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='glass project-card'><div class='project-heading'>Thumbnail preview unavailable</div><div class='project-meta'>No thumbnail files were detected in thumbnails/outputs/thumbnails.</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:18px;'><h3 style='margin:0;color:#fff'>Notes</h3></div>", unsafe_allow_html=True)
    st.info(
        "Your dashboard metrics are dynamically calculated from your project folders. Add content to renders, shorts, thumbnails, uploads, or outputs/scripts to update counts automatically."
    )


# ================================================
# FOOTER (premium)
# ================================================

st.markdown("---")
st.markdown(
    f"<div class='glass footer'><div>© {datetime.now().year} TubeAI Enterprise — Built for creators and teams</div><div style='color:#9aa7b8'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div></div>",
    unsafe_allow_html=True,
)
