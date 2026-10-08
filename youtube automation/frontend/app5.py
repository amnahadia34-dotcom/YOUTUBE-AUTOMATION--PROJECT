import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="AI Voice Agent Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== ENTERPRISE DARK GLASS STYLING (NO WHITE BACKGROUNDS) ==========
st.markdown("""
<style>
/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0a0f1e, #070b14, #04070f);
    background-attachment: fixed;
}
.main .block-container {
    padding-top: 0.5rem;
    padding-bottom: 2rem;
}
/* Metric Cards */
[data-testid="metric-container"] {
    background: rgba(18, 25, 45, 0.75);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(59, 130, 246, 0.3);
    padding: 15px;
    border-radius: 24px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}
[data-testid="metric-container"] label,
[data-testid="metric-container"] p {
    color: #e2e8ff !important;
}
/* DataFrames */
[data-testid="stDataFrame"] {
    background: rgba(12, 18, 30, 0.85) !important;
    border-radius: 20px;
    padding: 8px;
    border: 1px solid rgba(59, 130, 246, 0.25);
}
[data-testid="stDataFrame"] table {
    background: transparent !important;
    color: #e2e8f0 !important;
}
[data-testid="stDataFrame"] th {
    background: rgba(30, 40, 65, 0.95) !important;
    color: white !important;
}
[data-testid="stDataFrame"] td {
    background: rgba(20, 28, 48, 0.9) !important;
    color: #cbd5e6 !important;
}
/* Success & Info Boxes */
.stSuccess {
    background: rgba(16, 55, 35, 0.85) !important;
    backdrop-filter: blur(8px);
    border-left: 4px solid #10b981 !important;
    border-radius: 16px !important;
    color: #ccf0e6 !important;
}
.stInfo {
    background: rgba(20, 40, 75, 0.85) !important;
    backdrop-filter: blur(8px);
    border-left: 4px solid #3b82f6 !important;
    border-radius: 16px !important;
    color: #bfdbfe !important;
}
/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(6, 10, 20, 0.9) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(72, 187, 255, 0.2);
}
/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #1e3a8a, #4f46e5);
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 600;
    padding: 10px 24px;
    transition: 0.2s;
}
.stButton button:hover {
    background: linear-gradient(90deg, #2563eb, #6366f1);
    transform: scale(1.02);
}
/* Headings & text */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #f0f3ff !important;
    font-weight: 600;
}
p, label, div, span, .stMarkdown {
    color: #e2e8f0 !important;
}
/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
}
/* Voice Waveform Animation */
.waveform {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    height: 60px;
    background: rgba(0,0,0,0.3);
    border-radius: 40px;
    padding: 10px;
    margin: 10px 0;
}
.waveform span {
    width: 6px;
    height: 20px;
    background: #3b82f6;
    border-radius: 3px;
    animation: wave 0.8s ease-in-out infinite;
}
.waveform span:nth-child(2) { animation-delay: 0.1s; height: 35px; background: #4f46e5; }
.waveform span:nth-child(3) { animation-delay: 0.2s; height: 50px; background: #6366f1; }
.waveform span:nth-child(4) { animation-delay: 0.3s; height: 40px; background: #7c3aed; }
.waveform span:nth-child(5) { animation-delay: 0.4s; height: 55px; background: #8b5cf6; }
.waveform span:nth-child(6) { animation-delay: 0.5s; height: 30px; background: #3b82f6; }
.waveform span:nth-child(7) { animation-delay: 0.6s; height: 45px; background: #4f46e5; }
.waveform span:nth-child(8) { animation-delay: 0.7s; height: 25px; background: #6366f1; }
@keyframes wave {
    0%, 100% { transform: scaleY(0.5); }
    50% { transform: scaleY(1.2); }
}
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR (fixed, no st.page_link) ==========
with st.sidebar:
    # Company Logo
    st.markdown("""
    <div style='text-align: center; padding: 20px 0 10px 0;'>
        <div style='background: linear-gradient(135deg, #2563eb, #7c3aed); width: 60px; height: 60px; border-radius: 20px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
            <span style='font-size: 32px;'>🎙️</span>
        </div>
        <h3 style='margin-top: 10px;'>VoxAI</h3>
        <p style='font-size: 12px; opacity: 0.7;'>Enterprise Voice Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📋 Navigation")
    # Using simple markdown for menu (non‑interactive – just for demo look)
    st.markdown("🏠 **Dashboard**  &nbsp;&nbsp;&nbsp; `active`")
    st.markdown("📞 Call History")
    st.markdown("⚙️ Settings")
    st.markdown("📈 Analytics")
    st.divider()
    st.markdown("### ℹ️ System Status")
    st.success("🟢 All Systems Operational")
    st.caption("API Latency: 42ms")
    st.caption("Agents Online: 8/8")
    st.divider()
    st.markdown("### 💾 Demo Mode")
    st.info("Running simulated data")

# ========== TOP HEADER (Metrics + Agent Status) ==========
col_logo, col_title, col_status = st.columns([1, 3, 2])
with col_logo:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2563eb, #7c3aed); width: 50px; height: 50px; border-radius: 15px; display: flex; align-items: center; justify-content: center;'>
        <span style='font-size: 28px;'>🎙️</span>
    </div>
    """, unsafe_allow_html=True)
with col_title:
    st.markdown("""
    <h1 style='margin:0; padding:0; font-size: 2.2rem;'>AI Voice Agent Platform</h1>
    <p style='margin:0; opacity:0.7;'>Real-time conversational AI for enterprise</p>
    """, unsafe_allow_html=True)
with col_status:
    st.markdown("""
    <div style='background: rgba(16,55,35,0.8); border-radius: 30px; padding: 8px 16px; text-align: center; backdrop-filter: blur(8px);'>
        <span style='color: #10b981; font-weight: bold;'>🟢 AGENT ONLINE</span><br>
        <span style='font-size: 12px;'>Call Duration: 00:02:14</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== TOP METRICS ROW ==========
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("📞 Active Calls Today", "147", "+23")
with c2:
    st.metric("📅 Appointments", "54", "+11")
with c3:
    st.metric("💰 Revenue Generated", "$12.4K", "+18%")
with c4:
    st.metric("✨ Success Rate", "94%", "+5%")

st.divider()

# ========== MAIN TWO-COLUMN LAYOUT ==========
left_col, right_col = st.columns([2, 1])

with left_col:
    # Live Call + Waveform + Timer
    st.subheader("📞 Live Customer Call")
    col_call, col_wave = st.columns([1, 1])
    with col_call:
        st.success("● Call Connected")
        st.markdown("**Caller:** John Smith ( +1-555-234-5678 )")
        st.markdown("**Intent:** Insurance Inquiry")
        st.markdown("**Sentiment:** Positive 😊")
    with col_wave:
        # Animated waveform
        st.markdown("""
        <div class="waveform">
            <span></span><span></span><span></span><span></span>
            <span></span><span></span><span></span><span></span>
        </div>
        <p style='text-align:center; font-size:12px;'>🔊 Live audio stream • AI processing</p>
        """, unsafe_allow_html=True)
    
    # AI Agent Avatar + Transcript
    st.subheader("💬 Live Transcript")
    col_avatar, col_transcript = st.columns([1, 4])
    with col_avatar:
        st.markdown("""
        <div style='background: linear-gradient(145deg, #2563eb, #4f46e5); width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: auto;'>
            <span style='font-size: 40px;'>🤖</span>
        </div>
        <p style='text-align:center; margin-top: 8px;'><strong>AI Agent</strong><br>Sophia v3.2</p>
        """, unsafe_allow_html=True)
    with col_transcript:
        st.code("""
Customer: Hello, I need information about your insurance plans.

AI Agent: Of course, I'd be happy to help. May I know your name?

Customer: John Smith. I'm looking for family health coverage.

AI Agent: Thank you, John. Let me pull up the best options for you.

Customer: Can I book an appointment to speak with an agent?

AI Agent: Absolutely. I've scheduled a call for tomorrow at 11 AM.
        """)
    
    # Recent Calls Table
    st.subheader("🕒 Recent Calls")
    recent_calls = pd.DataFrame({
        "Time": ["10:32 AM", "10:15 AM", "09:58 AM", "09:40 AM", "09:22 AM"],
        "Customer": ["John Smith", "Sarah Lee", "Michael Chen", "Lisa Wong", "David Kim"],
        "Duration": ["2:14", "3:22", "1:45", "4:10", "2:55"],
        "Status": ["Completed", "Completed", "Completed", "Completed", "Missed"],
        "Score": [92, 88, 95, 79, 45]
    })
    st.dataframe(recent_calls, use_container_width=True, hide_index=True)

with right_col:
    # Agent Status Panel
    st.subheader("🤖 Agent Status")
    st.success("🟢 Online - Ready")
    st.progress(92, text="Lead Qualification Score")
    st.markdown("**Customer Sentiment:** Positive 😊")
    st.markdown("**Appointment:** Confirmed ✅")
    st.markdown("**CRM Sync:** Saved to HubSpot")
    
    # Current Call Details
    st.subheader("📞 Active Call Details")
    st.info("""
    **Call Duration:** 00:02:14 (live)  
    **Current Customer:** John Smith  
    **Phone:** +1-555-234-5678  
    **Intent:** Insurance Inquiry → Book Appointment  
    **AI Confidence:** 96%  
    """)
    
    # Voice Waveform (another visual)
    st.markdown("#### 🎵 Live Voice Activity")
    st.markdown("""
    <div class="waveform" style="height: 40px;">
        <span></span><span></span><span></span><span></span>
        <span></span><span></span><span></span><span></span>
    </div>
    """, unsafe_allow_html=True)
    
    # Upcoming Appointment
    st.subheader("📅 Next Appointment")
    st.info("""
    **Date:** 20 June 2026  
    **Time:** 11:00 AM  
    **Customer:** John Smith  
    **Type:** Insurance Consultation  
    **Agent:** Sophia (AI)
    """)

st.divider()

# ========== ENHANCED ANALYTICS CHART ==========
st.subheader("📊 Call Analytics (Last 6 Months)")
analytics = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Calls": [120, 180, 240, 320, 410, 530],
    "Appointments": [45, 68, 95, 130, 180, 245],
    "Revenue ($K)": [2.8, 4.2, 6.1, 8.5, 11.2, 14.7]
})
# Use area chart for better visual
st.area_chart(analytics.set_index("Month")[["Calls", "Appointments"]])
st.caption("📈 Steady growth in calls & appointments after AI deployment in March")

# Final status
st.success("✅ AI Voice Agent Platform is fully operational • Real-time call simulation active")