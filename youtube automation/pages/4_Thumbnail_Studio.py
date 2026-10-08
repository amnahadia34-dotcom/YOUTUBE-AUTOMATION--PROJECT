# ================================================
# THUMBNAIL STUDIO - PROFESSIONAL THUMBNAIL CREATION
# ================================================

import streamlit as st
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(
    page_title="Thumbnail Studio - YouTube Automation SaaS",
    page_icon="🖼️",
    layout="wide"
)

st.markdown("""
<style>
    .thumbnail-preview {
        width: 100%;
        max-width: 320px;
        height: 180px;
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        border: 2px solid #ff0000;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: bold;
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

st.title("🖼️ Thumbnail Studio")
st.write("Create viral YouTube thumbnails with AI")

# ================================================
# TABS
# ================================================

tab1, tab2, tab3 = st.tabs(["AI Generator", "Templates", "Analytics"])

# ================================================
# TAB 1: AI GENERATOR
# ================================================

with tab1:
    st.markdown('<h2 class="section-header">🤖 AI Thumbnail Generator</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Content Details")
        
        video_title = st.text_input(
            "Video Title",
            placeholder="e.g., 10 AI Tools That Will Change Your Life",
            help="This will be analyzed for optimal thumbnail text"
        )
        
        thumbnail_text = st.text_input(
            "Thumbnail Text (optional)",
            placeholder="e.g., AI TOOLS",
            help="Main text to display on thumbnail"
        )
        
        style = st.selectbox(
            "Thumbnail Style",
            [
                "Bold & Bright",
                "Dark & Dramatic",
                "Minimalist",
                "Vibrant & Colorful",
                "Professional",
                "Gaming Style"
            ]
        )
    
    with col2:
        st.subheader("Design Settings")
        
        background_style = st.selectbox(
            "Background",
            ["Solid Color", "Gradient", "Image", "AI Generated", "Blur Effect"]
        )
        
        if background_style == "Solid Color":
            bg_color = st.color_picker("Pick color", "#ff0000")
        
        text_effect = st.multiselect(
            "Text Effects",
            ["Text Shadow", "Text Stroke", "Glow", "3D Effect", "Blur Background"],
            default=["Text Shadow", "Text Stroke"]
        )
        
        emoji_suggestions = st.checkbox("Include Emoji Suggestions", value=True)
    
    # Generate button
    if st.button("🎨 Generate Thumbnail", use_container_width=True):
        if not video_title:
            st.error("❌ Please enter a video title")
        else:
            with st.spinner("🎨 Creating thumbnail..."):
                st.success("✅ Thumbnail generated!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3>📺 Preview</h3>', unsafe_allow_html=True)
                    st.markdown("""
                    <div class="thumbnail-preview">
                        YOUR THUMBNAIL PREVIEW HERE
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Viral Score", "92/100", "+12")
                
                with col2:
                    st.markdown('<h3>🎯 Optimization Tips</h3>', unsafe_allow_html=True)
                    
                    st.info("""
                    ✅ **What works well:**
                    - Bold contrasting colors (Red + Yellow)
                    - Close-up face expressions
                    - Large readable text
                    - Maximum 4-5 words
                    - High contrast borders
                    
                    ⚠️ **Avoid:**
                    - Small text
                    - Too many elements
                    - Overly complex designs
                    - Poor color contrast
                    """)
                
                # Download options
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📥 Download JPG",
                        "image_data",
                        file_name="thumbnail.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
                
                with col2:
                    st.download_button(
                        "📥 Download PNG",
                        "image_data",
                        file_name="thumbnail.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                with col3:
                    if st.button("➕ Upload to Video", use_container_width=True):
                        st.success("Thumbnail linked to video!")

# ================================================
# TAB 2: TEMPLATES
# ================================================

with tab2:
    st.markdown('<h2 class="section-header">📋 Thumbnail Templates</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    templates = [
        ("Bold Text", "Best for tutorials"),
        ("Face + Text", "Best for personal brand"),
        ("Two-Panel", "Best for comparisons"),
        ("Number List", "Best for lists"),
        ("Product Focus", "Best for reviews"),
        ("Minimal Clean", "Best for professional")
    ]
    
    for idx, (name, desc) in enumerate(templates):
        with st.columns(3)[idx % 3]:
            with st.expander(f"📋 {name}"):
                st.write(f"Use case: {desc}")
                st.markdown("""
                <div class="thumbnail-preview" style="height: 150px;">
                    TEMPLATE PREVIEW
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Use {name} Template", use_container_width=True, key=f"template_{idx}"):
                    st.switch_page("4_Thumbnail_Studio")

# ================================================
# TAB 3: A/B TESTING ANALYTICS
# ================================================

with tab3:
    st.markdown('<h2 class="section-header">📊 Thumbnail A/B Testing</h2>', unsafe_allow_html=True)
    
    test_data = {
        "Thumbnail": ["Design A (Bold Red)", "Design B (Dark Blue)", "Design C (Gradient)"],
        "Impressions": [15234, 12847, 18923],
        "Clicks": [623, 445, 1128],
        "CTR": ["4.1%", "3.5%", "6.0%"],
        "Views": [478, 312, 892],
        "Status": ["Running", "Running", "🏆 Winner"]
    }
    
    import pandas as pd
    df = pd.DataFrame(test_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📈 CTR Comparison")
    
    fig = go.Figure(data=[
        go.Bar(x=["Design A", "Design B", "Design C"], y=[4.1, 3.5, 6.0], marker_color='#ff0000')
    ])
    
    fig.update_layout(
        title="Click-Through Rate by Thumbnail Design",
        xaxis_title="Thumbnail Design",
        yaxis_title="CTR (%)",
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(color='#ffffff')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("🏆 Design C is your best performer! Consider using this style for future videos.")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
