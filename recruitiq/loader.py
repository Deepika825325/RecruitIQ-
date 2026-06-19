"""
Streams candidate records from candidates.jsonl or candidates.jsonl.gz
without loading the entire file into memory at once.
"""

import gzip
import json
from pathlib import Path
from typing import Iterator


def load_candidates(path: str) -> Iterator[dict]:
    """
    Yields one candidate dict at a time. Handles both plain .jsonl
    and gzipped .jsonl.gz transparently based on file extension.
    """
    p = Path(path)
    opener = gzip.open if p.suffix == ".gz" else open

    with opener(p, "rt", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed JSON at line {line_num}: {e}")


def load_candidates_list(path: str, limit: int | None = None) -> list[dict]:
    """
    Convenience wrapper that materializes candidates into a list.
    Use `limit` during development to avoid loading all 100K while testing.
    """
    candidates = []
    for i, c in enumerate(load_candidates(path)):
        if limit is not None and i >= limit:
            break
        candidates.append(c)
    return candidates


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python loader.py <path_to_candidates.jsonl[.gz]>")
        sys.exit(1)

    count = 0
    for _ in load_candidates(sys.argv[1]):
        count += 1
    print(f"Loaded {count} candidates from {sys.argv[1]}")