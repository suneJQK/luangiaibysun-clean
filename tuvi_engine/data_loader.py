"""Load V2 data catalogs without coupling callers to repository paths."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_star_registry() -> dict[str, Any]:
    return load_json("data/stars.json")


def load_engine_config() -> dict[str, Any]:
    return load_json("data/tu_vi_engine.json")


def load_cach_cuc() -> list[dict[str, Any]]:
    data = load_json("data/cach_cuc.json")
    if not isinstance(data, list):
        return []

    # Keep the rich source file intact while allowing verified rule corrections
    # to be versioned separately and applied deterministically at runtime.
    overrides = load_json("data/cach_cuc_overrides.json")
    if isinstance(overrides, dict):
        merged: list[dict[str, Any]] = []
        for item in data:
            current = dict(item)
            replacement = overrides.get(str(item.get("id")))
            if isinstance(replacement, dict):
                current["conditions"] = replacement
            merged.append(current)
        return merged

    return data
