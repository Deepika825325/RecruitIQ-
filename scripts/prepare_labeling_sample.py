import sys
import csv
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.pipeline import passes_stage_a, score_survivors, load_weights
from recruitiq.scoring.career_score import EmbeddingsLookup
from recruitiq.scoring.skills_score import classify_skill

CANDIDATES_PATH = "data/raw/candidates.jsonl"
OUTPUT_PATH = "data/processed/labeling_sample.csv"
SAMPLE_SIZE = 200


def load_jd_text():
    with open("configs/jd_config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["jd_full_text"]


def top_skills_str(candidate, limit=3):
    skills = candidate.get("skills", [])
    evidenced = [
        s for s in skills
        if classify_skill(s.get("name", "")) in ("core", "bonus")
        and s.get("duration_months", 0) > 0
    ]
    evidenced.sort(key=lambda s: s.get("duration_months", 0), reverse=True)
    return "; ".join(f"{s['name']}({s.get('duration_months',0)}mo)" for s in evidenced[:limit])


def current_role_snippet(candidate):
    history = candidate.get("career_history", [])
    if not history:
        return ""
    current = next((r for r in history if r.get("is_current")), history[0])
    return current.get("description", "")[:200]


def stratified_sample(results, sample_size):
    sorted_results = sorted(results, key=lambda r: -r["final_score"])
    n = len(sorted_results)
    bucket_count = 10
    bucket_size = n // bucket_count
    per_bucket = sample_size // bucket_count

    sample = []
    for i in range(bucket_count):
        start = i * bucket_size
        end = start + bucket_size if i < bucket_count - 1 else n
        bucket = sorted_results[start:end]
        step = max(1, len(bucket) // per_bucket)
        sample.extend(bucket[::step][:per_bucket])

    return sample


def main():
    jd_text = load_jd_text()
    weights = load_weights()
    lookup = EmbeddingsLookup()

    survivors = [c for c in load_candidates(CANDIDATES_PATH) if passes_stage_a(c)]
    results = score_survivors(survivors, jd_text, lookup, weights)

    sample = stratified_sample(results, SAMPLE_SIZE)

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "candidate_id", "current_title", "current_company", "years_of_experience",
            "top_skills", "current_role_snippet",
            "title_score", "skills_score", "career_score", "structured_score",
            "behavioral_multiplier", "final_score", "manual_label"
        ])
        for r in sample:
            c = r["candidate"]
            profile = c.get("profile", {})
            writer.writerow([
                r["candidate_id"],
                profile.get("current_title", ""),
                profile.get("current_company", ""),
                profile.get("years_of_experience", ""),
                top_skills_str(c),
                current_role_snippet(c),
                r["title_score"], r["skills_score"], r["career_score"], r["structured_score"],
                r["behavioral_multiplier"], r["final_score"], ""
            ])

    print(f"Wrote {len(sample)} candidates to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
