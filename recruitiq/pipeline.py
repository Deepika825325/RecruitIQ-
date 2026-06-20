from recruitiq.scoring.title_score import classify_title
from recruitiq.scoring.skills_score import skills_score
from recruitiq.filters.hard_filters import apply_hard_filters

RESCUE_SKILLS_THRESHOLD = 0.5


def passes_stage_a(candidate: dict) -> bool:
    multiplier, _ = apply_hard_filters(candidate)
    if multiplier < 1.0:
        return False

    title = candidate.get("profile", {}).get("current_title", "")
    tier, _ = classify_title(title)

    if tier == "tier_a":
        return True  # title alone is selective enough

    if tier in ("tier_b", "tier_c"):
        # Rescue path: real weighted skill evidence, not just keyword count.
        # This is what catches plain-language hidden gems like CAND_0000010.
        return skills_score(candidate) >= RESCUE_SKILLS_THRESHOLD

    return False  # tier_d, unknown — never rescued