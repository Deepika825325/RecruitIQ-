import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Honeypot Audit", layout="wide")
st.title("Honeypot and Disqualification Audit")

AUDIT_PATH = PROJECT_ROOT / "data" / "processed" / "honeypot_audit.json"

if not AUDIT_PATH.exists():
    st.warning("No audit data found. Run scripts/audit_honeypots.py first.")
else:
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        audit = json.load(f)

    status = audit["status"]
    if status == "PASS":
        st.success(f"Status: PASS - honeypot rate {audit['honeypot_rate']}% (threshold {audit['threshold']}%)")
    else:
        st.error(f"Status: FAIL - honeypot rate {audit['honeypot_rate']}% exceeds threshold {audit['threshold']}%")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Submitted", audit["total"])
    col2.metric("Honeypots Detected", audit["honeypot_count"])
    col3.metric("Consulting-Only Detected", audit["consulting_count"])

    if audit["flagged"]:
        st.markdown("---")
        st.subheader("Flagged Candidates")
        st.dataframe(pd.DataFrame(audit["flagged"]), use_container_width=True)
    else:
        st.markdown("---")
        st.markdown("No candidates flagged. The top 100 are clean of honeypots and consulting-only careers.")
