import sys
import time
import yaml
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sentence_transformers import SentenceTransformer
from recruitiq.loader import load_candidates
from recruitiq.utils.text_cleaning import build_career_text

CANDIDATES_PATH = "data/raw/candidates.jsonl"
OUTPUT_DIR = Path("data/processed")
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64
JD_CONFIG_PATH = Path("configs/jd_config.yaml")


def load_jd_text() -> str:
    with open(JD_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["jd_full_text"]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading sentence-transformer model (one-time download if not cached)...")
    model = SentenceTransformer(MODEL_NAME)

    print("Loading candidates and building career texts...")
    candidate_ids = []
    texts = []
    for c in load_candidates(CANDIDATES_PATH):
        candidate_ids.append(c["candidate_id"])
        texts.append(build_career_text(c))
    print(f"Loaded {len(texts)} candidates.")

    print("Encoding candidate career texts — this may take a few minutes, that's expected...")
    start = time.time()
    embeddings = model.encode(
        texts, batch_size=BATCH_SIZE, show_progress_bar=True, convert_to_numpy=True
    )
    elapsed = time.time() - start
    print(f"Encoding done in {elapsed:.1f}s")

    np.save(OUTPUT_DIR / "embeddings.npy", embeddings.astype(np.float32))
    np.save(OUTPUT_DIR / "candidate_ids.npy", np.array(candidate_ids))

    print("Encoding JD comparison text...")
    jd_text = load_jd_text()
    jd_embedding = model.encode([jd_text], convert_to_numpy=True)[0]
    np.save(OUTPUT_DIR / "jd_embedding.npy", jd_embedding.astype(np.float32))

    print("Saved embeddings.npy, candidate_ids.npy, jd_embedding.npy to data/processed/")


if __name__ == "__main__":
    main()