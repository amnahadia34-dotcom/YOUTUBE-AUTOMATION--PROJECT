# ================================================
# SETTINGS - CONFIGURATION & API KEYS
# ================================================

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Settings - YouTube Automation SaaS",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
<style>
    .settings-section {
        background: #0f172a;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff0000;
        margin: 20px 0;
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

st.title("⚙️ Settings")
st.write("Configure your YouTube Automation SaaS Platform")

# ================================================
# TABS
# ================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "API Keys", "YouTube Accounts", "Voice Settings", "Preferences", "Account"
])

# ================================================
# TAB 1: API KEYS
# ================================================

with tab1:
    st.markdown('<h2 class="section-header">🔑 API Keys Configuration</h2>', unsafe_have_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 OpenAI API Key")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Get from https://platform.openai.com/api-keys"
        )
        
        if openai_key:
            st.success("✅ OpenAI key configured")
        else:
            st.warning("⚠️ OpenAI key not configured")
        
        st.link_button(
            "Get OpenAI API Key",
            "https://platform.openai.com/api-keys",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### 🤗 HuggingFace API Key")
        
        hf_key = st.text_input(
            "HuggingFace API Key",
            type="password",
            placeholder="hf_...",
            help="Get from https://huggingface.co/settings/tokens"
        )
        
        if hf_key:
            st.success("✅ HuggingFace key configured")
        else:
            st.warning("⚠️ HuggingFace key not configured")
        
        st.link_button(
            "Get HuggingFace API Key",
            "https://huggingface.co/settings/tokens",
            use_container_width=True
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎙️ ElevenLabs API Key")
        
        elevenlabs_key = st.text_input(
            "ElevenLabs API Key",
            type="password",
            placeholder="sk_...",
            help="Get from https://elevenlabs.io/api"
        )
        
        if elevenlabs_key:
            st.success("✅ ElevenLabs key configured")
        else:
            st.info("ℹ️ Optional - Uses gTTS if not configured")
        
        st.link_button(
            "Get ElevenLabs API Key",
            "https://elevenlabs.io/api",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### 📺 YouTube Credentials")
        
        youtube_creds = st.file_uploader(
            "Upload client_secret.json",
            type=["json"],
            help="YouTube OAuth credentials JSON file"
        )
        
        if youtube_creds:
            st.success("✅ YouTube credentials configured")
        else:
            st.warning("⚠️ YouTube credentials not configured")
        
        st.link_button(
            "Get YouTube Credentials",
            "https://console.cloud.google.com/",
            use_container_width=True
        )
    
    # Save button
    st.markdown("---")
    if st.button("💾 Save API Keys", use_container_width=True):
        st.success("✅ API keys saved successfully!")

# ================================================
# TAB 2: YOUTUBE ACCOUNTS
# ================================================

with tab2:
    st.markdown('<h2 class="section-header">📺 Connected YouTube Accounts</h2>', unsafe_have_html=True)
    
    accounts = [
        {
            "name": "My Main Channel",
            "channel_id": "UCxxxxxxxxxxxxxx",
            "subscribers": "24.5K",
            "videos": 187,
            "is_primary": True
        }
    ]
    
    for account in accounts:
        with st.expander(f"📺 {account['name']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Channel ID:** `{account['channel_id']}`")
                st.write(f"**Subscribers:** {account['subscribers']}")
            
            with col2:
                st.write(f"**Total Videos:** {account['videos']}")
                st.write(f"**Primary:** {'✅ Yes' if account['is_primary'] else '❌ No'}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit {account['name']}", key=f"edit_{account['name']}"):
                    st.info("Edit mode")
            with col2:
                if st.button(f"Disconnect {account['name']}", key=f"disc_{account['name']}"):
                    st.warning("Account disconnected")
    
    st.markdown("---")
    
    if st.button("➕ Add New Account", use_container_width=True):
        st.info("Follow YouTube OAuth flow to connect a new account")

# ================================================
# TAB 3: VOICE SETTINGS
# ================================================

with tab3:
    st.markdown('<h2 class="section-header">🎙️ Voice & Audio Settings</h2>', unsafe_have_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Default Voice Settings")
        
        default_provider = st.selectbox(
            "Default TTS Provider",
            ["Google TTS (Free)", "ElevenLabs (Premium)"]
        )
        
        default_gender = st.selectbox(
            "Default Voice Gender",
            ["Male", "Female"]
        )
        
        default_language = st.selectbox(
            "Default Language",
            ["English", "Spanish", "French", "Hindi", "Urdu"]
        )
    
    with col2:
        st.markdown("### Audio Quality")
        
        voice_speed = st.slider(
            "Voice Speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        voice_pitch = st.slider(
            "Voice Pitch",
            min_value=0.5,
            max_value=1.5,
            value=1.0,
            step=0.1
        )
        
        volume = st.slider(
            "Audio Volume",
            min_value=0,
            max_value=100,
            value=80,
            step=5
        )
    
    st.markdown("---")
    if st.button("💾 Save Voice Settings", use_container_width=True):
        st.success("✅ Voice settings saved!")

# ================================================
# TAB 4: PREFERENCES
# ================================================

with tab4:
    st.markdown('<h2 class="section-header">🎨 User Preferences</h2>', unsafe_have_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Theme & Display")
        
        theme = st.selectbox(
            "Theme",
            ["Dark (Default)", "Light", "Auto"]
        )
        
        sidebar_state = st.selectbox(
            "Sidebar",
            ["Expanded", "Collapsed"]
        )
        
        st.checkbox("Show Tooltips", value=True)
        st.checkbox("Show Notifications", value=True)
    
    with col2:
        st.markdown("### Notifications")
        
        st.checkbox("Email Notifications", value=True)
        st.checkbox("Upload Reminders", value=True)
        st.checkbox("Performance Reports", value=True)
        st.checkbox("Trending Alerts", value=False)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Default Settings")
        
        default_privacy = st.selectbox(
            "Default Privacy Status",
            ["Public", "Unlisted", "Private"]
        )
        
        default_category = st.selectbox(
            "Default Video Category",
            ["Science & Technology", "Education", "Entertainment", "Music"]
        )
    
    with col2:
        st.markdown("### Auto-Features")
        
        st.checkbox("Auto-Generate Scripts", value=True)
        st.checkbox("Auto-Generate Thumbnails", value=True)
        st.checkbox("Auto-Generate Captions", value=True)
        st.checkbox("Auto-Add Background Music", value=True)
    
    st.markdown("---")
    if st.button("💾 Save Preferences", use_container_width=True):
        st.success("✅ Preferences saved!")

# ================================================
# TAB 5: ACCOUNT
# ================================================

with tab5:
    st.markdown('<h2 class="section-header">👤 Account Management</h2>', unsafe_have_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Account Information")
        
        st.write(f"**Username:** user@example.com")
        st.write(f"**Account Type:** Premium")
        st.write(f"**Subscription Status:** Active ✅")
        st.write(f"**Joined:** January 15, 2024")
        
        st.markdown("---")
        
        st.markdown("### Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("🔑 Update Password", use_container_width=True):
            if new_password == confirm_password:
                st.success("✅ Password updated successfully!")
            else:
                st.error("❌ Passwords do not match")
    
    with col2:
        st.markdown("### Subscription")
        
        st.metric("Plan", "Premium")
        st.metric("Monthly Cost", "$29.99")
        st.metric("Renewal Date", "March 15, 2024")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.link_button("View Plan Details", "#", use_container_width=True)
        with col_b:
            st.link_button("Upgrade Plan", "#", use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### Danger Zone")
        
        st.warning("⚠️ Careful! These actions cannot be undone.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🗑️ Delete All Data", use_container_width=True):
                st.error("Are you sure? Click again to confirm.")
        with col_b:
            if st.button("❌ Close Account", use_container_width=True):
                st.error("Account closure initiated.")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
