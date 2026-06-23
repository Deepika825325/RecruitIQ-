import sys
import csv
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.filters.honeypot_detector import detect_honeypot
from recruitiq.filters.hard_filters import is_consulting_only, load_jd_config

SUBMISSION_PATH = "data/outputs/submission.csv"
CANDIDATES_PATH = "data/raw/candidates.jsonl"
OUTPUT_PATH = "data/processed/honeypot_audit.json"


def main():
    with open(SUBMISSION_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        submitted_ids = {row["candidate_id"] for row in reader}

    jd_config = load_jd_config()
    consulting_firms = jd_config.get("consulting_firms", [])

    candidates_by_id = {}
    for c in load_candidates(CANDIDATES_PATH):
        if c["candidate_id"] in submitted_ids:
            candidates_by_id[c["candidate_id"]] = c

    honeypot_count = 0
    consulting_count = 0
    flagged = []

    for cid in submitted_ids:
        candidate = candidates_by_id.get(cid)
        if candidate is None:
            continue

        is_hp, reasons = detect_honeypot(candidate)
        is_consulting = is_consulting_only(candidate.get("career_history", []), consulting_firms)

        if is_hp:
            honeypot_count += 1
            flagged.append({"candidate_id": cid, "type": "honeypot", "reasons": reasons})
        if is_consulting:
            consulting_count += 1
            flagged.append({"candidate_id": cid, "type": "consulting_only", "reasons": []})

    total = len(submitted_ids)
    honeypot_rate = honeypot_count / total * 100 if total else 0
    status = "FAIL" if honeypot_rate > 10 else "PASS"

    print(f"Total submitted candidates: {total}")
    print(f"Honeypots detected: {honeypot_count} ({honeypot_rate:.2f}%)")
    print(f"Consulting-only detected: {consulting_count}")
    print(f"Status: {status}")

    result = {
        "total": total,
        "honeypot_count": honeypot_count,
        "honeypot_rate": round(honeypot_rate, 2),
        "consulting_count": consulting_count,
        "threshold": 10,
        "status": status,
        "flagged": flagged,
    }

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Audit result saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
