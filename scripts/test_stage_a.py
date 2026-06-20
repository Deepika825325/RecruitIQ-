import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recruitiq.loader import load_candidates
from recruitiq.pipeline import passes_stage_a

CANDIDATES_PATH = "data/raw/candidates.jsonl"


def main():
    start = time.time()
    total = 0
    survivors = 0

    for candidate in load_candidates(CANDIDATES_PATH):
        total += 1
        if passes_stage_a(candidate):
            survivors += 1

    elapsed = time.time() - start

    print(f"Total candidates:     {total}")
    print(f"Stage A survivors:    {survivors}")
    print(f"Survival rate:        {survivors/total*100:.2f}%")
    print(f"Time taken:           {elapsed:.1f}s")


if __name__ == "__main__":
    main()
