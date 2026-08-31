"""
pages/3_📋_Metadata_Parser.py — Metadata & Timeline Module
ASSIGNED TO: Member 3

Responsibilities:
- Extract real video metadata
- Extract available creation/start timestamps
- Detect suspicious timestamps
- Convert timestamps to UTC
- Reconstruct recording timeline
- Display first frame
- Play original evidence video
- Extract multiple evidence frames
- Provide frame-by-frame forensic examination
- Provide evidence frame indexing
- Provide basic frame statistics
"""

import streamlit as st
import tempfile
import os
import pandas as pd
import plotly.express as px
import datetime
import hashlib

from utils.metadata import (
    extract_metadata,
    get_recording_timeline,
    normalize_timestamp,
    is_suspicious_timestamp,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Metadata Parser | DVR Forensic",
    page_icon="📋",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("📋 Metadata Parser & Timeline")

st.markdown(
    """
    **Forensic video metadata examination, timestamp analysis,
    recording timeline reconstruction and evidence-frame indexing.**
    """
)

st.divider()


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded = st.file_uploader(
    "📁 Upload surveillance / DVR evidence",
    type=[
        "mp4",
        "avi",
        "dav",
        "mkv",
        "mov",
        "mpeg4",
    ],
    help="Upload a surveillance or DVR video file for forensic analysis.",
)


# ============================================================
# NO FILE
# ============================================================

if not uploaded:

    st.info(
        "👆 Upload a surveillance video to begin forensic analysis."
    )

    st.markdown(
        """
        ### 🔎 This module will analyze

        - 📊 Video duration
        - 📐 Resolution and frame rate
        - 🎞️ Total frame count
        - 💾 Evidence file size
        - 🧾 Container and codec information
        - 🕰️ Embedded timestamps
        - ⚠️ Suspicious / reset timestamps
        - 🌍 UTC normalization
        - 🕐 Recording timeline
        - ▶️ Original evidence playback
        - 🖼️ Multiple evidence frames
        - 🔢 Frame numbers and timestamps
        - 📈 Basic frame statistics
        - 🧾 Forensic analysis summary
        """
    )

    st.stop()


# ============================================================
# TEMPORARY FILE
# ============================================================

suffix = os.path.splitext(uploaded.name)[1] or ".mp4"

tmp_path = None


try:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:

        temp_file.write(uploaded.getbuffer())
        tmp_path = temp_file.name


    # ========================================================
    # IMPORT OPENCV
    # ========================================================

    try:

        import cv2
        import numpy as np

    except ImportError as e:

        st.error(
            f"OpenCV/Numpy is required: {e}"
        )

        st.stop()


    # ========================================================
    # METADATA EXTRACTION
    # ========================================================

    with st.spinner(
        "🔍 Analyzing forensic evidence..."
    ):

        meta = extract_metadata(
            tmp_path
        )


    # ========================================================
    # ERROR
    # ========================================================

    if "error" in meta:

        st.error(
            f"❌ Could not analyze evidence: {meta['error']}"
        )

        st.stop()


    st.success(
        "✅ Evidence analyzed successfully."
    )


    # Store metadata for Report Generator
    st.session_state.metadata = meta


    # ========================================================
    # EVIDENCE IDENTIFICATION
    # ========================================================

    st.divider()

    st.subheader(
        "🔎 Evidence Identification"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Evidence File",
            uploaded.name,
        )


    with col2:

        st.metric(
            "Container",
            meta.get(
                "Container Format",
                "Unknown",
            ),
        )


    with col3:

        st.metric(
            "Video Codec",
            meta.get(
                "Video Codec",
                "Unknown",
            ),
        )


    st.caption(
        "Source information shown above is extracted from the uploaded evidence."
    )


    # ========================================================
    # EVIDENCE FILE HASH
    # ========================================================

    st.markdown(
        "### 🔐 Evidence Integrity"
    )


    try:

        with open(
            tmp_path,
            "rb",
        ) as hash_file:

            sha256_hash = hashlib.sha256()

            for chunk in iter(
                lambda: hash_file.read(1024 * 1024),
                b"",
            ):

                sha256_hash.update(
                    chunk
                )

            file_hash = sha256_hash.hexdigest()


        st.code(
            file_hash,
            language="text",
        )

        st.caption(
            "SHA-256 hash generated from the uploaded evidence file."
        )

        # Save hash for report generation
        st.session_state.metadata[
            "SHA-256"
        ] = file_hash

    except Exception as e:

        st.warning(
            f"Could not calculate SHA-256 hash: {e}"
        )


    # ========================================================
    # VIDEO PROPERTIES
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Video Properties"
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Duration",
            meta.get(
                "Duration (readable)",
                "N/A",
            ),
        )


    with col2:

        st.metric(
            "Resolution",
            meta.get(
                "Resolution",
                "N/A",
            ),
        )


    with col3:

        st.metric(
            "Frame Rate",
            f"{meta.get('FPS', 'N/A')} FPS",
        )


    with col4:

        st.metric(
            "Total Frames",
            meta.get(
                "Total Frames",
                "N/A",
            ),
        )


    # ========================================================
    # TECHNICAL PROPERTIES
    # ========================================================

    st.subheader(
        "📐 Technical Properties"
    )


    technical_rows = [
        [
            "Duration",
            meta.get(
                "Duration (readable)",
                "N/A",
            ),
        ],
        [
            "FPS",
            meta.get(
                "FPS",
                "N/A",
            ),
        ],
        [
            "Width",
            meta.get(
                "Width (px)",
                "N/A",
            ),
        ],
        [
            "Height",
            meta.get(
                "Height (px)",
                "N/A",
            ),
        ],
        [
            "Total Frames",
            meta.get(
                "Total Frames",
                "N/A",
            ),
        ],
        [
            "File Size",
            f"{meta.get('File Size (MB)', 'N/A')} MB",
        ],
        [
            "File Created",
            meta.get(
                "File Created",
                "N/A",
            ),
        ],
        [
            "Container",
            meta.get(
                "Container Format",
                "N/A",
            ),
        ],
        [
            "Video Codec",
            meta.get(
                "Video Codec",
                "N/A",
            ),
        ],
        [
            "Video Start Time",
            meta.get(
                "Video Start Time",
                "N/A",
            ),
        ],
    ]


    technical_df = pd.DataFrame(
        technical_rows,
        columns=[
            "Property",
            "Value",
        ],
    )


    # IMPORTANT:
    # st.table avoids the Streamlit width/type issue
    # seen with st.dataframe in this environment.

    st.table(
        technical_df
    )


    # ========================================================
    # COMPLETE METADATA
    # ========================================================

    with st.expander(
        "📋 View Complete Extracted Metadata"
    ):

        metadata_rows = [
            [
                str(key),
                str(value),
            ]
            for key, value in meta.items()
        ]


        metadata_df = pd.DataFrame(
            metadata_rows,
            columns=[
                "Property",
                "Value",
            ],
        )


        st.table(
            metadata_df
        )


    # ========================================================
    # ORIGINAL VIDEO PLAYBACK
    # ========================================================

    st.divider()

    st.subheader(
        "▶️ Evidence Video Playback"
    )


    st.markdown(
        """
        Play the original uploaded surveillance evidence directly
        for visual verification.
        """
    )


    try:

        with open(
            tmp_path,
            "rb",
        ) as video_file:

            video_bytes = video_file.read()


        st.video(
            video_bytes
        )

    except Exception as e:

        st.warning(
            f"⚠️ Video playback unavailable: {e}"
        )


    # ========================================================
    # TIMESTAMP FORENSICS
    # ========================================================

    st.divider()

    st.subheader(
        "🕰️ Timestamp Forensics"
    )


    embedded_timestamp = meta.get(
        "Embedded Creation Time"
    )


    suspicious = False


    if embedded_timestamp:

        st.markdown(
            "#### Source Timestamp"
        )


        st.code(
            str(
                embedded_timestamp
            ),
            language="text",
        )


        suspicious = is_suspicious_timestamp(
            embedded_timestamp
        )


        if suspicious:

            st.error(
                "⚠️ SUSPICIOUS TIMESTAMP"
            )


            st.warning(
                """
                The embedded timestamp is near the Unix epoch
                or otherwise appears invalid.

                This may indicate:

                • DVR clock reset
                • Missing clock configuration
                • Invalid container metadata
                • Incorrect timestamp written during encoding

                The timestamp should therefore **not automatically
                be treated as the actual recording date**.
                """
            )


        else:

            st.success(
                "✅ Timestamp appears valid"
            )


        # ----------------------------------------------------
        # UTC NORMALIZATION
        # ----------------------------------------------------

        st.markdown(
            "#### 🌍 UTC Normalization"
        )


        normalized = normalize_timestamp(
            embedded_timestamp
        )


        st.code(
            normalized,
            language="text",
        )


        st.caption(
            "UTC conversion is displayed for cross-camera comparison. "
            "A normalized timestamp does not guarantee that the original "
            "DVR clock was accurate."
        )


    else:

        st.info(
            "ℹ️ No embedded creation timestamp was found in this evidence."
        )


        st.caption(
            "The recording timeline will use the file creation timestamp "
            "as a fallback."
        )


    # ========================================================
    # RECORDING TIMELINE
    # ========================================================

    st.divider()

    st.subheader(
        "🕐 Recording Timeline"
    )


    timeline_data = get_recording_timeline(
        meta,
        camera_name="CAM-01",
    )


    if timeline_data:

        timeline_df = pd.DataFrame(
            timeline_data
        )


        start_time = timeline_data[0][
            "Start"
        ]


        finish_time = timeline_data[0][
            "Finish"
        ]


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Recording Start",
                start_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )


        with col2:

            st.metric(
                "Recording End",
                finish_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )


        with col3:

            st.metric(
                "Timeline Duration",
                timeline_data[0][
                    "Duration"
                ],
            )


        # ----------------------------------------------------
        # TIMELINE CHART
        # ----------------------------------------------------

        st.markdown(
            "#### 📈 Recording Segment"
        )


        fig = px.timeline(
            timeline_df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Status",
            hover_data=[
                "Camera",
                "Start Time",
                "End Time",
                "Duration",
                "Timestamp Source",
            ],
            title="DVR Recording Timeline",
        )


        fig.update_yaxes(
            autorange="reversed"
        )


        fig.update_layout(
            height=300,
            xaxis_title="Recording Time",
            yaxis_title="Camera",
        )


        st.plotly_chart(
            fig,
            use_container_width=True,
        )


        # ----------------------------------------------------
        # TIMELINE DETAILS
        # ----------------------------------------------------

        st.markdown(
            "#### 📋 Recording Segment Details"
        )


        display_columns = [
            "Camera",
            "Start Time",
            "End Time",
            "Duration",
            "Status",
            "Timestamp Source",
        ]


        available_columns = [
            column
            for column in display_columns
            if column in timeline_df.columns
        ]


        st.table(
            timeline_df[
                available_columns
            ]
        )


    # ========================================================
    # FIRST EVIDENCE FRAME
    # ========================================================

    st.divider()

    st.subheader(
        "🖼️ First Evidence Frame"
    )


    try:

        cap = cv2.VideoCapture(
            tmp_path
        )


        ret, frame = cap.read()


        cap.release()


        if ret:

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )


            col1, col2, col3 = st.columns(
                [1, 2, 1]
            )


            with col2:

                st.image(
                    frame_rgb,
                    caption="Frame 0 — First frame of evidence",
                    width=600,
                )


        else:

            st.warning(
                "⚠️ Could not extract the first frame."
            )


    except Exception as e:

        st.warning(
            f"⚠️ Could not extract first frame: {e}"
        )


    # ========================================================
    # EVIDENCE FRAME BROWSER
    # ========================================================

    st.divider()

    st.subheader(
        "🖼️ Evidence Frame Browser"
    )


    st.markdown(
        """
        Extract multiple real frames from the uploaded recording
        for rapid forensic examination.
        """
    )


    # --------------------------------------------------------
    # FRAME INFORMATION
    # --------------------------------------------------------

    total_frames = int(
        meta.get(
            "Total Frames",
            0,
        )
    )


    fps = float(
        meta.get(
            "FPS",
            0,
        )
    )


    duration_seconds = float(
        meta.get(
            "Duration (seconds)",
            0,
        )
    )


    if total_frames > 0:

        max_evidence_frames = min(
            12,
            total_frames,
        )


        if max_evidence_frames >= 3:

            evidence_count = st.slider(
                "Number of evidence frames",
                min_value=3,
                max_value=max_evidence_frames,
                value=min(
                    6,
                    max_evidence_frames,
                ),
                step=1,
            )

        else:

            evidence_count = max_evidence_frames


        # ----------------------------------------------------
        # GENERATE EVENLY SPACED FRAME INDICES
        # ----------------------------------------------------

        if evidence_count == 1:

            frame_indices = [
                0
            ]

        else:

            frame_indices = [
                int(
                    round(
                        i
                        * (total_frames - 1)
                        / (evidence_count - 1)
                    )
                )
                for i in range(
                    evidence_count
                )
            ]


        frame_indices = list(
            dict.fromkeys(
                frame_indices
            )
        )


        # ----------------------------------------------------
        # EXTRACT FRAMES
        # ----------------------------------------------------

        evidence_frames = []


        with st.spinner(
            "🎞️ Extracting evidence frames..."
        ):

            cap = cv2.VideoCapture(
                tmp_path
            )


            for frame_number in frame_indices:

                cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    frame_number,
                )


                ret, frame = cap.read()


                if not ret:

                    continue


                frame_rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )


                # Exact video position
                if fps > 0:

                    timestamp_seconds = (
                        frame_number / fps
                    )

                else:

                    timestamp_seconds = 0


                timestamp = str(
                    datetime.timedelta(
                        seconds=round(
                            timestamp_seconds,
                            2,
                        )
                    )
                )


                # ------------------------------------------------
                # BASIC FRAME STATISTICS
                # ------------------------------------------------

                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY,
                )


                brightness = float(
                    np.mean(gray)
                )


                contrast = float(
                    np.std(gray)
                )


                evidence_frames.append(
                    {
                        "frame_number": frame_number,
                        "timestamp": timestamp,
                        "timestamp_seconds": timestamp_seconds,
                        "image": frame_rgb,
                        "brightness": round(
                            brightness,
                            2,
                        ),
                        "contrast": round(
                            contrast,
                            2,
                        ),
                    }
                )


            cap.release()


        # ----------------------------------------------------
        # FRAME STRIP
        # ----------------------------------------------------

        st.markdown(
            "#### 🎞️ Evidence Frame Strip"
        )


        if evidence_frames:

            for row_start in range(
                0,
                len(evidence_frames),
                3,
            ):

                row_frames = evidence_frames[
                    row_start:
                    row_start + 3
                ]


                columns = st.columns(
                    len(row_frames)
                )


                for column, evidence in zip(
                    columns,
                    row_frames,
                ):

                    with column:

                        st.image(
                            evidence["image"],
                            caption=(
                                f"Frame "
                                f"{evidence['frame_number']} "
                                f"• "
                                f"{evidence['timestamp']}"
                            ),
                            width=300,
                        )


                        st.caption(
                            f"Brightness: "
                            f"{evidence['brightness']} | "
                            f"Contrast: "
                            f"{evidence['contrast']}"
                        )


            # ------------------------------------------------
            # EVIDENCE FRAME INDEX
            # ------------------------------------------------

            st.markdown(
                "#### 📋 Evidence Frame Index"
            )


            frame_table_rows = []


            for i, item in enumerate(
                evidence_frames
            ):

                if total_frames > 1:

                    progress = (
                        item["frame_number"]
                        / (total_frames - 1)
                    ) * 100

                else:

                    progress = 0


                frame_table_rows.append(
                    {
                        "Evidence Frame": i + 1,
                        "Frame Number": item[
                            "frame_number"
                        ],
                        "Video Time": item[
                            "timestamp"
                        ],
                        "Position": (
                            f"{progress:.1f}%"
                        ),
                        "Brightness": item[
                            "brightness"
                        ],
                        "Contrast": item[
                            "contrast"
                        ],
                    }
                )


            frame_table = pd.DataFrame(
                frame_table_rows
            )


            st.table(
                frame_table
            )


            # ------------------------------------------------
            # DETAILED FRAME EXAMINATION
            # ------------------------------------------------

            st.divider()

            st.markdown(
                "#### 🔍 Detailed Frame Examination"
            )


            selected_index = st.selectbox(
                "Select an evidence frame",
                options=list(
                    range(
                        len(evidence_frames)
                    )
                ),
                format_func=lambda x: (
                    f"Evidence Frame {x + 1} — "
                    f"Frame "
                    f"{evidence_frames[x]['frame_number']} "
                    f"— "
                    f"{evidence_frames[x]['timestamp']}"
                ),
            )


            selected = evidence_frames[
                selected_index
            ]


            col1, col2 = st.columns(
                [2, 1]
            )


            with col1:

                st.image(
                    selected["image"],
                    caption=(
                        f"Evidence Frame "
                        f"{selected_index + 1}"
                    ),
                    width=700,
                )


            with col2:

                st.markdown(
                    "### Frame Information"
                )


                st.metric(
                    "Frame Number",
                    selected[
                        "frame_number"
                    ],
                )


                st.metric(
                    "Video Position",
                    selected[
                        "timestamp"
                    ],
                )


                if total_frames > 1:

                    frame_progress = (
                        selected[
                            "frame_number"
                        ]
                        / (total_frames - 1)
                    ) * 100

                else:

                    frame_progress = 0


                st.metric(
                    "Video Progress",
                    f"{frame_progress:.2f}%",
                )


                if fps > 0:

                    st.metric(
                        "Frame Rate",
                        f"{fps:.2f} FPS",
                    )


                st.metric(
                    "Brightness",
                    selected[
                        "brightness"
                    ],
                )


                st.metric(
                    "Contrast",
                    selected[
                        "contrast"
                    ],
                )


                st.caption(
                    """
                    Frame numbers provide a precise reference
                    for returning to the original evidence.
                    """
                )


            # ------------------------------------------------
            # FRAME NAVIGATION
            # ------------------------------------------------

            st.markdown(
                "### 🎯 Evidence Navigation"
            )


            nav1, nav2, nav3 = st.columns(3)


            with nav1:

                if selected_index > 0:

                    st.write(
                        "⬅️ Previous evidence frame"
                    )

                else:

                    st.write(
                        "⬅️ First evidence frame"
                    )


            with nav2:

                st.write(
                    f"Evidence "
                    f"{selected_index + 1} "
                    f"of "
                    f"{len(evidence_frames)}"
                )


            with nav3:

                if (
                    selected_index
                    < len(evidence_frames) - 1
                ):

                    st.write(
                        "Next evidence frame ➡️"
                    )

                else:

                    st.write(
                        "Last evidence frame ➡️"
                    )


        else:

            st.warning(
                "⚠️ No evidence frames could be extracted."
            )


    else:

        st.warning(
            "⚠️ Invalid frame count."
        )


    # ========================================================
    # FRAME TIMELINE VISUALIZATION
    # ========================================================

    if evidence_frames:

        st.divider()

        st.subheader(
            "📍 Evidence Frame Distribution"
        )


        frame_plot_df = pd.DataFrame(
            [
                {
                    "Frame": item[
                        "frame_number"
                    ],
                    "Time (seconds)": round(
                        item[
                            "timestamp_seconds"
                        ],
                        2,
                    ),
                }
                for item in evidence_frames
            ]
        )


        fig_frames = px.scatter(
            frame_plot_df,
            x="Time (seconds)",
            y="Frame",
            hover_data=[
                "Frame",
                "Time (seconds)",
            ],
            title="Indexed Evidence Frames Across Recording",
        )


        fig_frames.update_layout(
            height=350,
            xaxis_title="Video Time (seconds)",
            yaxis_title="Frame Number",
        )


        st.plotly_chart(
            fig_frames,
            use_container_width=True,
        )


        st.caption(
            "Each point represents an actual frame extracted from the uploaded evidence."
        )


    # ========================================================
    # FORENSIC SUMMARY
    # ========================================================

    st.divider()

    st.subheader(
        "🧾 Forensic Analysis Summary"
    )


    summary_items = []


    summary_items.append(
        f"📁 Evidence: {uploaded.name}"
    )


    summary_items.append(
        f"🎞️ Duration: "
        f"{meta.get('Duration (readable)', 'N/A')}"
    )


    summary_items.append(
        f"📐 Resolution: "
        f"{meta.get('Resolution', 'N/A')}"
    )


    summary_items.append(
        f"🎥 Codec: "
        f"{meta.get('Video Codec', 'N/A')}"
    )


    summary_items.append(
        f"🎞️ Total Frames: "
        f"{meta.get('Total Frames', 'N/A')}"
    )


    summary_items.append(
        f"🔐 SHA-256: "
        f"{meta.get('SHA-256', 'Not calculated')}"
    )


    if embedded_timestamp:

        if suspicious:

            summary_items.append(
                "⚠️ Embedded timestamp requires forensic verification"
            )

        else:

            summary_items.append(
                "✅ Embedded timestamp appears valid"
            )

    else:

        summary_items.append(
            "ℹ️ No embedded timestamp available"
        )


    summary_items.append(
        "🔎 Recording timeline reconstructed from available evidence metadata"
    )


    summary_items.append(
        "🖼️ Evidence frames indexed for rapid examination"
    )


    if evidence_frames:

        summary_items.append(
            f"🎯 {len(evidence_frames)} evidence frames extracted"
        )


    for item in summary_items:

        st.write(
            f"- {item}"
        )


    st.success(
        "✅ Metadata and evidence-frame analysis completed."
    )


# ============================================================
# CLEANUP
# ============================================================

finally:

    if tmp_path:

        try:

            os.unlink(
                tmp_path
            )

        except Exception:

            pass