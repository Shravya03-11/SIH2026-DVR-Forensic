"""
pages/4_🗂️_Recovery_Simulator.py — Deleted Footage Recovery Module
ASSIGNED TO: Member 4
YOUR TASKS:
  [ ] The basic animation is done — make the hex display look more realistic
  [ ] Add a bar chart showing: Total Space / Used Space / Recovered Space
  [ ] Add a "sector map" visual (colored blocks showing used/free/recovered sectors)
  [ ] Make the recovered files table more detailed
  [ ] Add a download button for the "recovered" file (use the uploaded file as a placeholder)
"""

import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="Recovery | DVR Forensic", page_icon="🗂️", layout="wide")

st.title("🗂️ Deleted Footage Recovery")
st.markdown("Scan disk image for deleted, fragmented, or overwritten video recordings using forensic file carving.")
st.divider()

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📁 Upload disk image or video file to scan",
    type=["mp4", "avi", "dav", "h264", "mkv", "mov", "img", "bin"],
)

if uploaded:
    file_bytes  = uploaded.getvalue()
    filesize_mb = len(file_bytes) / (1024 * 1024)

    st.info(f"📁 File loaded: **{uploaded.name}** ({filesize_mb:.2f} MB) — Ready to scan")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Size",      f"{filesize_mb:.1f} MB")
    col2.metric("Estimated Sectors", f"{int(filesize_mb * 512):,}")
    col3.metric("Scan Method",      "H.264 Header Carving")

    st.divider()

    if st.button("🔍 Start Recovery Scan", type="primary"):

        # ── Scanning Animation ────────────────────────────────────────
        st.markdown("### 🔬 Scanning in Progress...")
        progress  = st.progress(0)
        status    = st.empty()
        hex_display = st.empty()

        # Simulate hex dump display
        def random_hex_line(offset: int) -> str:
            hex_bytes = " ".join(f"{random.randint(0, 255):02X}" for _ in range(16))
            return f"0x{offset:08X}  {hex_bytes}"

        scan_stages = [
            (5,  "Initializing sector scanner..."),
            (12, "Scanning MBR (Master Boot Record)..."),
            (20, "Parsing partition table..."),
            (30, "Scanning unallocated space — Zone A (0x00000000 - 0x0FFFFFFF)..."),
            (38, "Detected H.264 NAL Unit header at 0x4A2F08C0!"),
            (45, "Scanning Zone B (0x10000000 - 0x1FFFFFFF)..."),
            (55, "Found video fragment — CAM02 stream at 0x1B8A34D0..."),
            (62, "Scanning Zone C (0x20000000 - 0x2FFFFFFF)..."),
            (70, "Partial H.265 stream detected at 0x27CE1200..."),
            (78, "Reconstructing file fragments..."),
            (85, "Verifying recovered stream integrity..."),
            (92, "Computing recovery confidence scores..."),
            (100, "✅ Scan complete!"),
        ]

        for pct, msg in scan_stages:
            time.sleep(0.5)
            progress.progress(pct)
            status.info(f"🔍 {msg}")

            # Show moving hex display for visual effect
            if pct < 92:
                offset = random.randint(0, 0xFFFFFF)
                hex_lines = "\n".join(random_hex_line(offset + i * 16) for i in range(6))
                hex_display.code(hex_lines, language=None)

        hex_display.empty()
        st.success("🎉 Recovery scan complete!")
        st.balloons()
        st.divider()

        # ── Disk Space Visual ─────────────────────────────────────────
        st.subheader("💾 Disk Analysis")

        total   = filesize_mb
        used    = round(total * random.uniform(0.55, 0.75), 1)
        deleted = round(total * random.uniform(0.10, 0.20), 1)
        free    = round(total - used - deleted, 1)

        import plotly.graph_objects as go
        fig = go.Figure(go.Bar(
            x=["Used Space", "Deleted (Recoverable)", "Free Space"],
            y=[used, deleted, free],
            marker_color=["#3B82F6", "#F59E0B", "#22C55E"],
            text=[f"{used:.1f} MB", f"{deleted:.1f} MB", f"{free:.1f} MB"],
            textposition="outside",
        ))
        fig.update_layout(
            title="Disk Space Distribution",
            plot_bgcolor  = "#0A0F1E",
            paper_bgcolor = "#0A0F1E",
            font_color    = "#E2E8F0",
            yaxis_title   = "Size (MB)",
            height        = 300,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Sector Map ────────────────────────────────────────────────
        # TODO (Member 4): Make this look better — add a grid of colored boxes
        st.subheader("🗺️ Sector Map")
        st.markdown("""
        <div style="font-family: monospace; font-size: 10px; line-height: 1.4; 
                    background:#0F172A; padding:1rem; border-radius:8px; 
                    border:1px solid #1E293B;">
        """, unsafe_allow_html=True)

        sector_html = ""
        for i in range(200):
            r = random.random()
            if r < 0.60:
                color = "#3B82F6"  # Used (blue)
            elif r < 0.75:
                color = "#F59E0B"  # Deleted (yellow)
            elif r < 0.85:
                color = "#22C55E"  # Recovered (green)
            else:
                color = "#1E293B"  # Free (dark)
            sector_html += f'<span style="display:inline-block;width:12px;height:12px;background:{color};margin:1px;border-radius:2px;" title="Sector {i}"></span>'

        st.markdown(f"""
        <div style="background:#0F172A; padding:1rem; border-radius:8px; border:1px solid #1E293B;">
            {sector_html}
            <br/><br/>
            <span style="color:#3B82F6;">■</span> Used &nbsp;
            <span style="color:#F59E0B;">■</span> Deleted &nbsp;
            <span style="color:#22C55E;">■</span> Recovered &nbsp;
            <span style="color:#1E293B; border:1px solid #475569;">■</span> Free
        </div>
        """, unsafe_allow_html=True)

        # ── Recovered Files Table ─────────────────────────────────────
        st.divider()
        st.subheader("📁 Recovered Files")

        # Generate realistic-looking recovered files
        recovered = [
            {
                "File":            "CAM01_20240815_143022.mp4",
                "Size":            f"{random.randint(50, 200)} MB",
                "Sector Start":    f"0x{random.randint(0x1000000, 0x9000000):08X}",
                "Camera":          "CAM-01",
                "Estimated Date":  "2024-08-15 14:30:22",
                "Recovery Status": "✅ Complete",
                "Confidence":      f"{random.randint(90, 99)}%",
            },
            {
                "File":            "CAM02_20240815_143508.mp4",
                "Size":            f"{random.randint(50, 200)} MB",
                "Sector Start":    f"0x{random.randint(0x1000000, 0x9000000):08X}",
                "Camera":          "CAM-02",
                "Estimated Date":  "2024-08-15 14:35:08",
                "Recovery Status": "✅ Complete",
                "Confidence":      f"{random.randint(90, 99)}%",
            },
            {
                "File":            "CAM03_20240815_144012.mp4",
                "Size":            f"{random.randint(50, 200)} MB",
                "Sector Start":    f"0x{random.randint(0x1000000, 0x9000000):08X}",
                "Camera":          "CAM-03",
                "Estimated Date":  "2024-08-15 14:40:12",
                "Recovery Status": "⚠️ Partial",
                "Confidence":      f"{random.randint(60, 79)}%",
            },
        ]

        st.session_state.recovered_files = recovered
        st.dataframe(pd.DataFrame(recovered), use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Files Found",      len(recovered))
        col2.metric("Fully Recovered",  sum(1 for r in recovered if "Complete" in r["Recovery Status"]))
        col3.metric("Partial Recovery", sum(1 for r in recovered if "Partial"  in r["Recovery Status"]))

        # Download placeholder
        st.divider()
        st.download_button(
            "📥 Download Recovery Report (CSV)",
            data=pd.DataFrame(recovered).to_csv(index=False),
            file_name="recovery_report.csv",
            mime="text/csv",
        )

else:
    st.info("👆 Upload a file above to begin the recovery scan.")
    st.markdown("""
    **How forensic file carving works:**
    1. Scan every sector of the disk image
    2. Look for known file headers (H.264 starts with `0x00 0x00 0x00 0x01`)
    3. Extract data from that point until the file footer
    4. Reconstruct the file even if it was deleted
    
    > This simulation shows exactly what real forensic tools like **Scalpel** and **Foremost** do.
    """)
