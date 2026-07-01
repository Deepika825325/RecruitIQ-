import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_ROOT))

import json
import pandas as pd
import streamlit as st
from components.styles import apply_custom_style, page_header, metric_row, section_header

st.set_page_config(page_title="Honeypot Audit", layout="wide")
apply_custom_style()
page_header("Honeypot and Disqualification Audit", "Verifying the shortlist is free of trap candidates")

AUDIT_PATH = PROJECT_ROOT / "data" / "processed" / "honeypot_audit.json"

if not AUDIT_PATH.exists():
    st.warning("No audit data found. Run scripts/audit_honeypots.py first.")
else:
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        audit = json.load(f)

    status = audit["status"]
    color = "#4ADE80" if status == "PASS" else "#F87171"
    st.markdown(
        f"""
        <div style="background:{'#052E16' if status == 'PASS' else '#2D0A0A'};
            border:1px solid {'#166534' if status == 'PASS' else '#7F1D1D'};
            border-radius:12px;padding:1rem 1.4rem;margin-bottom:1.2rem;">
            <span style="color:{color};font-weight:800;font-size:1.05rem;">
                {status}
            </span>
            <span style="color:#94A3B8;font-size:0.95rem;margin-left:0.8rem;">
                Honeypot rate {audit['honeypot_rate']}% (threshold {audit['threshold']}%)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_row([
        ("Total Submitted", str(audit["total"])),
        ("Honeypots Detected", str(audit["honeypot_count"])),
        ("Consulting-Only Detected", str(audit["consulting_count"])),
        ("Honeypot Rate", f"{audit['honeypot_rate']}%"),
    ])

    st.markdown("---")

    if audit["flagged"]:
        section_header("Flagged Candidates")
        st.dataframe(pd.DataFrame(audit["flagged"]), use_container_width=True)
    else:
        section_header("Audit Result")
        st.markdown(
            """
            <div style="background:#052E16;border:1px solid #166534;border-radius:12px;
                padding:1.2rem 1.4rem;color:#4ADE80;font-weight:600;font-size:0.95rem;">
                Zero honeypots detected in the top 100. All submitted candidates passed
                the YOE consistency check, skill duration validation, and the
                consulting-only career filter. Disqualification risk: none.
            </div>
            """,
            unsafe_allow_html=True,
        )
