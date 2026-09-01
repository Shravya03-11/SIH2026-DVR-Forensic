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

import datetime
import os
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.pdf_report import generate_report

st.set_page_config(
    page_title="Report Generator | DVR Forensic",
    page_icon="📄",
    layout="wide",
)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def safe_filename(value: str) -> str:
    """Create a safe filename from a case ID."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return cleaned or "UNSPECIFIED_CASE"


def has_data(value) -> bool:
    """Check whether a session-state value contains useful data."""
    if value is None:
        return False
    if isinstance(value, (dict, list, tuple, set, str)):
        return len(value) > 0
    return bool(value)


def get_summary_rows():
    """Build a report-readiness table from analysis modules."""
    modules = [
        ("Device Detection", "device_info", "DVR brand, model and device details"),
        ("Acquisition & Hashing", "hashes", "MD5 and SHA-256 evidence integrity values"),
        ("Metadata Parser", "metadata", "Video properties, timestamps and timeline"),
        ("Recovery Simulator", "recovered_files", "Recovered/deleted footage entries"),
        ("AI Analytics", "detections", "Detected people, vehicles and objects"),
    ]

    rows = []
    for module, key, description in modules:
        complete = has_data(st.session_state.get(key))
        rows.append(
            {
                "Module": module,
                "Status": "Complete" if complete else "Pending",
                "Report contribution": description,
            }
        )
    return rows


def flatten_dict(data: dict) -> list[tuple[str, str]]:
    """Prepare dictionaries for display."""
    if not data:
        return [("Status", "No data available")]

    rows = []
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value = str(value)
        rows.append((str(key).replace("_", " ").title(), str(value)))
    return rows


# ── Header ────────────────────────────────────────────────────────────────────
st.title("📄 Forensic Report Generator")
st.caption(
    "Create a structured digital-evidence report from device, acquisition, "
    "metadata, recovery and AI-analysis findings."
)

summary_rows = get_summary_rows()
completed = sum(row["Status"] == "Complete" for row in summary_rows)
completion_rate = completed / len(summary_rows)

top_left, top_mid, top_right = st.columns([1.4, 1, 1])

with top_left:
    st.progress(completion_rate, text=f"Evidence workflow completion: {completed}/5 modules")

with top_mid:
    st.metric("Evidence Sources", f"{completed}/5")

with top_right:
    label = "Ready to generate" if completed >= 3 else "Partial evidence available"
    st.metric("Report Status", label)

if completed < 5:
    st.warning(
        "Some analysis modules have not been completed. The PDF can still be generated, "
        "but missing sections will be clearly marked as unavailable."
    )
else:
    st.success("All analysis modules are complete. Your report will include the full evidence summary.")

st.divider()

tab_case, tab_preview, tab_history = st.tabs(
    ["📝 Case Details", "👁️ Live Report Preview", "🗃️ Generated Reports"]
)

# ── Case details ──────────────────────────────────────────────────────────────
with tab_case:
    st.subheader("Case & Evidence Details")

    with st.form("report_form", border=True):
        left, right = st.columns(2)

        with left:
            case_id = st.text_input(
                "Case / FIR Number *",
                value=st.session_state.get("case_id", ""),
                placeholder="Example: FIR-2026-001",
            )
            officer = st.text_input(
                "Investigating Officer *",
                value=st.session_state.get("officer", ""),
                placeholder="Example: Insp. A. Sharma",
            )
            department = st.text_input(
                "Department / Unit",
                value=st.session_state.get("department", "Cyber Crime Division"),
            )
            location = st.text_input(
                "Incident / Evidence Location",
                value=st.session_state.get("location", ""),
                placeholder="Example: Sector 18, Noida",
            )

        with right:
            incident_date = st.date_input(
                "Incident Date",
                value=st.session_state.get("incident_date", datetime.date.today()),
            )
            report_date = st.date_input("Report Date", value=datetime.date.today())
            priority = st.select_slider(
                "Case Priority",
                options=["Low", "Medium", "High", "Critical"],
                value=st.session_state.get("priority", "Medium"),
            )
            classification = st.selectbox(
                "Document Classification",
                ["OFFICIAL USE ONLY", "RESTRICTED", "CONFIDENTIAL"],
                index=1,
            )

        evidence_description = st.text_input(
            "Evidence Description",
            value=st.session_state.get(
                "evidence_description",
                "DVR/CCTV video footage submitted for forensic examination",
            ),
        )

        notes = st.text_area(
            "Examiner Notes / Observations",
            value=st.session_state.get("report_notes", ""),
            height=130,
            placeholder="Mention chain-of-custody notes, notable events, limitations, or observations.",
        )

        acknowledgement = st.checkbox(
            "I confirm that the entered case information has been reviewed for accuracy."
        )

        submitted = st.form_submit_button(
            "🚀 Generate Forensic PDF Report",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not case_id.strip() or not officer.strip():
            st.error("Please enter both the Case / FIR Number and Investigating Officer.")
        elif not acknowledgement:
            st.error("Please confirm that the case information has been reviewed.")
        else:
            # Save form state for the preview and later revisits.
            st.session_state.update(
                {
                    "case_id": case_id.strip(),
                    "officer": officer.strip(),
                    "department": department.strip(),
                    "location": location.strip(),
                    "incident_date": incident_date,
                    "priority": priority,
                    "evidence_description": evidence_description.strip(),
                    "report_notes": notes.strip(),
                }
            )

            case_info = {
                "Case ID": case_id.strip(),
                "Investigating Officer": officer.strip(),
                "Department": department.strip(),
                "Incident Location": location.strip() or "Not specified",
                "Incident Date": str(incident_date),
                "Report Date": str(report_date),
                "Priority": priority,
                "Classification": classification,
                "Evidence Description": evidence_description.strip() or "Not specified",
                "Notes": notes.strip() or "No additional observations recorded.",
                "Analysis Completion": f"{completed}/5 modules",
            }

            with st.spinner("Compiling evidence findings and generating the PDF..."):
                pdf_bytes = generate_report(
                    case_info=case_info,
                    device_info=st.session_state.get("device_info", {}),
                    hashes=st.session_state.get("hashes", {}),
                    metadata=st.session_state.get("metadata", {}),
                    detections=st.session_state.get("detections", []),
                    recovered=st.session_state.get("recovered_files", []),
                )

            filename = (
                f"Forensic_Report_{safe_filename(case_id)}_"
                f"{datetime.date.today().isoformat()}.pdf"
            )
            output_path = OUTPUT_DIR / filename
            output_path.write_bytes(pdf_bytes)

          # Save report details so download remains available during this session
            st.session_state["generated_pdf"] = pdf_bytes
            st.session_state["generated_filename"] = filename

# Used by the "Generated Report Centre" tab
            st.session_state["latest_pdf"] = pdf_bytes
            st.session_state["latest_pdf_name"] = filename
            st.session_state["latest_output_path"] = str(output_path)

            st.success("Forensic PDF report generated successfully and saved to outputs.")

            confirmation_left, confirmation_right = st.columns([3, 1])

            with confirmation_left:
                st.info(
                    f"Report reference: **{filename}**  \n"
                    f"Case ID: **{case_id}**  \n"
                    f"Generated on: **{datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}**"
    )

            with confirmation_right:
                st.metric("Report Status", "Complete")

            st.divider()
            st.subheader("Report Download")

            st.download_button(
               label="📥 Download Forensic PDF Report",
               data=st.session_state["generated_pdf"],
               file_name=st.session_state["generated_filename"],
               mime="application/pdf",
               type="primary",
               use_container_width=True,
)
# ── Interactive preview ───────────────────────────────────────────────────────
with tab_preview:
    st.subheader("Report Evidence Preview")
    st.caption("This is the information currently available to the PDF generator.")

    preview_left, preview_right = st.columns([1.1, 1])

    with preview_left:
        st.markdown("#### Analysis completeness")
        readiness_df = pd.DataFrame(summary_rows)

        def status_icon(status):
            return "✅ Complete" if status == "Complete" else "⚠️ Pending"

        readiness_df["Status"] = readiness_df["Status"].apply(status_icon)
        st.dataframe(readiness_df, hide_index=True, use_container_width=True)

        st.markdown("#### Integrity indicator")
        hashes = st.session_state.get("hashes", {})
        if has_data(hashes):
            st.success("Hash values are available for evidence-integrity documentation.")
            hash_rows = pd.DataFrame(flatten_dict(hashes), columns=["Algorithm / Field", "Value"])
            st.dataframe(hash_rows, hide_index=True, use_container_width=True)
        else:
            st.error("No hashes found. Run Acquisition before final report submission.")

    with preview_right:
        st.markdown("#### Device findings")
        device_df = pd.DataFrame(
            flatten_dict(st.session_state.get("device_info", {})),
            columns=["Field", "Value"],
        )
        st.dataframe(device_df, hide_index=True, use_container_width=True)

        st.markdown("#### Video metadata")
        metadata_df = pd.DataFrame(
            flatten_dict(st.session_state.get("metadata", {})),
            columns=["Field", "Value"],
        )
        st.dataframe(metadata_df, hide_index=True, use_container_width=True)

    detection_data = st.session_state.get("detections", [])
    recovered_data = st.session_state.get("recovered_files", [])

    stat1, stat2, stat3 = st.columns(3)
    stat1.metric("AI Findings", len(detection_data) if isinstance(detection_data, list) else 0)
    stat2.metric("Recovered Items", len(recovered_data) if isinstance(recovered_data, list) else 0)
    stat3.metric("Evidence Completeness", f"{int(completion_rate * 100)}%")

    if has_data(detection_data):
        with st.expander("🤖 AI Detection Results", expanded=False):
            if isinstance(detection_data, list):
                st.dataframe(pd.DataFrame(detection_data), use_container_width=True)
            else:
                st.write(detection_data)

    if has_data(recovered_data):
        with st.expander("🗂️ Recovery Results", expanded=False):
            if isinstance(recovered_data, list):
                st.dataframe(pd.DataFrame(recovered_data), use_container_width=True)
            else:
                st.write(recovered_data)

# ── Generated PDFs ────────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Generated Report Centre")

    if st.session_state.get("latest_pdf"):
        st.success(f"Latest report: {st.session_state['latest_pdf_name']}")

        download_col, email_col = st.columns(2)

        with download_col:
            st.download_button(
                "📥 Download Latest PDF",
                data=st.session_state["latest_pdf"],
                file_name=st.session_state["latest_pdf_name"],
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

        with email_col:
            if st.button("📧 Email Report", use_container_width=True):
                st.info(
                    "Email integration placeholder: connect this button to an approved "
                    "departmental SMTP/API service before deployment."
                )

    existing_reports = sorted(OUTPUT_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)

    if existing_reports:
        st.markdown("#### Saved PDF reports")
        report_rows = [
            {
                "Filename": report.name,
                "Generated": datetime.datetime.fromtimestamp(report.stat().st_mtime).strftime(
                    "%d %b %Y, %I:%M %p"
                ),
                "Size (KB)": round(report.stat().st_size / 1024, 1),
            }
            for report in existing_reports
        ]
        st.dataframe(pd.DataFrame(report_rows), hide_index=True, use_container_width=True)
    else:
        st.info("No generated reports yet.")