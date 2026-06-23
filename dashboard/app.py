import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import streamlit as st

st.set_page_config(page_title="RecruitIQ", layout="wide")

st.title("RecruitIQ")
st.caption("Intelligent candidate ranking for the Redrob AI Hackathon")

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
st.markdown(
    """
    Use the sidebar to navigate:

    - JD Breakdown: what the role actually requires
    - Funnel View: how 100,000 candidates narrow down to the final shortlist
    - Top 100 Rankings: the full ranked shortlist with reasoning
    - Score Explainability: per-candidate score breakdown
    - Honeypot Audit: disqualification risk check
    - Live Demo: run the ranker live on a small sample
    """
)

if DETAILED_PATH.exists():
    with open(DETAILED_PATH, "r", encoding="utf-8") as f:
        detailed = json.load(f)
    st.markdown("---")
    st.subheader("Top 5 Candidates")
    for row in detailed[:5]:
        st.markdown(f"Rank {row['rank']} - {row['candidate_id']} (score: {row['score']})")
        st.caption(row["reasoning"])
