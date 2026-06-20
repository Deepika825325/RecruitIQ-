import sys
import time
import argparse
import csv
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.pipeline import passes_stage_a, score_survivors, rank_top_n, load_weights
from recruitiq.scoring.career_score import EmbeddingsLookup
from recruitiq.reasoning.generator import generate_reasoning

TOP_N = 100


def load_jd_text(config_path: str = "configs/jd_config.yaml") -> str:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["jd_full_text"]


def main():
    parser = argparse.ArgumentParser(description="RecruitIQ candidate ranker")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl[.gz]")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    start = time.time()

    jd_text = load_jd_text()
    weights = load_weights()
    lookup = EmbeddingsLookup()

    print("Loading candidates and applying Stage A filter...")
    survivors = [c for c in load_candidates(args.candidates) if passes_stage_a(c)]
    print(f"Stage A survivors: {len(survivors)}")

    print("Scoring Stage B (title, skills, career, structured, behavioral)...")
    results = score_survivors(survivors, jd_text, lookup, weights)

    top_results = rank_top_n(results, top_n=TOP_N)

    print(f"Writing top {len(top_results)} candidates to {args.out}...")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for i, r in enumerate(top_results, start=1):
            reasoning = generate_reasoning(r["candidate"], r)
            writer.writerow([r["candidate_id"], i, r["final_score"], reasoning])

    elapsed = time.time() - start
    print(f"Done in {elapsed:.1f}s (must be well under 5 minutes)")


if __name__ == "__main__":
    main()