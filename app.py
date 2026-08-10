import os
import tempfile
import time
import cv2
import streamlit as st
from PIL import Image

from src.preprocess import (
    load_image,
    convert_to_grayscale,
    apply_threshold,
    remove_noise,
)

from src.ocr_engine import (
    extract_text,
    extract_text_with_boxes,
)

from src.extractor import extract_details
from src.validator import validate_details
from src.exporter import export_json, export_csv


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="DriveSight AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def load_css():
    with open("assets/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


load_css()


def display_value(value):
    if value in [None, "", "Not Found"]:
        return "Not Found"
    return value


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown("""
<div style="
background:linear-gradient(135deg,#2563EB,#1D4ED8);
padding:40px;
border-radius:22px;
box-shadow:0 10px 30px rgba(37,99,235,.4);
margin-bottom:30px;
">

<h1 style="margin:0;color:white;">
🚗 DriveSight AI
</h1>

<h3 style="color:#E5E7EB;">
AI Powered Driving Licence Recognition
</h3>

<p style="color:white;font-size:18px;">
Recognize • Extract • Validate • Export
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("""
### AI-Powered Driving Licence Recognition

Upload → OCR → Extract → Validate → Export
""")

st.divider()

# ---------------------------------------------------
# UPLOAD
# ---------------------------------------------------

st.markdown("## 📂 Upload Driving Licence")

uploaded_file = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG / PNG",
    label_visibility="collapsed"
)

st.divider()

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        use_container_width=True
    )

    if st.button(
        "🚀 Extract Information",
        use_container_width=True
    ):

        with st.spinner("Running OCR..."):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".jpg"
            ) as tmp:

                tmp.write(uploaded_file.getbuffer())
                image_path = tmp.name

            start_time = time.time()

            progress = st.progress(0)

            try:

                progress.progress(10)

                opencv_image = load_image(image_path)

                gray = convert_to_grayscale(opencv_image)

                threshold = apply_threshold(gray)

                clean = remove_noise(threshold)

                progress.progress(35)

                text = extract_text(clean)

                ocr_results = extract_text_with_boxes(clean)

                progress.progress(60)

                if ocr_results:

                    avg_confidence = (
                        sum(
                            result[2]
                            for result in ocr_results
                        )
                        / len(ocr_results)
                    ) * 100

                else:

                    avg_confidence = 0

                details = extract_details(text)

                details, validation = validate_details(details)

                progress.progress(80)

                filled = sum(
                    value not in [None, "", "Not Found"]
                    for value in details.values()
                )

                total_fields = len(details)

                processing_time = (
                    time.time() - start_time
                )

                boxed_image = opencv_image.copy()

                for result in ocr_results:

                    box = result[0]

                    detected_text = result[1]

                    confidence = result[2]

                    top_left = tuple(
                        map(int, box[0])
                    )

                    bottom_right = tuple(
                        map(int, box[2])
                    )

                    if confidence >= 0.85:

                        color = (0, 255, 0)

                    elif confidence >= 0.60:

                        color = (0, 255, 255)

                    else:

                        color = (0, 0, 255)

                    cv2.rectangle(
                        boxed_image,
                        top_left,
                        bottom_right,
                        color,
                        2
                    )

                    cv2.putText(
                        boxed_image,
                        f"{detected_text} ({confidence:.2f})",
                        (top_left[0], top_left[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        2
                    )

                progress.progress(100)

            except Exception as e:

                st.error(f"Error : {e}")

                st.stop()

            finally:

                if os.path.exists(image_path):

                    os.remove(image_path)

                                # ---------------------------------------------------
            # EXTRACTION COMPLETE
            # ---------------------------------------------------

            st.success("✅ Extraction Complete!")

            # ---------------------------------------------------
            # AI SUMMARY
            # ---------------------------------------------------

            st.markdown(f"""
            <div style="
                background:linear-gradient(135deg,#1E3A8A,#2563EB);
                padding:25px;
                border-radius:18px;
                color:white;
                box-shadow:0 8px 18px rgba(0,0,0,.18);
                margin-bottom:25px;
            ">

            <h2 style="margin-top:0;">
            🤖 AI Analysis Summary
            </h2>

            <hr style="border:1px solid rgba(255,255,255,.2);">

            <p style="font-size:18px;">
            ✅ OCR completed successfully
            </p>

            <p style="font-size:18px;">
            📄 <b>Fields Extracted:</b> {filled}/{total_fields}
            </p>

            <p style="font-size:18px;">
            🎯 <b>Average Confidence:</b> {avg_confidence:.2f}%
            </p>

            <p style="font-size:18px;">
            ⚡ <b>Processing Time:</b> {processing_time:.2f} sec
            </p>

            </div>
            """, unsafe_allow_html=True)


            # ---------------------------------------------------
            # OCR QUALITY
            # ---------------------------------------------------

            if avg_confidence >= 90:

                st.success("🟢 Excellent OCR Quality")

            elif avg_confidence >= 75:

                st.warning("🟡 Good OCR Quality")

            else:

                st.error("🔴 Poor OCR Quality")


            # ---------------------------------------------------
            # OCR COMPARISON
            # ---------------------------------------------------

            st.header("🖼 OCR Comparison")

            left, right = st.columns(2)

            with left:

                st.subheader("📷 Original Licence")

                st.image(
                    image,
                    use_container_width=True
                )

            with right:

                st.subheader("🔍 OCR Detection")

                st.image(
                    cv2.cvtColor(
                        boxed_image,
                        cv2.COLOR_BGR2RGB
                    ),
                    use_container_width=True
                )

            st.divider()


            # ---------------------------------------------------
            # DOWNLOAD OCR IMAGE
            # ---------------------------------------------------

            _, buffer = cv2.imencode(
                ".png",
                boxed_image
            )

            st.download_button(
                "📥 Download OCR Image",
                data=buffer.tobytes(),
                file_name="ocr_detection.png",
                mime="image/png",
                use_container_width=True
            )

            st.divider()


            # ---------------------------------------------------
            # AI DASHBOARD
            # ---------------------------------------------------

            st.header("📊 AI Dashboard")

            c1, c2, c3, c4 = st.columns(4)

            # ---------------- CARD 1 ---------------- #

with c1:

    st.markdown(f"""
    <div style="
    background:linear-gradient(135deg,#2563EB,#1D4ED8);
    padding:22px;
    border-radius:20px;
    text-align:center;
    color:white;
    box-shadow:0 10px 25px rgba(37,99,235,.30);
    ">

    <h1>📝</h1>

    <h2>{len(text)}</h2>

    <p>Words Detected</p>

    </div>
    """, unsafe_allow_html=True)


# ---------------- CARD 2 ---------------- #

with c2:

    st.markdown(f"""
    <div style="
    background:linear-gradient(135deg,#10B981,#059669);
    padding:22px;
    border-radius:20px;
    text-align:center;
    color:white;
    box-shadow:0 10px 25px rgba(16,185,129,.30);
    ">

    <h1>🎯</h1>

    <h2>{avg_confidence:.1f}%</h2>

    <p>Confidence</p>

    </div>
    """, unsafe_allow_html=True)


# ---------------- CARD 3 ---------------- #

with c3:

    st.markdown(f"""
    <div style="
    background:linear-gradient(135deg,#F59E0B,#D97706);
    padding:22px;
    border-radius:20px;
    text-align:center;
    color:white;
    box-shadow:0 10px 25px rgba(245,158,11,.30);
    ">

    <h1>⚡</h1>

    <h2>{processing_time:.2f}s</h2>

    <p>Processing Time</p>

    </div>
    """, unsafe_allow_html=True)


# ---------------- CARD 4 ---------------- #

with c4:

    st.markdown(f"""
    <div style="
    background:linear-gradient(135deg,#8B5CF6,#7C3AED);
    padding:22px;
    border-radius:20px;
    text-align:center;
    color:white;
    box-shadow:0 10px 25px rgba(124,58,237,.30);
    ">

    <h1>📄</h1>

    <h2>{filled}/{total_fields}</h2>

    <p>Fields Extracted</p>

    </div>
    """, unsafe_allow_html=True)

st.divider()
                        # =====================================================
            # EXTRACTED INFORMATION
            # =====================================================

st.header("📋 Extracted Information")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.metric(
        "👤 Full Name",
        display_value(details.get("name"))
    )

    st.metric(
        "🪪 Licence Number",
        display_value(details.get("license_number"))
    )

    st.metric(
        "🎂 Date of Birth",
            display_value(details.get("dob"))
    )

with col2:

    st.metric(
        "📅 Issue Date",
        display_value(details.get("issue_date"))
    )

    st.metric(
        "📅 Expiry Date",
        display_value(details.get("expiry_date"))
    )

    validation_status = validation.get(
        "license_number",
        "Unknown"
    )

                if validation_status == "Valid":
                    validation_display = "🟢 Valid"
                elif validation_status == "Invalid":
                    validation_display = "🔴 Invalid"
                else:
                    validation_display = "🟡 Unknown"

                st.metric(
                    "✅ Validation",
                    validation_display
                )

            st.divider()

            # =====================================================
            # MISSING FIELDS
            # =====================================================

            missing = [
                key.replace("_", " ").title()
                for key, value in details.items()
                if value in [None, "", "Not Found"]
            ]

            st.subheader("🔍 Extraction Report")

            if missing:

                st.warning(
                    "⚠ Missing Fields:\n\n• "
                    + "\n• ".join(missing)
                )

            else:

                st.success(
                    "✅ All expected fields extracted successfully."
                )

            st.divider()

            # =====================================================
            # RAW OCR
            # =====================================================

            with st.expander(
                "📜 View Raw OCR Output",
                expanded=False
            ):

                if text:

                    for line in text:

                        st.write("•", line)

                else:

                    st.info("No text detected.")

            st.divider()

            # =====================================================
            # EXPORT
            # =====================================================

            st.header("📥 Export Results")

            json_data = export_json(details)

            csv_data = export_csv(details)

            e1, e2 = st.columns(2)

            with e1:

                st.download_button(
                    "📄 Download JSON",
                    data=json_data,
                    file_name="license_details.json",
                    mime="application/json",
                    use_container_width=True,
                )

            with e2:

                st.download_button(
                    "📊 Download CSV",
                    data=csv_data,
                    file_name="license_details.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.success("Export completed successfully ✔")

            st.divider()

                        # =====================================================
            # PROJECT INSIGHTS
            # =====================================================

            st.header("📈 Project Insights")

            insight1, insight2 = st.columns(2)

            with insight1:

                st.info("""
### 🤖 AI Processing Pipeline

✔ Image Upload

✔ Image Preprocessing

✔ OCR using EasyOCR

✔ Text Extraction

✔ Information Validation

✔ JSON / CSV Export
""")

            with insight2:

                st.info("""
### 🛠 Technologies Used

• Python

• Streamlit

• OpenCV

• EasyOCR

• Pillow

• Regex

• JSON

• CSV
""")

            st.divider()

            # =====================================================
            # WHY DRIVESIGHT AI
            # =====================================================

            st.header("✨ Why DriveSight AI?")

            feature1, feature2, feature3 = st.columns(3)

            with feature1:

                st.success("""
### ⚡ Fast

Processes licence within seconds.
""")

            with feature2:

                st.success("""
### 🎯 Accurate

AI-assisted OCR with confidence score.
""")

            with feature3:

                st.success("""
### 📥 Export Ready

Download JSON, CSV and OCR image instantly.
""")

            st.divider()

            # =====================================================
            # ABOUT
            # =====================================================

            st.header("ℹ About Project")

            st.markdown("""
DriveSight AI is an **AI-powered Driving Licence Information Extraction System** built using
Computer Vision and Optical Character Recognition (OCR).

The application automatically:

- Detects text from driving licences
- Extracts important fields
- Validates licence information
- Generates structured outputs
- Exports data in multiple formats

This project demonstrates practical applications of **Artificial Intelligence, Computer Vision,
Image Processing and OCR**.
""")

            st.divider()

            # =====================================================
            # FOOTER
            # =====================================================

            st.markdown("""
<hr>

<div style="text-align:center;">

<h2>🚗 DriveSight AI</h2>

<h4>AI Powered Driving Licence Recognition System</h4>

<p>
Built with ❤️ using
<b>Python</b>,
<b>OpenCV</b>,
<b>EasyOCR</b>,
<b>Streamlit</b>
</p>

<p>
Developed by <b>Trisha Verma</b>
</p>

<p style="color:gray;">
Version 1.0
</p>

</div>
""", unsafe_allow_html=True)