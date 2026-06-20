from recruitiq.scoring.career_score import tfidf_career_scores

JD_TEXT = (
    "Build ranking and retrieval systems using embeddings and vector "
    "databases, with rigorous evaluation using NDCG and MRR."
)


def test_relevant_career_scores_higher():
    relevant = {
        "candidate_id": "CAND_0000001",
        "profile": {"summary": "Built ranking systems using embeddings and vector search."},
        "career_history": [
            {"description": "Designed retrieval pipeline with hybrid search and NDCG evaluation."}
        ],
    }
    irrelevant = {
        "candidate_id": "CAND_0000002",
        "profile": {"summary": "Managed marketing campaigns and social media content."},
        "career_history": [{"description": "Led demand generation and SEO strategy."}],
    }

    scores = tfidf_career_scores(JD_TEXT, [relevant, irrelevant])
    assert scores["CAND_0000001"] > scores["CAND_0000002"]


def test_empty_candidate_list():
    assert tfidf_career_scores(JD_TEXT, []) == {}