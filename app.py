# import streamlit as st
# from pii_masker import mask_pii
# from transcriber import transcribe_audio
# from summarizer import classify_transcript_topic
# import os

# # Streamlit config
# st.set_page_config(page_title="Audio PII Masker AI", layout="wide")

# st.markdown("""
#     <style>
#     .centered-title {
#         text-align: center;
#         font-size: 2.2em;
#         font-weight: bold;
#         margin-bottom: 0.2em;
#     }
#     .subtext {
#         text-align: center;
#         color: #666;
#         font-size: 1.1em;
#         margin-top: 0;
#         margin-bottom: 2em;
#     }
#     .uploaded-audio {
#         display: flex;
#         align-items: center;
#         justify-content: space-between;
#         margin-top: 10px;
#     }
#     .stButton>button {
#         width: 100%;
#         padding: 0.6em;
#         font-size: 1em;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.markdown("<div class='centered-title'>Audio Transcriber & PII Masker</div>", unsafe_allow_html=True)
# st.markdown("<div class='subtext'>Upload an audio file to transcribe and automatically mask names, numbers, cities, emails, and more.</div>", unsafe_allow_html=True)

# # Upload section
# uploaded_file = st.file_uploader("Upload audio (MP3, WAV, M4A, etc.)", type=["mp3", "wav", "m4a", "flac", "ogg", "webm", "aac", "wma"])

# if uploaded_file:
#     os.makedirs("audio_files", exist_ok=True)
#     file_path = os.path.join("audio_files", uploaded_file.name)

#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.read())

#     st.success("Audio uploaded successfully!")

#     # Show audio player beside filename
#     with st.container():
#         col1, col2 = st.columns([1, 3])
#         with col1:
#             st.markdown(f"**File:** `{uploaded_file.name}`")
#         with col2:
#             st.audio(file_path)

#     st.markdown("---")

#     if st.button("Transcribe & Auto-Mask PII"):
#         with st.spinner("Processing audio..."):
#             original_text = transcribe_audio(file_path)
#             masked_text = mask_pii(original_text)
#             topic_line = classify_transcript_topic(original_text)

#         st.markdown("## Overview")
#         st.info(topic_line)

#         st.markdown("## Transcripts")

#         # Show side-by-side columns
#         col1, col2 = st.columns(2)

#         with col1:
#             st.markdown("**Original Transcript**")
#             st.text_area("Original", original_text, height=300)

#         with col2:
#             st.markdown("**Masked Transcript**")
#             st.text_area("Masked", masked_text, height=300)

#         # Download option
#         st.download_button(
#             label="Download Masked Transcript",
#             data=masked_text,
#             file_name="masked_transcript.txt",
#             mime="text/plain"
#         )

#         # Cleanup
#         os.remove(file_path)


import streamlit as st
from pii_masker import mask_pii
from transcriber import transcribe_audio
from summarizer import classify_transcript_topic
from audio_recorder_streamlit import audio_recorder
import os
import time
import wave
import contextlib

# Page config
st.set_page_config(page_title="Audio PII Masker AI", layout="wide")

# --- Session State ---
if "recording" not in st.session_state:
    st.session_state.recording = False
if "timer" not in st.session_state:
    st.session_state.timer = 0

# --- Functions ---
def start_recording():
    st.session_state.recording = True
    st.session_state.timer = 0

def stop_recording():
    st.session_state.recording = False

# --- Custom Styling ---
st.markdown("""
    <style>
    .centered-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .subtext {
        text-align: center;
        color: #555;
        font-size: 1.1em;
        margin-bottom: 2em;
    }
    .stButton>button {
        width: 100%;
        padding: 0.6em;
        font-size: 1em;
        background-color: #3f51b5;
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #303f9f;
    }
    .loader {
        text-align: center;
        font-size: 1.2em;
        padding-top: 10px;
        color: #444;
        animation: blink 1.5s linear infinite;
    }
    @keyframes blink {
        0% {opacity: 0.2;}
        50% {opacity: 1;}
        100% {opacity: 0.2;}
    }
    </style>
""", unsafe_allow_html=True)

# --- Title and Description ---
st.markdown("<div class='centered-title'>Audio Transcriber & PII Masker</div>", unsafe_allow_html=True)
st.markdown("<div class='subtext'>Upload or record audio to transcribe and automatically mask names, PINs, cities, emails, and more.</div>", unsafe_allow_html=True)

# --- Audio Input Mode ---
mode = st.radio("Choose audio input mode:", ["Upload Audio", "Record Live"], horizontal=True)
file_path = None

# --- Upload Mode ---
if mode == "Upload Audio":
    uploaded_file = st.file_uploader("Upload audio (MP3, WAV, etc.)", type=["mp3", "wav", "m4a", "flac", "ogg", "webm", "aac", "wma"])
    if uploaded_file:
        os.makedirs("audio_files", exist_ok=True)
        file_path = os.path.join("audio_files", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("Audio uploaded successfully!")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**File:** `{uploaded_file.name}`")
        with col2:
            st.audio(file_path)

# --- Record Mode ---
# --- Record Mode ---
elif mode == "Record Live":
    # Initialize session state
    if "recorded_audio_bytes" not in st.session_state:
        st.session_state.recorded_audio_bytes = None
    if "audio_processed" not in st.session_state:
        st.session_state.audio_processed = False
    
    st.write("")  # Spacer
    
    # Center the recording controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Recording status and controls
        if not st.session_state.recorded_audio_bytes:
            st.markdown("""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <div style='color: #666; font-size: 1.1em; margin-bottom: 15px;'>
                        Ready to record audio
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Audio recorder
            audio_bytes = audio_recorder(
                text="Record Audio",
                icon_size="2x",
                recording_color="#ff4444",
                neutral_color="#4CAF50"
            )
            
            # Process new recording
            if audio_bytes:
                st.session_state.recorded_audio_bytes = audio_bytes
                st.session_state.audio_processed = False
                st.rerun()
        
        else:
            # Show recording completed status
            st.markdown("""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <div style='color: #4CAF50; font-size: 1.2em; font-weight: bold; margin-bottom: 10px;'>
                        ✅ Recording completed
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Save audio to file for processing
            os.makedirs("audio_files", exist_ok=True)
            file_path = os.path.join("audio_files", "recorded_audio.wav")
            with open(file_path, "wb") as f:
                f.write(st.session_state.recorded_audio_bytes)
            
            # Validate recording duration
            try:
                with contextlib.closing(wave.open(file_path, 'rb')) as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = round(frames / float(rate), 2)
            except:
                duration = 0
            
            if duration < 1:
                st.warning("⚠️ Recording too short. Please try again.")
                st.session_state.recorded_audio_bytes = None
                if os.path.exists(file_path):
                    os.remove(file_path)
                st.rerun()
            else:
                st.success(f"Recording successful! Duration: {duration} seconds")
                
                # Show audio player
                st.audio(st.session_state.recorded_audio_bytes)
                
                # Record again button (only show if not processed yet)
                if not st.session_state.audio_processed:
                    if st.button("🔄 Record Again", key="record_again", use_container_width=True):
                        st.session_state.recorded_audio_bytes = None
                        st.session_state.audio_processed = False
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        st.rerun()

# Set file_path for the main transcribe button (outside the mode check)
if mode == "Record Live" and st.session_state.get("recorded_audio_bytes"):
    # Ensure file exists for transcribe button
    os.makedirs("audio_files", exist_ok=True)
    file_path = os.path.join("audio_files", "recorded_audio.wav")
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(st.session_state.recorded_audio_bytes)

# --- Transcribe and Mask ---
if file_path and st.button("Transcribe & Auto-Mask PII"):
    if mode == "Record Live":
        st.session_state.audio_processed = True
    with st.spinner("Transcribing, masking, and analyzing..."):
        placeholder = st.empty()
        placeholder.markdown("<div class='loader'>Analyzing audio... Please wait</div>", unsafe_allow_html=True)

        # Simulate delay (optional, remove in real usage)
        time.sleep(1)

        original_text = transcribe_audio(file_path)
        masked_text = mask_pii(original_text)
        topic_line = classify_transcript_topic(original_text)

        placeholder.empty()

    st.markdown("## Overview")
    st.info(topic_line)

    st.markdown("## Transcripts")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original Transcript**")
        st.text_area("Original", original_text, height=300)

    with col2:
        st.markdown("**Masked Transcript**")
        st.text_area("Masked", masked_text, height=300)

    st.download_button(
        label="Download Masked Transcript",
        data=masked_text,
        file_name="masked_transcript.txt",
        mime="text/plain"
    )

    os.remove(file_path)
