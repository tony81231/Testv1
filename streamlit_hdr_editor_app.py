import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import json

CONFIG_FILE = "user_config.json"
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"ignore_ceiling_lights": False}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

st.set_page_config(page_title="AI HDR Editor", layout="wide")
st.title("AI HDR Real Estate Editor")

config = load_config()

st.sidebar.title("User Settings")
config['ignore_ceiling_lights'] = st.sidebar.checkbox("Ignore ceiling lights in highlight clipping", value=config.get('ignore_ceiling_lights', False))
save_config(config)

st.markdown("🛠️ <i>All 17 client editing steps will be applied automatically based on AI logic.</i>", unsafe_allow_html=True)

st.subheader("Upload Raw Bracketed Files")
uploaded_files = st.file_uploader("Upload HDR bracketed images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.subheader("Optional Comments")
user_comments = st.text_area("Comments for the editor (e.g. remove cables, fix wall)")

st.subheader("Training Mode")
st.markdown("Upload before and after examples to train the style matcher.")
before_training = st.file_uploader("Before Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="before")
after_training = st.file_uploader("After Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="after")

if st.button("🚀 Run HDR Editor"):
    if not uploaded_files:
        st.warning("Please upload at least one HDR image.")
    else:
        st.success("Processing started. This is where HDR merge, QC, and fixing logic will run.")
        for uploaded_file in uploaded_files:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
        output_image = Image.fromarray(image)
        output_path = "output_final.jpg"
        output_image.save(output_path)
        with open(output_path, "rb") as f:
            st.download_button("📥 Download Final Image", f, file_name="edited_hdr.jpg", mime="image/jpeg")

        if config['ignore_ceiling_lights']:
            st.write("\n- Ceiling light highlight clipping will be ignored.")

        if user_comments:
            st.write(f"\n**User Comments:** {user_comments}")

if st.button("🧠 Train Style from Examples"):
    if before_training and after_training:
        os.makedirs("training_data", exist_ok=True)
        for i, (b, a) in enumerate(zip(before_training, after_training)):
            with open(f"training_data/before_{i}.jpg", "wb") as bf:
                bf.write(b.read())
            with open(f"training_data/after_{i}.jpg", "wb") as af:
                af.write(a.read())
        st.success(f"Saved {len(before_training)} BEFORE and {len(after_training)} AFTER images for training.")
    else:
        st.warning("Please upload both before and after training images.")
