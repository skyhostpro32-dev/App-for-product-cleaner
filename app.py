import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io
from rembg import remove
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="AI Smart Product Cleaner", layout="centered")

st.title("🛍️ AI Product Cleaner (Smart Brush)")

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((600, 400))
    img_np = np.array(image)

    st.image(image, caption="Original")

    # -----------------------
    # 🤖 AI Background Removal
    # -----------------------
    if st.button("Remove Background (AI)"):
        with st.spinner("AI Processing..."):
            output = remove(image)
            output_np = np.array(output)

            alpha = output_np[:, :, 3]
            st.session_state["alpha"] = alpha
            st.session_state["fg"] = output_np[:, :, :3]

        st.success("AI Background Removed")

    # -----------------------
    # ✏️ SMART BRUSH
    # -----------------------
    if "fg" in st.session_state:

        st.subheader("✏️ Smart Brush Correction")

        fg = st.session_state["fg"]
        alpha = st.session_state["alpha"]

        col1, col2 = st.columns(2)

        with col1:
            st.image(fg, caption="AI Result")

        with col2:
            canvas = st_canvas(
                fill_color="rgba(255, 0, 0, 0.3)",
                stroke_width=15,
                stroke_color="red",
                height=400,
                width=600,
                drawing_mode="freedraw",
                key="canvas",
            )

        if st.button("Apply Smart Correction"):

            smart_mask = alpha.copy()

            # Get user brush
            if canvas.image_data is not None:
                user_mask = canvas.image_data[:, :, 3]
                user_mask = (user_mask > 0).astype("uint8") * 255

                # 🔥 SMART EXPANSION
                kernel = np.ones((25, 25), np.uint8)
                expanded = cv2.dilate(user_mask, kernel, iterations=2)

                # Combine with AI mask
                smart_mask = cv2.bitwise_or(alpha, expanded)

            # -----------------------
            # ⚪ White Background
            # -----------------------
            white_bg = np.ones_like(fg) * 255

            fg_part = cv2.bitwise_and(fg, fg, mask=smart_mask)
            bg_part = cv2.bitwise_and(white_bg, white_bg, mask=cv2.bitwise_not(smart_mask))

            final = cv2.add(fg_part, bg_part)

            result_img = Image.fromarray(final)

            st.image(result_img, caption="Final Result")

            # Download
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")

            st.download_button(
                "Download",
                data=buf.getvalue(),
                file_name="smart_result.png",
                mime="image/png"
            )
