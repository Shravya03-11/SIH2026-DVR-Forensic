"""
pages/5_🤖_AI_Analytics.py — AI Video Analytics Module
ASSIGNED TO: Member 5
YOUR TASKS:
  [ ] The frame-by-frame object detection is ready — test it
  [ ] Add the motion detection tab (use detect_motion from utils/detector.py)
  [ ] Add the face blur tab (use blur_faces from utils/detector.py)
  [ ] Add a detection summary chart (bar chart of detected object counts)
  [ ] Add a confidence filter slider
"""

import streamlit as st
import tempfile
import os
import cv2
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Analytics | DVR Forensic", page_icon="🤖", layout="wide")

st.title("🤖 AI Video Analytics")
st.markdown("Detect faces, people, vehicles, and objects in surveillance footage using YOLOv8.")
st.divider()

# ── Load Model (cached so it only loads once) ─────────────────────────────────
@st.cache_resource
def load_model():
    from ultralytics import YOLO
    return YOLO("yolov8n.pt")  # Auto-downloads ~6MB model

with st.spinner("🔄 Loading AI model (downloads on first run)..."):
    model = load_model()

st.success("✅ YOLOv8 model loaded!")

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📁 Upload video for AI analysis",
    type=["mp4", "avi", "mkv", "mov"],
)

if uploaded:
    suffix = os.path.splitext(uploaded.name)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded.read())
        tmp_path = f.name

    cap        = cv2.VideoCapture(tmp_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS)

    st.info(f"📹 Video loaded: **{total_frames}** frames @ **{fps:.1f} FPS**")
    cap.release()

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🎯 Object Detection", "🏃 Motion Detection", "🙈 Face Blur"])

    # ── Tab 1: Object Detection ───────────────────────────────────────────────
    with tab1:
        st.subheader("🎯 Object Detection")
        st.markdown("Navigate frames and detect objects (people, cars, bags, etc.) using YOLOv8.")

        # Frame slider
        frame_num = st.slider(
            "Select frame to analyze",
            min_value=0,
            max_value=max(total_frames - 1, 0),
            value=0,
            step=max(1, total_frames // 50),
        )

        conf_threshold = st.slider("Confidence threshold", 0.1, 1.0, 0.25, 0.05)

        if st.button("🔍 Analyze This Frame", type="primary"):
            cap = cv2.VideoCapture(tmp_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()

            if ret:
                with st.spinner("🤖 Running AI detection..."):
                    from utils.detector import detect_objects
                    annotated, detections = detect_objects(frame, model)

                col1, col2 = st.columns([2, 1])
                with col1:
                    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    st.image(annotated_rgb, caption=f"Frame {frame_num} — AI Detection Result", use_column_width=True)

                with col2:
                    if detections:
                        st.markdown(f"**{len(detections)} objects detected:**")
                        det_df = pd.DataFrame(detections)
                        st.dataframe(det_df, use_container_width=True, hide_index=True)

                        # Store detections for report
                        st.session_state.detections = detections

                        # Count chart
                        counts = det_df["Object"].value_counts().reset_index()
                        counts.columns = ["Object", "Count"]
                        fig = px.bar(
                            counts, x="Object", y="Count",
                            color="Count",
                            color_continuous_scale="Blues",
                            title="Detected Objects Count",
                        )
                        fig.update_layout(
                            plot_bgcolor="#0A0F1E",
                            paper_bgcolor="#0A0F1E",
                            font_color="#E2E8F0",
                            height=250,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No objects detected in this frame. Try another frame or lower the confidence threshold.")
            else:
                st.error("Could not read this frame.")

    # ── Tab 2: Motion Detection ───────────────────────────────────────────────
    with tab2:
        st.subheader("🏃 Motion Detection")
        st.markdown("Compare two frames to detect movement and highlight motion areas.")

        col1, col2 = st.columns(2)
        frame1_num = col1.number_input("Frame 1", 0, total_frames - 1, 0)
        frame2_num = col2.number_input("Frame 2", 0, total_frames - 1, min(30, total_frames - 1))

        if st.button("🔍 Detect Motion", type="primary"):
            cap = cv2.VideoCapture(tmp_path)

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame1_num)
            ret1, frame1 = cap.read()

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame2_num)
            ret2, frame2 = cap.read()

            cap.release()

            if ret1 and ret2:
                with st.spinner("Detecting motion..."):
                    from utils.detector import detect_motion
                    motion_frame, motion_pct = detect_motion(frame1, frame2)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB),
                             caption=f"Frame {frame1_num}", use_column_width=True)
                with col2:
                    st.image(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB),
                             caption=f"Frame {frame2_num}", use_column_width=True)
                with col3:
                    st.image(cv2.cvtColor(motion_frame, cv2.COLOR_BGR2RGB),
                             caption="Motion Areas (green boxes)", use_column_width=True)

                st.metric("Motion Level", f"{motion_pct:.1f}%")
                if motion_pct > 10:
                    st.warning(f"⚠️ Significant motion detected ({motion_pct:.1f}% of frame changed)!")
                elif motion_pct > 2:
                    st.info(f"ℹ️ Minor motion detected ({motion_pct:.1f}%)")
                else:
                    st.success(f"✅ No significant motion ({motion_pct:.1f}%)")
            else:
                st.error("Could not read frames.")

    # ── Tab 3: Face Blur ──────────────────────────────────────────────────────
    with tab3:
        st.subheader("🙈 Face Privacy Protection")
        st.markdown("Automatically blur faces in surveillance footage for privacy compliance.")

        frame_num = st.slider("Select frame", 0, max(total_frames - 1, 0), 0, key="blur_slider")

        if st.button("🙈 Blur Faces", type="primary"):
            cap = cv2.VideoCapture(tmp_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()

            if ret:
                with st.spinner("Blurring faces..."):
                    from utils.detector import blur_faces
                    blurred = blur_faces(frame)

                col1, col2 = st.columns(2)
                col1.image(cv2.cvtColor(frame,   cv2.COLOR_BGR2RGB), caption="Original", use_column_width=True)
                col2.image(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB), caption="Faces Blurred", use_column_width=True)
                st.success("✅ Faces blurred for privacy protection")
            else:
                st.error("Could not read frame.")

    # Cleanup
    try:
        os.unlink(tmp_path)
    except Exception:
        pass

else:
    st.info("👆 Upload a video file to start AI analysis.")
    st.markdown("""
    **This module can detect:**
    - 👤 People / persons
    - 🚗 Vehicles (cars, motorcycles, trucks)
    - 🎒 Bags and objects
    - 🏃 Motion between frames
    - 😶 Faces (for blurring / privacy protection)
    
    **Powered by YOLOv8** — a state-of-the-art real-time object detection model.
    """)
