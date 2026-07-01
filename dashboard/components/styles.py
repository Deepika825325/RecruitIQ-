import streamlit as st


def apply_custom_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
        .stApp { background-color: #060C18 !important; }
        section[data-testid="stSidebar"] > div:first-child { background-color: #08101F !important; }
        .block-container { padding-top: 2rem !important; max-width: 1200px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="padding:2rem 0 1.5rem 0;">
            <div style="font-size:2.8rem;font-weight:800;
                background:linear-gradient(135deg,#818CF8 0%,#C084FC 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;line-height:1.15;letter-spacing:-0.02em;">
                {title}
            </div>
            <div style="color:#475569;font-size:1rem;margin-top:0.4rem;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str):
    st.markdown(
        f"""
        <div style="font-size:1.05rem;font-weight:700;color:#E2E8F0;
            margin:1.8rem 0 1rem 0;padding-bottom:0.45rem;
            border-bottom:2px solid #4F46E5;">
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(items: list[tuple[str, str]]):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div style="background:#0D1526;border:1px solid #1A2E50;
                    border-radius:14px;padding:1.2rem 1.4rem;">
                    <div style="color:#475569;font-size:0.72rem;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.08em;
                        margin-bottom:0.6rem;">{label}</div>
                    <div style="color:#818CF8;font-size:1.9rem;
                        font-weight:800;line-height:1;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def candidate_card(rank: int, candidate_id: str, score, reasoning: str):
    try:
        sv = float(score)
    except (TypeError, ValueError):
        sv = 0.0

    if sv >= 0.85:
        sc = "#4ADE80"
        bg = "rgba(74,222,128,0.1)"
    elif sv >= 0.70:
        sc = "#FBBF24"
        bg = "rgba(251,191,36,0.1)"
    else:
        sc = "#94A3B8"
        bg = "rgba(148,163,184,0.07)"

    st.markdown(
        f"""
        <div style="background:#0D1526;border:1px solid #1A2E50;
            border-left:4px solid #6366F1;border-radius:12px;
            padding:1.1rem 1.4rem;margin-bottom:0.8rem;">
            <div style="margin-bottom:0.6rem;overflow:hidden;">
                <span style="background:linear-gradient(135deg,#4F46E5,#7C3AED);
                    color:white;font-weight:700;font-size:0.68rem;
                    padding:0.2rem 0.6rem;border-radius:20px;
                    letter-spacing:0.06em;margin-right:0.6rem;">RANK {rank}</span>
                <span style="color:#E2E8F0;font-weight:700;
                    font-size:0.9rem;">{candidate_id}</span>
                <span style="float:right;background:{bg};
                    border:1px solid {sc}40;border-radius:8px;
                    padding:0.15rem 0.65rem;color:{sc};
                    font-weight:800;font-size:1rem;">{score}</span>
            </div>
            <div style="color:#64748B;font-size:0.87rem;
                line-height:1.6;">{reasoning}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_box(content: str):
    st.markdown(
        f"""
        <div style="background:#0A1A2E;border:1px solid #1A2E50;
            border-radius:12px;padding:1.1rem 1.4rem;color:#94A3B8;
            font-size:0.92rem;line-height:1.7;margin:0.6rem 0;">
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )
