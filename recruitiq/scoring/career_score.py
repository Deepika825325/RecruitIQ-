import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recruitiq.utils.text_cleaning import build_career_text

_PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"

TFIDF_WEIGHT = 0.5
EMBEDDING_WEIGHT = 0.5


def tfidf_career_scores(jd_text: str, candidates: list[dict]) -> dict[str, float]:
    """Pure TF-IDF component — no file dependency, fast, fully unit-testable."""
    texts = [build_career_text(c) for c in candidates]
    ids = [c["candidate_id"] for c in candidates]

    if not texts:
        return {}

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
    all_texts = [jd_text] + texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    jd_vec = tfidf_matrix[0]
    cand_vecs = tfidf_matrix[1:]
    sims = cosine_similarity(jd_vec, cand_vecs).flatten()

    return {cid: round(float(s), 4) for cid, s in zip(ids, sims)}


class EmbeddingsLookup:
    """Loads precomputed embeddings once, provides fast cosine lookup by candidate_id."""

    def __init__(self, processed_dir: Path = _PROCESSED_DIR):
        emb_path = processed_dir / "embeddings.npy"
        ids_path = processed_dir / "candidate_ids.npy"
        jd_path = processed_dir / "jd_embedding.npy"

        for p in (emb_path, ids_path, jd_path):
            if not p.exists():
                raise FileNotFoundError(
                    f"{p} not found. Run scripts/precompute_embeddings.py first."
                )

        embeddings = np.load(emb_path)
        ids_array = np.load(ids_path, allow_pickle=True)
        jd_vector = np.load(jd_path)

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.embeddings = embeddings / norms
        self.jd_vector = jd_vector / np.linalg.norm(jd_vector)
        self.id_to_index = {cid: i for i, cid in enumerate(ids_array)}

    def get(self, candidate_id: str) -> np.ndarray | None:
        idx = self.id_to_index.get(candidate_id)
        return None if idx is None else self.embeddings[idx]

    def similarity(self, candidate_id: str) -> float:
        vec = self.get(candidate_id)
        if vec is None:
            return 0.0
        sim = float(np.dot(vec, self.jd_vector))
        return max(0.0, sim)


def career_score_batch(
    candidates: list[dict], jd_text: str, lookup: EmbeddingsLookup
) -> dict[str, float]:
    tfidf_scores = tfidf_career_scores(jd_text, candidates)
    embedding_scores = {c["candidate_id"]: lookup.similarity(c["candidate_id"]) for c in candidates}

    combined = {}
    for c in candidates:
        cid = c["candidate_id"]
        t_score = tfidf_scores.get(cid, 0.0)
        e_score = embedding_scores.get(cid, 0.0)
        combined[cid] = round(TFIDF_WEIGHT * t_score + EMBEDDING_WEIGHT * e_score, 4)

    return combined