import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from streamlit_cropper import st_cropper
from PIL import Image

st.set_page_config(page_title="AI Watermark Remover", layout="centered")

st.title("🎬 Video Watermark Remover")
st.write("Video upload karein aur watermark area select karein.")

# 1. File Upload
uploaded_file = st.file_uploader("Video select karein...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Temporary file save karna
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    # Video ka pehla frame nikalna
    cap = cv2.VideoCapture(tfile.name)
    ret, frame = cap.read()
    cap.release()

    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        st.subheader("Step 2: Watermark select karein")
        
        # --- YAHAN BADLAV KIYA HAI (return_type='box') ---
        rect = st_cropper(img, realtime_update=True, box_color='#00FF00', aspect_ratio=None, return_type='box')
        
        if rect:
            # Coordinates dictionary se nikalna
            x = int(rect['left'])
            y = int(rect['top'])
            w = int(rect['width'])
            h = int(rect['height'])
            
            st.write(f"Selected Area: x={x}, y={y}, w={w}, h={h}")

            if st.button("🚀 Watermark Hatao aur Download Karo"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Processing Logic
                cap = cv2.VideoCapture(tfile.name)
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                output_path = "cleaned_video.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                mask = np.zeros((height, width), dtype=np.uint8)
                mask[y:y+h, x:x+w] = 255
                
                count = 0
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret: break
                    
                    # Magic Inpainting
                    res = cv2.inpaint(frame, mask, 7, cv2.INPAINT_TELEA)
                    out.write(res)
                    
                    count += 1
                    if count % 10 == 0:
                        progress = count / total_frames
                        progress_bar.progress(min(progress, 1.0))
                        status_text.text(f"Processing: {int(progress*100)}%")
                
                cap.release()
                out.release()
                
                st.success("✅ Kaam ho gaya!")
                
                # Download Button
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Clean Video",
                        data=file,
                        file_name="no_watermark.mp4",
                        mime="video/mp4"
                    )