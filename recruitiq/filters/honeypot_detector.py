def detect_honeypot(candidate: dict) -> tuple[bool, list[str]]:
    reasons = []

    yoe = candidate.get("profile", {}).get("years_of_experience", 0)
    career = candidate.get("career_history", [])

    total_months = sum(role.get("duration_months", 0) for role in career)
    total_years_from_career = total_months / 12

    if yoe > total_years_from_career + 2:
        reasons.append(
            f"yoe_mismatch: claims {yoe} yrs but career history only supports {total_years_from_career:.1f} yrs"
        )

    for skill in candidate.get("skills", []):
        if skill.get("proficiency") in ("expert", "advanced") and skill.get("duration_months", 0) == 0:
            reasons.append(
                f"zero_duration_skill: '{skill.get('name')}' marked {skill.get('proficiency')} with 0 months"
            )

    is_honeypot = len(reasons) > 0
    return is_honeypot, reasons