"""
Day 2 sanity check: run title scoring + hard filters + a coarse skills
check across the full 100K candidate pool. Reports survivor count and timing.
"""

import time
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.scoring.title_score import classify_title
from recruitiq.filters.hard_filters import apply_hard_filters, load_jd_config

CANDIDATES_PATH = "data/raw/candidates.jsonl"
MIN_CORE_SKILL_MATCHES = 2

_JD_CONFIG = load_jd_config()


def get_core_skill_keywords(jd_config: dict) -> list[str]:
    """Flatten only the most discriminating skill categories — not python,
    since almost everyone lists it and it won't help filter."""
    core = jd_config.get("core_skills", {})
    keywords = []
    keywords.extend(core.get("embeddings_retrieval", []))
    keywords.extend(core.get("vector_db_search", []))
    keywords.extend(core.get("eval_frameworks", []))
    return [k.lower() for k in keywords]


_CORE_KEYWORDS = get_core_skill_keywords(_JD_CONFIG)


def count_core_skill_matches(candidate: dict) -> int:
    skill_names = [s.get("name", "").lower() for s in candidate.get("skills", [])]
    matches = 0
    for skill_name in skill_names:
        if any(kw in skill_name for kw in _CORE_KEYWORDS):
            matches += 1
    return matches


def passes_stage_a(candidate: dict) -> bool:
    multiplier, _ = apply_hard_filters(candidate)
    if multiplier < 1.0:
        return False

    title = candidate.get("profile", {}).get("current_title", "")
    tier, _ = classify_title(title)

    if tier == "tier_a":
        return True  # title alone is selective enough

    if tier == "tier_b":
        return count_core_skill_matches(candidate) >= MIN_CORE_SKILL_MATCHES

    return False  # tier_c, tier_d, unknown — all excluded from Stage A


def main():
    start = time.time()

    total = 0
    survivors = 0
    disqualified = 0
    tier_a_survivors = 0
    tier_b_survivors = 0

    for candidate in load_candidates(CANDIDATES_PATH):
        total += 1

        multiplier, _ = apply_hard_filters(candidate)
        if multiplier < 1.0:
            disqualified += 1
            continue

        title = candidate.get("profile", {}).get("current_title", "")
        tier, _ = classify_title(title)

        if tier == "tier_a":
            survivors += 1
            tier_a_survivors += 1
        elif tier == "tier_b" and count_core_skill_matches(candidate) >= MIN_CORE_SKILL_MATCHES:
            survivors += 1
            tier_b_survivors += 1

    elapsed = time.time() - start

    print(f"Total candidates:        {total}")
    print(f"Hard-filtered out:       {disqualified}")
    print(f"Stage A survivors:       {survivors}")
    print(f"  -> from tier_a:        {tier_a_survivors}")
    print(f"  -> from tier_b+skills: {tier_b_survivors}")
    print(f"Survival rate:           {survivors/total*100:.2f}%")
    print(f"Time taken:              {elapsed:.1f}s")


if __name__ == "__main__":
    main()