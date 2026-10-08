import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
from streamlit_option_menu import option_menu
import time

# Page configuration
st.set_page_config(
    page_title="YouTube Automation Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and glassmorphism
st.markdown("""
<style>
    /* Global dark theme */
    .stApp {
        background: linear-gradient(135deg, #0a0f1e 0%, #0a0f1e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Glassmorphism effect */
    .glass-card {
        background: rgba(30, 40, 60, 0.4);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        background: rgba(30, 40, 60, 0.6);
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
        border-radius: 20px;
        padding: 1rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Custom metrics */
    .metric-container {
        background: rgba(20, 30, 45, 0.6);
        border-radius: 15px;
        padding: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1633t4s {
        background: rgba(10, 15, 30, 0.8);
        backdrop-filter: blur(10px);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(30, 40, 60, 0.3);
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
    }
    
    /* Chart styling */
    .js-plotly-plot {
        background: rgba(20, 30, 45, 0.4);
        border-radius: 15px;
        padding: 1rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(135deg, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar text */
    .css-10trblm, .css-1v3fvcr {
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Generate demo data
def generate_demo_data():
    # Generate dates for the last 30 days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    dates.reverse()
    
    # Views data with realistic growth pattern
    views_data = [1200 + (i * 150) + random.randint(-100, 200) for i in range(30)]
    views_data = [max(500, x) for x in views_data]
    
    # Subscribers data
    subs_data = [50 + (i * 8) + random.randint(-5, 15) for i in range(30)]
    subs_data = [max(20, x) for x in subs_data]
    
    # Watch time data (in minutes)
    watch_time = [v * 3.5 + random.randint(-50, 100) for v in views_data]
    watch_time = [max(100, x) for x in watch_time]
    
    # CTR data
    ctr_data = [round(random.uniform(4.5, 8.5), 2) for _ in range(30)]
    
    # Revenue data (in USD)
    revenue_data = [round(v * 0.0025 + random.uniform(-1, 2), 2) for v in views_data]
    revenue_data = [max(0.5, x) for x in revenue_data]
    
    return {
        'dates': dates,
        'views': views_data,
        'subscribers': subs_data,
        'watch_time': watch_time,
        'ctr': ctr_data,
        'revenue': revenue_data
    }

# Initialize demo data
demo_data = generate_demo_data()

# Sidebar navigation
with st.sidebar:
    st.image("https://placehold.co/200x60/6366f1/white?text=YouTubeAutomation", use_column_width=True)
    st.markdown("---")
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "Content Research", "AI Script Studio", "SEO Studio", "Thumbnail Studio", "Content Calendar", "Analytics"],
        icons=["house", "search", "pen", "graph-up", "image", "calendar", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background": "rgba(30, 40, 60, 0.3)"},
            "icon": {"color": "#6366f1", "font-size": "1.2rem"},
            "nav-link": {"color": "#e2e8f0", "font-size": "0.9rem", "margin": "0.2rem 0"},
            "nav-link-selected": {"background": "linear-gradient(135deg, #6366f1, #a855f7)"},
        }
    )
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    total_views = sum(demo_data['views'])
    total_subs = sum(demo_data['subscribers'])
    total_rev = sum(demo_data['revenue'])
    
    st.metric("Total Views", f"{total_views:,}", "+15%")
    st.metric("Subscribers", f"{total_subs:,}", "+8%")
    st.metric("Revenue", f"${total_rev:,.2f}", "+22%")

# Main content area
if selected == "Dashboard":
    st.title("📊 Analytics Dashboard")
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='glass-card'>
            <h3 style='margin:0; font-size:0.9rem;'>Total Views</h3>
            <div class='kpi-value'>{:,.0f}</div>
            <p style='margin:0; color:#10b981;'>↑ 15.3%</p>
        </div>
        """.format(sum(demo_data['views'])), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='glass-card'>
            <h3 style='margin:0; font-size:0.9rem;'>Subscribers</h3>
            <div class='kpi-value'>{:,.0f}</div>
            <p style='margin:0; color:#10b981;'>↑ 8.2%</p>
        </div>
        """.format(sum(demo_data['subscribers'])), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='glass-card'>
            <h3 style='margin:0; font-size:0.9rem;'>Watch Time (hrs)</h3>
            <div class='kpi-value'>{:,.0f}</div>
            <p style='margin:0; color:#10b981;'>↑ 12.7%</p>
        </div>
        """.format(sum(demo_data['watch_time']) // 60), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='glass-card'>
            <h3 style='margin:0; font-size:0.9rem;'>Revenue</h3>
            <div class='kpi-value'>${:,.2f}</div>
            <p style='margin:0; color:#10b981;'>↑ 22.1%</p>
        </div>
        """.format(sum(demo_data['revenue'])), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Growth Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Views Growth")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=demo_data['dates'], y=demo_data['views'], mode='lines+markers', name='Views', line=dict(color='#6366f1', width=2)))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', xaxis_title="Date", yaxis_title="Views")
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue Growth")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=demo_data['dates'][-7:], y=demo_data['revenue'][-7:], name='Revenue', marker_color='#a855f7'))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', xaxis_title="Date", yaxis_title="Revenue ($)")
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Engagement Rate")
        engagement_rate = (sum(demo_data['views']) / max(1, sum(demo_data['subscribers'])) * 100)
        fig = go.Figure(go.Indicator(mode="gauge+number", value=engagement_rate, title={'text': "Engagement %"}, domain={'x': [0, 1], 'y': [0, 1]}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#6366f1"}}))
        fig.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Average CTR")
        avg_ctr = np.mean(demo_data['ctr'][-7:])
        fig = go.Figure(go.Indicator(mode="gauge+number", value=avg_ctr, title={'text': "Click-Through Rate %"}, domain={'x': [0, 1], 'y': [0, 1]}, gauge={'axis': {'range': [None, 15]}, 'bar': {'color': "#a855f7"}}))
        fig.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("### 👁️ Audience Retention")
        retention = [80, 75, 68, 62, 55, 48, 42, 38, 35, 32]
        fig = go.Figure(data=[go.Scatter(y=retention, mode='lines+markers', line=dict(color='#6366f1', width=2))])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', xaxis_title="Time (minutes)", yaxis_title="Retention %")
        st.plotly_chart(fig, use_container_width=True)

elif selected == "Content Research":
    st.title("🔍 Content Research Studio")
    st.markdown("---")
    
    # Trending Topics
    st.markdown("### 🔥 Trending Topics")
    trending_topics = [
        {"topic": "AI Automation 2025", "volume": "125K", "competition": "Medium", "score": 92},
        {"topic": "YouTube Growth Hacks", "volume": "89K", "competition": "High", "score": 78},
        {"topic": "Passive Income Ideas", "volume": "156K", "competition": "Very High", "score": 65},
        {"topic": "Productivity Tools", "volume": "67K", "competition": "Low", "score": 88},
        {"topic": "Digital Marketing", "volume": "98K", "competition": "High", "score": 71}
    ]
    
    for topic in trending_topics:
        st.markdown(f"""
        <div class='glass-card'>
            <h4>{topic['topic']}</h4>
            <p>📊 Search Volume: {topic['volume']} | 🎯 Competition: {topic['competition']} | ⭐ Score: {topic['score']}/100</p>
            <progress value="{topic['score']}" max="100" style="width:100%; height:10px; border-radius:5px;"></progress>
        </div>
        """, unsafe_allow_html=True)
    
    # Viral Topic Finder
    st.markdown("### 🚀 Viral Topic Finder")
    col1, col2 = st.columns(2)
    
    with col1:
        topic_input = st.text_input("Enter niche or keyword", placeholder="e.g., Artificial Intelligence")
        if st.button("Find Viral Topics", use_container_width=True):
            viral_topics = [
                "Why AI Will Replace 50% of Jobs by 2026",
                "The Secret YouTube Algorithm That Nobody Talks About",
                "How I Made $10,000 With Zero Skills",
                "The Future of Content Creation in 2025"
            ]
            for topic in viral_topics:
                st.success(f"🔥 {topic}")
    
    with col2:
        st.markdown("#### 💡 Viral Potential Score")
        scores = [85, 92, 78, 95, 88]
        fig = go.Figure(data=[go.Bar(x=["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"], y=scores, marker_color='#6366f1')])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)
    
    # Competitor Analysis
    st.markdown("### 🎯 Competitor Analysis")
    competitors = [
        {"name": "TechTuber Pro", "subscribers": "1.2M", "avg_views": "250K", "growth": "+15%", "strategy": "High quality tutorials"},
        {"name": "AI Mastery", "subscribers": "850K", "avg_views": "180K", "growth": "+22%", "strategy": "Daily shorts + long form"},
        {"name": "Growth Hacker", "subscribers": "2.1M", "avg_views": "450K", "growth": "+8%", "strategy": "Controversial topics"}
    ]
    
    for comp in competitors:
        st.markdown(f"""
        <div class='glass-card'>
            <h4>📺 {comp['name']}</h4>
            <p>👥 {comp['subscribers']} subs | 📈 {comp['avg_views']} avg views | 🚀 Growth: {comp['growth']}</p>
            <p>💡 Strategy: {comp['strategy']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Keyword Research
    st.markdown("### 🔑 Keyword Research")
    keywords = [
        {"keyword": "AI tools 2025", "volume": "45K", "difficulty": "Low", "cpc": "$2.50"},
        {"keyword": "YouTube automation", "volume": "22K", "difficulty": "Medium", "cpc": "$3.20"},
        {"keyword": "make money online", "volume": "110K", "difficulty": "High", "cpc": "$4.80"},
        {"keyword": "content creation tips", "volume": "18K", "difficulty": "Low", "cpc": "$1.90"}
    ]
    
    df_keywords = pd.DataFrame(keywords)
    st.dataframe(df_keywords, use_container_width=True, hide_index=True)

elif selected == "AI Script Studio":
    st.title("✍️ AI Script Studio")
    st.markdown("---")
    
    script_type = st.selectbox("Select Script Type", ["Long Video Script", "Shorts Script", "Viral Hook", "Story Script", "CTA"])
    
    topic = st.text_input("Video Topic", placeholder="e.g., How to grow your YouTube channel")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        tone = st.selectbox("Tone", ["Professional", "Casual", "Energetic", "Educational", "Inspirational"])
    with col2:
        length = st.selectbox("Duration", ["Short (1-2 min)", "Medium (3-5 min)", "Long (8-10 min)"])
    
    if st.button("Generate Script", use_container_width=True):
        if script_type == "Long Video Script":
            script = f"""
            **INTRO (0:00 - 0:30)**
            🎬 Hook: "Are you ready to discover the ultimate secret to {topic.lower()}?"
            
            **SECTION 1 (0:30 - 2:00)**
            Let me share with you three game-changing strategies that transformed my approach to {topic.lower()}...
            
            **SECTION 2 (2:00 - 4:00)**
            The first strategy that nobody talks about is...
            
            **SECTION 3 (4:00 - 6:00)**
            Now here's where most creators go wrong...
            
            **CONCLUSION (6:00 - 8:00)**
            To wrap this up, remember these key points...
            🔥 Like and subscribe for more content on {topic.lower()}!
            """
        elif script_type == "Shorts Script":
            script = f"""🔥 {topic.upper()} in 60 seconds!

⏰ 0:00 - The problem
⏰ 0:15 - The solution
⏰ 0:30 - Step-by-step
⏰ 0:45 - Game-changing results

💡 Pro tip: Save this for later!
🎯 Want part 2? Comment "YES" below!

#shorts #{topic.replace(' ', '')}"""
        elif script_type == "Viral Hook":
            hooks = [
                f"⚠️ STOP scrolling! This {topic} secret will shock you!",
                f"💀 Most people fail at {topic} because they don't know THIS...",
                f"🚀 How I mastered {topic} in just 7 days (and you can too)",
                f"🤯 The {topic} hack that made me $10,000"
            ]
            script = "\n\n".join(hooks)
        elif script_type == "Story Script":
            script = f"""📖 THE STORY OF {topic.upper()}

Once upon a time, I was struggling with {topic.lower()}...
Everything changed when I discovered one simple technique.

The moment I applied this knowledge, everything transformed.
Now it's YOUR turn to experience the same breakthrough.

Subscribe to join the journey! 🎯"""
        else:  # CTA Generator
            scripts = [
                f"🔥 If you enjoyed this {topic} tutorial, smash that like button!",
                f"🎯 Ready to level up your {topic} game? Subscribe now for weekly tips!",
                f"💎 Want exclusive {topic} strategies? Hit the bell icon!",
                f"🚀 Share this with someone who needs to see this {topic} breakdown!"
            ]
            script = random.choice(scripts)
        
        st.markdown("### 📝 Generated Script")
        st.markdown(f"""
        <div class='glass-card'>
            {script.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        st.download_button("Download Script", script, file_name=f"script_{topic}.txt", use_container_width=True)

elif selected == "SEO Studio":
    st.title("🔍 SEO Studio")
    st.markdown("---")
    
    seo_topic = st.text_input("Video Topic for SEO Optimization", placeholder="e.g., AI Automation Tutorial")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Title Generator", "Description Generator", "Tags Generator", "SEO Score"])
    
    with tab1:
        if st.button("Generate Titles", key="titles"):
            titles = [
                f"How to Master {seo_topic} in 2025",
                f"The Ultimate {seo_topic} Guide for Beginners",
                f"10 {seo_topic} Secrets You Never Knew",
                f"Why {seo_topic} is Changing Everything",
                f"${seo_topic}: The Complete Beginner's Guide"
            ]
            for title in titles:
                st.markdown(f"✅ {title}")
    
    with tab2:
        if st.button("Generate Description", key="desc"):
            description = f"""🔥 MASTER {seo_topic.upper()} IN 2025 🔥

Are you ready to transform your understanding of {seo_topic}? In this comprehensive guide, I'll reveal the exact strategies that top creators use to dominate this space.

📌 TIMESTAMPS:
0:00 - Introduction
1:30 - What is {seo_topic}?
3:45 - Key Strategies
6:20 - Common Mistakes
8:15 - Advanced Techniques
10:00 - Conclusion

💡 RESOURCES MENTIONED:
• Exclusive templates (link in bio)
• Free checklist (download below)

🎯 SUBSCRIBE for weekly {seo_topic} content!

👍 LIKE if this helped you understand {seo_topic} better!

💬 COMMENT your biggest takeaway below!

#seo #youtubetips #{seo_topic.replace(' ', '')} #contentcreation"""
            st.text_area("Generated Description", description, height=300)
            st.download_button("Copy Description", description, use_container_width=True)
    
    with tab3:
        if st.button("Generate Tags", key="tags"):
            base_tags = [seo_topic, f"{seo_topic} tutorial", f"learn {seo_topic}", f"{seo_topic} 2025", f"best {seo_topic}", f"{seo_topic} guide", f"{seo_topic} for beginners", "youtube seo", "video optimization", "content strategy"]
            tags_string = ", ".join(base_tags)
            st.markdown(f"### 🏷️ Recommended Tags")
            st.code(tags_string)
            
            hashtags = [f"#{tag.replace(' ', '')}" for tag in base_tags[:7]]
            st.markdown("### #️⃣ Auto-Generated Hashtags")
            st.markdown(" ".join(hashtags))
    
    with tab4:
        st.markdown("### 📊 SEO Score Meter")
        score = random.randint(65, 98)
        fig = go.Figure(go.Indicator(mode="gauge+number+delta", value=score, title={'text': "SEO Score"}, delta={'reference': 80}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#6366f1"}, 'steps': [{'range': [0, 50], 'color': "red"}, {'range': [50, 80], 'color': "yellow"}, {'range': [80, 100], 'color': "green"}]}))
        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 💡 Optimization Tips")
        st.info("✅ Add your main keyword in first 60 characters of title")
        st.info("✅ Include timestamps in description")
        st.info("✅ Use 15-20 relevant tags")
        st.info("✅ Add cards and end screens")

elif selected == "Thumbnail Studio":
    st.title("🎨 Thumbnail Studio")
    st.markdown("---")
    
    thumbnail_topic = st.text_input("Video Topic for Thumbnail", placeholder="e.g., Make Money Online")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💡 Thumbnail Ideas")
        ideas = [
            f"Shocked face + {thumbnail_topic} results",
            f"Before/After comparison of {thumbnail_topic}",
            f"Big red arrow pointing to {thumbnail_topic} hack",
            f"Split screen showing struggle vs success in {thumbnail_topic}"
        ]
        for idea in ideas:
            st.markdown(f"🎯 {idea}")
    
    with col2:
        st.markdown("### 📝 Text Overlay Generator")
        text_styles = ["Big Bold Text", "Gradient Text", "Outline Text", "Shadow Text"]
        selected_style = st.selectbox("Text Style", text_styles)
        
        if st.button("Generate Text Overlays"):
            overlays = [
                f"🔥 {thumbnail_topic.upper()} SECRET!",
                f"💰 {thumbnail_topic.upper()} MADE EASY",
                f"⚠️ DON'T DO {thumbnail_topic.upper()}",
                f"🎯 {thumbnail_topic.upper()} HACK REVEALED"
            ]
            for overlay in overlays:
                st.markdown(f"✨ {overlay}")
    
    st.markdown("---")
    st.markdown("### 🖼️ Thumbnail Preview Area")
    st.markdown("""
    <div class='glass-card' style='text-align: center; min-height: 200px; display: flex; align-items: center; justify-content: center;'>
        <div>
            <p style='font-size: 3rem;'>🎬</p>
            <h3>Thumbnail Preview</h3>
            <p>Your generated thumbnail will appear here</p>
            <p style='font-size: 0.8rem; color: #6366f1;'>🎯 CTR Prediction: High (8.5-12%)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎨 Color Psychology Guide")
    colors_data = {
        "Red": "Urgency, Excitement", "Blue": "Trust, Professional", "Yellow": "Attention, Optimism",
        "Green": "Growth, Money", "Purple": "Creative, Premium", "Orange": "Energetic, Fun"
    }
    for color, meaning in colors_data.items():
        st.markdown(f"🎨 **{color}**: {meaning}")

elif selected == "Content Calendar":
    st.title("📅 Content Calendar")
    st.markdown("---")
    
    view_type = st.radio("View", ["Weekly Schedule", "Monthly Planner", "Publishing Queue"], horizontal=True)
    
    if view_type == "Weekly Schedule":
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        content_types = ["Long-form", "Shorts", "Live Stream", "Tutorial", "Case Study", "Behind Scenes", "Q&A"]
        
        schedule_data = []
        for i, day in enumerate(days):
            schedule_data.append({
                "Day": day,
                "Content Type": content_types[i % len(content_types)],
                "Topic": f"Mastering {['AI', 'SEO', 'YouTube Growth', 'Content Creation', 'Productivity', 'Marketing', 'Automation'][i]}",
                "Status": "Scheduled" if i < 5 else "Draft",
                "Time": "10:00 AM"
            })
        
        df_schedule = pd.DataFrame(schedule_data)
        st.dataframe(df_schedule, use_container_width=True, hide_index=True)
        
        st.markdown("### ⏰ Posting Schedule")
        fig = go.Figure(data=[go.Bar(x=days, y=[1500, 2200, 1800, 2500, 3000, 4500, 3500], marker_color='#6366f1')])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', xaxis_title="Day", yaxis_title="Expected Views")
        st.plotly_chart(fig, use_container_width=True)
    
    elif view_type == "Monthly Planner":
        st.markdown("### 📆 April 2025 Content Plan")
        
        month_data = []
        for week in range(1, 5):
            for day in range(1, 8):
                if len(month_data) < 30:
                    month_data.append({
                        "Date": f"April {len(month_data) + 1}",
                        "Content Title": f"Day {len(month_data) + 1}: {random.choice(['AI Tutorial', 'Growth Hack', 'Case Study', 'Tool Review', 'Strategy Guide'])}",
                        "Status": random.choice(["Published", "Scheduled", "Draft", "Idea"]),
                        "Priority": random.choice(["High", "Medium", "Low"])
                    })
        
        df_month = pd.DataFrame(month_data[:21])
        st.dataframe(df_month, use_container_width=True, hide_index=True)
    
    else:  # Publishing Queue
        st.markdown("### ⏳ Publishing Queue")
        
        queue_data = [
            {"Title": "How AI is Replacing Traditional Workflows", "Date": "Tomorrow", "Time": "10:00 AM", "Status": "Ready"},
            {"Title": "Top 10 AI Tools You Must Use", "Date": "Apr 15", "Time": "2:00 PM", "Status": "Editing"},
            {"Title": "Future of AI Automation", "Date": "Apr 18", "Time": "9:00 AM", "Status": "Scheduled"},
            {"Title": "YouTube Algorithm Secrets", "Date": "Apr 20", "Time": "11:30 AM", "Status": "Draft"}
        ]
        
        for item in queue_data:
            st.markdown(f"""
            <div class='glass-card'>
                <h4>{item['Title']}</h4>
                <p>📅 {item['Date']} at {item['Time']} | 🎯 Status: {item['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Add to Queue", use_container_width=True):
            st.success("New video added to publishing queue!")

elif selected == "Analytics":
    st.title("📈 Advanced Analytics")
    st.markdown("---")
    
    time_range = st.selectbox("Time Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👁️ Views Analytics")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=demo_data['dates'][-14:], y=demo_data['views'][-14:], mode='lines', name='Views', line=dict(color='#6366f1', width=3)))
        fig.add_trace(go.Scatter(x=demo_data['dates'][-14:], y=[np.mean(demo_data['views'][-14:])]*14, mode='lines', name='Average', line=dict(color='#a855f7', width=2, dash='dash')))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', title="Views Trend")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 CTR Analytics")
        ctr_fig = go.Figure(data=[go.Bar(x=demo_data['dates'][-7:], y=demo_data['ctr'][-7:], marker_color='#a855f7')])
        ctr_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', title="Click-Through Rate Trend")
        st.plotly_chart(ctr_fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⏱️ Watch Time Analytics")
        watch_hours = [w/60 for w in demo_data['watch_time'][-14:]]
        fig = go.Figure(data=[go.Scatter(x=demo_data['dates'][-14:], y=watch_hours, mode='lines+markers', fill='tozeroy', marker_color='#6366f1')])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', title="Watch Time (Hours)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 💬 Engagement Analytics")
        engagement_data = {
            "Likes": random.randint(5000, 15000),
            "Comments": random.randint(500, 2000),
            "Shares": random.randint(300, 1500),
            "Saves": random.randint(1000, 3000)
        }
        
        fig = go.Figure(data=[go.Pie(labels=list(engagement_data.keys()), values=list(engagement_data.values()), marker=dict(colors=['#6366f1', '#a855f7', '#06b6d4', '#10b981']))])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', title="Engagement Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Demographics
    st.markdown("### 🌍 Audience Demographics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 👥 Age Groups")
        ages = ["18-24", "25-34", "35-44", "45+"]
        values = [35, 45, 15, 5]
        fig = go.Figure(data=[go.Bar(x=ages, y=values, marker_color='#6366f1')])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌎 Top Countries")
        countries = ["USA", "UK", "Canada", "Australia", "Germany"]
        percentages = [45, 20, 15, 10, 5]
        fig = go.Figure(data=[go.Pie(labels=countries, values=percentages, marker=dict(colors=['#6366f1', '#a855f7', '#06b6d4', '#10b981', '#f59e0b']))])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### 📱 Device Usage")
        devices = ["Mobile", "Desktop", "Tablet", "TV"]
        usage = [65, 25, 7, 3]
        fig = go.Figure(data=[go.Bar(x=devices, y=usage, marker_color='#a855f7')])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', height=300)
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.1)); border-radius: 20px; margin-top: 2rem;'>
    <p style='color: #94a3b8;'>🚀 YouTube Automation Platform | Enterprise SaaS Solution</p>
    <p style='color: #64748b; font-size: 0.8rem;'>© 2025 All Rights Reserved | Demo Version</p>
</div>
""", unsafe_allow_html=True)