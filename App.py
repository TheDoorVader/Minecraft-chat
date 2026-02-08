import streamlit as st
import cv2
import numpy as np
import easyocr
import re

st.title("📍 Minecraft Proximity Link")
st.write("Point your phone at the coordinates on your screen.")

# Initialize OCR reader
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

# Camera Input
img_file = st.camera_input("Scan your coordinates")

if img_file:
    # Convert image to OCR format
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    # Run OCR
    results = reader.readtext(image)
    full_text = " ".join([res[1] for res in results])
    
    # Find numbers (X, Y, Z)
    coords = re.findall(r'-?\d+', full_text)
    
    if len(coords) >= 3:
        x, y, z = int(coords[0]), int(coords[1]), int(coords[2])
        st.success(f"Detected: X: {x}, Y: {y}, Z: {z}")
        
        # PROXIMITY LOGIC
        # Replace these with your friend's coordinates for testing
        friend_x, friend_z = 100, 200 
        distance = ((x - friend_x)**2 + (z - friend_z)**2)**0.5
        
        st.metric("Distance to Friend", f"{int(distance)} blocks")
        
        if distance < 15:
            st.warning("🔊 THEY CAN HEAR YOU (Close)")
        else:
            st.info("🔇 TOO FAR (Out of range)")
    else:
        st.error("Could not read coordinates. Make sure they are clear in the photo.")
      
