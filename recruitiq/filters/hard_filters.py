import yaml
from pathlib import Path
from recruitiq.filters.honeypot_detector import detect_honeypot

_JD_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "jd_config.yaml"


def load_jd_config(path: Path = _JD_CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_JD_CONFIG = load_jd_config()
_DISQUALIFIER_MULTIPLIER = 0.05


def is_consulting_only(career_history: list[dict], consulting_firms: list[str]) -> bool:
    if not career_history:
        return False

    consulting_lower = [c.lower() for c in consulting_firms]

    for role in career_history:
        company = role.get("company", "").lower()
        if not any(cf in company for cf in consulting_lower):
            return False

    return True


def apply_hard_filters(candidate: dict, jd_config: dict = _JD_CONFIG) -> tuple[float, list[str]]:
    reasons = []
    consulting_firms = jd_config.get("consulting_firms", [])
    career = candidate.get("career_history", [])

    if is_consulting_only(career, consulting_firms):
        reasons.append("consulting_only_career")

    is_honeypot, honeypot_reasons = detect_honeypot(candidate)
    if is_honeypot:
        reasons.extend(honeypot_reasons)

    multiplier = _DISQUALIFIER_MULTIPLIER if reasons else 1.0
    return multiplier, reasons