import yaml
from pathlib import Path

from recruitiq.scoring.title_score import classify_title, title_score
from recruitiq.scoring.skills_score import skills_score
from recruitiq.scoring.structured_score import structured_score
from recruitiq.scoring.career_score import career_score_batch, EmbeddingsLookup
from recruitiq.scoring.behavioral_score import behavioral_multiplier
from recruitiq.filters.hard_filters import apply_hard_filters

_WEIGHTS_PATH = Path(__file__).resolve().parents[1] / "configs" / "weights.yaml"
RESCUE_SKILLS_THRESHOLD = 0.5


def load_weights(path: Path = _WEIGHTS_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def passes_stage_a(candidate: dict) -> bool:
    multiplier, _ = apply_hard_filters(candidate)
    if multiplier < 1.0:
        return False

    title = candidate.get("profile", {}).get("current_title", "")
    tier, _ = classify_title(title)

    if tier == "tier_a":
        return True

    if tier in ("tier_b", "tier_c"):
        return skills_score(candidate) >= RESCUE_SKILLS_THRESHOLD

    return False


def score_survivors(
    survivors: list[dict], jd_text: str, lookup: EmbeddingsLookup, weights: dict
) -> list[dict]:
    """
    Computes all Stage B layer scores plus the final combined score for
    every survivor. Career score is computed as a batch (needs the full
    set for TF-IDF fitting); the rest are computed per-candidate.
    """
    career_scores = career_score_batch(survivors, jd_text, lookup)

    results = []
    for c in survivors:
        cid = c["candidate_id"]

        t = title_score(c)
        s = skills_score(c)
        ca = career_scores.get(cid, 0.0)
        st = structured_score(c)

        raw = (
            weights["title"] * t
            + weights["skills"] * s
            + weights["career"] * ca
            + weights["structured"] * st
        )

        mult = behavioral_multiplier(c)
        final = round(raw * mult, 4)

        results.append(
            {
                "candidate_id": cid,
                "title_score": t,
                "skills_score": s,
                "career_score": ca,
                "structured_score": st,
                "behavioral_multiplier": mult,
                "final_score": final,
                "candidate": c,
            }
        )

    return results


def rank_top_n(results: list[dict], top_n: int = 100) -> list[dict]:
    """Sorts by final_score descending, candidate_id ascending on ties —
    matches validate_submission.py's required tie-break rule exactly."""
    sorted_results = sorted(results, key=lambda r: (-r["final_score"], r["candidate_id"]))
    return sorted_results[:top_n]