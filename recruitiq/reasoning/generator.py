from recruitiq.scoring.skills_score import classify_skill


def _top_evidence_skills(candidate: dict, limit: int = 2) -> list[dict]:
    skills = candidate.get("skills", [])
    evidenced = [
        s for s in skills
        if classify_skill(s.get("name", "")) in ("core", "bonus")
        and s.get("duration_months", 0) > 0
    ]
    evidenced.sort(key=lambda s: s.get("duration_months", 0), reverse=True)
    return evidenced[:limit]


def _skill_phrase(top_skills: list[dict]) -> str:
    if not top_skills:
        return "no strongly matched core skills"
    parts = [f"{s['name']} ({s.get('duration_months', 0)}mo)" for s in top_skills]
    return ", ".join(parts)


def _identify_concern(candidate: dict, scores: dict) -> str | None:
    sig = candidate.get("redrob_signals", {})
    notice = sig.get("notice_period_days")
    open_to_work = sig.get("open_to_work_flag", True)

    if notice is not None and notice > 60:
        return f"{notice}-day notice period may slow onboarding"
    if not open_to_work:
        return "not currently flagged open to work, may need active outreach"
    if scores.get("career_score", 1.0) < 0.15:
        return "career history reads less directly relevant despite skill evidence"
    return None


def generate_reasoning(candidate: dict, scores: dict) -> str:
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "Unknown role")
    company = profile.get("current_company", "")

    top_skills = _top_evidence_skills(candidate)
    skill_phrase = _skill_phrase(top_skills)

    base = f"{yoe:.1f}yr {title} at {company}, with evidence in {skill_phrase}."

    concern = _identify_concern(candidate, scores)
    if concern:
        base += f" Note: {concern}."

    return base