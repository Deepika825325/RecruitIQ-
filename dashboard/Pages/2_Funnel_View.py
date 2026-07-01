import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_ROOT))

import json
import streamlit as st
import plotly.graph_objects as go
from components.styles import apply_custom_style, page_header, metric_row, section_header

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
        marker={"color": ["#4F46E5", "#7C3AED", "#A855F7"]},
        connector={"line": {"color": "#1A2540", "width": 2}},
    ))
    fig.update_layout(
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#CBD5E1", "family": "Inter"},
        margin={"t": 20, "b": 20},
    )
    st.plotly_chart(fig, use_container_width=True)

    total = funnel["total_candidates"]
    surv = funnel["stage_a_survivors"]
    final = funnel["final_shortlist"]
    metric_row([
        ("Total Candidates", f"{total:,}"),
        ("Stage A Survivors", f"{surv:,} ({surv/total*100:.2f}%)"),
        ("Final Shortlist", f"{final} ({final/surv*100:.2f}%)"),
    ])

    st.markdown("---")
    section_header("How the Funnel Works")
    st.markdown(
        "<div style='color:#94A3B8;line-height:1.8;'>Stage A applies hard filters: consulting-only career detection, "
        "title-domain classification, and a skills-based rescue path for non-obvious titles. "
        "Stage B applies full weighted scoring across title, skills evidence, career evidence, "
        "structured fit, and a behavioral availability multiplier trained via LightGBM lambdarank.</div>",
        unsafe_allow_html=True,
    )
