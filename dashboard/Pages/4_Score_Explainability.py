import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import streamlit as st
import plotly.graph_objects as go
from dashboard.components.styles import apply_custom_style, page_header

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

    options = [f"{d['rank']} - {d['candidate_id']} ({d['current_title']})" for d in data]
    selected = st.selectbox("Select a candidate", options)
    selected_index = options.index(selected)
    candidate = data[selected_index]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(candidate["candidate_id"])
        st.markdown(f"Title: {candidate['current_title']}")
        st.markdown(f"Company: {candidate['current_company']}")
        st.markdown(f"Experience: {candidate['years_of_experience']} years")
        st.markdown(f"Location: {candidate['location']}")
        st.markdown(f"Final Score: {candidate['score']}")
        st.markdown(f"Behavioral Multiplier: {candidate['behavioral_multiplier']}")
        st.info(candidate["reasoning"])

    with col2:
        categories = ["Title", "Skills", "Career", "Structured"]
        values = [
            candidate["title_score"],
            candidate["skills_score"],
            candidate["career_score"],
            candidate["structured_score"],
        ]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            line={"color": "#8B5CF6"},
            fillcolor="rgba(139, 92, 246, 0.3)",
        ))
        fig.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 1]}},
            showlegend=False,
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#E2E8F0"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Model Feature Importance")
    if IMPORTANCE_PATH.exists():
        with open(IMPORTANCE_PATH, "r", encoding="utf-8") as f:
            importance = json.load(f)

        names = list(importance["feature_importance_pct"].keys())
        pcts = list(importance["feature_importance_pct"].values())

        fig2 = go.Figure(go.Bar(
            x=pcts, y=names, orientation="h",
            marker={"color": "#6366F1"},
        ))
        fig2.update_layout(
            height=300,
            xaxis_title="Gain percent",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#E2E8F0"},
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(f"Trained on {importance['trained_on_count']} hand-labeled candidates using LightGBM lambdarank")
    else:
        st.info("No trained model found. Hand-set weights are being used.")
