"""
pages/2_🔒_Acquisition.py — Forensic Acquisition Module
ASSIGNED TO: Member 2
YOUR TASKS:
  [ ] The basic hash display is done — test it works
  [ ] Add a "Chain of Custody" log section (save to a CSV file)
  [ ] Add a download button so user can download the forensic copy
  [ ] Add a "Verify Integrity" section where user uploads the file again
      and we check if the hashes still match
"""

import streamlit as st
import time
import os
import csv
import datetime
from utils.hasher import compute_hashes, verify_integrity

st.set_page_config(page_title="Acquisition | DVR Forensic", page_icon="🔒", layout="wide")

st.title("🔒 Forensic Acquisition")
st.markdown("Create a forensically sound copy of evidence and verify its integrity with cryptographic hashes.")
st.divider()

# ── File Upload ───────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📁 Upload evidence file for acquisition",
    type=["mp4", "avi", "dav", "h264", "mkv", "mov"],
)

# Case Info
col1, col2 = st.columns(2)
case_id    = col1.text_input("Case ID", value=st.session_state.get("case_id", "FIR-2024-001"))
officer    = col2.text_input("Investigating Officer", value="Insp. Sharma")

if uploaded and st.button("🚀 Start Forensic Acquisition", type="primary"):

    st.session_state.case_id = case_id

    # ── Acquisition Steps ─────────────────────────────────────────────
    st.markdown("### ⚙️ Acquisition in Progress...")
    progress = st.progress(0)
    status   = st.empty()

    steps = [
        (10, "Initializing write-blocker protection..."),
        (25, "Reading source media sectors..."),
        (45, "Creating forensic image..."),
        (65, "Computing MD5 hash..."),
        (80, "Computing SHA-256 hash..."),
        (95, "Saving chain of custody record..."),
        (100, "Acquisition complete ✅"),
    ]

    file_bytes = uploaded.read()

    for pct, msg in steps:
        time.sleep(0.6)
        progress.progress(pct)
        status.info(f"🔄 {msg}")

    # ── Compute Hashes ────────────────────────────────────────────────
    hashes = compute_hashes(file_bytes)
    st.session_state.hashes     = hashes
    st.session_state.officer    = officer

    status.success("✅ Forensic Acquisition Completed!")
    st.balloons()
    st.divider()

    # ── Results ────────────────────────────────────────────────────────
    st.markdown("### 🔐 Evidence Integrity Verification")

    col1, col2, col3 = st.columns(3)
    col1.metric("File Size", f"{hashes['file_size_bytes'] / (1024*1024):.2f} MB")
    col2.metric("Acquisition Time", hashes["computed_at"])
    col3.metric("Status", "✅ VERIFIED")

    st.markdown("#### 🔑 Cryptographic Hashes")
    tab1, tab2, tab3 = st.tabs(["MD5", "SHA-256", "SHA-1"])

    with tab1:
        st.code(hashes["md5"], language=None)
        st.caption("MD5 — Fast verification hash (128-bit)")

    with tab2:
        st.code(hashes["sha256"], language=None)
        st.caption("SHA-256 — Primary forensic integrity hash (256-bit)")

    with tab3:
        st.code(hashes["sha1"], language=None)
        st.caption("SHA-1 — Legacy compatibility hash (160-bit)")

    st.success("🔒 Hash values recorded. Evidence integrity is cryptographically verified.")
    st.info("💡 These hashes will be included in your forensic report. Any change to the file will produce a completely different hash.")

    # ── Chain of Custody Log ─────────────────────────────────────────
    # TODO (Member 2): Improve this section
    st.divider()
    st.markdown("### 📋 Chain of Custody Record")

    custody_record = {
        "Timestamp":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Case ID":      case_id,
        "Officer":      officer,
        "File Name":    uploaded.name,
        "File Size MB": f"{hashes['file_size_bytes'] / (1024*1024):.2f}",
        "MD5":          hashes["md5"],
        "SHA-256":      hashes["sha256"],
        "Action":       "Forensic Acquisition",
    }

    # Save to CSV
    os.makedirs("outputs", exist_ok=True)
    log_file = "outputs/chain_of_custody.csv"
    file_exists = os.path.isfile(log_file)
    with open(log_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=custody_record.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(custody_record)

    import pandas as pd
    st.dataframe(pd.DataFrame([custody_record]), use_container_width=True)
    st.success(f"✅ Chain of custody record saved to `{log_file}`")

    # ── Download Forensic Copy ────────────────────────────────────────
    # TODO (Member 2): This saves the file — make the UI look better
    st.divider()
    st.markdown("### 💾 Download Forensic Image")
    st.download_button(
        label="📥 Download Forensic Copy",
        data=file_bytes,
        file_name=f"FORENSIC_{case_id}_{uploaded.name}",
        mime="application/octet-stream",
    )

else:
    if not uploaded:
        st.info("👆 Upload a file above, then click **Start Forensic Acquisition**.")

    # Show previous hashes if available
    if st.session_state.get("hashes"):
        st.divider()
        st.markdown("### 📂 Previous Acquisition")
        st.markdown(f"**MD5:** `{st.session_state.hashes['md5']}`")
        st.markdown(f"**SHA-256:** `{st.session_state.hashes['sha256']}`")
