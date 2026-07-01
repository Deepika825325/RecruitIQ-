import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_ROOT))

import yaml
import streamlit as st
from components.styles import apply_custom_style, page_header, section_header

st.set_page_config(page_title="JD Breakdown", layout="wide")
apply_custom_style()
page_header("Job Description Breakdown", "What the role actually requires, beyond keywords")

JD_CONFIG_PATH = PROJECT_ROOT / "configs" / "jd_config.yaml"
with open(JD_CONFIG_PATH, "r", encoding="utf-8") as f:
    jd_config = yaml.safe_load(f)

role = jd_config.get("role", {})
st.markdown(
    f"""
    <div style="background:#0D1526; border:1px solid #1A2E50; border-radius:12px;
    padding:1rem 1.4rem; margin-bottom:1.5rem;">
        <div style="color:#818CF8; font-weight:700; font-size:1.1rem;">{role.get('title','')}</div>
        <div style="color:#475569; font-size:0.9rem;">{role.get('company','')} - {role.get('stage','')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    section_header("Must Haves")
    for item in jd_config.get("must_haves", []):
        st.markdown(f"- {item}")
    section_header("Nice to Haves")
    for item in jd_config.get("nice_to_haves", []):
        st.markdown(f"- {item}")

with col2:
    section_header("Disqualifiers")
    for key, value in jd_config.get("disqualifiers", {}).items():
        if value:
            st.markdown(f"- {key.replace('_', ' ')}")
    section_header("Location Preference")
    location = jd_config.get("location", {})
    st.markdown(f"Preferred: {', '.join(location.get('preferred_cities', []))}")
    st.markdown(f"Welcome: {', '.join(location.get('welcome_cities', []))}")

st.markdown("---")
section_header("Full JD Comparison Text")
st.info(jd_config.get("jd_full_text", ""))

st.markdown("---")
section_header("Ideal Candidate Profile")
ideal = jd_config.get("ideal_candidate_profile", {})
for key, value in ideal.items():
    st.markdown(f"**{key.replace('_', ' ')}:** {value}")
