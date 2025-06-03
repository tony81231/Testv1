
import streamlit as st
import os
from PIL import Image
import numpy as np
import cv2
import tempfile
import traceback

st.set_page_config(page_title="AI HDR Debug Editor", layout="wide")
st.title("🔧 Debug Mode: AI HDR Real Estate Editor")

# Sidebar settings
st.sidebar.header("Settings")
ignore_lights = st.sidebar.checkbox("Ignore ceiling lights", value=True)
style_mode = st.sidebar.radio("Style Mode", ["BB Standards", "Style-Match"])
steps = st.sidebar.text_area("Editing Instructions (Manual)")
comments = st.sidebar.text_area("Optional Comments")

# File upload
st.subheader("Upload HDR Bracketed Images (3+ exposures)")
uploads = st.file_uploader("Upload JPG/PNG files", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Log function
def debug_log(message):
    st.code(f"[DEBUG] {message}")

if uploads:
    debug_log(f"{len(uploads)} files uploaded.")

if st.button("Run HDR Merge"):
    if not uploads or len(uploads) < 2:
        st.warning("Please upload at least 2 bracketed images.")
    else:
        try:
            st.info("Beginning processing...")
            temp_dir = tempfile.mkdtemp()
            debug_log(f"Temporary directory: {temp_dir}")
            image_paths = []

            for file in uploads:
                path = os.path.join(temp_dir, file.name)
                with open(path, "wb") as f:
                    f.write(file.read())
                image_paths.append(path)

            debug_log(f"Saved {len(image_paths)} images.")

            # Load images
            images = []
            for path in image_paths:
                img = cv2.imread(path)
                if img is None:
                    debug_log(f"Failed to read: {path}")
                    continue
                debug_log(f"Read image: {path} shape={img.shape}")
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                images.append(img_rgb)

            if len(images) < 2:
                st.error("Failed to read at least 2 valid images.")
            else:
                debug_log("Starting Mertens HDR merge...")
                merge_mertens = cv2.createMergeMertens()
                blended = merge_mertens.process(images)
                final_image = (blended * 255).astype("uint8")
                st.image(final_image, caption="HDR Output", use_container_width=True)

                output_path = os.path.join(temp_dir, "debug_output.jpg")
                Image.fromarray(final_image).save(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("Download HDR Output", f, file_name="debug_output.jpg")

        except Exception as e:
            st.error(f"Exception occurred: {str(e)}")
            st.code(traceback.format_exc())
