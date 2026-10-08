import streamlit as st
import requests

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="HuggingFace AI Image Generator",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #000428, #004e92);
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

.stTextArea textarea {
    background-color: #08142b !important;
    color: white !important;
    border-radius: 15px !important;
    border: 1px solid #3b82f6 !important;
}

.stTextInput input {
    background-color: #08142b !important;
    color: white !important;
    border-radius: 15px !important;
    border: 1px solid #3b82f6 !important;
}

.stButton button {
    background: linear-gradient(90deg, #ff512f, #dd2476);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 25px;
    font-size: 18px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.title("🎬 HuggingFace AI Cinematic Generator")

st.markdown("""
## 🚀 FREE AI Image Generation

Generate:
- Cinematic scenes
- AI thumbnails
- YouTube visuals
- Realistic movie frames
""")

# =====================================================
# API TOKEN
# =====================================================

hf_token = st.text_input(
    "🔑 HuggingFace Token",
    type="password"
)

# =====================================================
# PROMPT
# =====================================================

prompt = st.text_area(
    "🎥 Cinematic Prompt",
    height=250,
    value="""
Ultra realistic cinematic scene,
dramatic lighting,
professional movie shot,
epic atmosphere,
realistic animation,
high detail,
4k quality,
cyberpunk futuristic city,
cinematic composition,
volumetric lighting
"""
)

# =====================================================
# GENERATE BUTTON
# =====================================================

if st.button("🔥 Generate AI Scene"):

    if not hf_token:

        st.error("❌ HuggingFace token missing")
        st.stop()

    try:

        # =================================================
        # HEADERS
        # =================================================

        headers = {
            "Authorization": f"Bearer {hf_token}"
        }

        # =================================================
        # LIGHTWEIGHT MODEL
        # =================================================

        API_URL = (
            "https://api-inference.huggingface.co/models/"
            "runwayml/stable-diffusion-v1-5"
        )

        # =================================================
        # PAYLOAD
        # =================================================

        payload = {
            "inputs": prompt,
            "options": {
                "wait_for_model": True
            }
        }

        st.info("🎬 Generating cinematic AI scene...")

        # =================================================
        # REQUEST
        # =================================================

        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=300
        )

        # =================================================
        # STATUS
        # =================================================

        st.write(f"📡 Status Code: {response.status_code}")

        # =================================================
        # ERROR HANDLING
        # =================================================

        if response.status_code != 200:

            st.error("❌ AI generation failed")

            try:
                st.json(response.json())
            except:
                st.code(response.text)

            st.stop()

        # =================================================
        # IMAGE OUTPUT
        # =================================================

        image_bytes = response.content

        st.success("✅ AI Scene Generated Successfully")

        st.image(
            image_bytes,
            caption="🎬 AI Cinematic Scene",
            use_container_width=True
        )

        # =================================================
        # DOWNLOAD BUTTON
        # =================================================

        st.download_button(
            "⬇ Download AI Image",
            data=image_bytes,
            file_name="cinematic_scene.png",
            mime="image/png"
        )

    except requests.exceptions.ConnectionError:

        st.error("""
❌ Connection Error

HuggingFace API server resolve nahi ho raha.

Possible reasons:
- Internet DNS issue
- ISP block
- VPN/WARP disconnected
""")

    except Exception as e:

        st.error(f"❌ Error: {e}")