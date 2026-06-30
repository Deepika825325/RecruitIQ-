import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import streamlit as st
import plotly.graph_objects as go
from dashboard.components.styles import apply_custom_style, page_header

st.set_page_config(page_title="Funnel View", layout="wide")
apply_custom_style()
page_header("Candidate Funnel", "How 100,000 candidates narrow down to the final shortlist")

FUNNEL_PATH = PROJECT_ROOT / "data" / "outputs" / "funnel_stats.json"

if not FUNNEL_PATH.exists():
    st.warning("No funnel data found. Run scripts/rank.py first.")
else:
    with open(FUNNEL_PATH, "r", encoding="utf-8") as f:
        funnel = json.load(f)

    fig = go.Figure(go.Funnel(
        y=["Total Candidates", "Stage A Survivors", "Final Shortlist"],
        x=[funnel["total_candidates"], funnel["stage_a_survivors"], funnel["final_shortlist"]],
        textinfo="value+percent initial",
        marker={"color": ["#6366F1", "#8B5CF6", "#C084FC"]},
    ))
    fig.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E2E8F0"},
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Candidates", f"{funnel['total_candidates']:,}")
    col2.metric(
        "Stage A Survivors",
        f"{funnel['stage_a_survivors']:,}",
        f"{funnel['stage_a_survivors'] / funnel['total_candidates'] * 100:.2f}% of total",
    )
    col3.metric(
        "Final Shortlist",
        funnel["final_shortlist"],
        f"{funnel['final_shortlist'] / funnel['stage_a_survivors'] * 100:.2f}% of survivors",
    )

    st.markdown("---")
    st.markdown(
        """
        Stage A applies hard filters and a title-tier check with a skills-based
        rescue path for non-obvious titles. Stage B applies full weighted scoring
        across title, skills, career evidence, structured fit, and a behavioral
        availability multiplier.
        """
    )
