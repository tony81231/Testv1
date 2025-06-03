import streamlit as st
import os
from PIL import Image
import io
import json
import zipfile
import shutil

# -----------------------------
# Config
# -----------------------------
CONFIG_PATH = "user_config.json"
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"ignore_ceiling_lights": False, "editing_steps": "", "comments": "", "style_mode": "BB Standards"}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

config = load_config()

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="AI HDR Editor", layout="wide")
st.title("🏠 AI HDR Real Estate Editor")

st.sidebar.header("User Settings")
config["ignore_ceiling_lights"] = st.sidebar.checkbox("Ignore ceiling lights in highlight clipping", value=config.get("ignore_ceiling_lights", False))

style_mode = st.sidebar.radio("Style Mode", ["BB Standards", "Style-Match"], index=0 if config.get("style_mode") == "BB Standards" else 1)
config["style_mode"] = style_mode

editing_steps = st.sidebar.text_area("Editing Steps (type manually):", value=config.get("editing_steps", ""))
config["editing_steps"] = editing_steps

comments = st.text_area("Optional Comments", value=config.get("comments", ""))
config["comments"] = comments

save_config(config)

# -----------------------------
# Training Mode
# -----------------------------
st.subheader("Training Mode")
before_images = st.file_uploader("Before Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
after_images = st.file_uploader("After Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# -----------------------------
# Process Images
# -----------------------------
if st.button("Begin Processing"):
    if not before_images:
        st.warning("Please upload at least one 'before' image.")
    else:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        with st.spinner("Processing images..."):
            for i, uploaded_file in enumerate(before_images):
                image = Image.open(uploaded_file).convert("RGB")
                if config["style_mode"] == "Style-Match" and after_images and i < len(after_images):
                    try:
                        reference = Image.open(after_images[i]).convert("RGB")
                        styled_image = Image.blend(image, reference, alpha=0.5)
                    except Exception:
                        styled_image = image
                else:
                    styled_image = image

                styled_image.save(f"{output_dir}/edited_{i+1}.jpg")

            # Create ZIP
            zip_path = "processed_images.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for filename in os.listdir(output_dir):
                    zipf.write(os.path.join(output_dir, filename), arcname=filename)

        st.success("✅ Processing complete!")
        with open(zip_path, "rb") as f:
            st.download_button("Download ZIP", data=f, file_name="processed_images.zip", mime="application/zip")

# -----------------------------
# Preview (Optional)
# -----------------------------
if before_images:
    st.subheader("📸 Preview Before Images")
    cols = st.columns(min(4, len(before_images)))
    for i, file in enumerate(before_images):
        img = Image.open(file)
        cols[i % len(cols)].image(img, caption=file.name, use_column_width=True)

if after_images:
    st.subheader("🎯 Preview After Images")
    cols = st.columns(min(4, len(after_images)))
    for i, file in enumerate(after_images):
        img = Image.open(file)
        cols[i % len(cols)].image(img, caption=file.name, use_column_width=True)
