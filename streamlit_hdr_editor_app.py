import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import json

# Ensure training data folder exists
os.makedirs("training_data", exist_ok=True)

st.set_page_config(page_title="HDR AI Editor", layout="wide")
st.title("📸 AI HDR Real Estate Editor (BoxBrownie Style)")

# ---------- Functions ----------
def merge_hdr(images):
    merge = cv2.createMergeDebevec()
    hdr = merge.process(images)
    tonemap = cv2.createTonemap(gamma=2.2)
    ldr = tonemap.process(hdr)
    return np.clip(ldr * 255, 0, 255).astype('uint8')

def analyze_qc(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return {
        "brightness": float(np.mean(gray)),
        "contrast": float(np.std(gray)),
        "highlight_clipping": float(np.sum(img > 245)) / img.size > 0.01
    }

def fix_image(img, qc):
    result = img.copy()
    if qc['brightness'] < 100:
        result = cv2.convertScaleAbs(result, alpha=1.2, beta=40)
    if qc['contrast'] < 40:
        lab = cv2.cvtColor(result, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
        cl = clahe.apply(l)
        result = cv2.cvtColor(cv2.merge((cl,a,b)), cv2.COLOR_LAB2RGB)
    return result

def apply_style_match(img, after_img):
    matched = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype('float32')
    target = cv2.cvtColor(after_img, cv2.COLOR_RGB2LAB).astype('float32')
    for i in range(3):
        mean_src, std_src = cv2.meanStdDev(matched[:,:,i])
        mean_tgt, std_tgt = cv2.meanStdDev(target[:,:,i])
        matched[:,:,i] = (matched[:,:,i] - mean_src[0][0]) * (std_tgt[0][0] / (std_src[0][0] + 1e-5)) + mean_tgt[0][0]
    return cv2.cvtColor(np.clip(matched, 0, 255).astype('uint8'), cv2.COLOR_LAB2RGB)

# ---------- Sidebar Options ----------
steps = [
    "Image sharpening",
    "Remove photographer’s reflection",
    "HDR bracketing with indoor window replacement",
    "Add fire to fireplaces",
    "Flash reflection removal",
    "Dust spot removal",
    "TV screen replacement",
    "Tone adjustment",
    "Ocean/River Water Enhancement",
    "Remove pool cleaners from water",
    "Lawn enhancement – repair or replace",
    "Sky Replacement",
    "Brightness & contrast adjustment",
    "Lens distortion removal",
    "Remove minor blemishes",
    "Vertical & horizontal straightening",
    "White balancing"
]
selected_steps = [st.sidebar.checkbox(step, value=True) for step in steps]
ignore_lights = st.sidebar.checkbox("Ignore ceiling lights in highlight clipping", value=True)
training_mode = st.sidebar.checkbox("Enable Training Mode")

# ---------- Upload Interface ----------
st.subheader("📂 Upload Bracketed Images")
files = st.file_uploader("Upload 3+ bracketed exposures", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

after_example = st.file_uploader("Upload AFTER image (style match)", type=['jpg','jpeg','png'])
before_examples = st.file_uploader("Upload BEFORE images (for training)", type=['jpg','jpeg','png'], accept_multiple_files=True, key="before")
after_examples = st.file_uploader("Upload AFTER images (for training)", type=['jpg','jpeg','png'], accept_multiple_files=True, key="after")

comments = st.text_area("📋 Job Notes or Special Instructions")

# ---------- Main Logic ----------
if st.button("🚀 Run Editor") and files and len(files) >= 3:
    st.info("Processing HDR Merge...")
    imgs = [np.array(Image.open(f).convert('RGB')) for f in files]
    hdr_img = merge_hdr(imgs)
    st.image(hdr_img, caption="Merged HDR", use_column_width=True)

    qc = analyze_qc(hdr_img)
    st.write("QC Report:", qc)
    if ignore_lights:
        qc['highlight_clipping'] = False

    fixed_img = fix_image(hdr_img, qc)
    st.image(fixed_img, caption="Auto-Fixed", use_column_width=True)

    if after_example:
        after_img = np.array(Image.open(after_example).convert('RGB'))
        fixed_img = apply_style_match(fixed_img, after_img)
        st.image(fixed_img, caption="Styled to After Example", use_column_width=True)

    st.success("✅ Editing Complete")
    result_img = Image.fromarray(fixed_img)
    result_img.save("output_final.jpg")
    with open("output_final.jpg", "rb") as f:
        st.download_button("📥 Download Final Image", f, file_name="edited_hdr.jpg", mime="image/jpeg")

    # Training Mode
    if training_mode and before_examples and after_examples:
        st.success(f"Saved {len(before_examples)} BEFORE and {len(after_examples)} AFTER images.")
        for i, (b, a) in enumerate(zip(before_examples, after_examples)):
            with open(f"training_data/before_{i}.jpg", "wb") as bf:
                bf.write(b.read())
            with open(f"training_data/after_{i}.jpg", "wb") as af:
                af.write(a.read())
        st.write("Training data saved to /training_data.")

elif st.button("🚀 Run Editor"):
    st.warning("Please upload at least 3 bracketed exposures.")
