from recruitiq.scoring.title_score import classify_title


def test_tier_a_strong_fit():
    tier, score = classify_title("Recommendation Systems Engineer")
    assert tier == "tier_a"
    assert score == 1.0


def test_tier_d_reject():
    tier, score = classify_title("HR Manager")
    assert tier == "tier_d"
    assert score == 0.05


def test_tier_b_borderline():
    tier, score = classify_title("Software Engineer")
    assert tier == "tier_b"


def test_tier_c_borderline():
    tier, score = classify_title("Data Engineer")
    assert tier == "tier_c"


def test_unknown_title():
    tier, score = classify_title("Chief Vibes Officer")
    assert tier == "unknown"