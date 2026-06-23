import sys
import time
import argparse
import csv
import json
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.pipeline import passes_stage_a, score_survivors, rank_top_n, load_weights, load_ranker_model
from recruitiq.scoring.career_score import EmbeddingsLookup
from recruitiq.reasoning.generator import generate_reasoning

TOP_N = 100


def load_jd_text(config_path="configs/jd_config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["jd_full_text"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    start = time.time()

    jd_text = load_jd_text()
    weights = load_weights()
    lookup = EmbeddingsLookup()
    ranker_model = load_ranker_model()

    print("Loading candidates and applying Stage A filter...")
    all_candidates = list(load_candidates(args.candidates))
    total_candidates = len(all_candidates)
    survivors = [c for c in all_candidates if passes_stage_a(c)]
    print(f"Stage A survivors: {len(survivors)}")

    print(f"Using {'trained LightGBM ranker' if ranker_model else 'hand-set weights'}...")
    results = score_survivors(survivors, jd_text, lookup, weights, ranker_model=ranker_model)

    top_results = rank_top_n(results, top_n=TOP_N)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Writing top {len(top_results)} candidates to {out_path}...")
    detailed_rows = []
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for i, r in enumerate(top_results, start=1):
            reasoning = generate_reasoning(r["candidate"], r)
            writer.writerow([r["candidate_id"], i, r["final_score"], reasoning])

            profile = r["candidate"].get("profile", {})
            detailed_rows.append({
                "candidate_id": r["candidate_id"],
                "rank": i,
                "score": r["final_score"],
                "reasoning": reasoning,
                "current_title": profile.get("current_title", ""),
                "current_company": profile.get("current_company", ""),
                "years_of_experience": profile.get("years_of_experience", 0),
                "location": profile.get("location", ""),
                "title_score": r["title_score"],
                "skills_score": r["skills_score"],
                "career_score": r["career_score"],
                "structured_score": r["structured_score"],
                "behavioral_multiplier": r["behavioral_multiplier"],
            })

    detailed_path = out_path.parent / "submission_detailed.json"
    with open(detailed_path, "w", encoding="utf-8") as f:
        json.dump(detailed_rows, f, indent=2)

    elapsed = time.time() - start

    funnel_stats = {
        "total_candidates": total_candidates,
        "stage_a_survivors": len(survivors),
        "final_shortlist": len(top_results),
        "runtime_seconds": round(elapsed, 1),
    }
    funnel_path = out_path.parent / "funnel_stats.json"
    with open(funnel_path, "w", encoding="utf-8") as f:
        json.dump(funnel_stats, f, indent=2)

    print(f"Done in {elapsed:.1f}s")
    print(f"Detailed breakdown saved to {detailed_path}")
    print(f"Funnel stats saved to {funnel_path}")


if __name__ == "__main__":
    main()
