# ================================================
# ANALYTICS - DETAILED PERFORMANCE METRICS
# ================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Analytics - YouTube Automation SaaS",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background: #0f172a;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff0000;
        margin: 10px 0;
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

st.title("📊 Analytics")
st.write("Detailed performance metrics and insights")

# ================================================
# FILTERS
# ================================================

st.markdown('<h2 class="section-header">🔍 Filters</h2>', unsafe_have_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    date_range = st.selectbox("Time Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])

with col2:
    video_filter = st.selectbox("Video Type", ["All Videos", "Long-form", "Shorts", "Hybrid"])

with col3:
    metric_filter = st.selectbox("Metric", ["Views", "Engagement", "Revenue", "Watch Time"])

with col4:
    sort_by = st.selectbox("Sort By", ["Views", "Engagement Rate", "Date", "Watch Time"])

# ================================================
# TOP METRICS
# ================================================

st.markdown('<h2 class="section-header">📈 Key Metrics</h2>', unsafe_have_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Views", "42,859", "+18%", delta_color="off")

with col2:
    st.metric("Total Watch Time", "1,247 hours", "+32%", delta_color="off")

with col3:
    st.metric("Engagement Rate", "4.8%", "+0.6%", delta_color="off")

with col4:
    st.metric("Subscriber Growth", "+247", "+89", delta_color="off")

# ================================================
# VIDEO PERFORMANCE TABLE
# ================================================

st.markdown('<h2 class="section-header">🎬 Video Performance</h2>', unsafe_have_html=True)

video_data = {
    "Video Title": [
        "10 AI Tools That Changed My Life",
        "Python Tutorial for Beginners",
        "Blockchain Explained",
        "Web Development Roadmap",
        "AI Trends 2024"
    ],
    "Views": [4287, 2156, 3421, 1892, 5634],
    "Watch Time": ["143 hrs", "89 hrs", "127 hrs", "72 hrs", "198 hrs"],
    "Avg Duration": ["4:32", "8:15", "6:48", "5:23", "7:12"],
    "Engagement": ["5.2%", "3.8%", "4.9%", "3.2%", "6.1%"],
    "Likes": [234, 98, 178, 71, 289],
    "Comments": [45, 23, 38, 12, 67]
}

df_videos = pd.DataFrame(video_data)
st.dataframe(df_videos, use_container_width=True, hide_index=True)

# ================================================
# CHARTS
# ================================================

st.markdown('<h2 class="section-header">📉 Performance Charts</h2>', unsafe_have_html=True)

tab1, tab2, tab3 = st.tabs(["Views Trend", "Engagement", "Watch Time"])

with tab1:
    dates = pd.date_range(start='2024-01-01', periods=30)
    views = [100 + i * 70 + (i % 7) * 40 for i in range(30)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=views,
        mode='lines+markers',
        name='Daily Views',
        line=dict(color='#ff0000', width=2)
    ))
    
    fig.update_layout(
        title="Views Trend (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Views",
        hovermode='x unified',
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(color='#ffffff'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    engagement_data = {
        "Metric": ["Likes", "Comments", "Shares", "Subscribers"],
        "Count": [1247, 342, 187, 89]
    }
    
    df_eng = pd.DataFrame(engagement_data)
    
    fig = px.bar(
        df_eng,
        x="Metric",
        y="Count",
        color="Metric",
        color_discrete_sequence=['#ff0000', '#ff6b6b', '#ff3333', '#ff9999']
    )
    
    fig.update_layout(
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(color='#ffffff'),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = go.Figure(data=[
        go.Pie(
            labels=['Video 1', 'Video 2', 'Video 3', 'Video 4', 'Video 5'],
            values=[629, 312, 289, 178, 156],
            marker=dict(colors=['#ff0000', '#ff6b6b', '#ff3333', '#ff9999', '#ffcccc'])
        )
    ])
    
    fig.update_layout(
        title="Watch Time Distribution by Video",
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(color='#ffffff'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ================================================
# AUDIENCE INSIGHTS
# ================================================

st.markdown('<h2 class="section-header">👥 Audience Insights</h2>', unsafe_have_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Audience Regions")
    
    regions = {
        "Region": ["United States", "India", "United Kingdom", "Canada", "Australia"],
        "Views": [8723, 6421, 3214, 2891, 1876]
    }
    
    df_regions = pd.DataFrame(regions)
    st.dataframe(df_regions, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Traffic Sources")
    
    sources = {
        "Source": ["YouTube Search", "Suggested Videos", "External Links", "Playlists", "Direct"],
        "Percentage": [35, 28, 18, 12, 7]
    }
    
    df_sources = pd.DataFrame(sources)
    st.dataframe(df_sources, use_container_width=True, hide_index=True)

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
