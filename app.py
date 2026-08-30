"""
app.py — Main Home Page
ASSIGNED TO: Member 1
Your job: Make this home page look professional and impressive.
Add your team's names, a project description, and navigation cards.
"""

import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DVR/NVR Forensic Tool | SIH 2026",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared session state (used by all modules to share data) ─────────────────
if "case_id" not in st.session_state:
    st.session_state.case_id = ""
if "hashes" not in st.session_state:
    st.session_state.hashes = {}
if "metadata" not in st.session_state:
    st.session_state.metadata = {}
if "detections" not in st.session_state:
    st.session_state.detections = []
if "device_info" not in st.session_state:
    st.session_state.device_info = {}
if "recovered_files" not in st.session_state:
    st.session_state.recovered_files = []

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem 0;">
    <h1 style="font-size:3rem; font-weight:800; color:#00D4FF;">
        🔍 DVR/NVR Forensic Analysis Tool
    </h1>
    <p style="font-size:1.2rem; color:#94A3B8; max-width:700px; margin:auto;">
        A unified, vendor-agnostic platform for forensic acquisition, recovery,
        analysis, and reporting of surveillance evidence.
    </p>
    <br/>
    <span style="background:#1E293B; color:#00D4FF; padding:6px 16px;
                 border-radius:20px; font-size:0.9rem; border:1px solid #00D4FF;">
        🏆 Smart India Hackathon 2026 — Problem Statement PS1234
    </span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Stats Row ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Supported Brands", "8+", "Dahua, Hikvision, CP Plus...")
col2.metric("Hash Algorithms", "2", "MD5 + SHA-256")
col3.metric("AI Models", "YOLOv8", "Object + Face Detection")
col4.metric("Report Format", "PDF", "Court-admissible")

st.divider()

# ── Module Cards ─────────────────────────────────────────────────────────────
st.subheader("📦 Forensic Modules")
st.caption("Use the sidebar to navigate between modules, or click a card below.")

cards = [
    ("🔍", "Device Detection",     "Auto-identify DVR/NVR brand from uploaded footage",    "pages/1_🔍_Device_Detection"),
    ("🔒", "Forensic Acquisition", "Create forensic images with MD5 & SHA-256 verification","pages/2_🔒_Acquisition"),
    ("📋", "Metadata Parser",      "Extract timestamps, resolution, FPS, and channel info", "pages/3_📋_Metadata_Parser"),
    ("🗂️", "Recovery Simulator",   "Recover deleted and fragmented video recordings",       "pages/4_🗂️_Recovery_Simulator"),
    ("🤖", "AI Analytics",         "Detect faces, objects, and motion using YOLOv8",        "pages/5_🤖_AI_Analytics"),
    ("📄", "Report Generator",     "Generate court-admissible forensic PDF reports",        "pages/6_📄_Report_Generator"),
]

col_a, col_b, col_c = st.columns(3)
columns = [col_a, col_b, col_c]

for i, (icon, title, desc, _) in enumerate(cards):
    with columns[i % 3]:
        st.markdown(f"""
        <div style="background:#0F172A; border:1px solid #1E293B; border-radius:12px;
                    padding:1.2rem; margin-bottom:1rem; transition:all 0.2s;
                    border-left: 4px solid #00D4FF;">
            <h3 style="margin:0; color:#00D4FF;">{icon} {title}</h3>
            <p style="color:#94A3B8; margin:0.5rem 0 0 0; font-size:0.9rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Supported Brands ─────────────────────────────────────────────────────────
st.subheader("🏭 Supported DVR/NVR Brands")

brands = [
    ("Dahua Technology",  "🔴", ".dav format, JFFS2 filesystem"),
    ("Hikvision",         "🔵", ".mp4/.h264, proprietary NVR format"),
    ("CP Plus",           "🟢", ".h264 streams, custom metadata"),
    ("TP-Link",           "🟡", "VIGI format, cloud-linked storage"),
    ("Uniview",           "🟠", "UNV format, ONVIF compatible"),
    ("Matrix Comsec",     "🟣", "Custom storage, NVR-specific format"),
    ("Honeywell",         "⚪", "MAXPRO format, encrypted storage"),
    ("Godrej",            "🟤", "Custom H.265 container"),
]

cols = st.columns(4)
for i, (brand, dot, desc) in enumerate(brands):
    with cols[i % 4]:
        st.markdown(f"""
        <div style="background:#0F172A; border:1px solid #1E293B; border-radius:8px;
                    padding:0.8rem; margin-bottom:0.8rem; text-align:center;">
            <div style="font-size:1.5rem;">{dot}</div>
            <div style="color:#E2E8F0; font-weight:600; font-size:0.9rem;">{brand}</div>
            <div style="color:#64748B; font-size:0.75rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Quick Start ───────────────────────────────────────────────────────────────
st.subheader("🚀 Quick Start")
st.info("""
**How to use this tool:**
1. Go to **🔍 Device Detection** → Upload your DVR footage
2. Go to **🔒 Acquisition** → Generate forensic hashes
3. Go to **📋 Metadata Parser** → View video timeline
4. Go to **🗂️ Recovery** → Simulate deleted file recovery
5. Go to **🤖 AI Analytics** → Run face & object detection
6. Go to **📄 Report Generator** → Download your forensic PDF report
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#475569; padding:2rem 0; font-size:0.85rem;">
    Built for Smart India Hackathon 2026 &nbsp;|&nbsp;
    Problem: Multi-Vendor DVR/NVR Forensic Analysis &nbsp;|&nbsp;
    Team: [Your Team Name]
</div>
""", unsafe_allow_html=True)
