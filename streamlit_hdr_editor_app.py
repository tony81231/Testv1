import streamlit as st
import os
from PIL import Image
import numpy as np
import cv2
import tempfile

# Title and logo
st.set_page_config(page_title="AI HDR Real Estate Editor", layout="wide")
st.markdown("""
    <h1 style='text-align: center;'>🏡 AI HDR Real Estate Editor</h1>
""", unsafe_allow_html=True)

# Sidebar - Settings
st.sidebar.header("User Settings")
ignore_lights = st.sidebar.checkbox("Ignore ceiling lights in highlight clipping")
style_mode = st.sidebar.radio("Style Mode", ["BB Standards", "Style-Match"])
manual_steps = st.sidebar.text_area("Editing Steps (type manually):", height=120)
comments = st.sidebar.text_area("Optional Comments")

# Main area - Training mode
st.markdown("## Training Mode")
before_files = st.file_uploader("Before Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="before")
after_files = st.file_uploader("After Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="after")

# Raw uploads
st.markdown("## Raw HDR Brackets")
raw_uploads = st.file_uploader("Upload RAW bracketed images (3+ exposure levels)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="raw")

# Process
if st.button("Begin Processing"):
    if not raw_uploads:
        st.warning("Please upload raw bracketed images to begin processing.")
    else:
        with st.spinner("Processing images..."):
            temp_dir = tempfile.mkdtemp()
            merged_img = None

            # Save uploaded raw images temporarily
            paths = []
            for f in raw_uploads:
                path = os.path.join(temp_dir, f.name)
                with open(path, 'wb') as out:
                    out.write(f.read())
                paths.append(path)

            # Merge HDR basic fallback
            try:
                images = [cv2.imread(p) for p in paths]
                images = [cv2.cvtColor(img, cv2.COLOR_BGR2RGB) for img in images if img is not None]

                if len(images) >= 2:
                    merge_mertens = cv2.createMergeMertens()
                    blended = merge_mertens.process(images)
                    merged_img = (blended * 255).astype(np.uint8)
                else:
                    st.error("At least 2 valid bracket images required.")
            except Exception as e:
                st.error(f"HDR merge failed: {e}")

            # Post-processing placeholder
            if merged_img is not None:
                out_path = os.path.join(temp_dir, "edited_output.jpg")
                Image.fromarray(merged_img).save(out_path)
                st.image(merged_img, caption="Edited Output", use_container_width=True)
                with open(out_path, "rb") as f:
                    st.download_button("Download Final Image", f, file_name="edited_HDR_output.jpg")
            else:
                st.error("No image was processed.")
