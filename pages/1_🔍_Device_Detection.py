"""
pages/1_🔍_Device_Detection.py — Device Identification Module
ASSIGNED TO: Member 1
YOUR TASKS:
  [ ] Improve the brand detection rules (add more filename patterns)
  [ ] Add a vendor comparison table at the bottom
  [ ] Add file format explanation for each brand
  [ ] Style the result card nicely
"""

import streamlit as st

st.set_page_config(page_title="Device Detection | DVR Forensic", page_icon="🔍", layout="wide")

# ── Page Header ───────────────────────────────────────────────────────────────
st.title("🔍 Device Detection")
st.markdown("Upload surveillance footage to automatically identify the DVR/NVR brand and model.")
st.divider()

# ── Vendor Database ───────────────────────────────────────────────────────────
# TODO (Member 1): Add more keywords and models to improve detection accuracy
VENDOR_DB = {
    "dahua": {
        "brand":      "Dahua Technology",
        "model":      "DHI-NVR4108HS-8P-4KS2/L",
        "format":     ".dav / H.264 / H.265",
        "filesystem": "JFFS2 / Proprietary",
        "country":    "China 🇨🇳",
        "color":      "#FF6B35",
        "logo":       "🔴",
    },
    "hik": {
        "brand":      "Hikvision",
        "model":      "DS-7608NI-K2/8P",
        "format":     ".mp4 / .h264 / IVS",
        "filesystem": "Proprietary NVR Format",
        "country":    "China 🇨🇳",
        "color":      "#E53E3E",
        "logo":       "🔵",
    },
    "hikvision": {
        "brand":      "Hikvision",
        "model":      "DS-7608NI-K2/8P",
        "format":     ".mp4 / .h264 / IVS",
        "filesystem": "Proprietary NVR Format",
        "country":    "China 🇨🇳",
        "color":      "#E53E3E",
        "logo":       "🔵",
    },
    "cpplus": {
        "brand":      "CP Plus",
        "model":      "CP-UNR-4K4241-V3",
        "format":     ".h264 / .avi",
        "filesystem": "Custom EXT4 variant",
        "country":    "India 🇮🇳",
        "color":      "#38A169",
        "logo":       "🟢",
    },
    "cp-plus": {
        "brand":      "CP Plus",
        "model":      "CP-UNR-4K4241-V3",
        "format":     ".h264 / .avi",
        "filesystem": "Custom EXT4 variant",
        "country":    "India 🇮🇳",
        "color":      "#38A169",
        "logo":       "🟢",
    },
    "tplink": {
        "brand":      "TP-Link (VIGI)",
        "model":      "VIGI NVR1016H",
        "format":     ".mp4 (VIGI proprietary)",
        "filesystem": "FAT32 / Custom",
        "country":    "China 🇨🇳",
        "color":      "#D69E2E",
        "logo":       "🟡",
    },
    "tp-link": {
        "brand":      "TP-Link (VIGI)",
        "model":      "VIGI NVR1016H",
        "format":     ".mp4 (VIGI proprietary)",
        "filesystem": "FAT32 / Custom",
        "country":    "China 🇨🇳",
        "color":      "#D69E2E",
        "logo":       "🟡",
    },
    "uniview": {
        "brand":      "Uniview (UNV)",
        "model":      "NVR302-16E2-P16",
        "format":     ".mp4 / UNV stream",
        "filesystem": "ONVIF-compatible / Custom",
        "country":    "China 🇨🇳",
        "color":      "#DD6B20",
        "logo":       "🟠",
    },
    "matrix": {
        "brand":      "Matrix Comsec",
        "model":      "SATATYA NVRX 3202-16P",
        "format":     ".avi / Custom H.265",
        "filesystem": "Proprietary Matrix FS",
        "country":    "India 🇮🇳",
        "color":      "#805AD5",
        "logo":       "🟣",
    },
    "honeywell": {
        "brand":      "Honeywell Security",
        "model":      "MAXPRO NVR XE",
        "format":     ".mp4 / MAXPRO encrypted",
        "filesystem": "NTFS / Encrypted",
        "country":    "USA 🇺🇸",
        "color":      "#718096",
        "logo":       "⚪",
    },
    "godrej": {
        "brand":      "Godrej Security Solutions",
        "model":      "GEYE-NVR 3216-4K",
        "format":     ".mp4 / H.265 custom",
        "filesystem": "Custom Godrej FS",
        "country":    "India 🇮🇳",
        "color":      "#744210",
        "logo":       "🟤",
    },
}


def detect_brand(filename: str, filesize_mb: float) -> dict:
    """Detect DVR brand from filename keywords."""
    filename_lower = filename.lower()
    for keyword, info in VENDOR_DB.items():
        if keyword in filename_lower:
            return info
    # Default if unknown
    return {
        "brand":      "Unknown / Generic DVR",
        "model":      "Unable to determine",
        "format":     "Standard MP4 / AVI",
        "filesystem": "Unknown",
        "country":    "Unknown",
        "color":      "#4A5568",
        "logo":       "❓",
    }


# ── Upload Section ────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📁 Upload DVR footage file",
    type=["mp4", "avi", "dav", "h264", "mkv", "mov"],
    help="Upload any video file. Rename it with the brand name for better detection (e.g. dahua_cam01.mp4)"
)

if uploaded:
    filesize_mb = uploaded.size / (1024 * 1024)

    st.markdown("### 🔎 Analyzing file...")
    progress = st.progress(0)
    import time
    for i in range(0, 101, 20):
        time.sleep(0.1)
        progress.progress(i)

    # ── Run Detection ────────────────────────────────────────────────
    result = detect_brand(uploaded.name, filesize_mb)

    # ── Store in session state (for other pages) ──────────────────────
    st.session_state.device_info = result
    st.session_state.uploaded_filename = uploaded.name
    st.session_state.uploaded_filesize = filesize_mb
    st.session_state.uploaded_bytes = uploaded.getvalue()

    st.success("✅ Analysis complete!")
    st.divider()

    # ── Result Display ────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div style="background:#0F172A; border:2px solid {result['color']};
                    border-radius:16px; padding:1.5rem;">
            <div style="font-size:3rem; margin-bottom:0.5rem;">{result['logo']}</div>
            <h2 style="color:{result['color']}; margin:0;">{result['brand']}</h2>
            <p style="color:#94A3B8; margin:0.3rem 0;">📹 Model: {result['model']}</p>
            <p style="color:#94A3B8; margin:0.3rem 0;">📁 Format: {result['format']}</p>
            <p style="color:#94A3B8; margin:0.3rem 0;">💾 File System: {result['filesystem']}</p>
            <p style="color:#94A3B8; margin:0.3rem 0;">🌍 Origin: {result['country']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📊 File Information")
        st.metric("File Name", uploaded.name)
        st.metric("File Size", f"{filesize_mb:.2f} MB")
        st.metric("File Type", uploaded.type or "Unknown")

        if result["brand"] != "Unknown / Generic DVR":
            st.success(f"✅ Brand identified: **{result['brand']}**")
            st.info("💡 Tip: Proceed to **Forensic Acquisition** to hash this file.")
        else:
            st.warning("⚠️ Brand not identified. Try renaming the file with the brand name.")
            st.info("Example: `dahua_cam01.mp4`, `hikvision_footage.avi`")

    st.divider()

    # ── Vendor Comparison Table ────────────────────────────────────────
    # TODO (Member 1): Expand this table with more detailed information
    st.subheader("🏭 DVR/NVR Brand Comparison")
    import pandas as pd
    comparison = pd.DataFrame([
        ["Dahua Technology", ".dav / H.264", "JFFS2", "India, Global", "High"],
        ["Hikvision",        ".mp4 / H.264", "Proprietary", "India, Global", "Very High"],
        ["CP Plus",          ".h264 / .avi", "EXT4 variant", "India", "High"],
        ["TP-Link (VIGI)",   ".mp4",         "FAT32",        "Global", "Medium"],
        ["Uniview (UNV)",    ".mp4 / UNV",   "ONVIF / Custom","Global", "Medium"],
        ["Matrix Comsec",    ".avi / H.265", "Proprietary",  "India", "Medium"],
        ["Honeywell",        "MAXPRO / .mp4","NTFS / Encrypted","Global","Low"],
        ["Godrej",           ".mp4 / H.265", "Custom FS",    "India", "Low"],
    ], columns=["Brand", "Video Format", "File System", "Market", "India Prevalence"])

    st.dataframe(comparison, use_container_width=True, hide_index=True)

else:
    # ── Placeholder when no file uploaded ────────────────────────────
    st.info("👆 Upload a video file above to begin device identification.")

    st.markdown("#### 💡 Quick Test")
    st.code("""
Rename any .mp4 video on your computer to include a brand name:
  dahua_surveillance.mp4     → Detects as Dahua
  hikvision_cam.mp4          → Detects as Hikvision
  cpplus_entrance.avi        → Detects as CP Plus
Then upload it above!
    """)
