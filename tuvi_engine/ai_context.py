"""Build a compact, deterministic context payload for AI interpretation."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .data_loader import load_cach_cuc, load_json


_RELATION_DATA = load_json("data/relationships_ai.json")


def load_relationship_knowledge() -> dict[str, Any]:
    return deepcopy(_RELATION_DATA)


def _index_cach_cuc(items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {
        int(item["id"]): item
        for item in items
        if isinstance(item, dict) and item.get("id") is not None
    }


def _normalize_matched_cach_cuc(chart: dict[str, Any], catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index = _index_cach_cuc(catalog)
    matched = chart.get("cach_cuc", [])
    result: list[dict[str, Any]] = []

    if not isinstance(matched, list):
        return result

    for item in matched:
        if isinstance(item, int) and item in index:
            result.append(deepcopy(index[item]))
        elif isinstance(item, dict):
            item_id = item.get("id")
            if item_id is not None and int(item_id) in index:
                base = deepcopy(index[int(item_id)])
                base.update(deepcopy(item))
                result.append(base)
            else:
                result.append(deepcopy(item))

    return result


def build_ai_context(chart: dict[str, Any]) -> dict[str, Any]:
    """Combine chart structure, relationship knowledge and Cách Cục catalog.

    The function does not invent interpretation. It only packages source data
    so a downstream AI model can reason from explicit evidence.
    """
    if not isinstance(chart, dict):
        raise TypeError("chart phải là dict")

    cach_cuc_catalog = load_cach_cuc()
    context: dict[str, Any] = {
        "schema_version": "2.0-ai-context",
        "input": deepcopy(chart.get("input", {})),
        "thien_ban": deepcopy(chart.get("thien_ban", {})),
        "palaces": deepcopy(chart.get("12_cung", chart.get("dia_ban", []))),
        "relationship_knowledge": load_relationship_knowledge(),
        "matched_cach_cuc": _normalize_matched_cach_cuc(chart, cach_cuc_catalog),
        "reasoning_contract": {
            "use_only_provided_relations": True,
            "use_only_matched_cach_cuc": True,
            "do_not_invent_missing_stars_or_relations": True,
            "separate_facts_from_interpretation": True,
        },
    }
    return context


__all__ = ["build_ai_context", "load_relationship_knowledge"]
