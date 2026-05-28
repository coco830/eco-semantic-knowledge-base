import json
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTIFACT_MANIFEST = ROOT / "artifact_manifest.json"


@lru_cache(maxsize=1)
def artifact_map():
    if not ARTIFACT_MANIFEST.exists():
        return {}
    return json.loads(ARTIFACT_MANIFEST.read_text(encoding="utf-8")).get("artifacts", {})


def artifact_path(name):
    mapped = artifact_map().get(name)
    return ROOT / mapped if mapped else ROOT / name
