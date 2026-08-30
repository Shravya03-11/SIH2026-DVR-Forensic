"""
pages/6_📄_Report_Generator.py — Forensic Report Generator
ASSIGNED TO: Member 6 (Integration Lead)
YOUR TASKS:
  [ ] Test that the PDF generates correctly
  [ ] Make the form look nicer
  [ ] Add a preview of what will be in the report before generating
  [ ] If any module hasn't been run, show a checklist warning
  [ ] Add an "Email Report" placeholder button
"""

import streamlit as st
import datetime
import os

st.set_page_config(page_title="Report Generator | DVR Forensic", page_icon="📄", layout="wide")

st.title("📄 Forensic Report Generator")
st.markdown("Compile all analysis results into a professionally formatted, court-admissible forensic PDF report.")
st.divider()

# ── Data Readiness Check ──────────────────────────────────────────────────────
st.subheader("📋 Analysis Completeness Check")
st.caption("Complete all modules before generating the report for the best results.")

checks = {
    "🔍 Device Detection":    bool(st.session_state.get("device_info")),
    "🔒 Acquisition (Hashes)":bool(st.session_state.get("hashes")),
    "📋 Metadata Extracted":  bool(st.session_state.get("metadata")),
    "🗂️ Recovery Scan":       bool(st.session_state.get("recovered_files")),
    "🤖 AI Detection":        bool(st.session_state.get("detections")),
}

cols = st.columns(5)
for i, (label, done) in enumerate(checks.items()):
    with cols[i]:
        if done:
            st.success(f"{label}\n✅ Done")
        else:
            st.warning(f"{label}\n⚠️ Not run")

completed = sum(checks.values())
st.progress(completed / len(checks))
st.caption(f"{completed}/{len(checks)} modules completed. You can still generate a report — missing sections will show placeholders.")

st.divider()

# ── Case Information Form ─────────────────────────────────────────────────────
st.subheader("📝 Case Details")

with st.form("report_form"):
    col1, col2 = st.columns(2)

    with col1:
        case_id     = st.text_input("Case / FIR Number",   value=st.session_state.get("case_id", "FIR-2024-001"))
        officer     = st.text_input("Investigating Officer", value=st.session_state.get("officer", "Insp. Sharma"))
        department  = st.text_input("Department / Unit",    value="Cyber Crime Division")
        location    = st.text_input("Crime Location",       value="New Delhi")

    with col2:
        incident_date = st.date_input("Incident Date",     value=datetime.date(2024, 8, 15))
        report_date   = st.date_input("Report Date",       value=datetime.date.today())
        priority      = st.selectbox("Priority",           ["🔴 High", "🟡 Medium", "🟢 Low"])
        classification = st.selectbox("Classification",    ["CONFIDENTIAL", "RESTRICTED", "INTERNAL"])

    notes = st.text_area("Additional Notes / Observations", height=100,
                         placeholder="Add any relevant observations about the evidence...")

    submitted = st.form_submit_button("🚀 Generate Forensic Report", type="primary")

# ── Generate Report ───────────────────────────────────────────────────────────
if submitted:

    st.session_state.case_id = case_id
    st.session_state.officer = officer

    with st.spinner("📄 Generating forensic report..."):
        import time
        time.sleep(1.5)

        from utils.pdf_report import generate_report

        case_info = {
            "Case ID":          case_id,
            "Incident Date":    str(incident_date),
            "Report Date":      str(report_date),
            "Investigating Officer": officer,
            "Department":       department,
            "Crime Location":   location,
            "Priority":         priority,
            "Classification":   classification,
            "Notes":            notes or "None",
        }

        pdf_bytes = generate_report(
            case_info   = case_info,
            device_info = st.session_state.get("device_info",   {}),
            hashes      = st.session_state.get("hashes",        {}),
            metadata    = st.session_state.get("metadata",      {}),
            detections  = st.session_state.get("detections",    []),
            recovered   = st.session_state.get("recovered_files", []),
        )

    # Save locally
    os.makedirs("outputs", exist_ok=True)
    filename    = f"Forensic_Report_{case_id}_{datetime.date.today()}.pdf"
    output_path = os.path.join("outputs", filename)
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    st.success("✅ Forensic report generated successfully!")
    st.balloons()

    # ── Report Summary ────────────────────────────────────────────────
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Case ID",    case_id)
    col2.metric("Officer",    officer)
    col3.metric("Pages",      "~4–6")
    col4.metric("Format",     "PDF")

    # Report contents preview
    st.subheader("📋 Report Contents")
    sections = [
        ("1", "Case Information",         "✅" if case_id else "⚠️"),
        ("2", "Device Identification",    "✅" if st.session_state.get("device_info") else "⚠️ Placeholder"),
        ("3", "Evidence Integrity Hashes","✅" if st.session_state.get("hashes") else "⚠️ Placeholder"),
        ("4", "Video Metadata",           "✅" if st.session_state.get("metadata") else "⚠️ Placeholder"),
        ("5", "AI Detection Results",     "✅" if st.session_state.get("detections") else "⚠️ Placeholder"),
        ("6", "Recovered Files",          "✅" if st.session_state.get("recovered_files") else "⚠️ Placeholder"),
        ("7", "Legal Declaration",        "✅ Always included"),
    ]

    for num, section, status in sections:
        st.markdown(f"- **Section {num}:** {section} — {status}")

    # ── Download Buttons ──────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label    = "📥 Download PDF Report",
            data     = pdf_bytes,
            file_name= filename,
            mime     = "application/pdf",
            type     = "primary",
        )

    with col2:
        st.info(f"✅ Also saved locally to:\n`outputs/{filename}`")

    # TODO (Member 6): Add email functionality
    st.button("📧 Email Report (Coming Soon)", disabled=True)

else:
    # ── Instructions ──────────────────────────────────────────────────
    st.info("""
    **Instructions:**
    1. First, run all modules in the sidebar (Device Detection → AI Analytics)
    2. Fill in the case details above
    3. Click **Generate Forensic Report**
    4. Download the PDF — it's ready for court submission!
    """)

    st.markdown("#### 📄 What the report includes:")
    st.markdown("""
    | Section | Content |
    |---------|---------|
    | 1 | Case ID, Officer, Date, Location |
    | 2 | DVR brand, model, file format |
    | 3 | MD5 + SHA-256 hash values |
    | 4 | Video duration, resolution, FPS |
    | 5 | AI-detected objects and persons |
    | 6 | Recovered deleted files list |
    | 7 | Legal declaration + signature block |
    """)
