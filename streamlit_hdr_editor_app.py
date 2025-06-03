import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import json

# ------------------ Config ------------------
CONFIG_FILE = "user_config.json"
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"ignore_ceiling_lights": False, "selected_steps": []}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# ------------------ UI Setup ------------------
st.set_page_config(page_title="AI HDR Editor", layout="wide")
st.title("AI HDR Real Estate Editor")

config = load_config()

st.sidebar.title("User Settings")
config['ignore_ceiling_lights'] = st.sidebar.checkbox("Ignore ceiling lights in highlight clipping", value=config.get('ignore_ceiling_lights', False))

# 17 Client Editing Step Toggles
step_labels = [
    "1. Image sharpening",
    "2. Remove photographer’s reflection",
    "3. HDR bracketing with indoor window replacement",
    "4. Add fire to fireplaces",
    "5. Flash reflection removal",
    "6. Dust spot removal",
    "7. TV screen replacement",
    "8. Tone adjustment",
    "9. Ocean/River Water Enhancement",
    "10. Remove pool cleaners from water",
    "11. Lawn enhancement – repair or replace",
    "12. Sky Replacement",
    "13. Brightness & contrast adjustment",
    "14. Lens distortion removal",
    "15. Remove minor blemishes",
    "16. Vertical & horizontal straightening",
    "17. White balancing"
]

selected_steps = st.sidebar.multiselect("Select Editing Steps", step_labels, default=config.get("selected_steps", []))
config['selected_steps'] = selected_steps
save_config(config)

# ------------------ File Upload ------------------
st.subheader("Upload Raw Bracketed Files")
uploaded_files = st.file_uploader("Upload HDR bracketed images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.subheader("Optional Comments")
user_comments = st.text_area("Comments for the editor (e.g. remove cables, fix wall)")

# ------------------ Display Training Data ------------------
st.subheader("Training Mode")
st.markdown("Upload before and after examples to train the style matcher.")
before_training = st.file_uploader("Before Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="before")
after_training = st.file_uploader("After Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="after")

if st.button("Begin Processing"):
    if not uploaded_files:
        st.warning("Please upload at least one HDR image.")
    else:
        st.success("Processing started. This is where HDR merge, QC, and fixing logic will run.")

        # Placeholder logic
        for uploaded_file in uploaded_files:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)

        if before_training and after_training:
            st.success("Training style matcher from provided examples.")
            st.write(f"Loaded {len(before_training)} before and {len(after_training)} after images.")
        else:
            st.info("Style match training skipped: no examples provided.")

        st.write("\n**Selected Steps for Processing:**")
        st.write("\n".join(selected_steps))

        if config['ignore_ceiling_lights']:
            st.write("\n- Ceiling light highlight clipping will be ignored.")

        if user_comments:
            st.write(f"\n**User Comments:** {user_comments}")
