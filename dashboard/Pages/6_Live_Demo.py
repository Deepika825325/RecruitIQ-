import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import yaml
import streamlit as st

from recruitiq.pipeline import passes_stage_a, score_survivors, rank_top_n, load_weights, load_ranker_model
from recruitiq.scoring.career_score import EmbeddingsLookup
from recruitiq.reasoning.generator import generate_reasoning

st.set_page_config(page_title="Live Demo", layout="wide")
st.title("Live Demo")
st.caption("Runs the actual RecruitIQ pipeline live on a small candidate sample")

SAMPLE_PATH = PROJECT_ROOT / "sample_data" / "sandbox_sample.json"
JD_CONFIG_PATH = PROJECT_ROOT / "configs" / "jd_config.yaml"

with open(JD_CONFIG_PATH, "r", encoding="utf-8") as f:
    jd_text = yaml.safe_load(f)["jd_full_text"]

with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
    sample_candidates = json.load(f)

st.markdown(f"Sample size: {len(sample_candidates)} candidates")

if st.button("Run Pipeline"):
    start = time.time()

    weights = load_weights()
    lookup = EmbeddingsLookup()
    ranker_model = load_ranker_model()

    survivors = [c for c in sample_candidates if passes_stage_a(c)]
    st.markdown(f"Stage A survivors: {len(survivors)} of {len(sample_candidates)}")

    if survivors:
        results = score_survivors(survivors, jd_text, lookup, weights, ranker_model=ranker_model)
        ranked = rank_top_n(results, top_n=len(results))

        elapsed = time.time() - start
        st.success(f"Pipeline completed in {elapsed:.2f} seconds")

        for r in ranked:
            reasoning = generate_reasoning(r["candidate"], r)
            st.markdown(f"{r['candidate_id']} - score: {r['final_score']}")
            st.caption(reasoning)
    else:
        st.warning("No candidates survived Stage A in this sample.")
