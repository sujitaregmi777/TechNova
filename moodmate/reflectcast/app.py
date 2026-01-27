# app.py

import streamlit as st
import os

st.set_page_config(page_title="ReflectCast", layout="centered", initial_sidebar_state="collapsed")

st.title("🌙 ReflectCast")
st.subheader("Your nighttime emotional companion")

# Input from user
user_reflection = st.text_area("🌌 What's on your mind tonight?", placeholder="Feeling anxious and tired...")

# Emotion options
emotion = st.radio("😔 Choose your emotion:", ["Lonely", "Anxious", "Burnt Out", "Hopeful"])

# Ambient background
ambient = st.selectbox("🌊 Choose ambient background:", ["Rain", "Ocean", "Fireplace"])

# When user clicks the button
if st.button("📝 Generate My Podcast"):
    if user_reflection.strip() == "":
        st.warning("Please enter a reflection before generating.")
    else:
        st.info("🎙️ Generating your personalized podcast...")

        # Here, call your actual script + TTS generation code
        # For now, let's simulate
        # Example: generate_script_and_audio(user_reflection, emotion, ambient)

        # Assuming output file is saved to outputs/final_podcast.wav
        audio_path = "outputs/final_podcast.wav"
        if os.path.exists(audio_path):
            st.success("✅ Your nighttime podcast is ready!")
            st.audio(audio_path)
            st.download_button("🔽 Download", open(audio_path, 'rb'), file_name="ReflectCast.mp3")
        else:
            st.error("Failed to generate podcast. Check backend.")
