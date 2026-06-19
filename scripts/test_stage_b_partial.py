"""
Runs skills_score and structured_score across Stage A survivors,
and prints scores specifically for your 4 ground truth candidates
so you can sanity-check the new layers before moving to Day 4.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.scoring.title_score import classify_title
from recruitiq.scoring.skills_score import skills_score
from recruitiq.scoring.structured_score import structured_score
from recruitiq.filters.hard_filters import apply_hard_filters

CANDIDATES_PATH = "data/raw/candidates.jsonl"
GROUND_TRUTH_IDS = {
    "CAND_0000031": "strong_fit",
    "CAND_0000024": "reject",
    "CAND_0000015": "borderline_low",
    "CAND_0000010": "borderline_mid",
}


def main():
    skill_scores = []
    structured_scores = []
    ground_truth_results = {}

    for candidate in load_candidates(CANDIDATES_PATH):
        cid = candidate.get("candidate_id")

        if cid in GROUND_TRUTH_IDS:
            s_score = skills_score(candidate)
            st_score = structured_score(candidate)
            ground_truth_results[cid] = {
                "label": GROUND_TRUTH_IDS[cid],
                "skills_score": s_score,
                "structured_score": st_score,
            }

        multiplier, _ = apply_hard_filters(candidate)
        if multiplier < 1.0:
            continue

        title = candidate.get("profile", {}).get("current_title", "")
        tier, _ = classify_title(title)
        if tier not in ("tier_a", "tier_b"):
            continue

        skill_scores.append(skills_score(candidate))
        structured_scores.append(structured_score(candidate))

    print("=== Ground Truth Sanity Check ===")
    for cid, data in ground_truth_results.items():
        print(f"{cid} [{data['label']:15s}] skills={data['skills_score']:.4f}  structured={data['structured_score']:.4f}")

    print()
    print("=== Distribution across Stage A survivors ===")
    skill_scores.sort()
    structured_scores.sort()
    n = len(skill_scores)
    print(f"Skills score      -> min={skill_scores[0]:.3f}  median={skill_scores[n//2]:.3f}  max={skill_scores[-1]:.3f}")
    print(f"Structured score   -> min={structured_scores[0]:.3f}  median={structured_scores[n//2]:.3f}  max={structured_scores[-1]:.3f}")


if __name__ == "__main__":
    main()