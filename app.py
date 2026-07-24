import streamlit as st
from PIL import Image

# -------------------- PAGE CONFIG -------------------- #
st.set_page_config(
    page_title="DriveSight AI",
    page_icon="🚗",
    layout="wide"
)

# -------------------- CUSTOM CSS -------------------- #
st.markdown("""
<style>

.main-title{
    font-size:42px;
    font-weight:bold;
    color:#2E86C1;
}

.subtitle{
    font-size:18px;
    color:gray;
}

.card{
    padding:20px;
    border-radius:12px;
    background-color:#F8F9F9;
    border:1px solid #E5E7E9;
}

</style>
""", unsafe_allow_html=True)

# -------------------- HEADER -------------------- #

st.markdown(
    "<div class='main-title'>🚗 DriveSight AI</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>AI Powered Driving License Information Extraction System</div>",
    unsafe_allow_html=True
)

st.divider()

# -------------------- SIDEBAR -------------------- #

st.sidebar.title("📌 Project")

st.sidebar.info(
"""
DriveSight AI

Features

✅ Image Upload

✅ OCR

✅ Smart Extraction

✅ Validation

✅ Export CSV

✅ Export JSON
"""
)

# -------------------- LAYOUT -------------------- #

left, right = st.columns([1,1])

# -------------------- LEFT -------------------- #

with left:

    st.subheader("📤 Upload Driving License")

    uploaded_file = st.file_uploader(
        "Choose an Image",
        type=["jpg","jpeg","png"]
    )

# -------------------- RIGHT -------------------- #

with right:

    st.subheader("🖼 Image Preview")

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Driving License",
            use_container_width=True
        )

    else:

        st.info("Upload an image to preview.")

# -------------------- BUTTON -------------------- #

st.divider()

if uploaded_file:

    if st.button("🔍 Extract Information", use_container_width=True):

        st.success("Image uploaded successfully!")

        st.write("OCR integration coming in next step...")