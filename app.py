import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io
from rembg import remove
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="AI Product Cleaner PRO", layout="centered")

st.title("🛍️ AI Product Photo Cleaner (PRO)")

uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((600, 400))
    img_np = np.array(image)

    st.image(image, caption="Original Image")

    # -------------------------------
    # 🤖 Step 1: AI Background Removal
    # -------------------------------
    st.subheader("🤖 Step 1: Auto Background Removal")

    if st.button("Remove Background (AI)"):
        with st.spinner("Processing AI..."):
            output = remove(image)
            output_np = np.array(output)

            if output_np.shape[2] == 4:
                alpha = output_np[:, :, 3]
            else:
                alpha = cv2.cvtColor(output_np, cv2.COLOR_RGB2GRAY)

            st.session_state["alpha_mask"] = alpha
            st.session_state["ai_result"] = output_np[:, :, :3]

        st.success("Background removed!")

    # -------------------------------
    # ✏️ Step 2: Manual Fix
    # -------------------------------
    if "ai_result" in st.session_state:

        st.subheader("✏️ Step 2: Fix with Brush")

        result = st.session_state["ai_result"]

        col1, col2 = st.columns(2)

        with col1:
            st.image(result, caption="AI Result")

        with col2:
            canvas = st_canvas(
                fill_color="rgba(255, 0, 0, 0.3)",
                stroke_width=20,
                stroke_color="red",
                height=400,
                width=600,
                drawing_mode="freedraw",
                key="canvas",
            )

        # -------------------------------
        # ⚙️ Step 3: Final Output
        # -------------------------------
        st.subheader("⚙️ Step 3: Generate Final Image")

        if st.button("Generate Clean Image"):

            final = result.copy()

            # Apply manual mask removal
            if canvas.image_data is not None:
                mask = canvas.image_data[:, :, 3]
                mask = (mask > 0).astype("uint8") * 255

                if np.sum(mask) > 0:
                    kernel = np.ones((7, 7), np.uint8)
                    mask = cv2.dilate(mask, kernel, iterations=2)
                    final = cv2.inpaint(final, mask, 3, cv2.INPAINT_TELEA)

            # Apply white background using AI alpha
            alpha = st.session_state["alpha_mask"]

            white_bg = np.ones_like(final) * 255

            fg = cv2.bitwise_and(final, final, mask=alpha)
            bg = cv2.bitwise_and(white_bg, white_bg, mask=cv2.bitwise_not(alpha))

            combined = cv2.add(fg, bg)

            result_img = Image.fromarray(combined)

            st.subheader("✅ Final Result")
            st.image(result_img)

            # Download
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")

            st.download_button(
                "📥 Download Image",
                data=buf.getvalue(),
                file_name="pro_result.png",
                mime="image/png"
            )
