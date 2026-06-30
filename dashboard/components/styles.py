import streamlit as st

CUSTOM_CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap");

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

#MainMenu, footer, header {visibility: hidden;}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1 {
    font-weight: 800;
    font-size: 2.4rem;
    background: linear-gradient(135deg, #818CF8 0%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

h2, h3 {
    font-weight: 700;
    color: #E2E8F0;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1E293B 0%, #181F2E 100%);
    border: 1px solid #2D3A52;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8;
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

[data-testid="stMetricValue"] {
    color: #F8FAFC;
    font-weight: 800;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #2D3A52;
}

[data-testid="stSidebar"] {
    background: #0B1120;
    border-right: 1px solid #1E293B;
}

[data-testid="stSidebar"] .stPageLink, [data-testid="stSidebarNav"] a {
    border-radius: 8px;
}

div[data-testid="stExpander"] {
    border: 1px solid #2D3A52;
    border-radius: 12px;
    background: #161D2E;
}

.stAlert {
    border-radius: 12px;
}

div.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
}

div.stButton > button:hover {
    opacity: 0.9;
    color: white;
}

hr {
    border-color: #1E293B;
}

.candidate-card {
    background: linear-gradient(145deg, #1A2236 0%, #151B2B 100%);
    border: 1px solid #2D3A52;
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.8rem;
}

.candidate-rank-badge {
    display: inline-block;
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: white;
    font-weight: 700;
    font-size: 0.78rem;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    margin-right: 0.6rem;
}

.candidate-score {
    float: right;
    font-weight: 800;
    color: #A5B4FC;
    font-size: 1.05rem;
}

.candidate-reasoning {
    color: #94A3B8;
    font-size: 0.92rem;
    margin-top: 0.4rem;
    line-height: 1.5;
}
</style>
"""


def apply_custom_style():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color:#94A3B8; font-size:1.05rem; margin-top:-0.4rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)


def candidate_card(rank: int, candidate_id: str, score, reasoning: str):
    st.markdown(
        f"""
        <div class="candidate-card">
            <span class="candidate-rank-badge">RANK {rank}</span>
            <span class="candidate-score">{score}</span>
            <div style="font-weight:700; color:#F8FAFC; margin-top:0.5rem;">{candidate_id}</div>
            <div class="candidate-reasoning">{reasoning}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
