from recruitiq.scoring.structured_score import yoe_score, location_score, education_score


def test_yoe_sweet_spot():
    assert yoe_score(6) == 1.0
    assert yoe_score(9) == 1.0


def test_yoe_below_sweet_spot():
    assert yoe_score(0) == 0.4
    assert yoe_score(2.5) < 1.0


def test_yoe_above_sweet_spot():
    assert yoe_score(20) < yoe_score(12)
    assert yoe_score(12) < 1.0


def test_location_preferred_city():
    candidate = {
        "profile": {"location": "Pune, Maharashtra", "country": "India"},
        "redrob_signals": {"willing_to_relocate": False},
    }
    assert location_score(candidate) == 1.0


def test_location_outside_india_no_relocate():
    candidate = {
        "profile": {"location": "Toronto", "country": "Canada"},
        "redrob_signals": {"willing_to_relocate": False},
    }
    assert location_score(candidate) == 0.1


def test_education_unknown_defaults_neutral():
    candidate = {"education": []}
    assert education_score(candidate) == 0.5