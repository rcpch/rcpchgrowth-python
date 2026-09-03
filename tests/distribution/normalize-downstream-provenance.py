#!/usr/bin/env python3
"""Substitute only candidate engine provenance in downstream golden files."""

import json
import sys
from pathlib import Path

CANONICAL_ENGINE_NAME = "rcpch/rcpchgrowth-python"
SUPPORTED_ENGINE_NAMES = {"rcpchgrowth", CANONICAL_ENGINE_NAME}


def update(value, version: str, commit: str) -> int:
    changes = 0
    if isinstance(value, dict):
        engine = value.get("calculation_engine")
        if isinstance(engine, dict) and engine.get("name") in SUPPORTED_ENGINE_NAMES:
            engine["name"] = CANONICAL_ENGINE_NAME
            engine["version"] = version
            engine["commit"] = commit
            changes += 1
        for child in value.values():
            changes += update(child, version, commit)
    elif isinstance(value, list):
        for child in value:
            changes += update(child, version, commit)
    return changes


def main() -> None:
    golden_dir = Path(sys.argv[1])
    version = sys.argv[2]
    commit = sys.argv[3]
    changes = 0
    for path in golden_dir.rglob("*.json"):
        value = json.loads(path.read_text())
        file_changes = update(value, version, commit)
        if file_changes:
            path.write_text(json.dumps(value, indent=2) + "\n")
            changes += file_changes
    if not changes:
        raise SystemExit("No supported rcpchgrowth provenance found in downstream goldens")
    print(f"Normalized {changes} downstream provenance records")


if __name__ == "__main__":
    main()
