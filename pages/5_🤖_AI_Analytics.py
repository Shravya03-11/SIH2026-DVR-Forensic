"""
pages/5_🤖_AI_Analytics.py — AI Video Analytics Module
Complete, working implementation.
Tabs:
  1. Object Detection  — frame-by-frame YOLOv8 detection
  2. Face Detection    — OpenCV Haar cascade face finder
  3. Motion Detection  — compare two frames
  4. Face Blur         — privacy protection
  5. Full Video Scan   — scan entire video, log all events
"""

import streamlit as st
import tempfile
import os
import cv2
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Analytics | DVR Forensic",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Video Analytics")
st.markdown(
    "Detect faces, people, vehicles, and objects in surveillance footage "
    "using **YOLOv8** (object detection) and **OpenCV** (face detection)."
)
st.divider()

# ── 1. Load YOLO model once (cached across reruns) ────────────────────────────
@st.cache_resource(show_spinner=False)
def load_yolo():
    from ultralytics import YOLO
    return YOLO("yolov8n.pt")   # ~6 MB, auto-downloads on first run

with st.spinner("🔄 Loading YOLOv8 model…"):
    yolo_model = load_yolo()
st.success("✅ YOLOv8 model ready!")

# ── 2. File Upload ─────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📁 Upload surveillance video",
    type=["mp4", "avi", "mkv", "mov"],
)

# We keep the temp file path in session state so it survives button clicks
if uploaded:
    # Only write temp file when a NEW file is uploaded
    if st.session_state.get("ai_uploaded_name") != uploaded.name:
        # Delete old temp file if it exists
        old_path = st.session_state.get("ai_tmp_path", "")
        if old_path and os.path.exists(old_path):
            try:
                os.unlink(old_path)
            except Exception:
                pass

        suffix = os.path.splitext(uploaded.name)[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(uploaded.read())
            st.session_state.ai_tmp_path     = f.name
            st.session_state.ai_uploaded_name = uploaded.name

    tmp_path = st.session_state.ai_tmp_path

    # Basic video info
    cap          = cv2.VideoCapture(tmp_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps_val      = cap.get(cv2.CAP_PROP_FPS) or 25
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    duration_sec = total_frames / fps_val

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Frames",  f"{total_frames:,}")
    col2.metric("FPS",           f"{fps_val:.1f}")
    col3.metric("Resolution",    f"{width}×{height}")
    col4.metric("Duration",      f"{int(duration_sec//60)}m {int(duration_sec%60)}s")

    st.divider()

    # ── 3. Tabs ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Object Detection",
        "😶 Face Detection",
        "🏃 Motion Detection",
        "🙈 Face Blur",
        "📊 Full Video Scan",
    ])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — Object Detection
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("🎯 Object Detection")
        st.caption(
            "Select a frame and run YOLOv8 to detect people, vehicles, "
            "bags, and 80+ other object classes."
        )

        frame_num = st.slider(
            "Frame number",
            min_value=0,
            max_value=max(total_frames - 1, 0),
            value=0,
            step=max(1, total_frames // 100),
            key="obj_frame_slider",
        )
        conf_thresh = st.slider(
            "Confidence threshold  (lower = detect more, higher = detect less)",
            min_value=0.10,
            max_value=0.95,
            value=0.25,
            step=0.05,
            key="obj_conf",
        )

        if st.button("🔍 Detect Objects", type="primary", key="btn_obj"):
            cap = cv2.VideoCapture(tmp_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                st.error("❌ Could not read that frame. Try a different frame number.")
            else:
                with st.spinner("🤖 Running YOLOv8…"):
                    from utils.detector import detect_objects
                    annotated, detections = detect_objects(frame, yolo_model, conf=conf_thresh)

                # ── Display ──────────────────────────────────────────
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.image(
                        cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                        caption=f"Frame {frame_num}  — YOLOv8 Detection",
                        use_container_width=True,
                    )
                with c2:
                    if detections:
                        st.success(f"✅ {len(detections)} object(s) detected")
                        det_df = pd.DataFrame(detections)
                        st.dataframe(
                            det_df[["Object", "Confidence", "Bounding Box"]],
                            use_container_width=True,
                            hide_index=True,
                        )
                        # Save for report
                        st.session_state.detections = detections

                        # Bar chart
                        counts = (
                            det_df["Object"]
                            .value_counts()
                            .reset_index()
                        )
                        counts.columns = ["Object", "Count"]
                        fig = px.bar(
                            counts, x="Object", y="Count",
                            color="Count",
                            color_continuous_scale="Blues",
                            title="Detected Object Counts",
                        )
                        fig.update_layout(
                            plot_bgcolor  = "#0A0F1E",
                            paper_bgcolor = "#0A0F1E",
                            font_color    = "#E2E8F0",
                            height=250,
                            showlegend=False,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(
                            "No objects detected in this frame.\n\n"
                            "Try: lower the confidence threshold or pick a different frame."
                        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — Face Detection
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("😶 Face Detection")
        st.caption(
            "Uses OpenCV's Haar Cascade classifier to detect human faces. "
            "Works best on well-lit, front-facing footage."
        )

        frame_num_f = st.slider(
            "Frame number",
            min_value=0,
            max_value=max(total_frames - 1, 0),
            value=0,
            step=max(1, total_frames // 100),
            key="face_frame_slider",
        )

        if st.button("😶 Detect Faces", type="primary", key="btn_face"):
            cap = cv2.VideoCapture(tmp_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num_f)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                st.error("❌ Could not read that frame.")
            else:
                with st.spinner("🔍 Detecting faces…"):
                    from utils.detector import detect_faces
                    annotated_f, face_count, face_boxes = detect_faces(frame)

                c1, c2 = st.columns([3, 2])
                with c1:
                    st.image(
                        cv2.cvtColor(annotated_f, cv2.COLOR_BGR2RGB),
                        caption=f"Frame {frame_num_f}  — Face Detection Result",
                        use_container_width=True,
                    )
                with c2:
                    if face_count > 0:
                        st.success(f"✅ {face_count} face(s) detected")
                        face_data = pd.DataFrame([
                            {
                                "Face #": i + 1,
                                "X": x, "Y": y,
                                "Width (px)": w, "Height (px)": h,
                            }
                            for i, (x, y, w, h) in enumerate(face_boxes)
                        ])
                        st.dataframe(face_data, use_container_width=True, hide_index=True)
                        st.info(
                            "💡 Each face gets a teal bounding box. "
                            "Go to the **Face Blur** tab to anonymize them."
                        )
                    else:
                        st.warning(
                            "⚠️ No faces detected in this frame.\n\n"
                            "Tips:\n"
                            "- Try a different frame where faces are more visible\n"
                            "- Make sure faces are front-facing\n"
                            "- Low-resolution or dark footage reduces accuracy"
                        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 3 — Motion Detection
    # ════════════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("🏃 Motion Detection")
        st.caption(
            "Compare two frames to detect and highlight movement. "
            "Green boxes mark regions where significant motion occurred."
        )

        c1, c2 = st.columns(2)
        f1_num = c1.number_input(
            "Frame 1 (earlier)",  0, total_frames - 1, 0,
            key="mot_f1",
        )
        f2_num = c2.number_input(
            "Frame 2 (later)",    0, total_frames - 1, min(30, total_frames - 1),
            key="mot_f2",
        )
        sensitivity = st.slider(
            "Sensitivity  (higher = detect smaller movements)",
            min_value=5, max_value=80, value=25, step=5,
            key="mot_sens",
            help="Lower threshold value = more sensitive to motion",
        )

        if st.button("🏃 Detect Motion", type="primary", key="btn_motion"):
            cap = cv2.VideoCapture(tmp_path)

            cap.set(cv2.CAP_PROP_POS_FRAMES, f1_num)
            ret1, frame1 = cap.read()

            cap.set(cv2.CAP_PROP_POS_FRAMES, f2_num)
            ret2, frame2 = cap.read()

            cap.release()

            if not ret1 or not ret2:
                st.error("❌ Could not read one or both frames.")
            else:
                with st.spinner("📊 Analysing motion…"):
                    from utils.detector import detect_motion
                    # threshold inversed: high sensitivity slider → low threshold
                    thresh_val = 80 - sensitivity + 5
                    mot_frame, mot_pct, mot_regions = detect_motion(
                        frame1, frame2, threshold=thresh_val
                    )

                c1, c2, c3 = st.columns(3)
                c1.image(
                    cv2.cvtColor(frame1,    cv2.COLOR_BGR2RGB),
                    caption=f"Frame {f1_num}  (Before)",
                    use_container_width=True,
                )
                c2.image(
                    cv2.cvtColor(frame2,    cv2.COLOR_BGR2RGB),
                    caption=f"Frame {f2_num}  (After)",
                    use_container_width=True,
                )
                c3.image(
                    cv2.cvtColor(mot_frame, cv2.COLOR_BGR2RGB),
                    caption="Motion Regions (green boxes)",
                    use_container_width=True,
                )

                st.divider()
                m1, m2, m3 = st.columns(3)
                m1.metric("Motion Level",   f"{mot_pct:.1f}%")
                m2.metric("Motion Regions", mot_regions)
                m3.metric("Frame Gap",      f"{abs(f2_num - f1_num)} frames")

                if mot_pct > 15:
                    st.error(f"🔴 HIGH motion detected — {mot_pct:.1f}% of frame changed!")
                elif mot_pct > 5:
                    st.warning(f"⚠️ Moderate motion — {mot_pct:.1f}% of frame changed")
                elif mot_pct > 1:
                    st.info(f"ℹ️ Low motion — {mot_pct:.1f}% of frame changed")
                else:
                    st.success(f"✅ No significant motion ({mot_pct:.1f}%)")

    # ════════════════════════════════════════════════════════════════════
    # TAB 4 — Face Blur (Privacy)
    # ════════════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("🙈 Face Blur — Privacy Protection")
        st.caption(
            "Automatically detect and blur faces for GDPR / privacy compliance "
            "before sharing evidence."
        )

        frame_num_b = st.slider(
            "Frame number",
            min_value=0,
            max_value=max(total_frames - 1, 0),
            value=0,
            step=max(1, total_frames // 100),
            key="blur_frame_slider",
        )
        blur_strength = st.slider(
            "Blur strength",
            min_value=11, max_value=99, value=51, step=10,
            help="Higher = more blurred. Must be odd — we handle that automatically.",
            key="blur_strength",
        )

        if st.button("🙈 Blur Faces", type="primary", key="btn_blur"):
            cap = cv2.VideoCapture(tmp_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num_b)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                st.error("❌ Could not read that frame.")
            else:
                with st.spinner("🔒 Blurring faces…"):
                    from utils.detector import blur_faces
                    blurred_frame, face_count = blur_faces(frame, blur_strength=blur_strength)

                c1, c2 = st.columns(2)
                c1.image(
                    cv2.cvtColor(frame,         cv2.COLOR_BGR2RGB),
                    caption="Original Frame",
                    use_container_width=True,
                )
                c2.image(
                    cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2RGB),
                    caption=f"Privacy Protected  ({face_count} face(s) blurred)",
                    use_container_width=True,
                )

                if face_count > 0:
                    st.success(f"✅ {face_count} face(s) blurred successfully!")
                else:
                    st.warning(
                        "⚠️ No faces detected to blur in this frame. "
                        "Try a frame with clearly visible, front-facing faces."
                    )

                # Download blurred frame
                _, buf = cv2.imencode(".jpg", blurred_frame)
                st.download_button(
                    "📥 Download Privacy-Protected Frame",
                    data=buf.tobytes(),
                    file_name=f"blurred_frame_{frame_num_b}.jpg",
                    mime="image/jpeg",
                )

    # ════════════════════════════════════════════════════════════════════
    # TAB 5 — Full Video Scan
    # ════════════════════════════════════════════════════════════════════
    with tab5:
        st.subheader("📊 Full Video Scan")
        st.caption(
            "Automatically scan the entire video, sample frames at regular intervals, "
            "and build a timeline of all detected events."
        )

        sample_rate = st.slider(
            "Sample every N frames  (lower = more thorough, slower)",
            min_value=10, max_value=120, value=30, step=10,
            key="scan_sample",
        )
        scan_conf = st.slider(
            "Detection confidence threshold",
            min_value=0.10, max_value=0.90, value=0.30, step=0.05,
            key="scan_conf",
        )

        estimated_samples = total_frames // sample_rate
        st.info(
            f"⏱️ This will analyse **~{estimated_samples} frames** "
            f"out of {total_frames:,} total  "
            f"(1 every {sample_rate} frames = every {sample_rate/fps_val:.1f}s)"
        )

        if st.button("🚀 Start Full Video Scan", type="primary", key="btn_scan"):
            prog_bar = st.progress(0)
            status   = st.empty()

            # Manual scan with progress bar (can't use the function directly
            # because we need to update Streamlit's progress bar)
            cap       = cv2.VideoCapture(tmp_path)
            events    = []
            frame_idx = 0
            from utils.detector import detect_objects, _sec_to_hms

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % sample_rate == 0:
                    pct = min(int((frame_idx / max(total_frames, 1)) * 100), 99)
                    prog_bar.progress(pct)
                    status.info(
                        f"🔍 Scanning frame {frame_idx}/{total_frames}  "
                        f"({_sec_to_hms(frame_idx / fps_val)})"
                    )

                    _, detections = detect_objects(frame, yolo_model, conf=scan_conf)
                    if detections:
                        events.append({
                            "Frame":          frame_idx,
                            "Timestamp":      _sec_to_hms(frame_idx / fps_val),
                            "Objects Found":  ", ".join({d["Object"] for d in detections}),
                            "Count":          len(detections),
                        })

                frame_idx += 1

            cap.release()
            prog_bar.progress(100)
            status.empty()

            if events:
                st.success(
                    f"✅ Scan complete! Found objects in **{len(events)}** "
                    f"out of {estimated_samples} sampled frames."
                )
                events_df = pd.DataFrame(events)
                st.dataframe(events_df, use_container_width=True, hide_index=True)

                # Save to session state for report
                st.session_state.scan_events = events

                # Timeline chart
                st.markdown("#### 📈 Detection Event Timeline")
                fig2 = px.bar(
                    events_df, x="Timestamp", y="Count",
                    color="Count",
                    color_continuous_scale="Teal",
                    title="Objects Detected per Sampled Frame",
                )
                fig2.update_layout(
                    plot_bgcolor  = "#0A0F1E",
                    paper_bgcolor = "#0A0F1E",
                    font_color    = "#E2E8F0",
                    xaxis_title   = "Video Timestamp",
                    yaxis_title   = "Objects Detected",
                    height=350,
                )
                st.plotly_chart(fig2, use_container_width=True)

                # Download CSV
                st.download_button(
                    "📥 Download Scan Results (CSV)",
                    data=events_df.to_csv(index=False),
                    file_name="ai_scan_results.csv",
                    mime="text/csv",
                )
            else:
                st.warning(
                    "⚠️ No objects detected in any sampled frame.\n\n"
                    "Try: lower the confidence threshold or use a clearer video."
                )

# ── No file uploaded ──────────────────────────────────────────────────────────
else:
    st.info("👆 Upload a video file above to begin AI analysis.")
    st.markdown("""
    ### What this module can do:

    | Tab | Feature | Technology |
    |-----|---------|------------|
    | 🎯 Object Detection | Detect people, cars, bags, 80+ objects | YOLOv8 (ultralytics) |
    | 😶 Face Detection | Find faces with bounding boxes | OpenCV Haar Cascade |
    | 🏃 Motion Detection | Highlight movement between frames | OpenCV frame diff |
    | 🙈 Face Blur | Blur faces for privacy/GDPR | OpenCV Gaussian blur |
    | 📊 Full Video Scan | Scan entire video, build event timeline | YOLOv8 + Plotly |

    > **Tip:** Rename your test video with a brand name (e.g. `dahua_cam01.mp4`) 
    > so the Device Detection page can identify it too!
    """)
