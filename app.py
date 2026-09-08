import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
from reportlab.pdfgen import canvas

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Crop Health Monitoring Using Drone Images and AI",
    page_icon="🚁",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(to right, #ffffff, #f5f0ff);
}

/* Title */
h1 {
    color: #6a1b9a !important;
    text-align: center;
    font-weight: bold;
}

/* Section Headers */
h2, h3 {
    color: #7b1fa2 !important;
}

/* Normal Text */
p, div {
    color: #333333;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: white;
    border-radius: 15px;
    padding: 15px;
    border-left: 6px solid #9c27b0;
    box-shadow: 0px 4px 12px rgba(156,39,176,0.15);
}

/* Upload Box */
[data-testid="stFileUploader"] {
    background: white;
    border-radius: 15px;
    padding: 15px;
    border: 2px solid #e1bee7;
}

/* Progress Bar */
.stProgress > div > div {
    background-color: #9c27b0;
}

/* Download Button */
.stDownloadButton button {
    background: #9c27b0;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
}

/* Info Box */
.stInfo {
    background-color: #f3e5f5;
}

/* Success Box */
.stSuccess {
    background-color: #f8f5ff;
}

/* Warning Box */
.stWarning {
    background-color: #fff8e1;
}

</style>
""", unsafe_allow_html=True)

# ---------------- PDF REPORT ----------------

def create_report(health, disease):
    pdf_file = "Crop_Report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 800, "Drone Crop Health Report")

    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Crop Health : {health:.2f}%")
    c.drawString(100, 720, f"AI Prediction : {disease}")

    c.save()

    return pdf_file

# ---------------- HEADER ----------------

st.title("🚁 Smart Crop Health Monitoring System")

st.markdown("""
### 🌱 AI-Powered Precision Agriculture Dashboard

Upload a drone image and analyze crop health instantly.
""")

st.markdown("---")

# ---------------- IMAGE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "📤 Upload Drone Image",
    type=["jpg", "jpeg", "png"]
)

# ---------------- PROCESS IMAGE ----------------

if uploaded_file:

    file_bytes = np.asarray(
        bytearray(uploaded_file.read()),
        dtype=np.uint8
    )

    image = cv2.imdecode(file_bytes, 1)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Original Drone Image")
        st.image(image, use_container_width=True)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = np.array([25, 20, 20])
    upper_green = np.array([100, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    total_pixels = mask.size
    green_pixels = cv2.countNonZero(mask)

    health = (green_pixels / total_pixels) * 100

    with col2:
        st.subheader("🌿 Green Crop Detection")
        st.image(mask, use_container_width=True)

    st.markdown("---")

    st.subheader("📊 Crop Health Analysis")

    st.progress(int(health))

    c1, c2, c3 = st.columns(3)

    c1.metric("Health %", f"{health:.2f}")
    c2.metric("Healthy Area", f"{health:.2f}%")
    c3.metric("Affected Area", f"{100-health:.2f}%")

    # AI Prediction

    if health > 80:
        disease = "No Disease Detected"
    elif health > 60:
        disease = "Minor Leaf Stress"
    elif health > 40:
        disease = "Possible Nutrient Deficiency"
    else:
        disease = "High Disease Risk"

    st.subheader("🤖 AI Disease Prediction")
    st.info(disease)

    # Crop Condition

    if health > 50:
        st.success("✅ Crop Condition : HEALTHY")
    else:
        st.error("❌ Crop Condition : UNHEALTHY")

    # Pie Chart

    healthy = round(health, 2)
    unhealthy = round(100 - health, 2)

    df = pd.DataFrame({
        "Category": ["Healthy", "Affected"],
        "Percentage": [healthy, unhealthy]
    })

    fig = px.pie(
        df,
        values="Percentage",
        names="Category",
        title="🌱 Crop Health Distribution",
        color="Category",
        color_discrete_map={
            "Healthy": "#4CAF50",
            "Affected": "#FF9800"
        },
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)

    # Farmer Suggestions

    st.subheader("🌾 Farmer Recommendations")

    if health > 80:
        st.success(
            "Excellent crop condition. Continue current farming practices."
        )
    elif health > 60:
        st.warning(
            "Monitor irrigation and fertilizer levels regularly."
        )
    elif health > 40:
        st.warning(
            "Inspect crops for nutrient deficiency or pest attacks."
        )
    else:
        st.error(
            "Immediate field inspection recommended."
        )

    # PDF Report

    report = create_report(health, disease)

    with open(report, "rb") as file:
        st.download_button(
            "📄 Download PDF Report",
            file,
            file_name="Crop_Report.pdf"
        )

