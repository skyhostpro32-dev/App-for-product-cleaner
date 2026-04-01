import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import io
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="AI Product Photo Cleaner", layout="centered")

st.title("🛍️ AI Product Photo Cleaner")

uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((600, 400))
    img_np = np.array(image)

    st.image(image, caption="Original Image")

    st.subheader("✏️ Step 1: Remove unwanted parts (optional)")

    col1, col2 = st.columns(2)

    with col1:
        st.image(image)

    with col2:
        canvas = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=25,
            stroke_color="red",
            height=400,
            width=600,
            drawing_mode="freedraw",
            key="canvas",
        )

    st.subheader("⚙️ Step 2: Choose Enhancements")

    white_bg_option = st.checkbox("⚪ Apply White Background")
    shadow_option = st.checkbox("🌫️ Add Shadow")
    enhance_option = st.checkbox("✨ Enhance Image")

    if st.button("🚀 Process Image"):

        result = img_np.copy()

        # -------------------------------
        # 🧠 Manual Object Removal
        # -------------------------------
        if canvas.image_data is not None:
            mask = canvas.image_data[:, :, 3]
            mask = (mask > 0).astype("uint8") * 255

            if np.sum(mask) > 0:
                kernel = np.ones((7, 7), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=2)
                result = cv2.inpaint(result, mask, 3, cv2.INPAINT_TELEA)

        # -------------------------------
        # ⚪ Improved White Background
        # -------------------------------
        if white_bg_option:
            gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)

            edges = cv2.Canny(gray, 50, 150)

            kernel = np.ones((5, 5), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=2)

            mask_inv = cv2.bitwise_not(edges)
            mask_inv = cv2.GaussianBlur(mask_inv, (21, 21), 0)

            white_bg = np.ones_like(result) * 255

            fg = cv2.bitwise_and(result, result, mask=mask_inv)
            bg = cv2.bitwise_and(white_bg, white_bg, mask=cv2.bitwise_not(mask_inv))

            result = cv2.add(fg, bg)

        # -------------------------------
        # ✨ Enhancement
        # -------------------------------
        result_img = Image.fromarray(result)

        if enhance_option:
            contrast = ImageEnhance.Contrast(result_img)
            result_img = contrast.enhance(1.3)

            sharp = ImageEnhance.Sharpness(result_img)
            result_img = sharp.enhance(1.5)

        # -------------------------------
        # 🌫️ Shadow
        # -------------------------------
        if shadow_option:
            shadow = np.zeros_like(result) + 50
            shadow = cv2.GaussianBlur(shadow, (51, 51), 0)
            result_shadow = cv2.addWeighted(np.array(result_img), 1, shadow, 0.3, 0)
            result_img = Image.fromarray(result_shadow)

        # -------------------------------
        # ✅ Show Result
        # -------------------------------
        st.subheader("✅ Result")
        st.image(result_img)

        # -------------------------------
        # 📥 Download
        # -------------------------------
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")

        st.download_button(
            "📥 Download Image",
            data=buf.getvalue(),
            file_name="product_clean.png",
            mime="image/png"
        )
