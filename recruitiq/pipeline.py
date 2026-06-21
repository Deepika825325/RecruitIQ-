import yaml
import numpy as np
from pathlib import Path

from recruitiq.scoring.title_score import classify_title, title_score
from recruitiq.scoring.skills_score import skills_score
from recruitiq.scoring.structured_score import structured_score
from recruitiq.scoring.career_score import career_score_batch, EmbeddingsLookup
from recruitiq.scoring.behavioral_score import behavioral_multiplier
from recruitiq.filters.hard_filters import apply_hard_filters

_WEIGHTS_PATH = Path(__file__).resolve().parents[1] / "configs" / "weights.yaml"
_MODEL_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "ranker_model.txt"
RESCUE_SKILLS_THRESHOLD = 0.5


def load_weights(path=_WEIGHTS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_ranker_model(path=_MODEL_PATH):
    if not path.exists():
        return None
    import lightgbm as lgb
    return lgb.Booster(model_file=str(path))


def passes_stage_a(candidate):
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


def score_survivors(survivors, jd_text, lookup, weights, ranker_model=None):
    career_scores = career_score_batch(survivors, jd_text, lookup)

    results = []
    for c in survivors:
        cid = c["candidate_id"]

        t = title_score(c)
        s = skills_score(c)
        ca = career_scores.get(cid, 0.0)
        st = structured_score(c)

        if ranker_model is not None:
            features = np.array([[t, s, ca, st]])
            raw = float(ranker_model.predict(features)[0])
        else:
            raw = (
                weights["title"] * t
                + weights["skills"] * s
                + weights["career"] * ca
                + weights["structured"] * st
            )

        mult = behavioral_multiplier(c)
        final = round(raw * mult, 4)

        results.append({
            "candidate_id": cid,
            "title_score": t,
            "skills_score": s,
            "career_score": ca,
            "structured_score": st,
            "behavioral_multiplier": mult,
            "final_score": final,
            "candidate": c,
        })

    return results


def rank_top_n(results, top_n=100):
    sorted_results = sorted(results, key=lambda r: (-r["final_score"], r["candidate_id"]))
    return sorted_results[:top_n]
