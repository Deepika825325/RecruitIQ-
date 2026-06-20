from recruitiq.reasoning.generator import generate_reasoning


def test_strong_fit_reasoning_mentions_real_skills():
    candidate = {
        "profile": {
            "years_of_experience": 6.0,
            "current_title": "Recommendation Systems Engineer",
            "current_company": "Swiggy",
        },
        "skills": [
            {"name": "Information Retrieval", "proficiency": "expert", "duration_months": 84},
            {"name": "Sentence Transformers", "proficiency": "expert", "duration_months": 69},
        ],
        "redrob_signals": {"notice_period_days": 60, "open_to_work_flag": True},
    }
    scores = {"career_score": 0.35}
    text = generate_reasoning(candidate, scores)
    assert "Information Retrieval" in text or "Sentence Transformers" in text
    assert "Swiggy" in text


def test_flags_long_notice_period_concern():
    candidate = {
        "profile": {"years_of_experience": 5.0, "current_title": "ML Engineer", "current_company": "X"},
        "skills": [{"name": "Embeddings", "proficiency": "advanced", "duration_months": 30}],
        "redrob_signals": {"notice_period_days": 90, "open_to_work_flag": True},
    }
    scores = {"career_score": 0.3}
    text = generate_reasoning(candidate, scores)
    assert "notice period" in text.lower()


def test_no_skills_handled_gracefully():
    candidate = {
        "profile": {"years_of_experience": 3.0, "current_title": "Data Engineer", "current_company": "Y"},
        "skills": [],
        "redrob_signals": {"notice_period_days": 30, "open_to_work_flag": True},
    }
    scores = {"career_score": 0.5}
    text = generate_reasoning(candidate, scores)
    assert "no strongly matched core skills" in text