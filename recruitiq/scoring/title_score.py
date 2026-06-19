"""
Classifies a candidate's current title into a fit tier based on
configs/title_taxonomy.yaml, and returns a numeric score.
"""

import yaml
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "title_taxonomy.yaml"


def load_title_taxonomy(path: Path = _CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_TAXONOMY = load_title_taxonomy()


def classify_title(title: str, taxonomy: dict = _TAXONOMY) -> tuple[str, float]:
    """
    Returns (tier_name, score) for a given job title string.
    Checks tiers in priority order: A -> B -> C -> D.
    Falls back to 'unknown' if no keyword matches.
    """
    if not title:
        return "unknown", taxonomy["scores"]["unknown"]

    title_lower = title.lower().strip()

    for tier in ["tier_a", "tier_b", "tier_c", "tier_d"]:
        keywords = taxonomy.get(tier, [])
        for kw in keywords:
            if kw in title_lower:
                return tier, taxonomy["scores"][tier]

    return "unknown", taxonomy["scores"]["unknown"]


def title_score(candidate: dict, taxonomy: dict = _TAXONOMY) -> float:
    """Convenience wrapper — takes a full candidate dict, returns just the score."""
    title = candidate.get("profile", {}).get("current_title", "")
    _, score = classify_title(title, taxonomy)
    return score


if __name__ == "__main__":
    # Quick manual check against your ground truth candidates
    test_titles = [
        "Recommendation Systems Engineer",  # CAND_0000031 -> tier_a
        "HR Manager",                        # CAND_0000024 -> tier_d
        "Software Engineer",                 # CAND_0000015 -> tier_b
        "Data Engineer",                     # CAND_0000010 -> tier_c
    ]
    for t in test_titles:
        tier, score = classify_title(t)
        print(f"{t:35s} -> {tier} ({score})")