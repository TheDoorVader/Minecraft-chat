import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_server_state import server_state, server_state_lock
import cv2
import numpy as np
import easyocr
import re

# 1. Setup Shared "Whiteboard" for Coordinates
if "player_coords" not in server_state:
    with server_state_lock["player_coords"]:
        server_state["player_coords"] = {}

st.title("🎙️ Minecraft Realm Proximity Chat")

# User Name Setup
my_name = st.text_input("Enter your Minecraft Name:", "Player1")

# 2. OCR Reading Part (The "Eyes")
reader = st.cache_resource(lambda: easyocr.Reader(['en']))()
img_file = st.camera_input("Scan Coordinates")

if img_file:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    results = reader.readtext(image)
    full_text = " ".join([res[1] for res in results])
    coords = re.findall(r'-?\d+', full_text)
    
    if len(coords) >= 3:
        x, y, z = int(coords[0]), int(coords[1]), int(coords[2])
        # Write our coords to the shared whiteboard
        with server_state_lock["player_coords"]:
            server_state["player_coords"][my_name] = (x, z)
        st.success(f"Position Locked: {x}, {z}")

# 3. Voice Chat Part (The "Mouth")
st.subheader("Join Voice Channel")
webrtc_ctx = webrtc_streamer(
    key="proximity-voice",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": False, "audio": True},
)

# 4. Show who is nearby
st.write("---")
st.subheader("Nearby Players")
if my_name in server_state["player_coords"]:
    my_pos = server_state["player_coords"][my_name]
    for p_name, p_pos in server_state["player_coords"].items():
        if p_name != my_name:
            dist = ((my_pos[0] - p_pos[0])**2 + (my_pos[1] - p_pos[1])**2)**0.5
            status = "🔊 AUDIBLE" if dist < 20 else "🔇 TOO FAR"
            st.write(f"**{p_name}**: {int(dist)} blocks away ({status})")
            
