import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.scoring.title_score import classify_title
from recruitiq.scoring.career_score import career_score_batch, EmbeddingsLookup
from recruitiq.filters.hard_filters import apply_hard_filters

CANDIDATES_PATH = "data/raw/candidates.jsonl"
GROUND_TRUTH_IDS = {
    "CAND_0000031": "strong_fit",
    "CAND_0000024": "reject",
    "CAND_0000015": "borderline_low",
    "CAND_0000010": "borderline_mid",
}


def load_jd_text() -> str:
    with open("configs/jd_config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["jd_full_text"]


def main():
    jd_text = load_jd_text()
    lookup = EmbeddingsLookup()

    survivors = []
    for candidate in load_candidates(CANDIDATES_PATH):
        multiplier, _ = apply_hard_filters(candidate)
        if multiplier < 1.0:
            continue
        title = candidate.get("profile", {}).get("current_title", "")
        tier, _ = classify_title(title)
        if tier in ("tier_a", "tier_b"):
            survivors.append(candidate)

    print(f"Scoring career evidence for {len(survivors)} Stage A survivors...")
    scores = career_score_batch(survivors, jd_text, lookup)

    print("\n=== Ground Truth Career Scores ===")
    for cid, label in GROUND_TRUTH_IDS.items():
        score = scores.get(cid, "NOT IN STAGE A SURVIVORS")
        print(f"{cid} [{label:15s}] career_score={score}")

    sorted_scores = sorted(scores.values())
    n = len(sorted_scores)
    print(f"\nDistribution -> min={sorted_scores[0]:.3f}  median={sorted_scores[n//2]:.3f}  max={sorted_scores[-1]:.3f}")


if __name__ == "__main__":
    main()