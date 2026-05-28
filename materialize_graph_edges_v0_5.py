import gzip
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "graph_edges_v0_5.jsonl.gz"
TARGET = ROOT / "graph_edges_v0_5.jsonl"


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing compressed source: {SOURCE.name}")
    with gzip.open(SOURCE, "rb") as source, TARGET.open("wb") as target:
        shutil.copyfileobj(source, target)
    print(f"materialized {TARGET.name} from {SOURCE.name}")


if __name__ == "__main__":
    main()
