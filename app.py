import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io

st.set_page_config(page_title="AI Click Object Remover", layout="centered")

st.title("🧠 AI Click Object Remover (No Canvas)")

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    st.image(image, caption="Click position to remove object")

    x = st.slider("X Position", 0, image.width, image.width // 2)
    y = st.slider("Y Position", 0, image.height, image.height // 2)

    tolerance = st.slider("AI Sensitivity", 5, 50, 20)

    if st.button("Remove Object"):

        # Convert to BGR (OpenCV)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Create mask
        mask = np.zeros((image.height + 2, image.width + 2), np.uint8)

        # Flood fill (AI-like region)
        _, _, _, rect = cv2.floodFill(
            img_bgr.copy(),
            mask,
            seedPoint=(x, y),
            newVal=(255, 255, 255),
            loDiff=(tolerance, tolerance, tolerance),
            upDiff=(tolerance, tolerance, tolerance),
        )

        # Extract filled region
        mask = mask[1:-1, 1:-1] * 255

        # Smooth mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # Inpaint
        result = cv2.inpaint(img_np, mask, 3, cv2.INPAINT_TELEA)

        result_img = Image.fromarray(result)

        st.image(result_img, caption="Result")

        # Download
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")

        st.download_button(
            "Download",
            data=buf.getvalue(),
            file_name="removed.png",
            mime="image/png"
        )
