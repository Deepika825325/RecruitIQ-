import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
import streamlit as st
from dashboard.components.styles import apply_custom_style, page_header

st.set_page_config(page_title="JD Breakdown", layout="wide")
apply_custom_style()
page_header("Job Description Breakdown", "What the role actually requires, beyond keywords")

JD_CONFIG_PATH = PROJECT_ROOT / "configs" / "jd_config.yaml"

with open(JD_CONFIG_PATH, "r", encoding="utf-8") as f:
    jd_config = yaml.safe_load(f)

role = jd_config.get("role", {})
st.subheader(f"{role.get('title', '')} - {role.get('company', '')}")
st.caption(f"Stage: {role.get('stage', '')}")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Must Haves")
    for item in jd_config.get("must_haves", []):
        st.markdown(f"- {item}")

    st.markdown("### Nice to Haves")
    for item in jd_config.get("nice_to_haves", []):
        st.markdown(f"- {item}")

with col2:
    st.markdown("### Disqualifiers")
    for key, value in jd_config.get("disqualifiers", {}).items():
        if value:
            st.markdown(f"- {key.replace('_', ' ')}")

    st.markdown("### Location Preference")
    location = jd_config.get("location", {})
    st.markdown(f"Preferred cities: {', '.join(location.get('preferred_cities', []))}")
    st.markdown(f"Welcome cities: {', '.join(location.get('welcome_cities', []))}")

st.markdown("---")
st.markdown("### Full JD Comparison Text")
st.info(jd_config.get("jd_full_text", ""))

st.markdown("---")
st.markdown("### Ideal Candidate Profile")
ideal = jd_config.get("ideal_candidate_profile", {})
for key, value in ideal.items():
    st.markdown(f"{key.replace('_', ' ')}: {value}")
