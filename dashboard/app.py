import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import streamlit as st
from dashboard.components.styles import apply_custom_style, page_header, candidate_card

st.set_page_config(page_title="RecruitIQ", layout="wide")
apply_custom_style()

page_header("RecruitIQ", "Intelligent candidate ranking for the Redrob AI Hackathon")

FUNNEL_PATH = PROJECT_ROOT / "data" / "outputs" / "funnel_stats.json"
DETAILED_PATH = PROJECT_ROOT / "data" / "outputs" / "submission_detailed.json"

if FUNNEL_PATH.exists():
    with open(FUNNEL_PATH, "r", encoding="utf-8") as f:
        funnel = json.load(f)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Candidates", f"{funnel['total_candidates']:,}")
    col2.metric("Stage A Survivors", f"{funnel['stage_a_survivors']:,}")
    col3.metric("Final Shortlist", funnel["final_shortlist"])
    col4.metric("Runtime", f"{funnel['runtime_seconds']}s")
else:
    st.warning("No run data found. Run scripts/rank.py first to generate results.")

st.markdown("---")

if DETAILED_PATH.exists():
    with open(DETAILED_PATH, "r", encoding="utf-8") as f:
        detailed = json.load(f)
    st.markdown("### Top 5 Candidates")
    for row in detailed[:5]:
        candidate_card(row["rank"], row["candidate_id"], row["score"], row["reasoning"])
