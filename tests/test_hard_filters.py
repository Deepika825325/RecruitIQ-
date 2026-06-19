from recruitiq.filters.hard_filters import is_consulting_only
from recruitiq.filters.honeypot_detector import detect_honeypot


def test_consulting_only_true():
    career = [{"company": "TCS"}, {"company": "Infosys"}]
    assert is_consulting_only(career, ["TCS", "Infosys", "Wipro"]) is True


def test_consulting_only_false_with_product_company():
    career = [{"company": "TCS"}, {"company": "Swiggy"}]
    assert is_consulting_only(career, ["TCS", "Infosys", "Wipro"]) is False


def test_honeypot_yoe_mismatch():
    candidate = {
        "profile": {"years_of_experience": 10},
        "career_history": [{"duration_months": 12}],
        "skills": [],
    }
    is_hp, reasons = detect_honeypot(candidate)
    assert is_hp is True
    assert any("yoe_mismatch" in r for r in reasons)


def test_honeypot_zero_duration_skill():
    candidate = {
        "profile": {"years_of_experience": 5},
        "career_history": [{"duration_months": 60}],
        "skills": [{"name": "Python", "proficiency": "expert", "duration_months": 0}],
    }
    is_hp, reasons = detect_honeypot(candidate)
    assert is_hp is True
    assert any("zero_duration_skill" in r for r in reasons)


def test_clean_candidate_passes():
    candidate = {
        "profile": {"years_of_experience": 6},
        "career_history": [{"duration_months": 72}],
        "skills": [{"name": "Python", "proficiency": "expert", "duration_months": 60}],
    }
    is_hp, reasons = detect_honeypot(candidate)
    assert is_hp is False