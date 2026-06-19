PREFERRED_CITIES = ["pune", "noida"]
WELCOME_CITIES = ["hyderabad", "mumbai", "delhi", "ncr", "gurugram", "gurgaon"]

EDUCATION_TIER_SCORES = {
    "tier_1": 1.0,
    "tier_2": 0.8,
    "tier_3": 0.6,
    "tier_4": 0.4,
    "unknown": 0.5,
}


def yoe_score(years: float) -> float:
    """5-9 years is the JD's ideal band. Smooth taper outside it —
    no cliff-edge penalties, since the JD explicitly says this is a
    range, not a hard requirement."""
    if years < 0:
        return 0.0
    if 5 <= years <= 9:
        return 1.0
    if years < 5:
        return round(0.4 + 0.6 * (years / 5), 4)
    decay = (years - 9) * 0.08
    return round(max(0.3, 1.0 - decay), 4)


def location_score(candidate: dict) -> float:
    profile = candidate.get("profile", {})
    location = (profile.get("location") or "").lower()
    country = (profile.get("country") or "").lower()
    willing_to_relocate = candidate.get("redrob_signals", {}).get("willing_to_relocate", False)

    if country != "india":
        return 0.3 if willing_to_relocate else 0.1

    if any(city in location for city in PREFERRED_CITIES):
        return 1.0
    if any(city in location for city in WELCOME_CITIES):
        return 0.85

    return 0.7 if willing_to_relocate else 0.55


def education_score(candidate: dict) -> float:
    education = candidate.get("education", [])
    if not education:
        return 0.5  # neutral when no data — JD says skills matter more anyway

    tiers = [edu.get("tier", "unknown") for edu in education]
    scores = [EDUCATION_TIER_SCORES.get(t, 0.5) for t in tiers]
    return max(scores)  # best degree counts, not average


def structured_score(candidate: dict) -> float:
    weights = {"yoe": 0.5, "location": 0.35, "education": 0.15}

    yoe = candidate.get("profile", {}).get("years_of_experience", 0)
    s_yoe = yoe_score(yoe)
    s_loc = location_score(candidate)
    s_edu = education_score(candidate)

    combined = weights["yoe"] * s_yoe + weights["location"] * s_loc + weights["education"] * s_edu
    return round(combined, 4)


if __name__ == "__main__":
    test_candidate = {
        "profile": {
            "years_of_experience": 6.0,
            "location": "Bangalore, Karnataka",
            "country": "India",
        },
        "redrob_signals": {"willing_to_relocate": True},
        "education": [{"tier": "tier_2"}],
    }
    print("YOE score:       ", yoe_score(6.0))
    print("Location score:  ", location_score(test_candidate))
    print("Education score: ", education_score(test_candidate))
    print("Structured score:", structured_score(test_candidate))