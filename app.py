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


# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Smart Driving Licence OCR",
    page_icon="🚗",
    layout="wide"
)

def load_css():
    with open("assets/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

# ---------------- HELPER FUNCTION ---------------- #

def display_value(value):
    if value:
        return value
    return "Not Found"


# ---------------- HEADER ---------------- #

st.markdown("""
<div class="hero-card">

# 🚗Smart Driving Licence OCR

### AI-Powered Driving Licence Recognition System

Extract • Validate • Export • Analyze

Built using EasyOCR, OpenCV and Artificial Intelligence.

</div>
""", unsafe_allow_html=True)

st.divider()


# ---------------- SIDEBAR ---------------- #

st.sidebar.image(
    "https://img.icons8.com/fluency/96/car--v1.png",
    width=80,
)

st.sidebar.title("DriveSight AI")

st.sidebar.markdown("### Version 2.0")

st.sidebar.markdown("---")

st.sidebar.success("Features")

st.sidebar.markdown("""
✅ OCR Detection

✅ AI Information Extraction

✅ Validation

✅ JSON Export

✅ CSV Export

🚧 PDF Support

🚧 Excel Export

🚧 History
""")

st.sidebar.markdown("---")

st.sidebar.info(
    "Built with ❤️ using Python, EasyOCR, OpenCV and Streamlit."
)

st.markdown("""
<div class="upload-box">

## 📂 Upload Driving Licence

Supported formats:

**JPG • PNG • JPEG**

</div>
""", unsafe_allow_html=True)

# ---------------- IMAGE UPLOAD ---------------- #

uploaded_file = st.file_uploader(
    "Upload Driving Licence",
    type=["jpg", "jpeg", "png"]
)


if uploaded_file:

    left, right = st.columns([1, 1])

    with left:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Image",
            use_container_width=True
        )

    with right:

        if st.button("Extract Information", use_container_width=True):

            with st.spinner("Processing image..."):

                # Save uploaded image temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".jpg"
                ) as tmp:

                    tmp.write(uploaded_file.getbuffer())
                    image_path = tmp.name


                # ✅ Start timer here
                start_time = time.time()

                progress = st.progress(0)
                progress.progress(10)

                
                try:

                    # ---------------- PREPROCESS ---------------- #

                    opencv_image = load_image(image_path)

                    gray = convert_to_grayscale(opencv_image)

                    threshold = apply_threshold(gray)

                    clean = remove_noise(threshold)

                    progress.progress(35)

                    # ---------------- OCR ---------------- #

                    text = extract_text(clean)

                    ocr_results = extract_text_with_boxes(clean)

                    if ocr_results:
                         avg_confidence = (
                             sum(result[2] for result in ocr_results)
                             / len(ocr_results)
                        ) * 100

                    else:
                        avg_confidence = 0


                    progress.progress(70)

                    # ---------------- EXTRACTION ---------------- #

                    details = extract_details(text)

                    progress.progress(90)

                    details, validation = validate_details(details)

                    filled = sum(
                        value not in [None, "", "Not Found"]
                        for value in details.values()
                    )
                    total_fields = len(details)

                    processing_time = time.time() - start_time

                    progress.progress(100)

                    # ---------------- DRAW OCR BOXES ---------------- #

                    boxed_image = opencv_image.copy()

                    for result in ocr_results:

                        box = result[0]
                        detected_text = result[1]
                        confidence = result[2]

                        top_left = tuple(map(int, box[0]))
                        bottom_right = tuple(map(int, box[2]))

                        if confidence >= 0.85:
                            color = (0, 255, 0)

                        elif confidence >= 0.6:
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
                            (top_left[0], top_left[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 0, 0),
                            2
                        )

                except Exception as e:

                    st.error(f"Error: {e}")
                    st.stop()

                finally:

                    if os.path.exists(image_path):
                        os.remove(image_path)

            # ---------------- DISPLAY OCR ---------------- #

            st.success("✅ Extraction Complete!")

            st.markdown(f"""
            <div style="
            background:#eef6ff;
            padding:20px;
            border-radius:15px;
            border-left:6px solid #4F8BF9;
            margin-top:10px;
            margin-bottom:20px;
          ">

           <h3>🤖 AI Analysis Summary</h3>

           <ul>
           <li>✅ OCR completed successfully</li>
           <li>📄 Fields Extracted: <b>{filled}/{total_fields}</b></li>
           <li>🎯 Average Confidence: <b>{avg_confidence:.2f}%</b></li>
           <li>⏱ Processing Time: <b>{processing_time:.2f} sec</b></li>
           </ul>

           </div>
           """, unsafe_allow_html=True)

            

            if avg_confidence >= 90:
                st.success("🟢 Excellent OCR Quality")

            elif avg_confidence >= 75:
                st.warning("🟡 Good OCR Quality")

            else:
                 st.error("🔴 Poor OCR Quality - Try a clearer image")

            st.subheader("🖼 Image Comparison")

            img1, img2 = st.columns(2)

            with img1:

                st.image(
        image,
        caption="📷 Original Image",
        use_container_width=True
    )

            with img2:

                st.image(
        cv2.cvtColor(
            boxed_image,
            cv2.COLOR_BGR2RGB
        ),

        caption="🔍 OCR Detection",
        use_container_width=True
    )

            _, buffer = cv2.imencode(".png", boxed_image)

            st.download_button(
    "📥 Download Processed Image",
    buffer.tobytes(),
    file_name="processed_license.png",
    mime="image/png",
    use_container_width=True
)


            st.divider()                

            # ---------------- OCR STATISTICS ---------------- #

            st.subheader("📊 AI OCR Dashboard")


            quality_score = min(
                100,
                int(avg_confidence * 0.7 + filled * 6)
            )


            dash1, dash2, dash3, dash4 = st.columns(4)

            dash1.metric("📝 Words", len(text))

            dash2.metric("🎯 Confidence", f"{avg_confidence:.1f}%")

            dash3.metric("⏱ Processing", f"{processing_time:.2f}s")

            dash4.metric("📄 Quality", f"{quality_score}%")

            st.progress(int(avg_confidence))

            st.caption(f"""

            ✔ Fields Extracted: **{filled}/{total_fields}**

            ✔ OCR Confidence: **{avg_confidence:.2f}%**

            ✔ Processing Time: **{processing_time:.2f} sec**

            """)

            completion = filled / total_fields
            st.write("### 📋 Extraction Progress")
            st.progress(completion)


            st.divider()

            # ---------------- RESULTS ---------------- #

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "👤 Name",
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

                st.metric(
                    "✅ Validation",
                    "🟢 Valid"
                    if validation.get("license_number") == "Valid"
                    else "🔴 Invalid"
                )

            st.divider()

            missing = [
    key.replace("_", " ").title()
    for key, value in details.items()
    if value in [None, "", "Not Found"]
]

            if missing:
                st.warning(
        "⚠ Missing Fields: " + ", ".join(missing)
    )

            else:
                st.success(
        "✅ All expected fields were extracted."
    )

                st.divider()

            # ---------------- RAW OCR ---------------- #

            with st.expander("📜 Raw OCR Text"):

                for line in text:
                    st.write(line)

            st.divider()
        

            # ---------------- EXPORT ---------------- #

            st.subheader("📥 Export Results")

            json_data = export_json(details)
            csv_data = export_csv(details)

            export1, export2 = st.columns(2)

            with export1:

                st.download_button(
                    "⬇ Download JSON",
                    data=json_data,
                    file_name="license_details.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_json"
                )

            with export2:

                st.download_button(
                    "⬇ Download CSV",
                    data=csv_data,
                    file_name="license_details.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_csv"
                )

            st.divider()

            st.info(
                f"Detected {len(text)} text segments."
            )