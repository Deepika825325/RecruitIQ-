import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.pipeline import passes_stage_a
from recruitiq.scoring.career_score import career_score_batch, EmbeddingsLookup

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

    survivors = [c for c in load_candidates(CANDIDATES_PATH) if passes_stage_a(c)]

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