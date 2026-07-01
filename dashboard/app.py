import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_ROOT))

import json
import streamlit as st
from components.styles import apply_custom_style, page_header, metric_row, candidate_card, section_header, info_box

st.set_page_config(page_title="RecruitIQ", layout="wide", initial_sidebar_state="expanded")
apply_custom_style()

page_header("RecruitIQ", "Intelligent candidate ranking for the Redrob AI Hackathon")

FUNNEL_PATH = PROJECT_ROOT / "data" / "outputs" / "funnel_stats.json"
DETAILED_PATH = PROJECT_ROOT / "data" / "outputs" / "submission_detailed.json"

if FUNNEL_PATH.exists():
    with open(FUNNEL_PATH, "r", encoding="utf-8") as f:
        funnel = json.load(f)
    metric_row([
        ("Total Candidates", f"{funnel['total_candidates']:,}"),
        ("Stage A Survivors", f"{funnel['stage_a_survivors']:,}"),
        ("Final Shortlist", str(funnel["final_shortlist"])),
        ("Runtime", f"{funnel['runtime_seconds']}s"),
    ])
else:
    st.warning("No run data found. Run scripts/rank.py first.")

st.markdown("---")
section_header("Navigation")
info_box(
    "<b style='color:#818CF8;'>JD Breakdown</b> &nbsp;-&nbsp; what the role actually requires<br>"
    "<b style='color:#818CF8;'>Funnel View</b> &nbsp;-&nbsp; how 100,000 candidates narrow to a shortlist<br>"
    "<b style='color:#818CF8;'>Top 100 Rankings</b> &nbsp;-&nbsp; full ranked shortlist with reasoning<br>"
    "<b style='color:#818CF8;'>Score Explainability</b> &nbsp;-&nbsp; per-candidate score radar breakdown<br>"
    "<b style='color:#818CF8;'>Honeypot Audit</b> &nbsp;-&nbsp; disqualification risk check<br>"
    "<b style='color:#818CF8;'>Live Demo</b> &nbsp;-&nbsp; run the ranker live on a small sample"
)

if DETAILED_PATH.exists():
    with open(DETAILED_PATH, "r", encoding="utf-8") as f:
        detailed = json.load(f)
    section_header("Top 5 Candidates")
    for row in detailed[:5]:
        candidate_card(row["rank"], row["candidate_id"], row["score"], row["reasoning"])
