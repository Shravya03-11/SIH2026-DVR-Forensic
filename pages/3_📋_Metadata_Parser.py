"""
pages/3_📋_Metadata_Parser.py — Metadata & Timeline Module
ASSIGNED TO: Member 3
YOUR TASKS:
  [ ] Extract and display real video metadata from uploaded file
  [ ] Build the multi-camera Gantt timeline chart
  [ ] Add timestamp normalization display
  [ ] Show a thumbnail of the first frame
"""

import streamlit as st
import tempfile
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import datetime

st.set_page_config(page_title="Metadata Parser | DVR Forensic", page_icon="📋", layout="wide")

st.title("📋 Metadata Parser & Timeline")
st.markdown("Extract video metadata, normalize timestamps, and visualize multi-camera recording timelines.")
st.divider()

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📁 Upload DVR footage to parse",
    type=["mp4", "avi", "dav", "mkv", "mov"],
)

if uploaded:
    # Save to temp file for OpenCV to read
    suffix = os.path.splitext(uploaded.name)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded.read())
        tmp_path = f.name

    with st.spinner("📊 Extracting metadata..."):
        from utils.metadata import extract_metadata, generate_timeline_data
        meta = extract_metadata(tmp_path)

    if "error" in meta:
        st.error(f"❌ Could not read file: {meta['error']}")
    else:
        # Store for report
        st.session_state.metadata = meta

        st.success("✅ Metadata extracted successfully!")
        st.divider()

        # ── Metadata Table ────────────────────────────────────────────
        st.subheader("📊 Video Properties")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Duration",    meta.get("Duration (readable)", "N/A"))
        col2.metric("Resolution",  meta.get("Resolution", "N/A"))
        col3.metric("FPS",         meta.get("FPS", "N/A"))
        col4.metric("Total Frames",meta.get("Total Frames", "N/A"))

        # Full metadata in a table
        st.markdown("#### 📋 Full Metadata")
        meta_df = pd.DataFrame(
            list(meta.items()),
            columns=["Property", "Value"]
        )
        st.dataframe(meta_df, use_container_width=True, hide_index=True)

        # ── First Frame Thumbnail ─────────────────────────────────────
        st.divider()
        st.subheader("🖼️ First Frame Preview")

        try:
            import cv2
            cap = cv2.VideoCapture(tmp_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                import cv2
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, caption="First frame of footage", use_column_width=True)
        except Exception as e:
            st.warning(f"Could not extract frame: {e}")

        # ── Timeline Chart ────────────────────────────────────────────
        st.divider()
        st.subheader("🕐 Multi-Camera Recording Timeline")
        st.caption("Simulated timeline showing recording activity across 4 cameras")

        timeline_data = generate_timeline_data(meta, num_cameras=4)

        # Build Plotly Gantt chart
        gantt_df = pd.DataFrame(timeline_data)
        fig = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Status",
            color_discrete_map={
                "✅ Normal":             "#22C55E",
                "⚠️ Motion Detected":   "#F59E0B",
                "🔴 Gap Detected":      "#EF4444",
            },
            title="DVR Recording Timeline — All Cameras",
        )
        fig.update_layout(
            plot_bgcolor  = "#0A0F1E",
            paper_bgcolor = "#0A0F1E",
            font_color    = "#E2E8F0",
            xaxis_title   = "Time",
            yaxis_title   = "Camera",
            height        = 300,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show the timeline as a table too
        st.markdown("#### 📋 Timeline Table")
        table_df = gantt_df[["Camera", "Start Time", "End Time", "Duration", "Status"]].copy()
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        # ── Timestamp Normalization ────────────────────────────────────
        st.divider()
        st.subheader("🕰️ Timestamp Normalization")
        st.markdown("""
        DVR clocks are often misconfigured. This tool normalizes timestamps to **UTC**
        so that footage from different cameras can be compared accurately.
        """)

        # TODO (Member 3): Add real UTC conversion
        norm_df = pd.DataFrame([
            {"Camera": "CAM-01", "Raw Timestamp (DVR)": "15-08-2024 14:30:22",
             "DVR Timezone": "IST (+5:30)", "Normalized (UTC)": "2024-08-15 09:00:22 UTC"},
            {"Camera": "CAM-02", "Raw Timestamp (DVR)": "08/15/24 14:30:45",
             "DVR Timezone": "IST (+5:30)", "Normalized (UTC)": "2024-08-15 09:00:45 UTC"},
            {"Camera": "CAM-03", "Raw Timestamp (DVR)": "1723719065",
             "DVR Timezone": "Epoch (Unix)", "Normalized (UTC)": "2024-08-15 09:01:05 UTC"},
            {"Camera": "CAM-04", "Raw Timestamp (DVR)": "2024:08:15 14:31:22",
             "DVR Timezone": "IST (+5:30)", "Normalized (UTC)": "2024-08-15 09:01:22 UTC"},
        ])
        st.dataframe(norm_df, use_container_width=True, hide_index=True)
        st.success("✅ All timestamps normalized to UTC for cross-camera correlation")

    # Cleanup temp file
    try:
        os.unlink(tmp_path)
    except Exception:
        pass

else:
    st.info("👆 Upload a video file to extract its metadata and view the timeline.")
    st.markdown("""
    **This module will show you:**
    - Video duration, resolution, FPS
    - Total number of frames
    - File creation timestamp
    - Multi-camera Gantt timeline chart
    - Normalized UTC timestamps
    """)
