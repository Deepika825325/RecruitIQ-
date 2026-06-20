from datetime import date
from recruitiq.scoring.behavioral_score import behavioral_multiplier

REF_DATE = date(2026, 6, 20)


def test_active_engaged_high_multiplier():
    candidate = {
        "redrob_signals": {
            "open_to_work_flag": True,
            "last_active_date": "2026-06-18",
            "notice_period_days": 15,
            "recruiter_response_rate": 0.9,
            "interview_completion_rate": 1.0,
            "applications_submitted_30d": 5,
            "github_activity_score": 60,
        }
    }
    mult = behavioral_multiplier(candidate, reference_date=REF_DATE)
    assert mult > 1.1


def test_ghost_candidate_low_multiplier():
    candidate = {
        "redrob_signals": {
            "open_to_work_flag": False,
            "last_active_date": "2024-01-01",
            "notice_period_days": 150,
            "recruiter_response_rate": 0.05,
            "interview_completion_rate": 0.1,
            "applications_submitted_30d": 0,
            "github_activity_score": -1,
        }
    }
    mult = behavioral_multiplier(candidate, reference_date=REF_DATE)
    assert mult < 0.6


def test_multiplier_bounds():
    candidate = {"redrob_signals": {}}
    mult = behavioral_multiplier(candidate, reference_date=REF_DATE)
    assert 0.4 <= mult <= 1.3