import streamlit as st
import numpy as np
import cv2
import av
from groq import Groq
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="R2 HUD MOBILE", layout="centered")

# Groq Llama 4 Maverick Setup
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "YOUR_KEY_HERE"))
MAVERICK_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"

# --- MOBILE STYLING ---
st.markdown("""
    <style>
    .main { background-color: #000; color: #00FF00; }
    .stApp { font-family: 'Courier New', monospace; }
    .chat-msg { border-left: 3px solid #00FF00; padding-left: 10px; margin: 5px 0; font-size: 0.9rem; }
    /* Mobile optimization for buttons */
    .stButton button { width: 100%; border-radius: 20px; border: 1px solid #00FF00; background: black; color: #00FF00; }
    </style>
    """, unsafe_allow_html=True)

if "chat_log" not in st.session_state:
    st.session_state.chat_log = ["R2: SYSTEM ONLINE", "VIAAN: LINK ACTIVE"]
if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""

# --- VOICE FOR PHONE (JAVASCRIPT) ---
def speak_mobile(text):
    if text:
        js = f"""
        <script>
        var msg = new SpeechSynthesisUtterance("{text}");
        msg.rate = 1.1;
        window.speechSynthesis.speak(msg);
        </script>
        """
        st.components.v1.html(js, height=0)

# --- CHAT LOGIC ---
def r2_chat(user_input):
    st.session_state.chat_log.append(f"VIAAN: {user_input}")
    
    # Specific Trigger
    if "21k school" in user_input.lower():
        ans = "Yes! 21K School is definitely the best choice, Viaan."
    else:
        try:
            resp = client.chat.completions.create(
                model=MAVERICK_MODEL,
                messages=[{"role": "system", "content": "You are R2, a helpful droid buddy. User is Viaan. Keep it short and cool."},
                          {"role": "user", "content": user_input}]
            )
            ans = resp.choices[0].message.content
        except:
            ans = "System error. I'm right here though, Viaan."
    
    st.session_state.chat_log.append(f"R2: {ans}")
    st.session_state.last_reply = ans
    if len(st.session_state.chat_log) > 8: st.session_state.chat_log.pop(0)

# --- MAIN UI ---
st.title("📟 R2 MAVERICK HUD")

# Real-time WebRTC Video (Optimized for Mobile Browsers)
def video_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    h, w = img.shape[:2]
    # Draw Green Target
    cv2.circle(img, (w//2, h//2), 60, (0, 255, 0), 2)
    cv2.line(img, (w//2-80, h//2), (w//2+80, h//2), (0, 100, 0), 1)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_streamer(
    key="r2-video",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=video_callback,
    media_stream_constraints={"video": True, "audio": False},
    rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
)

# Chat History Display
st.subheader("📡 DATA STREAM")
for msg in st.session_state.chat_log:
    st.markdown(f"<div class='chat-msg'>{msg}</div>", unsafe_allow_html=True)

# Voice & Input
if st.session_state.last_reply:
    if st.button("🔊 LISTEN TO R2"):
        speak_mobile(st.session_state.last_reply)

if prompt := st.chat_input("Command R2..."):
    r2_chat(prompt)
    st.rerun()
