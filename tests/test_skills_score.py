from recruitiq.scoring.skills_score import skills_score


def test_strong_fit_scores_high():
    candidate = {
        "skills": [
            {"name": "Pinecone", "proficiency": "expert", "duration_months": 88, "endorsements": 10},
            {"name": "Embeddings", "proficiency": "expert", "duration_months": 60, "endorsements": 8},
            {"name": "Information Retrieval", "proficiency": "expert", "duration_months": 84, "endorsements": 12},
        ]
    }
    assert skills_score(candidate) > 0.5


def test_reject_scores_zero():
    candidate = {
        "skills": [
            {"name": "Figma", "proficiency": "beginner", "duration_months": 15, "endorsements": 0},
            {"name": "Docker", "proficiency": "beginner", "duration_months": 5, "endorsements": 0},
        ]
    }
    assert skills_score(candidate) == 0.0


def test_honeypot_zero_duration_scores_near_zero():
    candidate = {
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 0, "endorsements": 5},
        ]
    }
    assert skills_score(candidate) == 0.0


def test_cv_without_nlp_gets_penalized():
    candidate = {
        "skills": [
            {"name": "Computer Vision", "proficiency": "expert", "duration_months": 60, "endorsements": 10},
            {"name": "Object Detection", "proficiency": "expert", "duration_months": 60, "endorsements": 10},
        ]
    }
    score_with_penalty = skills_score(candidate)

    candidate_with_nlp = dict(candidate)
    candidate_with_nlp["skills"] = candidate["skills"] + [
        {"name": "Information Retrieval", "proficiency": "advanced", "duration_months": 40, "endorsements": 5}
    ]
    score_without_penalty = skills_score(candidate_with_nlp)

    assert score_without_penalty > score_with_penalty