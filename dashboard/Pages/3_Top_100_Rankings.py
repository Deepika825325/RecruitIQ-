import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Top 100 Rankings", layout="wide")
st.title("Top 100 Ranked Candidates")

DETAILED_PATH = PROJECT_ROOT / "data" / "outputs" / "submission_detailed.json"

if not DETAILED_PATH.exists():
    st.warning("No ranking data found. Run scripts/rank.py first.")
else:
    with open(DETAILED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Search by title or company")
    with col2:
        min_score = st.slider("Minimum score", float(df["score"].min()), float(df["score"].max()), float(df["score"].min()))

    filtered = df[df["score"] >= min_score]
    if search:
        mask = (
            filtered["current_title"].str.contains(search, case=False, na=False)
            | filtered["current_company"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.dataframe(
        filtered[
            ["rank", "candidate_id", "score", "current_title", "current_company",
             "years_of_experience", "location", "reasoning"]
        ],
        use_container_width=True,
        height=600,
    )

    st.caption(f"Showing {len(filtered)} of {len(df)} candidates")
