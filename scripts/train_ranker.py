import sys
import csv
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import lightgbm as lgb

LABELED_PATH = "data/processed/labeling_sample.csv"
MODEL_OUTPUT_PATH = "data/processed/ranker_model.txt"
IMPORTANCE_OUTPUT_PATH = "data/processed/feature_importance.json"
FEATURE_COLUMNS = ["title_score", "skills_score", "career_score", "structured_score"]


def load_labeled_data(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row.get("manual_label", "").strip()
            if label == "":
                continue
            rows.append(row)
    return rows


def main():
    rows = load_labeled_data(LABELED_PATH)
    if len(rows) < 30:
        print(f"Only {len(rows)} labeled rows found. Label at least 30-50 before training.")
        return

    X = np.array([[float(r[col]) for col in FEATURE_COLUMNS] for r in rows], dtype=np.float64)
    y = np.array([int(r["manual_label"]) for r in rows], dtype=np.int32)
    group = np.array([len(rows)], dtype=np.int32)

    train_data = lgb.Dataset(X, label=y, group=group, feature_name=FEATURE_COLUMNS)

    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "eval_at": [10, 50],
        "verbosity": -1,
        "num_leaves": 7,
        "min_data_in_leaf": 5,
        "learning_rate": 0.1,
    }

    model = lgb.train(params, train_data, num_boost_round=100)

    Path(MODEL_OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    model.save_model(MODEL_OUTPUT_PATH)

    importances = model.feature_importance(importance_type="gain")
    total = sum(importances)

    importance_dict = {}
    print("Feature importances (gain):")
    for name, imp in zip(FEATURE_COLUMNS, importances):
        pct = (imp / total * 100) if total > 0 else 0
        importance_dict[name] = round(float(pct), 2)
        print(f"  {name}: {imp:.1f} ({pct:.1f}%)")

    with open(IMPORTANCE_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "feature_importance_pct": importance_dict,
            "trained_on_count": len(rows),
        }, f, indent=2)

    print(f"Model saved to {MODEL_OUTPUT_PATH}")
    print(f"Feature importance saved to {IMPORTANCE_OUTPUT_PATH}")
    print(f"Trained on {len(rows)} labeled candidates")


if __name__ == "__main__":
    main()
