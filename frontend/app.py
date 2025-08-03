
import streamlit as st
import requests
import os
import sys
from pathlib import Path
import tempfile
import base64
import time

# Add root directory to Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Import translation services
from services.translate import detect_language, translate_to_english, translate_from_english

# Import speech recognition
import speech_recognition as sr
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder

# Streamlit UI Setup
st.set_page_config(page_title="Bus Agent", page_icon="🚌")
st.title("🚌 Multilingual Bus Info Agent")
st.markdown("Ask about bus timings from Madanapalli to any route (Supports Telugu, Hindi, Urdu, Tamil, Kannada, Malayalam, English)")

st.subheader("🎙 Speak Your Query")

# Session State
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# Function to convert text to speech
def text_to_speech(text, lang_info):
    try:
        # Use the TTS code from language info
        tts = gTTS(text=text, lang=lang_info['tts'])
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        return fp.name
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

# Function to recognize speech from audio bytes
def recognize_speech_from_bytes(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        # Create an AudioFile object from bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
            fp.write(audio_bytes)
            audio_path = fp.name
        
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        
        # First try with Indian English
        try:
            return recognizer.recognize_google(audio, language="en-IN")
        except sr.UnknownValueError:
            # Try with no specific language
            try:
                return recognizer.recognize_google(audio)
            except:
                return ""
    except Exception as e:
        st.error(f"Speech recognition error: {e}")
        return ""

# Audio recorder widget
st.write("Record your query:")
audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_name="microphone",
    icon_size="2x",
)

# Process audio recording
if audio_bytes:
    # Recognize speech
    recognized_text = recognize_speech_from_bytes(audio_bytes)
    if recognized_text:
        st.session_state.voice_text = recognized_text
        st.success(f"🎤 You said: {recognized_text}")
    else:
        st.warning("Could not recognize speech. Please try again.")

# Input Box (either voice or manual)
user_query = st.text_input("Where do you want to go?", value=st.session_state.voice_text)

# Call FastAPI to check bus
if st.button("Check Bus Timings") and user_query.strip():
    with st.spinner("Processing your request..."):
        try:
            # Detect language
            lang_info = detect_language(user_query)
            
            # Translate to English if needed
            query_in_english = (
                translate_to_english(user_query, source_lang=lang_info)
                if lang_info['tts'] != 'en'
                else user_query
            )

            # Call backend API
            try:
                response = requests.get(
                    "http://127.0.0.1:8000/bus", 
                    params={"destination": query_in_english},
                    timeout=5
                )
                response.raise_for_status()
                data = response.json()
            except (requests.ConnectionError, requests.Timeout):
                st.error("⚠️ Backend service is not running. Please start the backend server first.")
                st.stop()
            except requests.HTTPError as e:
                st.error(f"Backend error: {e}")
                st.stop()

            if "departure_times" in data:
                route = data["route"]
                timings = ", ".join(data["departure_times"])
                bus_type = data["bus_type"]
                msg = f"Buses to {route} ({bus_type}): {timings}"

                # Translate back to original language
                final_msg = (
                    translate_from_english(msg, target_lang=lang_info)
                    if lang_info['tts'] != 'en'
                    else msg
                )
                
                # Display result
                st.success(final_msg)
                
                # Generate and play audio response
                audio_file = text_to_speech(final_msg, lang_info)
                if audio_file:
                    audio_bytes = open(audio_file, "rb").read()
                    st.audio(audio_bytes, format="audio/mp3")
                
            else:
                fallback_msg = data.get("message", "No buses found")
                translated_msg = (
                    translate_from_english(fallback_msg, target_lang=lang_info)
                    if lang_info['tts'] != 'en'
                    else fallback_msg
                )
                st.warning(translated_msg)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")