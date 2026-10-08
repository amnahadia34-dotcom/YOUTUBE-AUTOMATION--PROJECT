import streamlit as st
import requests

# Backend URL
API_URL = "http://127.0.0.1:8000/generate-content"

st.set_page_config(page_title="YouTube Automation", layout="centered")

st.title("🚀 AI YouTube Automation System")

st.write("Enter a topic and generate full YouTube content automatically!")

# Input box
topic = st.text_input("Enter Topic")

# Button
if st.button("Generate Content"):

    if not topic:
        st.warning("Please enter a topic")
    else:
        with st.spinner("Generating content..."):
            try:
                response = requests.post(API_URL, json={"topic": topic})

                if response.status_code == 200:
                    data = response.json()

                    st.success("Content Generated Successfully!")

                    # Script
                    st.subheader("📜 Script")
                    st.write(data["script"])

                    # Video Path
                    st.subheader("🎬 Video File")
                    st.write(data["video_path"])

                    # YouTube Link
                    st.subheader("🔗 YouTube Link")
                    st.write(data["youtube_url"])

                else:
                    st.error(f"Error: {response.text}")

            except Exception as e:
                st.error(f"Connection Error: {e}")