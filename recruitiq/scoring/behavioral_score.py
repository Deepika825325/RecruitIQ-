from datetime import date


def _days_since(date_str: str, reference_date: date | None = None) -> int:
    reference_date = reference_date or date.today()
    try:
        d = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return 9999
    return (reference_date - d).days


def _activity_recency_score(last_active_date: str, reference_date: date | None = None) -> float:
    days = _days_since(last_active_date, reference_date)
    if days <= 7:
        return 1.0
    if days <= 30:
        return 0.85
    if days <= 90:
        return 0.5
    if days <= 180:
        return 0.25
    return 0.1


def _notice_period_score(notice_days: int) -> float:
    if notice_days <= 15:
        return 1.0
    if notice_days <= 30:
        return 0.85
    if notice_days <= 60:
        return 0.6
    if notice_days <= 90:
        return 0.35
    return 0.15


def availability_score(candidate: dict, reference_date: date | None = None) -> float:
    sig = candidate.get("redrob_signals", {})
    open_to_work = sig.get("open_to_work_flag", False)
    recency = _activity_recency_score(sig.get("last_active_date", ""), reference_date)
    notice = _notice_period_score(sig.get("notice_period_days", 180))

    score = 0.40 * (1.0 if open_to_work else 0.3) + 0.35 * recency + 0.25 * notice
    return round(score, 4)


def engagement_score(candidate: dict) -> float:
    sig = candidate.get("redrob_signals", {})
    response_rate = sig.get("recruiter_response_rate", 0.0) or 0.0
    interview_completion = sig.get("interview_completion_rate", 0.0) or 0.0
    applications = sig.get("applications_submitted_30d", 0) or 0
    github = sig.get("github_activity_score", -1)

    application_score = min(applications / 5.0, 1.0)
    github_score = 0.0 if github is None or github < 0 else min(github / 60.0, 1.0)

    score = (
        0.40 * response_rate
        + 0.30 * interview_completion
        + 0.15 * application_score
        + 0.15 * github_score
    )
    return round(score, 4)


def behavioral_multiplier(candidate: dict, reference_date: date | None = None) -> float:
    avail = availability_score(candidate, reference_date)
    engage = engagement_score(candidate)
    combined = 0.5 * avail + 0.5 * engage
    multiplier = 0.4 + 0.9 * combined
    return round(multiplier, 4)


if __name__ == "__main__":
    active_engaged = {
        "redrob_signals": {
            "open_to_work_flag": True,
            "last_active_date": date.today().isoformat(),
            "notice_period_days": 15,
            "recruiter_response_rate": 0.9,
            "interview_completion_rate": 1.0,
            "applications_submitted_30d": 5,
            "github_activity_score": 60,
        }
    }
    ghost = {
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
    print("Active/engaged multiplier:", behavioral_multiplier(active_engaged))
    print("Ghost candidate multiplier:", behavioral_multiplier(ghost))