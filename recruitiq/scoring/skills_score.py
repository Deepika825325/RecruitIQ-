import math
import yaml
from pathlib import Path

_SKILLS_TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "configs" / "skills_taxonomy.yaml"
_JD_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "jd_config.yaml"


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_SKILLS_TAXONOMY = _load_yaml(_SKILLS_TAXONOMY_PATH)
_JD_CONFIG = _load_yaml(_JD_CONFIG_PATH)

PROFICIENCY_WEIGHTS = {
    "beginner": 0.25,
    "intermediate": 0.5,
    "advanced": 0.75,
    "expert": 1.0,
}

CATEGORY_MULTIPLIERS = {
    "core": 1.0,
    "bonus": 0.5,
    "language": 0.3,
}

NORMALIZATION_CONSTANT = 8.0
PENALTY_MULTIPLIER = 0.3
MAX_ENDORSEMENT_BOOST_COUNT = 50
ENDORSEMENT_BOOST_RATE = 0.005


def _flatten(keyword_lists: list[list[str]]) -> list[str]:
    flat = []
    for lst in keyword_lists:
        flat.extend(lst)
    return [k.lower() for k in flat]


_CORE_KEYWORDS = _flatten([
    _JD_CONFIG["core_skills"]["embeddings_retrieval"],
    _JD_CONFIG["core_skills"]["vector_db_search"],
    _JD_CONFIG["core_skills"]["eval_frameworks"],
])
_LANGUAGE_KEYWORDS = [k.lower() for k in _JD_CONFIG["core_skills"]["core_language"]]
_BONUS_KEYWORDS = [k.lower() for k in _SKILLS_TAXONOMY.get("bonus_skills", [])]
_PENALTY_KEYWORDS = [k.lower() for k in _JD_CONFIG.get("penalty_domains", [])]


def _classify_skill(skill_name: str) -> str | None:
    name = skill_name.lower()
    if any(kw in name for kw in _CORE_KEYWORDS):
        return "core"
    if any(kw in name for kw in _BONUS_KEYWORDS):
        return "bonus"
    if any(kw in name for kw in _LANGUAGE_KEYWORDS):
        return "language"
    return None


def _is_penalty_skill(skill_name: str) -> bool:
    name = skill_name.lower()
    return any(kw in name for kw in _PENALTY_KEYWORDS)


def _skill_contribution(skill: dict, category: str) -> float:
    proficiency = skill.get("proficiency", "beginner")
    duration = skill.get("duration_months", 0)
    endorsements = skill.get("endorsements", 0)

    prof_weight = PROFICIENCY_WEIGHTS.get(proficiency, 0.25)
    duration_factor = math.log(1 + duration)  # 0 months -> log(1) = 0, kills honeypot skills
    endorsement_factor = 1 + min(endorsements, MAX_ENDORSEMENT_BOOST_COUNT) * ENDORSEMENT_BOOST_RATE
    category_multiplier = CATEGORY_MULTIPLIERS.get(category, 0)

    return prof_weight * duration_factor * endorsement_factor * category_multiplier


def skills_score(candidate: dict) -> float:
    skills = candidate.get("skills", [])
    raw_total = 0.0
    has_core_skill = False
    has_penalty_skill = False

    for skill in skills:
        name = skill.get("name", "")
        category = _classify_skill(name)

        if category is not None:
            raw_total += _skill_contribution(skill, category)
            if category == "core":
                has_core_skill = True

        if _is_penalty_skill(name):
            has_penalty_skill = True

    normalized = min(1.0, raw_total / NORMALIZATION_CONSTANT)

    # JD rule: CV/speech/robotics specialists are fine IF they also have
    # real NLP/IR exposure. Penalty only applies when core skill is absent.
    if has_penalty_skill and not has_core_skill:
        normalized *= PENALTY_MULTIPLIER

    return round(normalized, 4)


if __name__ == "__main__":
    # Quick manual check using real data shapes from your ground truth candidates
    strong_fit = {
        "skills": [
            {"name": "Pinecone", "proficiency": "expert", "duration_months": 88, "endorsements": 10},
            {"name": "Embeddings", "proficiency": "expert", "duration_months": 60, "endorsements": 8},
            {"name": "Information Retrieval", "proficiency": "expert", "duration_months": 84, "endorsements": 12},
            {"name": "Sentence Transformers", "proficiency": "expert", "duration_months": 69, "endorsements": 6},
            {"name": "Image Classification", "proficiency": "advanced", "duration_months": 28, "endorsements": 2},
        ]
    }
    reject = {
        "skills": [
            {"name": "Figma", "proficiency": "beginner", "duration_months": 15, "endorsements": 0},
            {"name": "Docker", "proficiency": "beginner", "duration_months": 5, "endorsements": 0},
        ]
    }
    honeypot = {
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 0, "endorsements": 5},
        ]
    }

    print("Strong fit score:", skills_score(strong_fit))
    print("Reject score:    ", skills_score(reject))
    print("Honeypot score:  ", skills_score(honeypot))