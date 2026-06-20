def build_career_text(candidate: dict) -> str:
    profile = candidate.get("profile", {})
    summary = profile.get("summary", "") or ""

    career = candidate.get("career_history", [])
    descriptions = [role.get("description", "") or "" for role in career]

    combined = summary + " " + " ".join(descriptions)
    return combined.strip()