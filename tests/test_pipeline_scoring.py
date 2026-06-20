from recruitiq.pipeline import rank_top_n


def test_rank_top_n_sorts_descending():
    results = [
        {"candidate_id": "CAND_0000003", "final_score": 0.5},
        {"candidate_id": "CAND_0000001", "final_score": 0.9},
        {"candidate_id": "CAND_0000002", "final_score": 0.7},
    ]
    ranked = rank_top_n(results, top_n=3)
    scores = [r["final_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rank_top_n_tie_break_by_candidate_id():
    results = [
        {"candidate_id": "CAND_0000005", "final_score": 0.8},
        {"candidate_id": "CAND_0000002", "final_score": 0.8},
    ]
    ranked = rank_top_n(results, top_n=2)
    assert ranked[0]["candidate_id"] == "CAND_0000002"
    assert ranked[1]["candidate_id"] == "CAND_0000005"


def test_rank_top_n_respects_limit():
    results = [{"candidate_id": f"CAND_000000{i}", "final_score": float(i)} for i in range(1, 6)]
    ranked = rank_top_n(results, top_n=3)
    assert len(ranked) == 3