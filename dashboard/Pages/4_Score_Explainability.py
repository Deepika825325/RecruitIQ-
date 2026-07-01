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
from components.styles import apply_custom_style, page_header, section_header

st.set_page_config(page_title="Score Explainability", layout="wide")
apply_custom_style()
page_header("Score Explainability", "Per-candidate breakdown across all scoring layers")

DETAILED_PATH = PROJECT_ROOT / "data" / "outputs" / "submission_detailed.json"
IMPORTANCE_PATH = PROJECT_ROOT / "data" / "processed" / "feature_importance.json"

if not DETAILED_PATH.exists():
    st.warning("No ranking data found. Run scripts/rank.py first.")
else:
    with open(DETAILED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    options = [f"Rank {d['rank']} - {d['candidate_id']} ({d['current_title']})" for d in data]
    selected = st.selectbox("Select a candidate to inspect", options)
    selected_index = options.index(selected)
    c = data[selected_index]

    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        section_header("Candidate Details")
        st.markdown(f"**ID:** {c['candidate_id']}")
        st.markdown(f"**Title:** {c['current_title']}")
        st.markdown(f"**Company:** {c['current_company']}")
        st.markdown(f"**Experience:** {c['years_of_experience']} years")
        st.markdown(f"**Location:** {c['location']}")
        st.markdown(f"**Final Score:** {c['score']}")
        st.markdown(f"**Behavioral Multiplier:** {c['behavioral_multiplier']}")
        st.markdown("---")
        section_header("Reasoning")
        st.info(c["reasoning"])

    with col2:
        section_header("Score Radar")
        categories = ["Title", "Skills", "Career", "Structured"]
        values = [c["title_score"], c["skills_score"], c["career_score"], c["structured_score"]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Score",
            fillcolor="rgba(129,140,248,0.25)",
        ))
        fig.update_layout(
            polar={
                "radialaxis": {"visible": True, "range": [0, 1], "color": "#475569"},
                "bgcolor": "rgba(0,0,0,0)",
                "angularaxis": {"color": "#475569"},
            },
            showlegend=False,
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#CBD5E1"},
            margin={"t": 30, "b": 30, "l": 50, "r": 50},
        )
        st.plotly_chart(fig, use_container_width=True)

    if IMPORTANCE_PATH.exists():
        st.markdown("---")
        section_header("LightGBM Feature Importance")
        with open(IMPORTANCE_PATH, "r", encoding="utf-8") as f:
            importance = json.load(f)

        names = list(importance["feature_importance_pct"].keys())
        pcts = list(importance["feature_importance_pct"].values())

        fig2 = go.Figure(go.Bar(
            x=pcts, y=names, orientation="h",
            marker={"color": ["#818CF8", "#A78BFA", "#C084FC", "#E879F9"]},
            text=[f"{p:.1f}%" for p in pcts],
            textposition="outside",
        ))
        fig2.update_layout(
            height=280,
            xaxis_title="Gain percent",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#CBD5E1"},
            xaxis={"gridcolor": "#1A2540"},
            yaxis={"gridcolor": "#1A2540"},
            margin={"t": 10, "b": 10},
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(f"Trained on {importance['trained_on_count']} hand-labeled candidates using LightGBM lambdarank")
