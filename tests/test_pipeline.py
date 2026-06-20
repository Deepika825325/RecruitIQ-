from recruitiq.pipeline import passes_stage_a


def test_tier_a_always_passes():
    candidate = {
        "profile": {"current_title": "Recommendation Systems Engineer"},
        "career_history": [{"company": "Swiggy", "duration_months": 72}],
        "skills": [],
    }
    assert passes_stage_a(candidate) is True


def test_tier_c_rescued_by_strong_skills():
    candidate = {
        "profile": {"current_title": "Data Engineer", "years_of_experience": 4.6},
        "career_history": [{"company": "Ola", "duration_months": 55}],
        "skills": [
            {"name": "BM25", "proficiency": "advanced", "duration_months": 55, "endorsements": 5},
            {"name": "Elasticsearch", "proficiency": "intermediate", "duration_months": 17, "endorsements": 2},
        ],
    }
    assert passes_stage_a(candidate) is True


def test_tier_d_never_rescued():
    candidate = {
        "profile": {"current_title": "HR Manager"},
        "career_history": [{"company": "TCS", "duration_months": 90}],
        "skills": [
            {"name": "Pinecone", "proficiency": "expert", "duration_months": 60, "endorsements": 10},
        ],
    }
    assert passes_stage_a(candidate) is False